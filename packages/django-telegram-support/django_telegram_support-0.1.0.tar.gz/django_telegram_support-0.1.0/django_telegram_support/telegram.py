import requests
from .conf import BOT_TOKEN, CHAT_ID

API_URL = "https://api.telegram.org/bot{token}/{method}"

def send_message(text: str, parse_mode: str | None = "Markdown") -> bool:
    if not BOT_TOKEN or not CHAT_ID:
        return False
    url = API_URL.format(token=BOT_TOKEN, method="sendMessage")
    payload = {"chat_id": CHAT_ID, "text": text[:4096]}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        resp = requests.post(url, json=payload, timeout=7)
        return resp.ok
    except requests.RequestException:
        return False
