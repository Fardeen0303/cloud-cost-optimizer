import logging
import os
import requests

logger = logging.getLogger(__name__)

SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
TEAMS_WEBHOOK_URL = os.getenv('TEAMS_WEBHOOK_URL')


def _post(url: str, payload: dict, platform: str):
    try:
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        logger.info(f"{platform} alert sent successfully")
    except Exception as e:
        logger.error(f"Failed to send {platform} alert: {e}")


def send_slack(message: str, color: str = "#36a64f"):
    if not SLACK_WEBHOOK_URL:
        return
    _post(SLACK_WEBHOOK_URL, {
        "attachments": [{
            "color": color,
            "text": message,
            "footer": "Cloud Cost Optimizer"
        }]
    }, "Slack")


def send_teams(title: str, message: str, color: str = "00FF00"):
    if not TEAMS_WEBHOOK_URL:
        return
    _post(TEAMS_WEBHOOK_URL, {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": color,
        "summary": title,
        "sections": [{"activityTitle": title, "activityText": message}]
    }, "Teams")


def alert(title: str, message: str, level: str = "info"):
    color_map = {"info": ("#36a64f", "00FF00"), "warning": ("#ffc107", "FFC107"), "critical": ("#dc3545", "FF0000")}
    slack_color, teams_color = color_map.get(level, color_map["info"])
    full_message = f"*{title}*\n{message}"
    send_slack(full_message, slack_color)
    send_teams(title, message, teams_color)
