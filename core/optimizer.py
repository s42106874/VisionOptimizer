import psutil
import os
import ctypes

class SystemOptimizer:
    @staticmethod
    def boost_memory():
        """
        Aggressively clears working sets of all processes.
        Returns dict with details: freed_bytes, before_percent, after_percent, processes_count
        """
        try:
            # Stats before
            mem_info_before = psutil.virtual_memory()
            mem_before_used = mem_info_before.used
            percent_before = mem_info_before.percent
            
            # Windows API to empty working set
            psapi = ctypes.windll.psapi
            kernel32 = ctypes.windll.kernel32
            
            count = 0
            
            # Walk through all processes
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    pid = proc.info['pid']
                    if pid == 0 or pid == 4: # Skip System Idle and System
                        continue
                        
                    handle = kernel32.OpenProcess(0x001F0FFF, False, pid) # All access
                    if handle:
                        ret = psapi.EmptyWorkingSet(handle)
                        if ret:
                            count += 1
                        kernel32.CloseHandle(handle)
                except Exception:
                    continue
                    
            # Check result
            mem_info_after = psutil.virtual_memory()
            mem_after_used = mem_info_after.used
            percent_after = mem_info_after.percent
            
            freed = max(0, mem_before_used - mem_after_used)
            
            return {
                'freed_bytes': freed,
                'before_percent': percent_before,
                'after_percent': percent_after,
                'processes_count': count
            }
        except Exception as e:
            print(f"Optimization error: {e}")
            return {
                'freed_bytes': 0,
                'before_percent': 0,
                'after_percent': 0,
                'processes_count': 0
            }
