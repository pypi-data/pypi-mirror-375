"""Logging configuration module"""

import sys
from typing import Any, Dict

import structlog

from utils.config import settings


def setup_logging() -> None:
    """Setup structured logging"""

    # Simple renderer for clean output
    def clean_renderer(logger, method_name, event_dict):
        event = event_dict.get('event', '')
        cluster = event_dict.get('cluster', '')
        
        if event == 'initializing_remote_chaos_manager':
            return "🔄 Initializing..."
        elif event == 'adding_remote_cluster_by_name':
            return f"🔗 Connecting to {cluster[:25]}..."
        elif event == 'eks_cluster_added':
            return f"✅ Connected to {cluster[:25]}..."
        elif event == 'chaos_mesh_mcp_initialization_complete':
            cluster_count = event_dict.get('cluster_count', 0)
            cluster_names = event_dict.get('cluster_names', [])
            
            if cluster_count > 0:
                result = f"🚀 Ready! Connected to {cluster_count} cluster(s):\n"
                for name in cluster_names:
                    result += f"  📊 {name[:40]}...\n"
                return result.rstrip()
            else:
                return "🚀 Ready! (No clusters connected)"
        elif method_name == 'error':
            return f"❌ {event_dict.get('error', 'Error')}"
        
        # Skip empty lines by not returning anything for unmatched events
        raise structlog.DropEvent

    processors = [clean_renderer]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(20),
        logger_factory=structlog.WriteLoggerFactory(sys.stderr),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Create logger instance"""
    return structlog.get_logger(name)


class AuditLogger:
    """Dedicated audit logger"""

    def __init__(self):
        self.logger = get_logger("audit")

    def log_experiment_created(
        self,
        cluster: str,
        experiment_type: str,
        experiment_name: str,
        target: Dict[str, Any],
    ) -> None:
        """Log experiment creation"""
        self.logger.info(
            "chaos_experiment_created",
            cluster=cluster,
            experiment_type=experiment_type,
            experiment_name=experiment_name,
            target=target,
            action="CREATE_EXPERIMENT",
        )

    def log_experiment_started(
        self,
        cluster: str,
        experiment_name: str,
    ) -> None:
        """Log experiment start"""
        self.logger.info(
            "chaos_experiment_started",
            cluster=cluster,
            experiment_name=experiment_name,
            action="START_EXPERIMENT",
        )

    def log_experiment_stopped(
        self,
        cluster: str,
        experiment_name: str,
        reason: str = "user_request",
    ) -> None:
        """Log experiment stop"""
        self.logger.info(
            "chaos_experiment_stopped",
            cluster=cluster,
            experiment_name=experiment_name,
            reason=reason,
            action="STOP_EXPERIMENT",
        )

    def log_security_violation(self, action: str, resource: str, reason: str) -> None:
        """Log security violation"""
        self.logger.warning(
            "security_violation",
            action=action,
            resource=resource,
            reason=reason,
        )


# Global audit logger instance
audit_logger = AuditLogger()
