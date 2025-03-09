import json
import requests
from datetime import datetime
from ..utils.environment import EnvironmentUtils as env
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class SlackNotifier:
    def __init__(self):
        self.webhook_url = env.get_env_var('SLACK_WEBHOOK')  # secrets.envから取得

    def send_error_notification(self, operation_type, error_message):
        """エラー通知をSlackに送信"""
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 エラーが発生しました",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*操作種別:*\n{operation_type}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*発生日時:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*エラー内容:*\n```{error_message}```"
                    }
                },
                {
                    "type": "divider"
                }
            ]
            
            payload = {
                "blocks": blocks
            }
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info("✓ Slackにエラー通知を送信しました")
                return True
            else:
                logger.error(f"❌ Slack通知の送信に失敗: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Slack通知の送信に失敗: {str(e)}")
            return False 