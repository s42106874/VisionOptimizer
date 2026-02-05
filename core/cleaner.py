import os
import shutil
import glob
import tempfile

class JunkCleaner:
    @staticmethod
    def scan_junk():
        """
        Scans for junk files in common locations.
        Returns a list of dicts: {'path': str, 'size': int, 'type': str}
        """
        junk_files = []
        
        # Resolve properly
        user_temp = os.environ.get('TEMP') or tempfile.gettempdir()
        win_temp = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp')
        
        locations = [
            (user_temp, 'User Temp'),
            (win_temp, 'Windows Temp'),
            (os.path.join(os.environ.get('LOCALAPPDATA'), 'Microsoft', 'Windows', 'Explorer'), 'Thumbnail Cache'),
        ]
        
        # Use set to avoid duplicates if paths overlap
        scanned_paths = set()
        
        for path, label in locations:
            if not path or not os.path.exists(path):
                continue
                
            # Normalize path
            path = os.path.abspath(path)
            if path in scanned_paths:
                continue
            scanned_paths.add(path)
                
            try:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        try:
                            filepath = os.path.join(root, file)
                            # Skip if file is in use (basic check: try open)
                            # Actually scanning doesn't need open check, cleaning does.
                            # Just scan everything suitable.
                            
                            size = os.path.getsize(filepath)
                            junk_files.append({
                                'path': filepath,
                                'size': size,
                                'type': label
                            })
                        except:
                            pass
            except:
                pass
                
        return junk_files

    @staticmethod
    def clean_files(file_list):
        """
        Deletes the specified files.
        Returns (success_count, fail_count, total_size_cleaned)
        """
        success = 0
        fail = 0
        cleaned_size = 0
        
        for item in file_list:
            try:
                if os.path.isfile(item['path']):
                    os.remove(item['path'])
                    success += 1
                    cleaned_size += item['size']
                elif os.path.isdir(item['path']):
                    shutil.rmtree(item['path'])
                    success += 1
                    cleaned_size += item['size']
            except:
                fail += 1
                
        return success, fail, cleaned_size
