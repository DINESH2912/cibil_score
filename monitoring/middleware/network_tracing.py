# traffic_monitoring/middleware/network_tracing.py

import logging
import time

logger = logging.getLogger(__name__)

class NetworkTracingMiddleware:
    """
    Middleware to trace each request/response (user in and out).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # Log incoming request
        logger.info(
            f"➡️ Request: {request.method} {request.get_full_path()} "
            f"from {getattr(request, 'user', 'Anonymous')}"
        )

        response = self.get_response(request)

        duration = time.time() - start_time

        # Log outgoing response
        logger.info(
            f"⬅️ Response: {response.status_code} {request.get_full_path()} "
            f"(took {duration:.3f}s)"
        )

        return response
