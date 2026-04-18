import pytest
import os
from src.config_loader import ConfigLoader
from src.detector import Detector
from src.log_parser import LogParser

@pytest.fixture
def sample_config(tmp_path):
    config_file = tmp_path / "test_rules.yaml"
    content = """
rules:
  - name: "Test Rule"
    pattern: "ERROR_MATCH"
    severity: "CRITICAL"
    remediation:
      action: "restart"
"""
    config_file.write_text(content)
    return str(config_file)

def test_config_loading(sample_config):
    loader = ConfigLoader(sample_config)
    config = loader.load()
    assert len(config['rules']) == 1
    assert config['rules'][0]['name'] == "Test Rule"

def test_detection_logic():
    rules = [
        {"name": "OOM", "pattern": "OutOfMemoryError", "severity": "CRITICAL"}
    ]
    detector = Detector(rules)
    
    # Match
    match = detector.analyze_line("[2023] java.lang.OutOfMemoryError: Java heap space")
    assert match is not None
    assert match['name'] == "OOM"
    
    # No Match
    no_match = detector.analyze_line("[2023] INFO Everything is fine")
    assert no_match is None

def test_streaming_parser(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text("line1\nline2\n")
    
    parser = LogParser(str(log_file), follow=False)
    lines = list(parser.stream_logs())
    assert lines == ["line1", "line2"]
