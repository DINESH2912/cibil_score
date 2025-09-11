import time
import psutil
import logging

# Dedicated logger for API traffic
logger = logging.getLogger("api_logger")

class APILoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time

        # Memory used in MB
        memory_used = psutil.Process().memory_info().rss / (1024 * 1024)

        # Bytes sent & received
        bytes_sent = len(response.content)
        bytes_received = int(request.META.get('CONTENT_LENGTH') or 0)

        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        # Log request info
        logger.info(
            f"Path: {request.path}\n"
            f"Client IP: {ip_address}\n"
            f"Method: {request.method}\n"
            f"Status Code: {response.status_code}\n"
            f"Duration: {duration:.2f}s\n"
            f"Memory Used: {memory_used:.2f} MB\n"
            f"Bytes Sent: {bytes_sent}\n"
            f"Bytes Received: {bytes_received}\n"
            "---------------------"
        )

        return response
