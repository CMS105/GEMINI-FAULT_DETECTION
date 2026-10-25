import os
import requests

def send_slack_alert(message: str, webhook_url: str = None):
    """
    Sends automated alerts to a Slack channel when Gemini detects critical issues.
    """
    url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        print("[ALERT SKIPPED]: No SLACK_WEBHOOK_URL configured in .env")
        return
    
    try:
        payload = {"text": f"🚨 *Enterprise AI Triage Alert*\n{message}"}
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        print("[SLACK ALERT SENT]: Notification delivered successfully.")
    except Exception as err:
        print(f"[SLACK ALERT ERROR]: Failed to send notification: {err}")