# Django Telegram Support

A reusable **Django app** that provides a simple support/contact form and delivers messages directly to **Telegram**.  
Lightweight, pluggable, and configurable — drop it into any Django project in minutes.

---

## Features

- Support form with **email** + **message** fields  
- Basic anti-spam (honeypot + per-IP throttling)  
- Messages delivered straight to your Telegram chat  
- Adds a `SOURCE` tag so one bot can serve multiple projects  
- Templates are overrideable via settings  
- Safe for Telegram API limits (messages trimmed to 4096 chars)  

---

## Installation

Install from PyPI:

```bash
pip install django-telegram-support
```

Add to `INSTALLED_APPS` in **settings.py**:

```python
INSTALLED_APPS = [
    # ...
    "django_telegram_support",
]
```

Include URLs in your **urls.py**:

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path("support/", include("django_telegram_support.urls", namespace="django_telegram_support")),
]
```

Now open `/support/` in your browser.

---

## Setting up your Telegram bot

1. Open Telegram and chat with **[@BotFather](https://t.me/BotFather)**.  
2. Send `/newbot` and follow the prompts. You’ll receive a **bot token**.  
3. Start a chat with your new bot (click **Start**).  
4. Get your **chat_id** by visiting in a browser:  

   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```

   Then send any message to your bot. Your `chat.id` will appear in the JSON response.  

---

## Settings

Add these to your **settings.py**:

```python
# Required
DJANGO_TELEGRAM_SUPPORT_BOT_TOKEN = "123456789:ABCdefGhIJKlmNoPQRstuVWxyZ"
DJANGO_TELEGRAM_SUPPORT_CHAT_ID = "123456789"
DJANGO_TELEGRAM_SUPPORT_SOURCE = "MyProject"   # project identifier

# Optional: template path (default is internal fallback)
DJANGO_TELEGRAM_SUPPORT_TEMPLATE = "support/custom_support_form.html"

# Optional: context passed to template
DJANGO_TELEGRAM_SUPPORT_CONTEXT = {
    "brand_name": "Django Telegram Support",
    "page_title": "Contact Support",
}

# Limits
TELEGRAM_SUPPORT_MAX_MESSAGE_LEN = 3500   # max user input length
TELEGRAM_SUPPORT_THROTTLE_SECONDS = 60    # per-IP cooldown
```

### Setting Reference

| Setting                             | Description                                                        | Default value                                                                  |
|-------------------------------------|--------------------------------------------------------------------|--------------------------------------------------------------------------------|
| `DJANGO_TELEGRAM_SUPPORT_BOT_TOKEN` | Bot token from BotFather                                           | `None`                                                                         |
| `DJANGO_TELEGRAM_SUPPORT_CHAT_ID`   | Chat/channel/user id for message delivery                          | `None`                                                                         |
| `DJANGO_TELEGRAM_SUPPORT_SOURCE`    | Tag used in message header to identify project                     | `"unknown-project"`                                                            |
| `DJANGO_TELEGRAM_SUPPORT_TEMPLATE`  | Path to override form template                                     | `"support/custom_support_form.html"`                                           |
