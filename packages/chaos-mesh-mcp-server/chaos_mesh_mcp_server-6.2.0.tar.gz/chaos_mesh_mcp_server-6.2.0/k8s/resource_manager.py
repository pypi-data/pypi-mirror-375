"""EKS 클러스터 리소스 정보 조회 관리자"""

from typing import Any, Dict, List, Optional
from kubernetes import client
from utils.logger import get_logger

logger = get_logger(__name__)


class ResourceManager:
    """EKS 클러스터 리소스 정보 조회 관리자"""

    def __init__(self, k8s_client: client.ApiClient):
        self.k8s_client = k8s_client
        self.core_v1 = client.CoreV1Api(k8s_client)
        self.apps_v1 = client.AppsV1Api(k8s_client)

    def get_nodes(self) -> List[Dict[str, Any]]:
        """노드 정보 조회"""
        try:
            nodes = self.core_v1.list_node()
            return [
                {
                    "name": node.metadata.name,
                    "status": node.status.phase if node.status.phase else "Unknown",
                    "roles": [label.split("/")[-1] for label in node.metadata.labels.keys() 
                             if "node-role.kubernetes.io" in label],
                    "version": node.status.node_info.kubelet_version,
                    "instance_type": node.metadata.labels.get("node.kubernetes.io/instance-type", "Unknown"),
                    "zone": node.metadata.labels.get("topology.kubernetes.io/zone", "Unknown"),
                    "capacity": {
                        "cpu": node.status.capacity.get("cpu", "Unknown"),
                        "memory": node.status.capacity.get("memory", "Unknown"),
                        "pods": node.status.capacity.get("pods", "Unknown")
                    },
                    "conditions": [
                        {"type": condition.type, "status": condition.status}
                        for condition in (node.status.conditions or [])
                    ]
                }
                for node in nodes.items
            ]
        except Exception as e:
            logger.error("failed_to_get_nodes", error=str(e))
            raise

    def get_namespaces(self) -> List[Dict[str, Any]]:
        """네임스페이스 정보 조회"""
        try:
            namespaces = self.core_v1.list_namespace()
            return [
                {
                    "name": ns.metadata.name,
                    "status": ns.status.phase,
                    "created": ns.metadata.creation_timestamp.isoformat() if ns.metadata.creation_timestamp else None,
                    "labels": ns.metadata.labels or {},
                    "annotations": ns.metadata.annotations or {}
                }
                for ns in namespaces.items
            ]
        except Exception as e:
            logger.error("failed_to_get_namespaces", error=str(e))
            raise

    def get_deployments(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """디플로이먼트 정보 조회"""
        try:
            if namespace:
                deployments = self.apps_v1.list_namespaced_deployment(namespace)
            else:
                deployments = self.apps_v1.list_deployment_for_all_namespaces()
            
            return [
                {
                    "name": deploy.metadata.name,
                    "namespace": deploy.metadata.namespace,
                    "replicas": {
                        "desired": deploy.spec.replicas,
                        "ready": deploy.status.ready_replicas or 0,
                        "available": deploy.status.available_replicas or 0,
                        "unavailable": deploy.status.unavailable_replicas or 0
                    },
                    "strategy": deploy.spec.strategy.type if deploy.spec.strategy else "Unknown",
                    "created": deploy.metadata.creation_timestamp.isoformat() if deploy.metadata.creation_timestamp else None,
                    "labels": deploy.metadata.labels or {},
                    "selector": deploy.spec.selector.match_labels if deploy.spec.selector else {}
                }
                for deploy in deployments.items
            ]
        except Exception as e:
            logger.error("failed_to_get_deployments", error=str(e))
            raise

    def get_services(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """서비스 정보 조회"""
        try:
            if namespace:
                services = self.core_v1.list_namespaced_service(namespace)
            else:
                services = self.core_v1.list_service_for_all_namespaces()
            
            return [
                {
                    "name": svc.metadata.name,
                    "namespace": svc.metadata.namespace,
                    "type": svc.spec.type,
                    "cluster_ip": svc.spec.cluster_ip,
                    "external_ips": svc.spec.external_i_ps or [],
                    "ports": [
                        {
                            "name": port.name,
                            "port": port.port,
                            "target_port": str(port.target_port),
                            "protocol": port.protocol
                        }
                        for port in (svc.spec.ports or [])
                    ],
                    "selector": svc.spec.selector or {},
                    "created": svc.metadata.creation_timestamp.isoformat() if svc.metadata.creation_timestamp else None
                }
                for svc in services.items
            ]
        except Exception as e:
            logger.error("failed_to_get_services", error=str(e))
            raise

    def get_cluster_summary(self) -> Dict[str, Any]:
        """클러스터 리소스 요약 정보"""
        try:
            nodes = self.get_nodes()
            namespaces = self.get_namespaces()
            deployments = self.get_deployments()
            services = self.get_services()
            
            # 기존 get_cluster_pods 로직 재사용
            pods = self.core_v1.list_pod_for_all_namespaces()
            
            return {
                "summary": {
                    "nodes": len(nodes),
                    "namespaces": len(namespaces),
                    "deployments": len(deployments),
                    "services": len(services),
                    "pods": len(pods.items)
                },
                "node_status": {
                    status: len([n for n in nodes if n["status"] == status])
                    for status in set(node["status"] for node in nodes)
                },
                "pod_status": {
                    status: len([p for p in pods.items if p.status.phase == status])
                    for status in set(pod.status.phase for pod in pods.items if pod.status.phase)
                }
            }
        except Exception as e:
            logger.error("failed_to_get_cluster_summary", error=str(e))
            raise
