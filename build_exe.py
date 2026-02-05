import PyInstaller.__main__
import os
import shutil
import sys

# Increase recursion depth for complex imports
sys.setrecursionlimit(5000)

current_dir = os.path.dirname(os.path.abspath(__file__))
temp_build_dir = os.path.join(os.path.expanduser("~"), "Desktop", "VisionBuildTemp")

# Clean previous build temp
if os.path.exists(temp_build_dir):
    try:
        shutil.rmtree(temp_build_dir)
    except:
        print("Warning: Could not clean temp dir, proceeding anyway...")

os.makedirs(temp_build_dir, exist_ok=True)

print(f"Starting build process in temp dir: {temp_build_dir}")

try:
    # Run PyInstaller
    PyInstaller.__main__.run([
        os.path.join(current_dir, 'main.py'),
        '--name=VisionOptimizer',
        '--windowed',
        f'--icon={os.path.join(current_dir, "icon.ico")}',
        '--noconfirm',
        '--clean',
        f'--workpath={os.path.join(temp_build_dir, "build")}',
        f'--distpath={os.path.join(temp_build_dir, "dist")}',
        f'--specpath={temp_build_dir}',
        '--hidden-import=PySide6',
        '--hidden-import=psutil',
        # Add core and ui paths to search path
        f'--paths={current_dir}',
        f'--add-data={os.path.join(current_dir, "icon.ico")};.',
        '--uac-admin',
    ])

    print("Build finished successfully!")
    
    # Move result back
    dist_src = os.path.join(temp_build_dir, "dist", "VisionOptimizer")
    final_dest = os.path.join(current_dir, "dist", "VisionOptimizer")
    
    if os.path.exists(os.path.join(current_dir, "dist")):
        shutil.rmtree(os.path.join(current_dir, "dist"))
        
    shutil.copytree(dist_src, final_dest)
    print(f"Executable moved to: {final_dest}\\VisionOptimizer.exe")
    
    # Cleanup
    shutil.rmtree(temp_build_dir)

except Exception as e:
    print(f"Build failed: {e}")

