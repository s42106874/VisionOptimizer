import winreg
import ctypes
import os

class StartupManager:
    # Registry Paths
    PATHS = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run", r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32"),
    ]
    
    @staticmethod
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    @staticmethod
    def get_startup_items():
        """
        Retrieves startup items from HKCU and HKLM.
        Returns: list of dicts {'name', 'command', 'enabled', 'root', 'can_toggle'}
        """
        items = []
        is_admin = StartupManager.is_admin()
        
        # 1. Registry Items
        for root_hkey, run_path, approved_path in StartupManager.PATHS:
            root_name = "HKCU" if root_hkey == winreg.HKEY_CURRENT_USER else "HKLM"
            can_write = (root_hkey == winreg.HKEY_CURRENT_USER) or is_admin
            
            # Get Disabled Status map
            disabled_items = set()
            try:
                with winreg.OpenKey(root_hkey, approved_path, 0, winreg.KEY_READ) as key:
                    count = winreg.QueryInfoKey(key)[1]
                    for i in range(count):
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            if isinstance(value, bytes) and len(value) >= 1:
                                # Windows Convention: First byte odd = Disabled (03..), Even = Enabled (02..)
                                if value[0] % 2 != 0: 
                                    disabled_items.add(name)
                        except OSError:
                            pass
            except OSError:
                pass # Key might not exist
            
            # Read Run Key
            try:
                with winreg.OpenKey(root_hkey, run_path, 0, winreg.KEY_READ) as key:
                    count = winreg.QueryInfoKey(key)[1]
                    for i in range(count):
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            items.append({
                                'name': name,
                                'command': value,
                                'enabled': name not in disabled_items,
                                'root': root_name,
                                'can_toggle': can_write,
                                'approved_path': approved_path,
                                'root_hkey_val': root_hkey,
                                'type': 'registry'
                            })
                        except OSError:
                            pass
            except OSError:
                pass

        # 2. Startup Folder Items (Basic support: View and Delete only, Toggle is hard without admin/registry tricks)
        # For now, let's just list checking Registry is often what users mean by "Startup Manager".
        # If user says "incomplete", it might differ from Task Manager which aggregates everything.
        # Adding folders adds complexity (Start Menu shortcuts). 
        # Let's focus on making Registry ones work perfectly first.
                
        return items

    @staticmethod
    def set_startup_enabled(item, enabled):
        """
        Enable/Disable item by writing to StartupApproved key.
        """
        try:
            root = item['root_hkey_val']
            path = item['approved_path']
            name = item['name']
            
            # Need WRITE access. If HKLM and not admin, this will fail.
            # UI should prevent this call if not admin.
            
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
                # Try to read existing
                data = None
                try:
                    current_val, type_ = winreg.QueryValueEx(key, name)
                    if isinstance(current_val, bytes) and len(current_val) > 0:
                        ba = bytearray(current_val)
                        if enabled:
                            if ba[0] % 2 != 0: ba[0] -= 1 # Enable: Ensure even
                        else:
                            if ba[0] % 2 == 0: ba[0] += 1 # Disable: Ensure odd
                        data = bytes(ba)
                except FileNotFoundError:
                    pass

                if data is None:
                     # Create new 12-byte blob
                     # Enabled: 02... Disabled: 03...
                     data = bytes([0x02 if enabled else 0x03] + [0x00]*11)

                winreg.SetValueEx(key, name, 0, winreg.REG_BINARY, data)
                return True
                
        except OSError as e:
            print(f"Registry Error: {e}")
            return False

    @staticmethod
    def delete_startup_item(item):
        try:
            root = item['root_hkey_val']
            # Map path back roughly
            run_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            if item['root'] == 'HKLM' and 'Run32' in item['approved_path']:
                 run_path = r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"
            
            # Open Run key
            with winreg.OpenKey(root, run_path, 0, winreg.KEY_WRITE) as key:
                winreg.DeleteValue(key, item['name'])
                
            # Also try to clean up Approved key if exists
            try:
                with winreg.OpenKey(root, item['approved_path'], 0, winreg.KEY_WRITE) as key:
                    winreg.DeleteValue(key, item['name'])
            except:
                pass
                
            return True
        except OSError:
            return False
