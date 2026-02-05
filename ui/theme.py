
class Theme:
    # Modern Dark Theme Colors
    BACKGROUND = "#1a1b26"         # Deep background
    SURFACE = "#24283b"            # Card/Widget background
    SURFACE_HOVER = "#2f334d"      # Hover state
    PRIMARY = "#7aa2f7"            # Main Action Blue
    SECONDARY = "#bb9af7"          # Purple accent
    SUCCESS = "#9ece6a"            # Green
    WARNING = "#e0af68"            # Orange/Yellow
    ERROR = "#f7768e"             # Red
    
    TEXT_PRIMARY = "#c0caf5"
    TEXT_SECONDARY = "#a9b1d6"
    
    STYLESHEET = f"""
    QMainWindow {{
        background-color: {BACKGROUND};
    }}
    QWidget {{
        color: {TEXT_PRIMARY};
        font-family: 'Segoe UI', sans-serif;
        font-size: 14px;
    }}
    
    QLabel {{
        background-color: transparent;
    }}
    
    QMessageBox {{
        background-color: {SURFACE};
        border: 1px solid {SURFACE_HOVER};
    }}
    QMessageBox QLabel {{
        color: {TEXT_PRIMARY};
    }}
    QMessageBox QPushButton {{
        background-color: {SURFACE_HOVER};
        color: {TEXT_PRIMARY};
        border-radius: 5px;
        padding: 6px 15px;
        min-width: 60px;
    }}
    QMessageBox QPushButton:hover {{
        background-color: {PRIMARY};
        color: #1a1b26;
    }}
    
    /* Sidebar */
    QWidget#Sidebar {{
        background-color: {BACKGROUND};
        border-right: 1px solid #16161e;
        border-bottom-left-radius: 10px; /* For rounded window corner */
    }}
    
    /* Buttons in Sidebar */
    QPushButton#NavButton {{
        background-color: transparent;
        border: none;
        border-radius: 10px;
        color: {TEXT_SECONDARY};
        text-align: left;
        padding: 12px 20px;
        font-weight: 500;
    }}
    QPushButton#NavButton:hover {{
        background-color: {SURFACE_HOVER};
        color: {TEXT_PRIMARY};
    }}
    QPushButton#NavButton:checked {{
        background-color: {SURFACE};
        color: {PRIMARY};
        border-left: 3px solid {PRIMARY};
    }}
    
    /* Dashboard Cards */
    QFrame#Card {{
        background-color: {SURFACE};
        border-radius: 15px;
        border: 1px solid #1f2335;
    }}
    QFrame#Card:hover {{
        border: 1px solid {PRIMARY};
    }}
    
    QLabel#CardTitle {{
        color: {TEXT_SECONDARY};
        font-size: 13px;
        font-weight: bold;
        text-transform: uppercase;
        background-color: transparent;
    }}
    QLabel#CardValue {{
        color: {TEXT_PRIMARY};
        font-size: 28px;
        font-weight: bold;
        background-color: transparent;
    }}
    
    /* Action Button */
    QPushButton#ActionButton {{
        background-color: {PRIMARY};
        color: #15161e;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }}
    QPushButton#ActionButton:hover {{
        background-color: #89b4fa;
    }}
    QPushButton#ActionButton:pressed {{
        background-color: #6d91de;
    }}
    
    /* Dialogs */
    QDialog {{
        background-color: {BACKGROUND};
    }}
    """
