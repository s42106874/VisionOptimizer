import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QCloseEvent
from ui.theme import Theme
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from ui.boost_page import BoostPage
from ui.cleaner_page import CleanerPage
from ui.startup_page import StartupPage
from ui.hardware_page import HardwarePage
from ui.file_scanner_page import FileScannerPage
from ui.widgets import CustomDialog
from ui.title_bar import TitleBar
import qdarktheme

def create_tray_icon():
    """Create a simple colored icon for system tray"""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor(Theme.PRIMARY))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, 28, 28)
    painter.setBrush(QColor("#15161e"))
    painter.drawEllipse(8, 8, 16, 16)
    painter.end()
    return QIcon(pixmap)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("傲視系統優化大師")
        self.resize(1200, 800)
        
        # Main Container (Window Logic)
        self.main_container = QWidget()
        self.main_container.setObjectName("MainContainer")
        self.main_container.setStyleSheet(f"""
            QWidget#MainContainer {{
                background-color: {Theme.BACKGROUND};
                border: 1px solid #2f334d;
                border-radius: 10px;
            }}
        """)
        self.setCentralWidget(self.main_container)
        
        # Vertical Layout (Title Bar + Body)
        self.window_layout = QVBoxLayout(self.main_container)
        self.window_layout.setContentsMargins(0, 0, 0, 0)
        self.window_layout.setSpacing(0)
        
        # 1. Custom Title Bar
        self.title_bar = TitleBar(self)
        self.window_layout.addWidget(self.title_bar)
        
        # 2. Body (Sidebar + Content)
        body_widget = QWidget()
        body_widget.setStyleSheet("background-color: transparent;")
        body_layout = QHBoxLayout(body_widget)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self.switch_page)
        
        # Content Content
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"""
            QStackedWidget {{
                border-bottom-right-radius: 10px; 
                background-color: {Theme.BACKGROUND};
            }}
        """)
        
        # Pages
        self.page_dashboard = Dashboard()
        self.page_boost = BoostPage()
        self.page_cleaner = CleanerPage()
        self.page_startup = StartupPage()
        self.page_hardware = HardwarePage()
        self.page_file_scanner = FileScannerPage()
        
        self.content_stack.addWidget(self.page_dashboard)
        self.content_stack.addWidget(self.page_boost)
        self.content_stack.addWidget(self.page_cleaner)
        self.content_stack.addWidget(self.page_startup)
        self.content_stack.addWidget(self.page_hardware)
        self.content_stack.addWidget(self.page_file_scanner)
        
        # Add to body layout
        body_layout.addWidget(self.sidebar)
        body_layout.addWidget(self.content_stack)
        
        self.window_layout.addWidget(body_widget)
        
        # Select first page
        self.sidebar.btn_dashboard.click()
        
        # Tray setup
        self.tray = None
        self.init_tray()

    def switch_page(self, page_name):
        pages = {
            "儀表板": 0,
            "一鍵加速": 1,
            "垃圾清理": 2,
            "啟動管理": 3,
            "硬體資訊": 4,
            "檔案掃描": 5
        }
        if page_name in pages:
            self.content_stack.setCurrentIndex(pages[page_name])

    def init_tray(self):
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray = QSystemTrayIcon(self)
            self.tray.setIcon(create_tray_icon())
            self.tray.setToolTip("傲視系統優化大師\n正在初始化...")
            
            # Connect dashboard monitor to tray tooltip
            self.page_dashboard.monitor.stats_updated.connect(self.update_tray_tooltip)
            
            # Pass tray icon to boost page for notifications
            self.page_boost.set_tray_icon(self.tray)
            
            tray_menu = QMenu()
            tray_menu.setStyleSheet(f"""
                QMenu {{
                    background-color: {Theme.SURFACE};
                    color: {Theme.TEXT_PRIMARY};
                    border: 1px solid {Theme.SURFACE_HOVER};
                    border-radius: 5px;
                    padding: 5px;
                }}
                QMenu::item {{
                    padding: 8px 15px;
                }}
                QMenu::item:selected {{
                    background-color: {Theme.PRIMARY};
                    color: #15161e;
                }}
                QMenu::separator {{
                    height: 1px;
                    background: #2f334d;
                    margin: 5px;
                }}
            """)
            
            # Add status info actions (disabled, just for display)
            self.act_status_cpu = tray_menu.addAction("CPU: --%")
            self.act_status_cpu.setEnabled(False)
            self.act_status_ram = tray_menu.addAction("RAM: --%")
            self.act_status_ram.setEnabled(False)
            
            tray_menu.addSeparator()
            
            action_show = tray_menu.addAction("顯示主視窗")
            action_show.triggered.connect(self.showNormal)
            
            action_boost = tray_menu.addAction("🚀 一鍵加速")
            action_boost.triggered.connect(lambda: self.page_boost.start_boost() if self.page_boost.btn_boost.isEnabled() else None)
            
            tray_menu.addSeparator()
            
            action_quit = tray_menu.addAction("結束程式")
            action_quit.triggered.connect(self.quit_app)
            
            self.tray.setContextMenu(tray_menu)
            self.tray.activated.connect(lambda reason: self.showNormal() if reason == QSystemTrayIcon.DoubleClick else None)
            self.tray.show()

    def update_tray_tooltip(self, stats):
        if self.tray:
            cpu = stats['cpu']
            ram = stats['ram_percent']
            net_recv = stats['net_recv']
            
            # Format net speed
            if net_recv < 1024:
                speed = f"{int(net_recv)} B/s"
            elif net_recv < 1024**2:
                speed = f"{net_recv/1024:.1f} KB/s"
            else:
                speed = f"{net_recv/1024**2:.1f} MB/s"
                
            msg = f"傲視系統優化大師\nCPU: {cpu}%\nRAM: {ram}%\n下載: {speed}"
            self.tray.setToolTip(msg)
            
            # Update menu items text if menu exists
            if hasattr(self, 'act_status_cpu'):
                self.act_status_cpu.setText(f"CPU: {cpu}%")
                self.act_status_ram.setText(f"RAM: {ram}%")

    def quit_app(self):
        self.force_quit = True
        QApplication.instance().quit()

    def closeEvent(self, event: QCloseEvent):
        if hasattr(self, 'force_quit') and self.force_quit:
            # Clean exit
            try:
                self.page_dashboard.close_monitor()
            except: pass
            try:
                self.page_boost.close_monitor()
            except: pass
            event.accept()
            return

        dialog = CustomDialog("關閉程式", "您希望將程式縮小至系統托盤以在背景繼續優化，還是完全結束程式？", self)
        result = dialog.exec()
        
        if result == 101: # Minimize to Tray
            event.ignore()
            self.hide()
            if self.tray:
                self.tray.showMessage("傲視系統優化大師", "程式正在背景執行...", QSystemTrayIcon.Information, 2000)
        elif result == 102: # Quit
            # Safely stop all threads
            try:
                self.page_dashboard.close_monitor()
            except:
                pass
            try:
                self.page_boost.close_monitor()
            except:
                pass
            event.accept()
            QApplication.instance().quit()
        else: # Cancel
            event.ignore()

def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    # Setup AppUserModelID for Windows Taskbar Icon
    import ctypes
    myappid = 'vision.optimizer.master.1.0'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    app = QApplication(sys.argv)
    
    # Helper for PyInstaller --onefile support
    def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    
    # Set Application Icon
    icon_path = resource_path("icon.ico")
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    
    # Apply Dark Theme
    qdarktheme.setup_theme("dark", corner_shape="rounded")
    
    window = MainWindow()
    window.setWindowIcon(app_icon) # Ensure window also gets the icon
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
