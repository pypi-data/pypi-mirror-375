from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

from .forms import SupportForm
from .telegram import send_message
from .conf import THROTTLE_SECONDS, SOURCE, TELEGRAM_SUPPORT_CONTEXT, TELEGRAM_SUPPORT_TEMPLATE

def _throttle_key(request):
    ip = request.META.get("REMOTE_ADDR", "unknown")
    return f"tg_support_throttle:{ip}"

def _resolve_template_name():
    try:
        get_template(TELEGRAM_SUPPORT_TEMPLATE)
        return TELEGRAM_SUPPORT_TEMPLATE
    except TemplateDoesNotExist:
        return "django_telegram_support/support_form.html"

@require_http_methods(["GET", "POST"])
def support_view(request):
    template_name = _resolve_template_name()

    if request.method == "POST":
        form = SupportForm(request.POST)
        if form.is_valid():
            # Honeypot check
            if form.cleaned_data.get("website"):
                return redirect(request.path)

            # Throttle per IP
            key = _throttle_key(request)
            if cache.get(key):
                messages.error(request, "Please wait a minute before sending another message.")
                return redirect(request.path)
            cache.set(key, timezone.now().timestamp(), THROTTLE_SECONDS)

            email = form.cleaned_data["email"].strip()
            body = form.cleaned_data["message"].strip()

            header = f"*Support ({SOURCE})*\n*Email:* {email}\n\n*Message:*\n"
            remaining = 4096 - len(header)
            text = header + body[: max(0, remaining)]

            if send_message(text):
                messages.success(request, "Thanks! Your message has been sent.")
                # if SUCCESS_REDIRECT_NAME:
                #     return redirect(SUCCESS_REDIRECT_NAME)
                return redirect(request.path)
            else:
                messages.error(request, "Could not send your message. Please try again later.")
    else:
        form = SupportForm()

    context = {"form": form, **TELEGRAM_SUPPORT_CONTEXT}
    return render(request, template_name, context)
