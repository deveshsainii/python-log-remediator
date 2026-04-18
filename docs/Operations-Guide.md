# Operations Guide | Log Analysis & Auto-Remediation

This guide provides step-by-step instructions for Support Engineers and SREs to deploy, run, and monitor logs using this tool.

---

## 🛠️ Step 1: Preparation

Before running the tool, ensure your environment is ready.

1.  **Clone & Enter**:
    ```bash
    git clone https://github.com/deveshsainii/python-log-remediator.git
    cd python-log-remediator
    ```
2.  **Install Dependencies**:
    The tool requires FastAPI, Uvicorn, Rich, and other SRE libraries.
    ```bash
    pip install -r requirements.txt
    ```

---

## 🚀 Step 2: Starting the Tool

The tool can be started in three primary "Operational Modes."

### Mode A: The "Standard Scan" (One-time check)
Use this when you want to scan existing logs for a specific incident that happened in the past.
```bash
python src/main.py --logs logs/service.log
```

### Mode B: The "Live Monitor" (tail -f style)
Use this for active real-time monitoring of a production service.
```bash
python src/main.py --logs logs/service.log --follow
```

### Mode C: The "Safety/Dry-Run" Mode
**Crucial for Testing**: Use this to see what patterns are matched *without* actually triggering restarts or file deletions.
```bash
python src/main.py --logs logs/ --follow --dry-run
```

---

## 📂 Monitoring Log Directories

Our tool features a **Multiplexer**, meaning it can monitor an unlimited number of files in a folder simultaneously.

1.  **Point to a Directory**:
    ```bash
    python src/main.py --logs logs/ --follow
    ```
2.  **What happens next?**: 
    The tool will scan every `.log` (or text file) in the folder. If you add a new log file to that folder while the tool is running, it will automatically start monitoring the new file too!

---

## 🧪 Step 3: Performing a Live Test

To verify everything is configured correctly:

1.  **Start Terminal 1**: `python src/main.py --logs logs/ --follow --dry-run`
2.  **Open Terminal 2**: Use a command to "write" to the log:
    ```powershell
    # Windows PowerShell
    Add-Content logs/service.log "`n[ERROR] OutOfMemoryError detected!"
    ```
3.  **Confirm Results**:
    - Check the terminal output for the **Red Alert**.
    - Open the Web UI at **http://localhost:8080** to see the metric card update.

---

## 🖥️ Step 4: Accessing the Premium Dashboard

While the tool is running, it launches a professional SRE Dashboard.

1.  Open your browser to: **[http://localhost:8080](http://localhost:8080)**
2.  **Features**:
    - **Total Logs**: Tracks every line processed across all files.
    - **Incident Feed**: A scrolling live update of detections.
    - **Distribution**: A doughnut chart showing your warning vs critical error balance.

---

## 🏁 Operational Commands Summary

| Task | Command |
| :--- | :--- |
| **Check Port 8000** | Prometheus metrics (Raw) |
| **Check Port 8080** | Dashboard (UI) |
| **Emergency Stop** | `Ctrl + C` (Performs graceful shutdown) |
| **Custom Port** | `--metrics-port 9090` |
