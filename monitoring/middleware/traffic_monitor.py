# traffic_monitoring/middleware/traffic_monitor.py

import logging
import psutil
import time

logger = logging.getLogger(__name__)

class TrafficMonitorMiddleware:
    """
    Middleware to monitor request traffic and system usage (users, instance, memory).
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.request_count = 0
        self.start_time = time.time()

    def __call__(self, request):
        self.request_count += 1
        uptime = time.time() - self.start_time
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=None)

        logger.info(
            f"📊 TrafficMonitor | Requests so far: {self.request_count}, "
            f"Uptime: {uptime:.1f}s, CPU: {cpu}%, Memory: {mem.percent}%"
        )
        

        response = self.get_response(request)
        return response
