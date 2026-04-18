# System Architecture & Data Flow

This page provides a deep dive into how the **Log Analysis & Auto-Remediation Tool** processes data and handles system incidents.

---

## 🏗️ High-Level Component Map

The tool is divided into four main layers:

### 1. The Ingestion Layer (`log_parser.py`)
- **Responsibility**: Reading raw data from the filesystem.
- **Key Logic**: Uses an **Offset-based Polling Multiplexer**. 
- **How it works**: It maintains a dictionary of all files in the target directory and their last known byte-position (`tell()`). Every polling cycle, it checks if the file size has increased, seeks to the last offset, and reads only the new "delta" lines.

### 2. The Logic Layer (`detector.py`)
- **Responsibility**: Pattern recognition.
- **Key Logic**: Pre-compiled Regular Expressions (Regex).
- **Optimization**: To handle multi-GB logs, all rules are pre-compiled during startup. Each incoming line is matched against the rule set. The first rule to match triggers the pipeline.

### 3. The Action Layer (`remediator.py` & `notifier.py`)
- **Responsibility**: Response execution.
- **Remediator**: Executes idempotent shell commands (e.g., `systemctl restart`). It includes a safety engine that prevents directory traversal and protects core system paths.
- **Notifier**: Dispatches alerts via SMTP. It includes a **Stateful Throttle** to ensure that if a server enters a "Crash Loop," your inbox is not flooded with thousands of emails.

### 4. The Observability Layer (`main.py`)
- **Responsibility**: Exposing health metrics.
- **Metrics**: Exposes a Prometheus-compatible string on port 8000. This allow SREs to build Grafana dashboards showing error rates and remediation success counts.

---

## 🔄 Lifecycle of a Log Entry

1.  **Ingestion**: `LogParser` detects a new line in `/var/log/syslog`.
2.  **Detection**: `Detector` identifies the string `OutOfMemoryError`.
3.  **Metrics**: `logs_processed_total` and `errors_detected_total` counters are incremented.
4.  **Notification**: `Notifier` sends an email to the SRE team (checking the 5-minute cooldown first).
5.  **Remediation**: `Remediator` executes `sudo systemctl restart my-app`.
6.  **Audit**: The action and its result (success/fail) are logged to the console and metrics.
