import smtplib
import logging
import time
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Notifier:
    """Handles sending notifications (Email, etc.) with alert throttling."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get('notifications', {})
        self.email_config = self.config.get('email', {})
        self.enabled = self.email_config.get('enabled', False)
        
        # Throttling state: {rule_name: last_alert_time}
        self._last_alerts: Dict[str, float] = {}
        self.cooldown = self.email_config.get('cooldown_seconds', 300) # Default 5 mins

    def send_alert(self, rule: Dict[str, Any], log_line: str):
        """Sends an email alert if enabled and not throttled."""
        if not self.enabled:
            return

        rule_name = rule['name']
        now = time.time()
        
        # Throttling check
        if rule_name in self._last_alerts:
            elapsed = now - self._last_alerts[rule_name]
            if elapsed < self.cooldown:
                logger.debug(f"Alert throttled for {rule_name}. Next alert allowed in {int(self.cooldown - elapsed)}s")
                return

        logger.info(f"Sending alert for rule: {rule_name}")
        
        # Prepare message
        subject = f"[{rule['severity']}] Log Analysis Alert: {rule_name}"
        body = (
            f"Rule Matched: {rule_name}\n"
            f"Severity: {rule['severity']}\n"
            f"Log Line: {log_line}\n"
            f"Time: {time.ctime(now)}\n\n"
            f"Remediation Action: {rule.get('remediation', {}).get('action', 'None')}"
        )

        try:
            self._send_email(subject, body)
            self._last_alerts[rule_name] = now
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")

    def _send_email(self, subject: str, body: str):
        """Internal method to handle SMTP transport."""
        recipient = self.email_config.get('recipient')
        smtp_server = self.email_config.get('smtp_server')
        smtp_port = self.email_config.get('smtp_port', 587)
        
        # Get credentials from environment for security
        smtp_user = os.environ.get('SMTP_USER')
        smtp_pass = os.environ.get('SMTP_PASS')

        if not all([recipient, smtp_server]):
            logger.warning("Email configuration incomplete. Skipping alert.")
            return

        msg = MIMEMultipart()
        msg['From'] = smtp_user or "log-remediator@example.com"
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # In a real environment, you'd un-comment the SMTP logic below
        # For this demonstration, we will log the email instead
        logger.info(f"[EMAIL] Subject: {subject}")
        logger.debug(f"[EMAIL BODY]\n{body}")

        if smtp_user and smtp_pass:
            logger.info(f"Attempting to connect to {smtp_server}:{smtp_port}")
            # with smtplib.SMTP(smtp_server, smtp_port) as server:
            #     server.starttls()
            #     server.login(smtp_user, smtp_pass)
            #     server.send_message(msg)
            # logger.info("Email sent successfully.")
        else:
            logger.warning("No SMTP credentials found in environment. Email NOT sent to server (Mocking).")
