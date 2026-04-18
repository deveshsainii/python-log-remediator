import re
import logging
from typing import List, Dict, Any, Optional
from prometheus_client import Counter

logger = logging.getLogger(__name__)

# Prometheus Metrics
LOGS_PROCESSED = Counter('logs_processed_total', 'Total number of log lines processed')
ERRORS_DETECTED = Counter('errors_detected_total', 'Total errors detected', ['rule_name', 'severity'])

class Detector:
    """Detects patterns in log lines based on configured rules."""
    
    def __init__(self, rules: List[Dict[str, Any]]):
        self.rules = self._compile_rules(rules)

    def _compile_rules(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Pre-compiles regex patterns for performance."""
        compiled = []
        for rule in rules:
            try:
                rule['_regex'] = re.compile(rule['pattern'])
                compiled.append(rule)
            except re.error as e:
                logger.error(f"Invalid regex for rule '{rule['name']}': {e}")
        return compiled

    def analyze_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Analyzes a single log line against all rules."""
        LOGS_PROCESSED.inc()
        
        for rule in self.rules:
            if rule['_regex'].search(line):
                logger.warning(f"Detection: Rule '{rule['name']}' matched line: {line[:100]}...")
                ERRORS_DETECTED.labels(rule_name=rule['name'], severity=rule['severity']).inc()
                return rule
        return None
