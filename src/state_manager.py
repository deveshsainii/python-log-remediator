import threading
from typing import List, Dict, Any
from collections import deque

class StateManager:
    """Thread-safe state manager for sharing data between the parser and the dashboard."""
    
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(StateManager, cls).__new__(cls)
                cls._instance._init_state()
        return cls._instance

    def _init_state(self):
        self.stats = {
            "logs_processed": 0,
            "errors_detected": 0,
            "remediations_success": 0,
            "remediations_failed": 0,
        }
        # Keep the last 50 events for the live feed
        self.events = deque(maxlen=50)
        self.rule_distribution: Dict[str, int] = {}
        self.lock = threading.Lock()

    def update_stats(self, key: str, increment: int = 1):
        with self.lock:
            if key in self.stats:
                self.stats[key] += increment

    def add_event(self, event_type: str, message: str, severity: str = "INFO"):
        with self.lock:
            self.events.append({
                "timestamp": threading.local(), # Stub for actual time if needed
                "type": event_type,
                "message": message,
                "severity": severity
            })

    def increment_rule(self, rule_name: str):
        with self.lock:
            self.rule_distribution[rule_name] = self.rule_distribution.get(rule_name, 0) + 1

    def get_snapshot(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "stats": self.stats.copy(),
                "events": list(self.events),
                "distribution": self.rule_distribution.copy()
            }
