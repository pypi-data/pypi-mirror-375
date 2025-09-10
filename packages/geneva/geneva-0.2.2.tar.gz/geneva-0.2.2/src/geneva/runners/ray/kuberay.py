import hashlib
import logging
import random
from collections import Counter
from typing import Any, Optional, TypedDict

import attrs
import ray
from kubernetes import client
from kubernetes import config as kube_config

from geneva.config import ConfigBase
from geneva.eks import _KUBE_API_CLIENT

_LOG = logging.getLogger(__name__)

KUBERAY_API_GROUP = "ray.io"  # API group for KubeRay RayCluster CRD
KUBERAY_API_VERSION = "v1"  # CRD version
KUBERAY_API_GROUP_VERSION = f"{KUBERAY_API_GROUP}/{KUBERAY_API_VERSION}"
KUBERAY_JOB_API_KIND = "RayJob"
KUBERAY_JOB_API_NAME = "rayjobs"
KUBERAY_CLUSTER_PLURAL = "rayclusters"  # lowercase, plural form of the kind
GENEVA_NAMESPACE = "geneva"  # namespace where your clusters live


@attrs.define
class KuberayConfig(ConfigBase):
    checkpoint_store: str = attrs.field()
    ray_version: str = attrs.field()
    namespace: str = attrs.field(default="lancedb")
    worker_min_replicas: int = attrs.field(default=0)
    worker_max_replicas: int = attrs.field(default=10)

    @classmethod
    def name(cls) -> str:
        return "kuberay"


def launch_kuberay_job(
    db_uri: str,
    table_name: str,
    column: str,
    image: str,
    kuberay_config: KuberayConfig,
) -> None:
    # TODO api docs explaining the args supposed to be passed
    try:
        kube_config.load_kube_config()
    except Exception:
        kube_config.load_incluster_config()

    # note: this depends on prior call to build_api_client
    # and might be subject to race conditions
    api = client.CustomObjectsApi(api_client=_KUBE_API_CLIENT)

    job_definition = {
        "apiVersion": KUBERAY_API_GROUP_VERSION,
        "kind": KUBERAY_JOB_API_KIND,
        "metadata": {
            "name": generate_job_name(db_uri, table_name, column),
            "namespace": kuberay_config.namespace,
        },
        "spec": {
            "entrypoint": f"python3 -m geneva.runners.ray --db_uri {db_uri} --table_name {table_name} --column {column} --checkpoint_store {kuberay_config.checkpoint_store}",  # noqa E501
            "rayClusterSpec": {
                "rayVersion": kuberay_config.namespace,
                "headGroupSpec": {
                    "rayStartParams": {},
                    "template": {
                        "spec": {
                            "containers": [
                                {
                                    "name": "ray-head",
                                    "image": image,
                                    "imagePullPolicy": "IfNotPresent",
                                    "ports": [
                                        {
                                            "containerPort": 10001,
                                            "name": "client",
                                            "protocol": "TCP",
                                        },
                                        {
                                            "containerPort": 8265,
                                            "name": "dashboard",
                                            "protocol": "TCP",
                                        },
                                        {
                                            "containerPort": 6379,
                                            "name": "gsc-server",
                                            "protocol": "TCP",
                                        },
                                    ],
                                }
                            ]
                        }
                    },
                },
                "workerGroupSpecs": [
                    {
                        "groupName": "worker-group-1",
                        "minReplicas": kuberay_config.worker_min_replicas,
                        "maxReplicas": kuberay_config.worker_max_replicas,
                        "rayStartParams": {},
                        "template": {
                            "spec": {
                                "containers": [
                                    {
                                        "name": "ray-worker",
                                        "image": image,
                                        "imagePullPolicy": "IfNotPresent",
                                    }
                                ]
                            }
                        },
                    }
                ],
            },
        },
    }

    api.create_namespaced_custom_object(
        group=KUBERAY_API_GROUP,
        version=KUBERAY_API_VERSION,
        namespace=kuberay_config.namespace,
        plural=KUBERAY_JOB_API_NAME,
        body=job_definition,
    )


def generate_job_name(
    db_uri: str,
    table_name: str,
    column: str,
) -> str:
    db_name = db_uri.split("/")[-1]
    seed = random.randint(0, 1000000)
    job_name = f"ray-geneva-{db_name[:6]}-{table_name[6]}-{column[:6]}-{hashlib.md5(str(seed).encode()).hexdigest()[:6]}"  # noqa E501
    return job_name


