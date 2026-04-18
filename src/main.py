import argparse
import logging
import sys
import os
import signal
import threading
from rich.console import Console
from rich.logging import RichHandler
from prometheus_client import start_http_server

# Import local modules
from config_loader import ConfigLoader
from log_parser import LogParser
from detector import Detector
from remediator import Remediator
from notifier import Notifier
from dashboard import run_dashboard

# Setup Rich console and logging
console = Console()
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True, console=console)]
)
logger = logging.getLogger("main")

def handle_signal(sig, frame):
    logger.info("Gracefully shutting down...")
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Python-Based Log Analysis & Auto-Remediation Tool")
    parser.add_argument("--config", default="configs/default_rules.yaml", help="Path to config file")
    parser.add_argument("--logs", help="Path to log file or directory (overrides config)")
    parser.add_argument("--follow", action="store_true", help="Tail logs in real-time (tail -f style)")
    parser.add_argument("--dry-run", action="store_true", help="Detect but do not execute remediation")
    parser.add_argument("--metrics-port", type=int, default=8000, help="Prometheus metrics port")
    
    args = parser.parse_args()

    # Register signals
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        # 1. Load Config
        config_loader = ConfigLoader(args.config)
        config = config_loader.load()
        
        # 2. Setup Components
        log_source = args.logs or config_loader.log_source
        parser_instance = LogParser(log_source, follow=args.follow)
        detector = Detector(config_loader.rules)
        remediator = Remediator(dry_run=args.dry_run)
        notifier = Notifier(config)

        # 3. Start Dashboard (New)
        logger.info("Starting Dashboard on http://localhost:8080")
        threading.Thread(target=run_dashboard, args=(8080,), daemon=True).start()

        # 4. Start Metrics Server (Robustly)
        try:
            logger.info(f"Starting Prometheus server on port {args.metrics_port}")
            start_http_server(args.metrics_port)
        except OSError as e:
            logger.error(f"Failed to start Prometheus server (Is port {args.metrics_port} occupied?): {e}")
            logger.warning("Continuing without metrics server...")

        # 4. Processing Loop
        console.print("[bold green]Starting Log Analysis Engine...[/bold green]")
        for line in parser_instance.stream_logs():
            match = detector.analyze_line(line)
            if match:
                console.print(f"[bold red]CRITICAL:[/bold red] Detected rule match: [yellow]{match['name']}[/yellow]")
                
                # Trigger Notification
                notifier.send_alert(match, line)

                if 'remediation' in match:
                    remediator.execute(match['remediation'])
                else:
                    logger.info("No remediation action defined for this rule.")

    except Exception as e:
        logger.error(f"Fatal application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
