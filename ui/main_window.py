from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from ui.theme import Theme
from ui.sidebar import Sidebar
from ui.dashboard import Dashboard
from ui.boost_page import BoostPage
from ui.cleaner_page import CleanerPage
from ui.startup_page import StartupPage
from ui.hardware_page import HardwarePage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("傲視系統優化大師")
        self.resize(1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Apply global stylesheet
        self.setStyleSheet(Theme.STYLESHEET)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self.switch_page)
        
        # Content Area (Stacked Widget)
        self.content_stack = QStackedWidget()
        
        # Pages
        self.page_dashboard = Dashboard()
        self.page_boost = BoostPage()
        self.page_cleaner = CleanerPage()
        self.page_startup = StartupPage()
        self.page_hardware = HardwarePage()
        
        self.content_stack.addWidget(self.page_dashboard)
        self.content_stack.addWidget(self.page_boost)
        self.content_stack.addWidget(self.page_cleaner)
        self.content_stack.addWidget(self.page_startup)
        self.content_stack.addWidget(self.page_hardware)
        
        # Add to layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_stack)
        
        # Select first page
        self.sidebar.btn_dashboard.click()

    def switch_page(self, page_name):
        pages = {
            "儀表板": 0,
            "一鍵加速": 1,
            "垃圾清理": 2,
            "啟動管理": 3,
            "硬體資訊": 4
        }
        if page_name in pages:
            self.content_stack.setCurrentIndex(pages[page_name])
