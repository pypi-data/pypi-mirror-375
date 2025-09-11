"""Progress bar utilities for cluster operations"""

import asyncio
import logging
import sys
from typing import Optional

import structlog
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console(file=sys.stderr)


class ClusterConnectionProgress:
    """Progress bar for cluster connection operations"""
    
    def __init__(self):
        self.progress: Optional[Progress] = None
        self.task_id: Optional[int] = None
        self._original_log_level = None
    
    def start(self, cluster_name: str, total_steps: int = 5):
        """Start progress bar and suppress logs"""
        # Suppress structlog output during progress
        self._suppress_logs()
        
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
            transient=True
        )
        self.progress.start()
        self.task_id = self.progress.add_task(
            f"Connecting to {cluster_name[:30]}{'...' if len(cluster_name) > 30 else ''}...", 
            total=total_steps
        )
    
    def update(self, description: str, advance: int = 1):
        """Update progress"""
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, description=description, advance=advance)
    
    def complete(self, cluster_name: str):
        """Complete progress and restore logs"""
        if self.progress and self.task_id is not None:
            short_name = cluster_name[:30] + '...' if len(cluster_name) > 30 else cluster_name
            self.progress.update(self.task_id, description=f"✅ Connected to {short_name}")
            self.progress.stop()
        self._restore_logs()
    
    def error(self, cluster_name: str, error: str):
        """Show error and restore logs"""
        if self.progress:
            self.progress.stop()
        self._restore_logs()
        short_name = cluster_name[:30] + '...' if len(cluster_name) > 30 else cluster_name
        console.print(f"❌ Failed to connect to {short_name}: {error}", style="red")
    
    def _suppress_logs(self):
        """Temporarily suppress structlog output"""
        # Redirect stderr to devnull to suppress JSON logs
        self._original_stderr = sys.stderr
        sys.stderr = open('/dev/null', 'w')
    
    def _restore_logs(self):
        """Restore structlog output"""
        if hasattr(self, '_original_stderr'):
            sys.stderr.close()
            sys.stderr = self._original_stderr
