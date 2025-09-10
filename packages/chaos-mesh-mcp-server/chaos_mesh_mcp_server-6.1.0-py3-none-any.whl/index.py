"""
Chaos Mesh MCP Server - Remote Cluster Management
MCP server that enables AI agents to perform chaos engineering through Chaos Mesh on EKS clusters
"""

import asyncio
import json
import os
import time
from typing import Any, Dict, List, Optional

import mcp.server.stdio
import mcp.types as types
from mcp.server.fastmcp import FastMCP

from chaos.remote_cluster_manager import get_remote_cluster_manager
from k8s.cluster_manager import cluster_manager
from utils.config import ClusterConfig
from utils.logger import get_logger, setup_logging

# Logging setup
setup_logging()
logger = get_logger(__name__)

# MCP server instance
mcp = FastMCP("chaos-mesh-mcp")
remote_manager = None  # RemoteChaosManager instance
_initialization_complete = False  # Initialization complete flag


class RemoteChaosManager:
    """Integrated Remote Chaos Manager"""

    def __init__(self):
        self.remote_manager = get_remote_cluster_manager()

    async def initialize(self) -> None:
        """Initialize Remote Chaos Manager"""
        try:
            logger.info("initializing_remote_chaos_manager")

            await cluster_manager.initialize()

            await self.remote_manager.initialize()

            logger.info("remote_chaos_manager_initialized")

        except Exception as e:
            logger.error("remote_chaos_manager_init_failed", error=str(e))
            raise

    async def add_remote_cluster_by_name(
        self, cluster_name: str, region: str, role_arn: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add remote cluster by cluster name (reusing EKSManager functionality from test.py)"""
        try:
            logger.info(
                "adding_remote_cluster_by_name", cluster=cluster_name, region=region
            )

            # Create ClusterConfig
            cluster_config = ClusterConfig(
                name=cluster_name, region=region, role_arn=role_arn
            )

            # Add remote cluster
            result = await self.remote_manager.add_remote_cluster(cluster_config)

            if result["success"]:
                logger.info("remote_cluster_added_successfully", cluster=cluster_name)

                # Print cluster information
                await self._print_cluster_info(cluster_name)

            return result

        except Exception as e:
            logger.error(
                "add_remote_cluster_failed", cluster=cluster_name, error=str(e)
            )
            return {"success": False, "error": str(e)}

    async def install_chaos_mesh_on_cluster(
        self, cluster_name: str, namespace: str = "chaos-mesh"
    ) -> Dict[str, Any]:
        """Install Chaos Mesh on remote cluster (reusing install_chaos_mesh functionality from test.py)"""
        try:
            logger.info(
                "installing_chaos_mesh", cluster=cluster_name, namespace=namespace
            )

            result = await self.remote_manager.install_chaos_mesh_on_remote(
                cluster_name, namespace
            )

            if result["success"]:
                print(f"\n✅ Chaos Mesh installation completed: {cluster_name}")
                print("=" * 60)

                if "dashboard_info" in result:
                    dashboard_info = result["dashboard_info"]
                    if "error" not in dashboard_info:
                        print("🌐 Chaos Mesh Dashboard Access Information:")
                        print(f"   Service Name: {dashboard_info['service_name']}")
                        print(f"   Port: {dashboard_info['port']}")
                        print(f"   Namespace: {dashboard_info['namespace']}")
                        print("\n🚀 Access Method:")
                        print(f"   {dashboard_info['port_forward_command']}")
                        print(f"   Access {dashboard_info['access_url']} in browser")
                    else:
                        print(
                            f"⚠️ Dashboard information query failed: {dashboard_info['error']}"
                        )

                if "status" in result:
                    status = result["status"]
                    print("\n📊 Installation Status:")
                    print(f"   CRD Count: {status.get('crd_count', 0)}")
                    print(f"   Controller Count: {status.get('controller_count', 0)}")
                    print(
                        f"   Namespace Exists: {status.get('namespace_exists', False)}"
                    )

            return result

        except Exception as e:
            logger.error(
                "chaos_mesh_install_failed", cluster=cluster_name, error=str(e)
            )
            return {"success": False, "error": str(e)}

    async def create_pod_chaos_experiment(
        self,
        cluster_name: str,
        namespace: str = "default",
        target_app: str = "nginx",
        action: str = "pod-kill",
        duration: str = "60s",
        mode: str = "one",
    ) -> Dict[str, Any]:
        """Create Pod Chaos experiment (reusing create_pod_chaos_experiment functionality from test.py)"""
        try:
            logger.info(
                "creating_pod_chaos_experiment",
                cluster=cluster_name,
                target=target_app,
                action=action,
            )

            experiment_config = {
                "namespace": namespace,
                "selector": {"labelSelectors": {"app": target_app}},
                "action": action,
                "mode": mode,
                "duration": duration,
            }

            result = await self.remote_manager.create_remote_experiment(
                cluster_name,
                "pod_chaos",
                experiment_config,
            )

            if result["success"]:
                print("\n🧪 Pod Chaos experiment creation completed")
                print("=" * 50)
                print(f"   Experiment ID: {result['experiment_id']}")
                print(f"   Cluster: {cluster_name}")
                print(f"   Target: {target_app} (namespace: {namespace})")
                print(f"   Action: {action}")
                print(f"   Duration: {duration}")
                print(f"   Mode: {mode}")

            return result

        except Exception as e:
            logger.error(
                "pod_chaos_experiment_failed",
                cluster=cluster_name,
                target=target_app,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def create_network_chaos_experiment(
        self,
        cluster_name: str,
        namespace: str = "default",
        target_app: str = "nginx",
        action: str = "delay",
        duration: str = "60s",
        delay: str = "100ms",
        loss: str = "10",
    ) -> Dict[str, Any]:
        """Create Network Chaos experiment (reusing create_network_chaos_experiment functionality from test.py)"""
        try:
            logger.info(
                "creating_network_chaos_experiment",
                cluster=cluster_name,
                target=target_app,
                action=action,
            )

            experiment_config = {
                "namespace": namespace,
                "selector": {"labelSelectors": {"app": target_app}},
                "action": action,
                "mode": "one",
                "duration": duration,
            }

            # Additional settings by action
            if action == "delay":
                experiment_config["delay"] = {
                    "latency": delay,
                    "correlation": "100",
                    "jitter": "0ms",
                }
            elif action == "loss":
                experiment_config["loss"] = {"loss": loss, "correlation": "100"}

            result = await self.remote_manager.create_remote_experiment(
                cluster_name, "network_chaos", experiment_config
            )

            if result["success"]:
                print("\n🌐 Network Chaos experiment creation completed")
                print("=" * 50)
                print(f"   Experiment ID: {result['experiment_id']}")
                print(f"   Cluster: {cluster_name}")
                print(f"   Target: {target_app} (namespace: {namespace})")
                print(f"   Action: {action}")
                print(f"   Duration: {duration}")
                if action == "delay":
                    print(f"   Delay: {delay}")
                elif action == "loss":
                    print(f"   Packet Loss: {loss}%")

            return result

        except Exception as e:
            logger.error(
                "network_chaos_experiment_failed",
                cluster=cluster_name,
                target=target_app,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def create_stress_chaos_experiment(
        self,
        cluster_name: str,
        namespace: str = "default",
        target_app: str = "nginx",
        duration: str = "60s",
        cpu_workers: int = 1,
        memory_workers: int = 1,
        memory_size: str = "256MB",
    ) -> Dict[str, Any]:
        """Create Stress Chaos experiment (reusing create_stress_chaos_experiment functionality from test.py)"""
        try:
            logger.info(
                "creating_stress_chaos_experiment",
                cluster=cluster_name,
                target=target_app,
            )

            experiment_config = {
                "namespace": namespace,
                "selector": {"labelSelectors": {"app": target_app}},
                "mode": "one",
                "duration": duration,
                "stressors": {
                    "cpu": {"workers": cpu_workers, "load": 100},
                    "memory": {"workers": memory_workers, "size": memory_size},
                },
            }

            result = await self.remote_manager.create_remote_experiment(
                cluster_name, "stress_chaos", experiment_config
            )

            if result["success"]:
                print("\n💪 Stress Chaos experiment creation completed")
                print("=" * 50)
                print(f"   Experiment ID: {result['experiment_id']}")
                print(f"   Cluster: {cluster_name}")
                print(f"   Target: {target_app} (namespace: {namespace})")
                print(f"   Duration: {duration}")
                print(f"   CPU Workers: {cpu_workers}")
                print(f"   Memory Workers: {memory_workers}")
                print(f"   Memory Size: {memory_size}")

            return result

        except Exception as e:
            logger.error(
                "stress_chaos_experiment_failed",
                cluster=cluster_name,
                target=target_app,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def create_io_chaos_experiment(
        self,
        cluster_name: str,
        namespace: str = "default",
        target_app: str = "nginx",
        action: str = "latency",
        duration: str = "60s",
        volume_path: str = "/tmp",
        delay: str = "100ms",
    ) -> Dict[str, Any]:
        """Create IO Chaos experiment"""
        try:
            experiment_config = {
                "namespace": namespace,
                "selector": {"labelSelectors": {"app": target_app}},
                "action": action,
                "mode": "one",
                "duration": duration,
                "volumePath": volume_path,
                "delay": delay,
                "percent": 50,
            }

            result = await self.remote_manager.create_remote_experiment(
                cluster_name, "io_chaos", experiment_config
            )

            if result["success"]:
                print("\n💾 IO Chaos experiment creation completed")
                print("=" * 50)
                print(f"   Experiment ID: {result['experiment_id']}")
                print(f"   Cluster: {cluster_name}")
                print(f"   Target: {target_app} (namespace: {namespace})")
                print(f"   Action: {action}")
                print(f"   Volume Path: {volume_path}")
                print(f"   Delay: {delay}")

            return result

        except Exception as e:
            logger.error(
                "io_chaos_experiment_failed",
                cluster=cluster_name,
                target=target_app,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def create_dns_chaos_experiment(
        self,
        cluster_name: str,
        namespace: str = "default",
        target_app: str = "nginx",
        action: str = "random",
        duration: str = "60s",
        patterns: List[str] = None,
        delay: str = "100ms",
    ) -> Dict[str, Any]:
        """Create DNS Chaos experiment"""
        try:
            if patterns is None:
                patterns = ["google.com"]

            experiment_config = {
                "namespace": namespace,
                "selector": {"labelSelectors": {"app": target_app}},
                "action": action,
                "mode": "one",
                "duration": duration,
                "patterns": patterns,
            }

            if action == "delay":
                experiment_config["delay"] = delay

            result = await self.remote_manager.create_remote_experiment(
                cluster_name, "dns_chaos", experiment_config
            )

            if result["success"]:
                print("\n🌐 DNS Chaos experiment creation completed")
                print("=" * 50)
                print(f"   Experiment ID: {result['experiment_id']}")
                print(f"   Cluster: {cluster_name}")
                print(f"   Target: {target_app} (namespace: {namespace})")
                print(f"   Action: {action}")
                print(f"   Patterns: {', '.join(patterns)}")

            return result

        except Exception as e:
            logger.error(
                "dns_chaos_experiment_failed",
                cluster=cluster_name,
                target=target_app,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def create_time_chaos_experiment(
        self,
        cluster_name: str,
        namespace: str = "default",
        target_app: str = "nginx",
        duration: str = "60s",
        time_offset: str = "-10m",
    ) -> Dict[str, Any]:
        """Create Time Chaos experiment"""
        try:
            experiment_config = {
                "namespace": namespace,
                "selector": {"labelSelectors": {"app": target_app}},
                "mode": "one",
                "duration": duration,
                "timeOffset": time_offset,
            }

            result = await self.remote_manager.create_remote_experiment(
                cluster_name, "time_chaos", experiment_config
            )

            if result["success"]:
                print("\n⏰ Time Chaos experiment creation completed")
                print("=" * 50)
                print(f"   Experiment ID: {result['experiment_id']}")
                print(f"   Cluster: {cluster_name}")
                print(f"   Target: {target_app} (namespace: {namespace})")
                print(f"   Time Offset: {time_offset}")

            return result

        except Exception as e:
            logger.error(
                "time_chaos_experiment_failed",
                cluster=cluster_name,
                target=target_app,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def list_remote_clusters(self) -> List[Dict[str, Any]]:
        """List remote clusters"""
        try:
            clusters = self.remote_manager.list_remote_clusters()

            if clusters:
                print(f"\n📋 Remote cluster list ({len(clusters)} clusters)")
                print("=" * 80)

                for cluster in clusters:
                    status_emoji = {
                        "connected": "🟢",
                        "disconnected": "🔴",
                        "unhealthy": "🟡",
                    }.get(cluster["status"], "❓")

                    chaos_emoji = "✅" if cluster["chaos_mesh_installed"] else "❌"

                    print(f"{status_emoji} {cluster['name']}")
                    print(f"   Region: {cluster['region']}")
                    print(f"   Status: {cluster['status']}")
                    print(
                        f"   Chaos Mesh: {chaos_emoji} {'Installed' if cluster['chaos_mesh_installed'] else 'Not Installed'}"
                    )
                    print(f"   Added Time: {time.ctime(cluster['added_at'])}")
                    print()
            else:
                print("📋 No registered remote clusters.")

            return clusters

        except Exception as e:
            logger.error("list_remote_clusters_failed", error=str(e))
            return []

    async def get_cluster_pods(
        self, cluster_name: str, namespace: str = None
    ) -> List[Dict[str, Any]]:
        """Get cluster Pod list (reusing get_pod_status functionality from test.py)"""
        try:
            k8s_client = cluster_manager.get_k8s_client(cluster_name)
            if not k8s_client:
                return []

            from kubernetes import client

            core_v1 = client.CoreV1Api(k8s_client)

            if namespace:
                pods_response = core_v1.list_namespaced_pod(namespace=namespace)
            else:
                pods_response = core_v1.list_pod_for_all_namespaces()

            pods_info = []
            for pod in pods_response.items:
                pod_info = {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "node": pod.spec.node_name,
                    "created": pod.metadata.creation_timestamp.isoformat()
                    if pod.metadata.creation_timestamp
                    else None,
                    "labels": pod.metadata.labels or {},
                    "restart_count": sum(
                        container_status.restart_count
                        for container_status in (pod.status.container_statuses or [])
                    ),
                    "containers": len(pod.spec.containers)
                    if pod.spec.containers
                    else 0,
                    "ready_containers": sum(
                        1
                        for container_status in (pod.status.container_statuses or [])
                        if container_status.ready
                    ),
                }
                pods_info.append(pod_info)

            return pods_info

        except Exception as e:
            logger.error("get_cluster_pods_failed", cluster=cluster_name, error=str(e))
            return []

    def print_pods_summary(self, cluster_name: str, pods: List[Dict[str, Any]]):
        """Print Pod Summary"""
        if not pods:
            print(f"📋 No pods found in cluster '{cluster_name}'.")
            return

        print(f"\n📋 Cluster '{cluster_name}' Pod Status Summary (Total: {len(pods)})")
        print("=" * 80)

        # Group by namespace
        namespace_groups = {}
        for pod in pods:
            ns = pod["namespace"]
            if ns not in namespace_groups:
                namespace_groups[ns] = []
            namespace_groups[ns].append(pod)

        for namespace, ns_pods in namespace_groups.items():
            print(f"\n🏷️  Namespace: {namespace} ({len(ns_pods)} pods)")
            print("-" * 60)

            for pod in ns_pods:
                status_emoji = {
                    "Running": "🟢",
                    "Pending": "🟡",
                    "Failed": "🔴",
                    "Succeeded": "✅",
                    "Unknown": "❓",
                }.get(pod["status"], "❓")

                print(f"  {status_emoji} {pod['name']}")
                print(f"    Status: {pod['status']}")
                print(
                    f"    Containers: {pod['ready_containers']}/{pod['containers']} Ready"
                )
                print(f"    Restarts: {pod['restart_count']} times")
                if pod.get("node"):
                    print(f"    Node: {pod['node']}")
                print()

    async def _print_cluster_info(self, cluster_name: str):
        """Print cluster information"""
        try:
            cluster_info = await cluster_manager.get_cluster_info(cluster_name)

            if cluster_info:
                print(f"\n📊 Cluster '{cluster_name}' Information")
                print("=" * 60)
                print(f"   Region: {cluster_info.get('aws_region', 'N/A')}")
                print(f"   Status: {cluster_info.get('status', 'N/A')}")
                print(
                    f"   Kubernetes Version: {cluster_info.get('kubernetes_version', 'N/A')}"
                )
                print(f"   Namespace Count: {cluster_info.get('namespace_count', 0)}")

                if cluster_info.get("cluster_info"):
                    ci = cluster_info["cluster_info"]
                    print(f"   Endpoint: {ci.get('endpoint', 'N/A')}")
                    print(f"   EKS Version: {ci.get('version', 'N/A')}")

                chaos_mesh_info = cluster_info.get("chaos_mesh_installed", {})
                if isinstance(chaos_mesh_info, dict):
                    print(
                        f"   Chaos Mesh Installed: {'✅' if chaos_mesh_info.get('installed', False) else '❌'}"
                    )
                    if chaos_mesh_info.get("installed"):
                        print(
                            f"   Chaos Mesh CRDs: {chaos_mesh_info.get('crd_count', 0)}"
                        )
                        print(
                            f"   Chaos Mesh Controllers: {chaos_mesh_info.get('controller_count', 0)}"
                        )

        except Exception as e:
            logger.error(
                "print_cluster_info_failed", cluster=cluster_name, error=str(e)
            )

    async def shutdown(self) -> None:
        """Remote Chaos Manager termination"""
        logger.info("shutting_down_remote_chaos_manager")

        await self.remote_manager.shutdown()
        await cluster_manager.shutdown()

        logger.info("remote_chaos_manager_shutdown_complete")


async def initialize_on_startup():
    """Singleton RemoteChaosManager initialization on startup"""
    global remote_manager, _initialization_complete

    if _initialization_complete:
        logger.info("initialization_already_complete")
        return

    try:
        remote_manager = RemoteChaosManager()

        await remote_manager.initialize()

        logger.info("chaos_mesh_mcp_managers_initialized")

        clusters_config = os.environ.get("CLUSTERS_CONFIG", "")
        predefined_remote_clusters = []

        if clusters_config:
            try:
                # Try JSON format first
                clusters_data = json.loads(clusters_config)
                if isinstance(clusters_data, list):
                    predefined_remote_clusters = clusters_data
                else:
                    logger.error("CLUSTERS_CONFIG JSON must be an array")
            except json.JSONDecodeError:
                # Fallback to legacy format: "cluster1:region1,cluster2:region2"
                for cluster_entry in clusters_config.split(","):
                    cluster_entry = cluster_entry.strip()
                    if ":" in cluster_entry:
                        name, region = cluster_entry.split(":", 1)
                        predefined_remote_clusters.append(
                            {
                                "name": name.strip(),
                                "region": region.strip(),
                            }
                        )

        for cluster_config in predefined_remote_clusters:
            cluster_name = cluster_config["name"]
            region = cluster_config["region"]

            result = await remote_manager.add_remote_cluster_by_name(
                cluster_name, region
            )

            if result["success"]:
                logger.info("predefined_cluster_added", cluster=cluster_name)
            else:
                logger.error(
                    "predefined_cluster_add_failed",
                    cluster=cluster_name,
                    error=result["error"],
                )

        _initialization_complete = True
        logger.info("chaos_mesh_mcp_initialization_complete")

    except Exception as e:
        logger.error("initialization_failed", error=str(e))
        remote_manager = None
        _initialization_complete = False
        raise


@mcp.tool()
async def _initialize_managers():
    """Initialize Managers (Avoid Duplicated Initialization)"""
    global remote_manager, _initialization_complete

    if _initialization_complete and remote_manager is not None:
        logger.info("managers_already_initialized")
        return

    await initialize_on_startup()


async def handle_list_tools() -> List[types.Tool]:
    """Return list of available tools"""
    logger.info("Handling list_tools request")

    tools = [
        types.Tool(
            name="add_remote_cluster",
            description="Add a remote cluster by cluster name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {
                        "type": "string",
                        "description": "EKS cluster name to add",
                    },
                    "region": {
                        "type": "string",
                        "description": "AWS region (e.g., us-west-2)",
                    },
                    "role_arn": {
                        "type": "string",
                        "description": "IAM Role ARN (optional)",
                    },
                },
                "required": ["cluster_name", "region"],
            },
        ),
        types.Tool(
            name="list_remote_clusters",
            description="List registered remote clusters.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="install_chaos_mesh",
            description="Install Chaos Mesh on a remote cluster.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {
                        "type": "string",
                        "description": "Target cluster name",
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace to install in",
                        "default": "chaos-mesh",
                    },
                },
                "required": ["cluster_name"],
            },
        ),
        types.Tool(
            name="get_cluster_pods",
            description="Get the list of pods in a cluster.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {"type": "string", "description": "Cluster name"},
                    "namespace": {
                        "type": "string",
                        "description": "Namespace (optional, omit for all namespaces)",
                    },
                },
                "required": ["cluster_name"],
            },
        ),
        types.Tool(
            name="create_pod_chaos_experiment",
            description="Create a Pod Chaos experiment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {
                        "type": "string",
                        "description": "Target cluster name",
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Target namespace",
                        "default": "default",
                    },
                    "target_app": {
                        "type": "string",
                        "description": "Target app label",
                        "default": "nginx",
                    },
                    "action": {
                        "type": "string",
                        "description": "Action type",
                        "enum": ["pod-kill", "pod-failure"],
                        "default": "pod-kill",
                    },
                    "duration": {
                        "type": "string",
                        "description": "Duration",
                        "default": "60s",
                    },
                    "mode": {
                        "type": "string",
                        "description": "Selection mode",
                        "enum": [
                            "one",
                            "all",
                            "fixed",
                            "fixed-percent",
                            "random-max-percent",
                        ],
                        "default": "one",
                    },
                },
                "required": ["cluster_name"],
            },
        ),
        types.Tool(
            name="create_network_chaos_experiment",
            description="Create a Network Chaos experiment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {
                        "type": "string",
                        "description": "Target cluster name",
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Target namespace",
                        "default": "default",
                    },
                    "target_app": {
                        "type": "string",
                        "description": "Target app label",
                        "default": "nginx",
                    },
                    "action": {
                        "type": "string",
                        "description": "Action type",
                        "enum": ["delay", "loss", "duplicate", "corrupt"],
                        "default": "delay",
                    },
                    "duration": {
                        "type": "string",
                        "description": "Duration",
                        "default": "60s",
                    },
                    "delay": {
                        "type": "string",
                        "description": "Delay time (for delay action)",
                        "default": "100ms",
                    },
                    "loss": {
                        "type": "string",
                        "description": "Packet loss rate (for loss action)",
                        "default": "10",
                    },
                },
                "required": ["cluster_name"],
            },
        ),
        types.Tool(
            name="create_stress_chaos_experiment",
            description="Create a Stress Chaos experiment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {
                        "type": "string",
                        "description": "Target cluster name",
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Target namespace",
                        "default": "default",
                    },
                    "target_app": {
                        "type": "string",
                        "description": "Target app label",
                        "default": "nginx",
                    },
                    "duration": {
                        "type": "string",
                        "description": "Duration",
                        "default": "60s",
                    },
                    "cpu_workers": {
                        "type": "integer",
                        "description": "Number of CPU workers",
                        "default": 1,
                    },
                    "memory_workers": {
                        "type": "integer",
                        "description": "Number of memory workers",
                        "default": 1,
                    },
                    "memory_size": {
                        "type": "string",
                        "description": "Memory size",
                        "default": "256MB",
                    },
                },
                "required": ["cluster_name"],
            },
        ),
        types.Tool(
            name="create_io_chaos_experiment",
            description="Create an IO Chaos experiment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {
                        "type": "string",
                        "description": "Target cluster name",
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Target namespace",
                        "default": "default",
                    },
                    "target_app": {
                        "type": "string",
                        "description": "Target app label",
                        "default": "nginx",
                    },
                    "action": {
                        "type": "string",
                        "description": "Action type",
                        "enum": ["latency", "fault", "attrOverride"],
                        "default": "latency",
                    },
                    "duration": {
                        "type": "string",
                        "description": "Duration",
                        "default": "60s",
                    },
                    "volume_path": {
                        "type": "string",
                        "description": "Volume path",
                        "default": "/tmp",
                    },
                    "delay": {
                        "type": "string",
                        "description": "Delay time",
                        "default": "100ms",
                    },
                },
                "required": ["cluster_name"],
            },
        ),
        types.Tool(
            name="create_dns_chaos_experiment",
            description="Create a DNS Chaos experiment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {
                        "type": "string",
                        "description": "Target cluster name",
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Target namespace",
                        "default": "default",
                    },
                    "target_app": {
                        "type": "string",
                        "description": "Target app label",
                        "default": "nginx",
                    },
                    "action": {
                        "type": "string",
                        "description": "Action type",
                        "enum": ["random", "error", "delay"],
                        "default": "random",
                    },
                    "duration": {
                        "type": "string",
                        "description": "Duration",
                        "default": "60s",
                    },
                    "patterns": {
                        "type": "string",
                        "description": "DNS patterns (comma-separated)",
                        "default": "google.com",
                    },
                    "delay": {
                        "type": "string",
                        "description": "Delay time",
                        "default": "100ms",
                    },
                },
                "required": ["cluster_name"],
            },
        ),
        types.Tool(
            name="create_time_chaos_experiment",
            description="Create a Time Chaos experiment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {
                        "type": "string",
                        "description": "Target cluster name",
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Target namespace",
                        "default": "default",
                    },
                    "target_app": {
                        "type": "string",
                        "description": "Target app label",
                        "default": "nginx",
                    },
                    "duration": {
                        "type": "string",
                        "description": "Duration",
                        "default": "60s",
                    },
                    "time_offset": {
                        "type": "string",
                        "description": "Time offset",
                        "default": "-10m",
                    },
                },
                "required": ["cluster_name"],
            },
        ),
    ]

    logger.info(f"Returning {len(tools)} tools")
    return tools


@mcp.tool()
async def add_remote_cluster(
    cluster_name: str, region: str, role_arn: str = None
) -> Dict[str, Any]:
    """Add remote cluster by cluster name"""
    try:
        result = await remote_manager.add_remote_cluster_by_name(
            cluster_name=cluster_name,
            region=region,
            role_arn=role_arn,
        )

        if result["success"]:
            # Get cluster information
            cluster_info = await cluster_manager.get_cluster_info(cluster_name)

            response = {
                "status": "success",
                "cluster_name": cluster_name,
                "region": region,
                "cluster_info": cluster_info,
                "message": f"Cluster '{cluster_name}' has been successfully added.",
            }
        else:
            response = {
                "status": "failed",
                "cluster_name": cluster_name,
                "error": result.get("error", "Unknown error"),
                "message": f"Failed to add cluster '{cluster_name}'.",
            }

        result_text = f"Remote cluster addition result:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
        return {
            "content": [{"type": "text", "text": result_text}],
            "isError": not result["success"],
        }

    except Exception as e:
        logger.error("add_remote_cluster_failed", cluster=cluster_name, error=str(e))
        return {
            "content": [
                {"type": "text", "text": f"Failed to add remote cluster: {str(e)}"}
            ],
            "isError": True,
        }


@mcp.tool()
async def list_remote_clusters() -> Dict[str, Any]:
    """List remote clusters"""
    try:
        clusters = await remote_manager.list_remote_clusters()

        result = {
            "clusters": clusters,
            "total_count": len(clusters),
            "message": f"Total of {len(clusters)} remote clusters are registered.",
        }

        result_text = (
            f"Remote cluster list:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
        )
        return {"content": [{"type": "text", "text": result_text}], "isError": False}

    except Exception as e:
        logger.error("list_remote_clusters_failed", error=str(e))
        return {
            "content": [
                {"type": "text", "text": f"Failed to list remote clusters: {str(e)}"}
            ],
            "isError": True,
        }


@mcp.tool()
async def install_chaos_mesh(
    cluster_name: str, namespace: str = "chaos-mesh"
) -> Dict[str, Any]:
    """Install Chaos Mesh on remote cluster"""
    try:
        result = await remote_manager.install_chaos_mesh_on_cluster(
            cluster_name, namespace
        )

        if result["success"]:
            response = {
                "status": "success",
                "cluster_name": cluster_name,
                "namespace": namespace,
                "dashboard_info": result.get("dashboard_info", {}),
                "installation_status": result.get("status", {}),
                "message": f"Chaos Mesh installation completed on cluster '{cluster_name}'.",
            }
        else:
            response = {
                "status": "failed",
                "cluster_name": cluster_name,
                "error": result.get("error", "Unknown error"),
                "message": f"Chaos Mesh installation failed on cluster '{cluster_name}'.",
            }

        result_text = f"Chaos Mesh installation result:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
        return {
            "content": [{"type": "text", "text": result_text}],
            "isError": not result["success"],
        }

    except Exception as e:
        logger.error("install_chaos_mesh_failed", cluster=cluster_name, error=str(e))
        return {
            "content": [
                {"type": "text", "text": f"Chaos Mesh installation failed: {str(e)}"}
            ],
            "isError": True,
        }


@mcp.tool()
async def get_cluster_pods(cluster_name: str, namespace: str = "") -> Dict[str, Any]:
    """Get cluster pod list"""
    try:
        k8s_client = cluster_manager.get_k8s_client(cluster_name)
        if not k8s_client:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Cannot connect to cluster '{cluster_name}'.",
                    }
                ],
                "isError": True,
            }

        from kubernetes import client

        core_v1 = client.CoreV1Api(k8s_client)

        # If namespace is empty string or None, search all namespaces
        if namespace and namespace.strip():
            pods_response = core_v1.list_namespaced_pod(namespace=namespace)
        else:
            pods_response = core_v1.list_pod_for_all_namespaces()
            namespace = "all"  # For result display

        pods_info = []
        for pod in pods_response.items:
            pod_info = {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase,
                "node": pod.spec.node_name,
                "created": pod.metadata.creation_timestamp.isoformat()
                if pod.metadata.creation_timestamp
                else None,
                "labels": pod.metadata.labels or {},
                "restart_count": sum(
                    container_status.restart_count
                    for container_status in (pod.status.container_statuses or [])
                ),
                "containers": len(pod.spec.containers) if pod.spec.containers else 0,
                "ready_containers": sum(
                    1
                    for container_status in (pod.status.container_statuses or [])
                    if container_status.ready
                ),
            }
            pods_info.append(pod_info)

        result = {
            "cluster_name": cluster_name,
            "namespace": namespace,
            "pods": pods_info,
            "total_count": len(pods_info),
            "message": f"Retrieved {len(pods_info)} pods from cluster '{cluster_name}'.",
        }

        result_text = f"Pod list:\n{json.dumps(result, indent=2, ensure_ascii=False)}"
        return {"content": [{"type": "text", "text": result_text}], "isError": False}

    except Exception as e:
        logger.error("get_cluster_pods_failed", cluster=cluster_name, error=str(e))
        return {
            "content": [{"type": "text", "text": f"Failed to get pod list: {str(e)}"}],
            "isError": True,
        }


@mcp.tool()
async def create_pod_chaos_experiment(
    cluster_name: str,
    namespace: str = "default",
    target_app: str = "nginx",
    action: str = "pod-kill",
    duration: str = "60s",
    mode: str = "one",
) -> Dict[str, Any]:
    """Pod Chaos Experiment Generation"""
    try:
        logger.info(
            "creating_pod_chaos_experiment",
            cluster=cluster_name,
            target={
                "namespace": namespace,
                "selector": {"labelSelectors": {"app": target_app}},
                "action": action,
                "mode": mode,
                "duration": duration,
            },
            action=action,
        )

        experiment_config = {
            "namespace": namespace,
            "selector": {"labelSelectors": {"app": target_app}},
            "action": action,
            "mode": mode,
            "duration": duration,
        }

        result = await remote_manager.create_pod_chaos_experiment(
            cluster_name=cluster_name,
            namespace=namespace,
            target_app=target_app,
            action=action,
            duration=duration,
            mode=mode,
        )

        if result["success"]:
            response = {
                "status": "success",
                "experiment_id": result["experiment_id"],
                "cluster_name": cluster_name,
                "experiment_type": "pod_chaos",
                "config": experiment_config,
                "message": "Pod Chaos experiment created successfully.",
            }
        else:
            logger.error(
                "pod_chaos_experiment_validation_failed",
                cluster=cluster_name,
                config=experiment_config,
                error=result.get("error"),
            )
            response = {
                "status": "failed",
                "cluster_name": cluster_name,
                "error": result.get("error", "Unknown error"),
                "config": experiment_config,
                "message": "Failed to create Pod Chaos experiment.",
            }

        result_text = f"Pod Chaos Experiment Generation Result:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
        return {
            "content": [{"type": "text", "text": result_text}],
            "isError": not result["success"],
        }

    except Exception as e:
        logger.error(
            "create_pod_chaos_experiment_failed", cluster=cluster_name, error=str(e)
        )
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Pod Chaos Experiment Generation Failed: {str(e)}",
                }
            ],
            "isError": True,
        }


@mcp.tool()
async def create_network_chaos_experiment(
    cluster_name: str,
    namespace: str = "default",
    target_app: str = "nginx",
    action: str = "delay",
    duration: str = "60s",
    delay: str = "100ms",
    loss: str = "10",
) -> Dict[str, Any]:
    """Network Chaos Experiment Generation"""
    try:
        experiment_config = {
            "namespace": namespace,
            "selector": {"labelSelectors": {"app": target_app}},
            "action": action,
            "mode": "one",
            "duration": duration,
        }

        if action == "delay":
            experiment_config["delay"] = {
                "latency": delay,
                "correlation": "100",
                "jitter": "0ms",
            }
        elif action == "loss":
            experiment_config["loss"] = {"loss": loss, "correlation": "100"}

        result = await remote_manager.create_network_chaos_experiment(
            cluster_name,
            namespace=namespace,
            target_app=target_app,
            action=action,
            duration=duration,
            delay=delay,
            loss=loss,
        )

        if result["success"]:
            response = {
                "status": "success",
                "experiment_id": result["experiment_id"],
                "cluster_name": cluster_name,
                "experiment_type": "network_chaos",
                "config": experiment_config,
                "message": "Network Chaos experiment created successfully.",
            }
        else:
            response = {
                "status": "failed",
                "cluster_name": cluster_name,
                "error": result.get("error", "Unknown error"),
                "message": "Failed to create Network Chaos experiment.",
            }

        result_text = f"Network Chaos Experiment Generation Result:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
        return {
            "content": [{"type": "text", "text": result_text}],
            "isError": not result["success"],
        }

    except Exception as e:
        logger.error(
            "create_network_chaos_experiment_failed", cluster=cluster_name, error=str(e)
        )
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Network Chaos Experiment Generation Failed: {str(e)}",
                }
            ],
            "isError": True,
        }


@mcp.tool()
async def create_stress_chaos_experiment(
    cluster_name: str,
    namespace: str = "default",
    target_app: str = "nginx",
    duration: str = "60s",
    cpu_workers: int = 1,
    memory_workers: int = 1,
    memory_size: str = "256MB",
) -> Dict[str, Any]:
    """Stress Chaos Experiment Generation"""
    try:
        experiment_config = {
            "namespace": namespace,
            "selector": {"labelSelectors": {"app": target_app}},
            "mode": "one",
            "duration": duration,
            "stressors": {
                "cpu": {"workers": cpu_workers, "load": 100},
                "memory": {"workers": memory_workers, "size": memory_size},
            },
        }

        result = await remote_manager.create_stress_chaos_experiment(
            cluster_name=cluster_name,
            namespace=namespace,
            target_app=target_app,
            duration=duration,
            cpu_workers=cpu_workers,
            memory_workers=memory_workers,
            memory_size=memory_size,
        )

        if result["success"]:
            response = {
                "status": "success",
                "experiment_id": result["experiment_id"],
                "cluster_name": cluster_name,
                "experiment_type": "stress_chaos",
                "config": experiment_config,
                "message": "Stress Chaos experiment created successfully.",
            }
        else:
            response = {
                "status": "failed",
                "cluster_name": cluster_name,
                "error": result.get("error", "Unknown error"),
                "message": "Failed to create Stress Chaos experiment.",
            }

        result_text = f"Stress Chaos Experiment Generation Result:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
        return {
            "content": [{"type": "text", "text": result_text}],
            "isError": not result["success"],
        }

    except Exception as e:
        logger.error(
            "create_stress_chaos_experiment_failed", cluster=cluster_name, error=str(e)
        )
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Stress Chaos Experiment Generation Failed: {str(e)}",
                }
            ],
            "isError": True,
        }


@mcp.tool()
async def create_io_chaos_experiment(
    cluster_name: str,
    namespace: str = "default",
    target_app: str = "nginx",
    action: str = "latency",
    duration: str = "60s",
    volume_path: str = "/tmp",
    delay: str = "100ms",
) -> Dict[str, Any]:
    """IO Chaos Experiment Generation"""
    try:
        experiment_config = {
            "namespace": namespace,
            "selector": {"labelSelectors": {"app": target_app}},
            "action": action,
            "mode": "one",
            "duration": duration,
            "volumePath": volume_path,
            "delay": delay,
            "percent": 50,
        }

        result = await remote_manager.create_io_chaos_experiment(
            cluster_name=cluster_name,
            namespace=namespace,
            target_app=target_app,
            action=action,
            duration=duration,
            volume_path=volume_path,
            delay=delay,
        )

        if result["success"]:
            response = {
                "status": "success",
                "experiment_id": result["experiment_id"],
                "cluster_name": cluster_name,
                "experiment_type": "io_chaos",
                "config": experiment_config,
                "message": "IO Chaos experiment created successfully.",
            }
        else:
            response = {
                "status": "failed",
                "cluster_name": cluster_name,
                "error": result.get("error", "Unknown error"),
                "message": "Failed to create IO Chaos experiment.",
            }

        result_text = f"IO Chaos Experiment Generation Result:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
        return {
            "content": [{"type": "text", "text": result_text}],
            "isError": not result["success"],
        }

    except Exception as e:
        logger.error(
            "create_io_chaos_experiment_failed", cluster=cluster_name, error=str(e)
        )
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"IO Chaos Experiment Generation Failed: {str(e)}",
                }
            ],
            "isError": True,
        }


@mcp.tool()
async def create_dns_chaos_experiment(
    cluster_name: str,
    namespace: str = "default",
    target_app: str = "nginx",
    action: str = "random",
    duration: str = "60s",
    patterns: str = "google.com",
    delay: str = "100ms",
) -> Dict[str, Any]:
    """DNS Chaos Experiment Generation"""
    try:
        patterns_list = [p.strip() for p in patterns.split(",")]

        result = await remote_manager.create_dns_chaos_experiment(
            cluster_name=cluster_name,
            namespace=namespace,
            target_app=target_app,
            action=action,
            duration=duration,
            patterns=patterns_list,
            delay=delay,
        )

        experiment_config = {
            "namespace": namespace,
            "selector": {"labelSelectors": {"app": target_app}},
            "action": action,
            "duration": duration,
            "patterns": patterns_list,
        }

        if result["success"]:
            response = {
                "status": "success",
                "experiment_id": result["experiment_id"],
                "cluster_name": cluster_name,
                "experiment_type": "dns_chaos",
                "config": experiment_config,
                "message": "DNS Chaos experiment created successfully.",
            }
        else:
            response = {
                "status": "failed",
                "cluster_name": cluster_name,
                "error": result.get("error", "Unknown error"),
                "message": "Failed to create DNS Chaos experiment.",
            }

        result_text = f"DNS Chaos Experiment Generation Result:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
        return {
            "content": [{"type": "text", "text": result_text}],
            "isError": not result["success"],
        }

    except Exception as e:
        logger.error(
            "create_dns_chaos_experiment_failed", cluster=cluster_name, error=str(e)
        )
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"DNS Chaos Experiment Generation Failed: {str(e)}",
                }
            ],
            "isError": True,
        }


@mcp.tool()
async def create_time_chaos_experiment(
    cluster_name: str,
    namespace: str = "default",
    target_app: str = "nginx",
    duration: str = "60s",
    time_offset: str = "-10m",
) -> Dict[str, Any]:
    """Time Chaos Experiment Generation"""
    try:
        result = await remote_manager.create_time_chaos_experiment(
            cluster_name=cluster_name,
            namespace=namespace,
            target_app=target_app,
            duration=duration,
            time_offset=time_offset,
        )

        experiment_config = {
            "namespace": namespace,
            "selector": {"labelSelectors": {"app": target_app}},
            "duration": duration,
            "timeOffset": time_offset,
        }

        if result["success"]:
            response = {
                "status": "success",
                "experiment_id": result["experiment_id"],
                "cluster_name": cluster_name,
                "experiment_type": "time_chaos",
                "config": experiment_config,
                "message": "Time Chaos experiment created successfully.",
            }
        else:
            response = {
                "status": "failed",
                "cluster_name": cluster_name,
                "error": result.get("error", "Unknown error"),
                "message": "Failed to create Time Chaos experiment.",
            }

        result_text = f"Time Chaos Experiment Generation Result:\n{json.dumps(response, indent=2, ensure_ascii=False)}"
        return {
            "content": [{"type": "text", "text": result_text}],
            "isError": not result["success"],
        }

    except Exception as e:
        logger.error(
            "create_time_chaos_experiment_failed", cluster=cluster_name, error=str(e)
        )
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Time Chaos Experiment Generation Failed: {str(e)}",
                }
            ],
            "isError": True,
        }


@mcp.tool()
async def get_cluster_nodes(cluster_name: str) -> Dict[str, Any]:
    """Get cluster nodes information"""
    try:
        nodes = cluster_manager.get_nodes(cluster_name)

        result_text = f"Cluster Nodes Information ({cluster_name}):\n{json.dumps(nodes, indent=2, ensure_ascii=False)}"
        return {
            "content": [{"type": "text", "text": result_text}],
            "isError": False,
        }
    except Exception as e:
        logger.error("get_cluster_nodes_failed", cluster=cluster_name, error=str(e))
        return {
            "content": [
                {"type": "text", "text": f"Failed to get cluster nodes: {str(e)}"}
            ],
            "isError": True,
        }


@mcp.tool()
async def get_cluster_namespaces(cluster_name: str) -> Dict[str, Any]:
    """Get cluster namespaces information"""
    try:
        namespaces = cluster_manager.get_namespaces(cluster_name)

        result_text = f"Cluster Namespaces Information ({cluster_name}):\n{json.dumps(namespaces, indent=2, ensure_ascii=False)}"
        return {
            "content": [{"type": "text", "text": result_text}],
            "isError": False,
        }
    except Exception as e:
        logger.error(
            "get_cluster_namespaces_failed", cluster=cluster_name, error=str(e)
        )
        return {
            "content": [
                {"type": "text", "text": f"Failed to get cluster namespaces: {str(e)}"}
            ],
            "isError": True,
        }


@mcp.tool()
async def get_cluster_deployments(
    cluster_name: str, namespace: str = ""
) -> Dict[str, Any]:
    """Get cluster deployments information"""
    try:
        namespace_param = namespace if namespace else None
        deployments = cluster_manager.get_deployments(cluster_name, namespace_param)

        result_text = f"Cluster Deployments Information ({cluster_name}):\n{json.dumps(deployments, indent=2, ensure_ascii=False)}"
        return {
            "content": [{"type": "text", "text": result_text}],
            "isError": False,
        }
    except Exception as e:
        logger.error(
            "get_cluster_deployments_failed", cluster=cluster_name, error=str(e)
        )
        return {
            "content": [
                {"type": "text", "text": f"Failed to get cluster deployments: {str(e)}"}
            ],
            "isError": True,
        }


@mcp.tool()
async def get_cluster_services(
    cluster_name: str, namespace: str = ""
) -> Dict[str, Any]:
    """Get cluster services information"""
    try:
        namespace_param = namespace if namespace else None
        services = cluster_manager.get_services(cluster_name, namespace_param)

        result_text = f"Cluster Services Information ({cluster_name}):\n{json.dumps(services, indent=2, ensure_ascii=False)}"
        return {
            "content": [{"type": "text", "text": result_text}],
            "isError": False,
        }
    except Exception as e:
        logger.error("get_cluster_services_failed", cluster=cluster_name, error=str(e))
        return {
            "content": [
                {"type": "text", "text": f"Failed to get cluster services: {str(e)}"}
            ],
            "isError": True,
        }


@mcp.tool()
async def get_cluster_resource_summary(cluster_name: str) -> Dict[str, Any]:
    """Get cluster resource summary information"""
    try:
        cluster_summary = cluster_manager.get_cluster_summary(cluster_name)

        result_text = f"Cluster Resource Summary ({cluster_name}):\n{json.dumps(cluster_summary, indent=2, ensure_ascii=False)}"
        return {
            "content": [{"type": "text", "text": result_text}],
            "isError": False,
        }
    except Exception as e:
        logger.error(
            "get_cluster_resource_summary_failed", cluster=cluster_name, error=str(e)
        )
        return {
            "content": [
                {"type": "text", "text": f"Failed to get cluster summary: {str(e)}"}
            ],
            "isError": True,
        }


def run_server():
    """Run the MCP server"""

    async def init_and_run():
        try:
            await _initialize_managers()
            logger.info("mcp_server_initialization_complete")
        except Exception as e:
            logger.error("startup_initialization_failed", error=str(e))

    asyncio.run(init_and_run())

    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
