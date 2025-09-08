from django.urls import path
from .views import support_view

app_name = "django_telegram_support"
urlpatterns = [path("", support_view, name="support")]