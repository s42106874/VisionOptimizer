import os
import sys

def get_desktop_path():
    return os.path.join(os.path.expanduser("~"), "Desktop")

def debug():
    desktop = get_desktop_path()
    print(f"=== PATH DEBUG INFO ===")
    print(f"User Home: {os.path.expanduser('~')}")
    print(f"Desktop Path: {desktop}")
    print(f"Exists: {os.path.exists(desktop)}")
    
    if os.path.exists(desktop):
        print("\n=== LISTING DESKTOP ===")
        try:
            with os.scandir(desktop) as entries:
                for entry in entries:
                    print(f" - {entry.name} ({'DIR' if entry.is_dir() else 'FILE'})")
        except Exception as e:
            print(f"ERROR reading desktop: {e}")
            
    print("\n=== TRYING TO FIND 'TEST' FOLDER ===")
    test_path = os.path.join(desktop, "TEST")
    if os.path.exists(test_path):
        print(f"TEST folder FOUND at: {test_path}")
        try:
            print("Content:")
            for f in os.listdir(test_path):
                print(f"  - {f}")
        except Exception as e:
            print(f"Cannot read TEST content: {e}")
    else:
        print(f"TEST folder NOT FOUND at expected path: {test_path}")

if __name__ == "__main__":
    debug()
