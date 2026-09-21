"""Views for managing risk alert rules and events."""
from apps.alerts.models import AlertEvent, AlertRule
from apps.alerts.serializers import AlertEventSerializer, AlertRuleSerializer
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response


class AlertRuleViewSet(viewsets.ModelViewSet):
    serializer_class = AlertRuleSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        return AlertRule.objects.filter(user=self.request.user).select_related("portfolio").order_by("-created_at")


class AlertEventListView(generics.ListAPIView):
    serializer_class = AlertEventSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return AlertEvent.objects.filter(
            rule__user=self.request.user
        ).select_related("rule", "rule__portfolio").order_by("-created_at")


class AcknowledgeAlertView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        try:
            event = AlertEvent.objects.get(id=pk, rule__user=request.user)
        except AlertEvent.DoesNotExist:
            return Response(
                {"error": {"code": "EVENT_NOT_FOUND", "message": "Alert event not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )

        event.is_acknowledged = True
        event.save(update_fields=["is_acknowledged"])
        return Response({"message": "Alert acknowledged successfully."})
