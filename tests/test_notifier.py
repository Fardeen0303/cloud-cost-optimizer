import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'services', 'notifier'))
import notifier


def test_slack_not_called_without_webhook():
    with patch('notifier.requests.post') as mock_post:
        notifier.SLACK_WEBHOOK_URL = None
        notifier.send_slack("test message")
        mock_post.assert_not_called()


def test_teams_not_called_without_webhook():
    with patch('notifier.requests.post') as mock_post:
        notifier.TEAMS_WEBHOOK_URL = None
        notifier.send_teams("title", "message")
        mock_post.assert_not_called()


def test_slack_sends_correct_payload():
    with patch('notifier.requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        notifier.SLACK_WEBHOOK_URL = 'https://hooks.slack.com/test'
        notifier.send_slack("hello slack", color="#36a64f")
        mock_post.assert_called_once()
        payload = mock_post.call_args[1]['json']
        assert payload['attachments'][0]['text'] == "hello slack"
        assert payload['attachments'][0]['color'] == "#36a64f"


def test_teams_sends_correct_payload():
    with patch('notifier.requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        notifier.TEAMS_WEBHOOK_URL = 'https://outlook.office.com/webhook/test'
        notifier.send_teams("Alert Title", "Alert Body", color="FF0000")
        mock_post.assert_called_once()
        payload = mock_post.call_args[1]['json']
        assert payload['summary'] == "Alert Title"
        assert payload['themeColor'] == "FF0000"


def test_alert_calls_both():
    with patch('notifier.send_slack') as mock_slack, patch('notifier.send_teams') as mock_teams:
        notifier.alert("title", "message", level="warning")
        mock_slack.assert_called_once()
        mock_teams.assert_called_once()
