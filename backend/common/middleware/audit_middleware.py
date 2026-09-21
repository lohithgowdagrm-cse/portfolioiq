"""Audit middleware recording request IP and user context."""
import threading

_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, "request", None)


def get_client_ip(request):
    if not request:
        return "127.0.0.1"
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "127.0.0.1")


class AuditLogMiddleware:
    """Attaches request to thread-local storage for audit trail hooks."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        _thread_locals.request = None
        return response
