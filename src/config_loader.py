import yaml
import os
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Loads and validates configuration for the log analysis tool."""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Loads configuration from YAML or JSON file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            self._validate()
            logger.info(f"Configuration loaded successfully from {self.config_path}")
            return self.config
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            raise

    def _validate(self):
        """Basic validation of the configuration structure."""
        if 'rules' not in self.config:
            raise ValueError("Configuration missing 'rules' section")
        
        for rule in self.config['rules']:
            required_fields = ['name', 'pattern', 'severity']
            for field in required_fields:
                if field not in rule:
                    raise ValueError(f"Rule '{rule.get('name', 'Unknown')}' is missing required field: {field}")
            
            # Optional remediation check
            if 'remediation' in rule:
                if 'action' not in rule['remediation']:
                    raise ValueError(f"Remediation for rule '{rule['name']}' missing 'action'")

    @property
    def rules(self) -> List[Dict[str, Any]]:
        return self.config.get('rules', [])

    @property
    def log_source(self) -> str:
        return self.config.get('log_source', '/var/log')

    @property
    def prometheus_port(self) -> int:
        return self.config.get('prometheus_port', 8000)
