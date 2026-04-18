import subprocess
import logging
import os
import shutil
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from prometheus_client import Counter
from state_manager import StateManager

logger = logging.getLogger(__name__)

# Prometheus Metrics
REMEDIATIONS = Counter('remediations_total', 'Total remediations attempted', ['action', 'status'])

class Remediator:
    """Safely executes remediation actions."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.state = StateManager()

    def execute(self, remediation_config: Dict[str, Any]):
        """Entry point for remediation execution."""
        action = remediation_config.get('action')
        target = remediation_config.get('target', 'unknown')
        retries = remediation_config.get('retries', 3)

        logger.info(f"Triggering remediation: {action} on {target} (Dry-run: {self.dry_run})")
        
        if self.dry_run:
            logger.info(f"[DRY-RUN] Would execute {action} on {target}")
            REMEDIATIONS.labels(action=action, status='dry_run').inc()
            return

        try:
            self._dispatch(action, target, retries)
            REMEDIATIONS.labels(action=action, status='success').inc()
            self.state.update_stats("remediations_success")
            self.state.add_event("REMEDIATION", f"Success: {action} on {target}", "INFO")
        except Exception as e:
            logger.error(f"Remediation failed after retries: {str(e)}")
            REMEDIATIONS.labels(action=action, status='failed').inc()
            self.state.update_stats("remediations_failed")
            self.state.add_event("REMEDIATION", f"Failed: {action} on {target}", "CRITICAL")

    def _dispatch(self, action: str, target: str, retries: int):
        """Dispatches to specific remediation logic with retries."""
        
        @retry(
            stop=stop_after_attempt(retries),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=retry_if_exception_type(subprocess.CalledProcessError),
            reraise=True
        )
        def run_with_retry():
            if action == "restart_service":
                self._restart_service(target)
            elif action == "clear_cache":
                self._clear_cache(target)
            elif action == "kill_process":
                self._kill_process(target)
            else:
                raise ValueError(f"Unknown remediation action: {action}")

        run_with_retry()

    def _restart_service(self, service_name: str):
        """Restarts a systemd service safely."""
        # Validate service name to prevent malicious chars
        if not service_name.replace('-', '').replace('_', '').isalnum():
            raise ValueError(f"Invalid service name: {service_name}")
            
        logger.info(f"Restarting service: {service_name}")
        # shell=False (default) prevents shell injection
        subprocess.run(["sudo", "systemctl", "restart", service_name], check=True)

    def _clear_cache(self, directory: str):
        """Clears temporary files in a directory without using shell=True."""
        abs_path = os.path.abspath(directory)
        
        # Protected directory checks
        protected = ["/", "/root", "/home", "/etc", "/usr", "/var"]
        if abs_path in protected or not os.path.isdir(abs_path):
            raise ValueError(f"CRITICAL: Refusing to clear protected or invalid directory: {abs_path}")
        
        logger.info(f"Clearing contents of: {abs_path}")
        # Delete files inside without deleting the directory itself
        for filename in os.listdir(abs_path):
            file_path = os.path.join(abs_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f"Failed to delete {file_path}: {e}")

    def _kill_process(self, process_name: str):
        """Kills a process by name safely."""
        if ";" in process_name or "&" in process_name:
             raise ValueError(f"Invalid process name: {process_name}")

        logger.info(f"Killing process: {process_name}")
        subprocess.run(["sudo", "pkill", "-f", process_name], check=True)
