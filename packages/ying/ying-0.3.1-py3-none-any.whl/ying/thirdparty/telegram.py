"""
https://api.telegram.org/bot{bot_token}/getUpdates
"""
import requests
from ying.config import settings
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def send_message(chat_id, text):
    BOT_TOKEN = settings.get("tg_bot_token", None)
    if BOT_TOKEN is None:
        raise ValueError("tg_bot_token is not configured, please add it.")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    response = requests.post(url, data=payload)
    response_data = response.json()
    if response_data["ok"]:
        message_id = response_data["result"]["message_id"]
        logger.info(response_data)
    else:
        message_id = None
        logger.info(f"Failed to send message to {chat_id}: {text}")
        logger.info(response_data)
    return message_id


def edit_message_text(chat_id, message_id, text):
    BOT_TOKEN = settings.get("tg_bot_token", None)
    if BOT_TOKEN is None:
        raise ValueError("tg_bot_token is not configured, please add it.")

    edit_url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    edit_data = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "Markdown"}
    edit_response = requests.post(edit_url, data=edit_data)
    edit_response_data = edit_response.json()

    if edit_response_data["ok"]:
        logger.info("Message updated successfully")
    else:
        logger.info("Failed to update message")
        logger.info(edit_response_data)
