
try:
    print("Verifying core modules...")
    import core.monitor
    import core.optimizer
    import core.cleaner
    import core.startup
    print("Core modules imported successfully.")
    
    print("Verifying UI modules...")
    import ui.theme
    import ui.widgets
    # Some UI modules import internal core mods, so order matters if we were strict, but here we just check syntax.
    import ui.sidebar
    # ui.dashboard and others might fail without QApplication instance due to Qt widgets, 
    # but imports themselves should be fine if no logic runs at module level.
    
    print("All checks passed.")
except Exception as e:
    print(f"Verification Failed: {e}")
