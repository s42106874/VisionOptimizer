import psutil
import time
from PySide6.QtCore import QThread, Signal

class SystemMonitor(QThread):
    stats_updated = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.prev_net = psutil.net_io_counters()
        self.prev_time = time.time()

    def run(self):
        while self.running:
            try:
                current_time = time.time()
                cpu = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory()
                disk = psutil.disk_usage('C:')
                
                # Network Speed Calculation
                curr_net = psutil.net_io_counters()
                time_delta = current_time - self.prev_time
                
                # Avoid division by zero
                if time_delta == 0:
                    time_delta = 1
                
                sent_per_sec = (curr_net.bytes_sent - self.prev_net.bytes_sent) / time_delta
                recv_per_sec = (curr_net.bytes_recv - self.prev_net.bytes_recv) / time_delta
                
                self.prev_net = curr_net
                self.prev_time = current_time
                
                stats = {
                    'cpu': cpu,
                    'ram_percent': ram.percent,
                    'ram_used': round(ram.used / (1024**3), 1),
                    'ram_total': round(ram.total / (1024**3), 1),
                    'disk_percent': disk.percent,
                    'disk_free': round(disk.free / (1024**3), 1),
                    'net_sent': sent_per_sec, # Bytes/sec
                    'net_recv': recv_per_sec  # Bytes/sec
                }
                
                self.stats_updated.emit(stats)
                time.sleep(1) 
            except Exception as e:
                print(f"Error in monitor: {e}")
                time.sleep(2)

    def stop(self):
        self.running = False
        self.wait()
