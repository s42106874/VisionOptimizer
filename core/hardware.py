import psutil
import platform
import subprocess

class HardwareInfo:
    @staticmethod
    def get_cpu_info():
        try:
            cpu_name = platform.processor()
            cpu_count = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()
            freq_str = f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A"
            return {
                'name': cpu_name or "Unknown CPU",
                'cores': cpu_count,
                'frequency': freq_str
            }
        except:
            return {'name': 'Unknown', 'cores': 0, 'frequency': 'N/A'}

    @staticmethod
    def get_gpu_info():
        try:
            # Use PowerShell for better formatting and reliability
            cmd = "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"
            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command', cmd],
                capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW
            )
            gpus = [line.strip() for line in result.stdout.split('\n') if line.strip()]
            return list(set(gpus)) if gpus else ['Unknown GPU'] # Remove duplicates
        except:
            return ['Unknown GPU']

    @staticmethod
    def get_memory_info():
        mem = psutil.virtual_memory()
        return {
            'total': round(mem.total / (1024**3), 1),
            'available': round(mem.available / (1024**3), 1),
            'used': round(mem.used / (1024**3), 1),
            'percent': mem.percent
        }

    @staticmethod
    def get_disk_info():
        disks = []
        # all=False to ignore CD-ROMs etc unless mounted
        for partition in psutil.disk_partitions(all=False):
            try:
                # Filter out CD-ROMs and unmounted drives
                if 'cdrom' in partition.opts or partition.fstype == '':
                    continue
                    
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': round(usage.total / (1024**3), 1),
                    'used': round(usage.used / (1024**3), 1),
                    'free': round(usage.free / (1024**3), 1),
                    'percent': usage.percent
                })
            except:
                pass
        return disks

    @staticmethod
    def get_system_info():
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'machine': platform.machine(),
            'hostname': platform.node()
        }