def _ray_status() -> dict[str, any]:
    """Check the status of the compute cluster
    Checks ray actors, ray and k8s to show progress
    """
    status: dict[str, any] = {
        "cnt_ray_nodes": 0,
        "cnt_geneva_workers_active": 0,
        "cnt_geneva_workers_pending": 0,
    }

    try:
        # of machines in ray cluster
        nodes = ray.nodes()
        live_nodes = [n for n in nodes if n["Alive"]]
        status["cnt_ray_nodes"] = len(live_nodes)
    except Exception as e:
        _LOG.exception("Problem listing ray nodes")
        status["ray_nodes_error"] = e

    try:
        # this requires connecting to the ray dashboard
        from ray.util.state import list_actors

        actors = list_actors()
        live_actors = [a for a in actors if a.state == "ALIVE"]
        live_applier_actors = [
            a.actor_id for a in live_actors if a.class_name == "ApplierActor"
        ]
        status["cnt_geneva_workers_active"] = len(live_applier_actors)

        pending_actors = [a for a in actors if a.state == "PENDING_CREATION"]
        pending_applier_actors = [
            a.actor_id for a in pending_actors if a.class_name == "ApplierActor"
        ]
        status["cnt_geneva_workers_pending"] = len(pending_applier_actors)
    except Exception as e:
        _LOG.exception("Problem listing actors")
        status["geneva_workers_error"] = e

    _LOG.debug(f"cluster status: {status}")
    return status


class PodStatus(TypedDict):
    name: str
    phase: str  # Pending | Running | Succeeded | Failed | Unknown
    ready: bool
    node_type: str | None  # head | worker | None (if unlabeled)
    node_name: str | None
    waiting_reasons: Counter[str]  # main containers
    init_waiting_reasons: Counter[str]  # init containers
    pulling_count: int  # total containers currently "Pulling..."
    gpu_requested: bool
    node_is_gpu: bool | None


# Which extended resources count as "GPU"
_GPU_KEYS = ("nvidia.com/gpu", "amd.com/gpu", "intel.com/gpu")


def _qty_gt_zero(q: Any) -> bool:
    try:
        # K8s quantities for extended resources are ints (e.g. "1")
        return int(q) > 0
    except Exception:
        return False


def _container_wants_gpu(c: client.V1Container) -> bool:
    r = c.resources or client.V1ResourceRequirements()
    for d in (r.limits or {}), (r.requests or {}):
        for k in _GPU_KEYS:
            if k in d and _qty_gt_zero(d[k]):
                return True
    return False


def _pod_requests_gpu(pod: client.V1Pod) -> bool:
    spec = pod.spec
    if not spec:
        return False
    for c in spec.init_containers or []:
        if _container_wants_gpu(c):
            return True
    return any(_container_wants_gpu(c) for c in spec.containers or [])


def _node_is_gpu(v1: client.CoreV1Api, node_name: str, cache: dict[str, bool]) -> bool:
    if node_name in cache:
        return cache[node_name]
    try:
        n = v1.read_node(node_name)
        alloc = n.status.allocatable or {}
        has_gpu = any(_qty_gt_zero(alloc.get(k)) for k in _GPU_KEYS)
    except Exception:
        has_gpu = False
    cache[node_name] = has_gpu
    return has_gpu


def k8s_status(namespace: str = "geneva") -> list[PodStatus]:
    # Load your kubeconfig (or in-cluster config if running inside Kubernetes)
    try:
        kube_config.load_kube_config()
    except Exception:
        kube_config.load_incluster_config()

    # Instantiate CoreV1Api (ignore custom api_client if None)
    core_api = client.CoreV1Api(api_client=_KUBE_API_CLIENT)

    # List all pods in the namespace
    pods = core_api.list_namespaced_pod(namespace)

    # Filter Ray pods by label (adjust depending on your RayCluster setup)
    ray_pods = [
        pod
        for pod in pods.items
        if pod.metadata
        and pod.metadata.labels
        and "ray.io/node-type" in pod.metadata.labels
    ]

    # Summarize pod phases and conditions
    node_gpu_cache: dict[str, bool] = {}
    out: list[PodStatus] = []
    for pod in ray_pods:
        phase: str = pod.status.phase or "Unknown"
        conds: list[client.V1PodCondition] = pod.status.conditions or []
        cond_map = {c.type: c.status for c in conds}

        waiting: Counter[str] = Counter()
        init_waiting: Counter[str] = Counter()
        pulling_count = 0

        # Init containers
        for cs in pod.status.init_container_statuses or []:
            st = cs.state
            if st and st.waiting:
                reason = st.waiting.reason or "Waiting"
                init_waiting[reason] += 1
                if reason.lower().startswith("pull"):
                    pulling_count += 1

        # Main containers
        for cs in pod.status.container_statuses or []:
            st = cs.state
            if st and st.waiting:
                reason = st.waiting.reason or "Waiting"
                waiting[reason] += 1
                if reason.lower().startswith("pull"):
                    pulling_count += 1

        node_name = pod.spec.node_name if pod.spec else None
        node_is_gpu = (
            _node_is_gpu(core_api, node_name, node_gpu_cache) if node_name else None
        )

        out.append(
            PodStatus(
                name=pod.metadata.name,
                phase=phase,
                ready=(cond_map.get("Ready") == "True"),
                node_type=pod.metadata.labels.get("ray.io/node-type"),
                node_name=pod.spec.node_name if pod.spec else None,
                waiting_reasons=waiting,
                init_waiting_reasons=init_waiting,
                pulling_count=pulling_count,
                gpu_requested=_pod_requests_gpu(pod),
                node_is_gpu=node_is_gpu,
            )
        )
    return out


