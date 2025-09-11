import psutil
import time
from django.utils.deprecation import MiddlewareMixin

class TrafficMonitoringMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        # Request/Response timing
        duration = time.time() - getattr(request, "start_time", time.time())

        # Get system memory stats
        memory = psutil.virtual_memory()
        memory_info = f"Used: {memory.used // (1024*1024)}MB / Total: {memory.total // (1024*1024)}MB"

        # Get network I/O stats
        net_io = psutil.net_io_counters()
        traffic_info = f"Bytes Sent: {net_io.bytes_sent}, Bytes Received: {net_io.bytes_recv}"

        # Log to console (you can also save to DB or file)
        print(f"""
        ---- Traffic Log ----
        Path: {request.path}
        Method: {request.method}
        Duration: {duration:.2f}s
        Memory: {memory_info}
        Network: {traffic_info}
        ---------------------
        """)

        return response
