import os
import shutil
import subprocess
import sys

def build_safe():
    # 1. Setup paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Create a temp directory in user's temp folder or C drive to avoid Chinese characters
    import tempfile
    
    # Use a fixed temp dir in Desktop to be visible/safe
    base_temp = os.path.join(os.environ["USERPROFILE"], "Desktop", "VisionOptimizer_Build_Tmp")
    
    print(f"Creating temp build environment at: {base_temp}")
    
    if os.path.exists(base_temp):
        try:
            shutil.rmtree(base_temp)
        except Exception as e:
            print(f"Could not clean temp dir: {e}")
            return

    os.makedirs(base_temp)

    # 2. Copy source files
    print("Copying source files...")
    ignore_patterns = shutil.ignore_patterns(
        "__pycache__", "*.pyc", ".git", "dist", "build", "*.spec", "VisionBuildTemp"
    )
    shutil.copytree(current_dir, os.path.join(base_temp, "src"), ignore=ignore_patterns)

    # 3. Build command
    src_dir = os.path.join(base_temp, "src")
    main_py = os.path.join(src_dir, "main.py")
    icon_path = os.path.join(src_dir, "icon.ico")
    
    print("Running PyInstaller...")
    
    # Construct PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        main_py,
        "--name=VisionOptimizer",
        "--windowed",
        "--onefile",
        f"--icon={icon_path}",
        "--clean",
        "--noconfirm",
        f"--add-data={icon_path};.", 
        # "--uac-admin", # Removed to allow running without admin rights
        "--hidden-import=PySide6",
        "--hidden-import=qdarktheme",
        "--exclude-module=PyQt6",
        "--exclude-module=PyQt5",
        "--exclude-module=tkinter",
    ]
    
    try:
        # Run build in the temp src directory
        process = subprocess.run(
            cmd, 
            cwd=src_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        print(process.stdout)
        
        if process.returncode != 0:
            print("Build Failed explicitly.")
            return

        print("Build successful!")
        
        # 4. Copy Output back
        # Check for --onefile output (VisionOptimizer.exe directly in dist)
        exe_in_dist = os.path.join(src_dir, "dist", "VisionOptimizer.exe")
        dir_in_dist = os.path.join(src_dir, "dist", "VisionOptimizer")
        
        target_dir = os.path.join(current_dir, "dist")
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        if os.path.exists(exe_in_dist) and os.path.isfile(exe_in_dist):
            # Onefile mode
            final_exe = os.path.join(target_dir, "VisionOptimizer.exe")
            if os.path.exists(final_exe):
                os.remove(final_exe)
            shutil.copy2(exe_in_dist, final_exe)
            print(f"DONE! Executable is at: {final_exe}")
            
        elif os.path.exists(dir_in_dist) and os.path.isdir(dir_in_dist):
            # Onedir mode
            final_dest = os.path.join(target_dir, "VisionOptimizer")
            if os.path.exists(final_dest):
                shutil.rmtree(final_dest)
            shutil.copytree(dir_in_dist, final_dest)
            print(f"DONE! Application folder is at: {final_dest}")
            
        else:
            print(f"Error: Could not find built artifact in {os.path.join(src_dir, 'dist')}")
            # List directory specifically to debug
            print("Contents of dist:")
            try:
                print(os.listdir(os.path.join(src_dir, "dist")))
            except:
                print("Could not list dist directory")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Cleanup
        print("Cleaning up temp files...")
        try:
            shutil.rmtree(base_temp)
        except:
            print("Warning: Failed to clean up temp files completely.")

if __name__ == "__main__":
    build_safe()