def _node_ready_split_for(pod_statuses: list[PodStatus]) -> tuple[int, int, int, int]:
    """
    Returns (gpu_ready, gpu_notready, cpu_ready, cpu_notready)
    for nodes that host any of the provided pods.
    """
    v1 = client.CoreV1Api(api_client=_KUBE_API_CLIENT)
    nodes_seen: dict[str, bool] = {}  # node_name -> is_gpu
    ready_map: dict[str, bool] = {}  # node_name -> Ready True/False

    # collect unique node names from these pods
    node_names = {s["node_name"] for s in pod_statuses if s["node_name"]}

    # read node objects once
    for name in node_names:
        try:
            n = v1.read_node(name)
            conds = {c.type: c.status for c in (n.status.conditions or [])}
            is_ready = conds.get("Ready") == "True"
            alloc = n.status.allocatable or {}
            is_gpu = any(_qty_gt_zero(alloc.get(k)) for k in _GPU_KEYS)
            nodes_seen[name] = is_gpu
            ready_map[name] = is_ready
        except Exception:  # noqa PERF203
            # if we can’t read, treat as not ready & cpu
            nodes_seen[name] = False
            ready_map[name] = False

    gpu_ready = gpu_notready = cpu_ready = cpu_notready = 0
    for name, is_gpu in nodes_seen.items():
        if ready_map.get(name, False):
            if is_gpu:
                gpu_ready += 1
            else:
                cpu_ready += 1
        else:
            if is_gpu:
                gpu_notready += 1
            else:
                cpu_notready += 1
    return gpu_ready, gpu_notready, cpu_ready, cpu_notready


def kuberay_cluster_status(namespace: str, name: str) -> Optional[dict[str, Any]]:
    try:
        co = client.CustomObjectsApi(api_client=_KUBE_API_CLIENT)
        obj = co.get_namespaced_custom_object(
            group="ray.io",
            version="v1",
            namespace=namespace,
            plural="rayclusters",
            name=name,
        )
        return obj.get("status")
    except Exception:
        return None


class WorkerGroupBrief(TypedDict):
    name: str
    desired: int
    ready: int


class KuberaySummary(TypedDict):
    phase: (
        str  # "nodes-provisioning" | "pods-creating" | "cluster-cold" | "cluster-warm"
    )
    phase_idx: int  # monotonically increasing index for your progress bar
    pending: int
    running: int
    workers_ready: int
    waits_top3: list[tuple[str, int]]
    pulling: int
    total_pods: int

    # kuberay
    kr_state: str | None
    kr_desired_workers: int | None
    kr_available_workers: int | None
    kr_last_update: str | None
    kr_scaling: str | None  # "up" | "down" | "steady" | None
    kr_groups: list[WorkerGroupBrief]  # per workger-group ready/desired
    kr_last_condition: tuple[str, str] | None  # reason, type if present

    # pod splits
    pods_gpu_running: int
    pods_gpu_pending: int
    pods_cpu_running: int
    pods_cpu_pending: int
    workers_ready_gpu: int
    workers_ready_cpu: int

    # node splits (only nodes hosting this cluster’s pods)
    nodes_gpu_ready: int
    nodes_gpu_notready: int
    nodes_cpu_ready: int
    nodes_cpu_notready: int


def _get_int(d: dict[str, Any], *keys: str) -> Optional[int]:
    for k in keys:
        v = d.get(k)
        if isinstance(v, int):
            return v
    return None


def _parse_worker_groups(status: dict[str, Any]) -> list[WorkerGroupBrief]:
    out: list[WorkerGroupBrief] = []
    # Newer KubeRay surfaces workerGroupStatuses; older embeds in spec/status
    # differently
    wgs = status.get("workerGroupStatuses") or []
    for item in wgs:
        name = item.get("groupName") or item.get("name") or "worker"
        desired = _get_int(item, "desiredReplicas", "replicas", "desired") or 0
        ready = _get_int(item, "readyReplicas", "availableReplicas", "ready") or 0
        out.append(WorkerGroupBrief(name=name, desired=desired, ready=ready))
    return out


