# Troubleshooting & FAQ

Solving common issues with the Log Analysis & Auto-Remediation Tool.

---

## ❓ Common Issues

### 1. The tool isn't detecting my log lines
- **Check Regex**: Use a tool like [Regex101](https://regex101.com/) (Python flavor) to ensure your pattern matches exactly what is in the log.
- **Check Permissions**: Ensure the tool has read-access to the log file or directory.
- **Dry-Run Mode**: If `--dry-run` is ON, the tool will detect the lines but won't execute remediation. It will still log the detection to the console.

### 2. Prometheus port (8000) is already in use
- **Fix**: Change the port using the `--metrics-port` CLI argument:
  ```bash
  python src/main.py --metrics-port 9090
  ```

### 3. "ModuleNotFoundError: No module named 'rich'"
- **Fix**: You forgot to install the requirements. Run:
  ```bash
  pip install -r requirements.txt
  ```

### 4. Remediation actions are failing (Exit Code 1)
- **Linux Sudo**: Most actions like `systemctl` require `sudo`. Ensure the user running the tool is in the `sudoers` list or the tool is run as root.
- **Path Validation**: If you get a "Refusal to clear protected directory" error, it means your target directory is critical to the OS (like `/etc`). Change the target in your YAML.

---

## 📈 Optimization Tips

### Handling High Volume Logs
If you are processing logs that generate thousands of lines per second:
1.  **Reduce Rule Count**: Each rule adds a small amount of CPU overhead per line.
2.  **Use Specific Regex**: Anchoring your regex (using `^` for start of line) can significantly speed up matching.
3.  **Increase Poll Interval**: In `log_parser.py`, you can increase the `time.sleep(1)` to a higher value to reduce CPU context-switching.

---

## 💻 Monitoring with Prometheus

You can add this tool to your `prometheus.yml` configuration:

```yaml
scrape_configs:
  - job_name: 'log_remediator'
    static_configs:
      - targets: ['localhost:8000']
```

Then, you can create a Grafana dashboard with the query:
`sum(rate(errors_detected_total[5m])) by (rule_name)`
