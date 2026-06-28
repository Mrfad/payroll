# Backend\payroll\middleware.py
import logging
import time

logger = logging.getLogger("api_requests")


class ApiLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        user = request.user.username if request.user.is_authenticated else "Anonymous"

        # Log format: [METHOD] PATH - STATUS - USER - DURATION
        log_message = f"[{request.method}] {request.path} - {response.status_code} - {user} - {duration:.2f}s"

        if response.status_code >= 500:
            logger.error(log_message)
        elif response.status_code >= 400:
            logger.warning(log_message)
        else:
            logger.info(log_message)

        return response


import threading

_thread_locals = threading.local()


def get_current_user():
    return getattr(_thread_locals, "user", None)


def get_request_source():
    return getattr(_thread_locals, "source", "System / CLI")


class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = request.user if hasattr(request, "user") else None

        # Determine the source of the action
        source = "Unknown"
        if request.path.startswith("/admin/"):
            source = "Django Backend Admin"
        elif request.path.startswith("/api/"):
            client_platform = request.headers.get("X-Client-Platform", "API Client")
            source = f"API ({client_platform})"

        _thread_locals.source = source

        response = self.get_response(request)

        _thread_locals.user = None
        _thread_locals.source = None
        return response