def _parse_scaling(status: dict[str, Any]) -> Optional[str]:
    # Heuristic: desired vs available (or ready) tells the story
    desired = _get_int(status, "desiredWorkerReplicas", "desiredWorkerCount")
    avail = _get_int(status, "availableWorkerReplicas", "availableWorkerCount")
    if desired is None or avail is None:
        return None
    if desired > avail:
        return "up"
    if desired < avail:
        return "down"
    return "steady"


def _last_condition(status: dict[str, Any]) -> Optional[tuple[str, str]]:
    # Surfaces *some* operator condition, if present
    conds = status.get("conditions") or []
    if not isinstance(conds, list) or not conds:
        return None
    last = conds[-1]
    reason = str(last.get("reason") or "?")
    typ = str(last.get("type") or "?")
    return (reason, typ)


def summarize_k8s(
    statuses: list[PodStatus], cluster_name: str, namespace: str = "geneva"
) -> KuberaySummary:
    phases = Counter(s["phase"] for s in statuses)
    waits = Counter()
    pulling = 0
    workers_ready = 0
    workers_ready_gpu = 0
    workers_ready_cpu = 0
    pods_gpu_running = pods_gpu_pending = 0
    pods_cpu_running = pods_cpu_pending = 0

    for s in statuses:
        waits.update(s["waiting_reasons"])
        waits.update(s["init_waiting_reasons"])
        pulling += s["pulling_count"]
        if s["node_type"] == "worker" and s["phase"] == "Running" and s["ready"]:
            workers_ready += 1
            if s.get("gpu_requested"):
                workers_ready_gpu += 1
            else:
                workers_ready_cpu += 1

        # pod splits by GPU/CPU and phase
        is_gpu = bool(s.get("gpu_requested"))
        if s["phase"] == "Running":
            if is_gpu:
                pods_gpu_running += 1
            else:
                pods_cpu_running += 1
        elif s["phase"] == "Pending":
            if is_gpu:
                pods_gpu_pending += 1
            else:
                pods_cpu_pending += 1

    # Phase selection focused on “cold start” (= no workers ready yet)
    if phases["Pending"] > 0 and any(
        k.lower().startswith(("unschedulable", "waiting")) for k in waits
    ):
        phase, phase_idx = "nodes-provisioning", 1
    elif pulling > 0 or any(k.lower().startswith("containercreating") for k in waits):
        phase, phase_idx = "pods-creating", 2
    elif workers_ready == 0:
        phase, phase_idx = "cluster-cold", 3
    else:
        phase, phase_idx = "cluster-warm", 4

    kr_status = kuberay_cluster_status(namespace, cluster_name)
    if kr_status is None:
        _LOG.warning(
            f"Could not fetch KubeRay status for {namespace}/{cluster_name}..."
        )
        kr_status = {}

    desired = _get_int(kr_status, "desiredWorkerReplicas", "desiredWorkerCount")
    avail = _get_int(kr_status, "availableWorkerReplicas", "availableWorkerCount")
    groups = _parse_worker_groups(kr_status)
    scaling = _parse_scaling(kr_status)
    last_cond = _last_condition(kr_status)

    # Node readiness split (only nodes hosting our Ray pods)
    nodes_gpu_ready, nodes_gpu_notready, nodes_cpu_ready, nodes_cpu_notready = (
        _node_ready_split_for(statuses)
    )

    def _int_or_none(v: Any) -> int | None:
        return int(v) if isinstance(v, int) else None

    return KuberaySummary(
        phase=phase,
        phase_idx=phase_idx,
        pending=phases.get("Pending", 0),
        running=phases.get("Running", 0),
        workers_ready=workers_ready,
        waits_top3=waits.most_common(3),
        pulling=pulling,
        total_pods=len(statuses),
        kr_state=kr_status.get("state"),
        kr_desired_workers=_int_or_none(desired),
        kr_available_workers=_int_or_none(avail),
        kr_last_update=kr_status.get("lastUpdateTime"),
        kr_scaling=scaling,
        kr_groups=groups,
        kr_last_condition=last_cond,
        # NEW pod splits
        pods_gpu_running=pods_gpu_running,
        pods_gpu_pending=pods_gpu_pending,
        pods_cpu_running=pods_cpu_running,
        pods_cpu_pending=pods_cpu_pending,
        workers_ready_gpu=workers_ready_gpu,
        workers_ready_cpu=workers_ready_cpu,
        # NEW node splits
        nodes_gpu_ready=nodes_gpu_ready,
        nodes_gpu_notready=nodes_gpu_notready,
        nodes_cpu_ready=nodes_cpu_ready,
        nodes_cpu_notready=nodes_cpu_notready,
    )


def summarize_kuberay_status(
    namespace: str | None, cluster_name: str | None
) -> KuberaySummary:
    k8s_statuses = k8s_status(namespace=namespace)
    k8s_summary = summarize_k8s(
        k8s_statuses, cluster_name=cluster_name, namespace=namespace
    )
    return k8s_summary
