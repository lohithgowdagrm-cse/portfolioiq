"""Serializers and views for AuditLog."""
from rest_framework import generics, permissions, serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = AuditLog
        fields = ("id", "user_email", "action", "entity_type", "entity_id", "metadata", "ip_address", "timestamp")
        read_only_fields = fields


class AuditLogListView(generics.ListAPIView):
    """List audit events scoped to current user or all events for staff."""
    serializer_class = AuditLogSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return AuditLog.objects.all().select_related("user")
        return AuditLog.objects.filter(user=user).select_related("user")
