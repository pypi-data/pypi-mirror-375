from django.conf import settings

BOT_TOKEN = getattr(settings, "DJANGO_TELEGRAM_SUPPORT_BOT_TOKEN", None)
CHAT_ID = getattr(settings, "DJANGO_TELEGRAM_SUPPORT_CHAT_ID", None)
SOURCE = getattr(settings, "DJANGO_TELEGRAM_SUPPORT_SOURCE", "unknown-project")
TELEGRAM_SUPPORT_TEMPLATE = getattr(settings, "DJANGO_TELEGRAM_SUPPORT_TEMPLATE", "support/custom_support_form.html")

TELEGRAM_SUPPORT_CONTEXT = getattr(
    settings,
    "DJANGO_TELEGRAM_SUPPORT_CONTEXT", {
    "brand_name": "Django Telegram Support",
    "page_title": "Contact Support",
})

MAX_MESSAGE_LEN = getattr(settings, "TELEGRAM_SUPPORT_MAX_MESSAGE_LEN", 3500)
THROTTLE_SECONDS = getattr(settings, "TELEGRAM_SUPPORT_THROTTLE_SECONDS", 60)