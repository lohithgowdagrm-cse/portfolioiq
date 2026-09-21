"""URL routes for alert rules and events."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertRuleViewSet, AlertEventListView, AcknowledgeAlertView

router = DefaultRouter()
router.register(r"rules", AlertRuleViewSet, basename="alert_rule")

urlpatterns = [
    path("", include(router.urls)),
    path("events/", AlertEventListView.as_view(), name="alert_events"),
    path("events/<uuid:pk>/ack/", AcknowledgeAlertView.as_view(), name="acknowledge_alert"),
]
