# Configuration Guide

The tool is designed to be fully declarative. All behavior is controlled via a single YAML file (default is `configs/default_rules.yaml`).

---

## 📂 Log Source Configuration

- `log_source`: **(String)** Path to a single log file or a directory. If a directory is provided, the tool will multiplex all files within it.
- `prometheus_port`: **(Integer)** Port to host the metrics server.

---

## 🔔 Notification Reference

```yaml
notifications:
  email:
    enabled: true            # Set to false to disable all emails
    recipient: "admin@corp.com"
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    cooldown_seconds: 300    # Prevents alert fatigue
```

---

## ⚡ Detection Rules (`rules`)

Each rule in the `rules` list supports the following attributes:

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | String | A unique name for the rule (used in metrics/alerts). |
| `pattern` | Regex | The Python-compatible Regex to match against log lines. |
| `severity` | Enum | `INFO`, `WARNING`, or `CRITICAL`. |
| `remediation` | Object | (Optional) Instructions for fixing the error. |

### Remediation Object Details
- `action`: Supported values: `restart_service`, `clear_cache`, `kill_process`.
- `target`: The name of the service, directory path, or process name.
- `retries`: Number of times to attempt the action with exponential backoff.

---

## 🛠️ Advanced: Security & Hardening

### Environment Variables
For security, do not store passwords in the YAML. Use these:
- `SMTP_USER`: Your email username.
- `SMTP_PASS`: Your email app-password.

### Path Safety
The tool normalizes all paths. If you try to configure a remediation that deletes `/etc`, the tool will throw a `ValueError` for safety:
```python
# Internal Safety Check
if abs_path in protected_dirs:
    raise ValueError("Refusal to clear protected directory")
```
