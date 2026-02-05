from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from ui.theme import Theme

class Sidebar(QWidget):
    page_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(260)
        
        # Tech Style Background (Gradient)
        self.setStyleSheet(f"""
            QWidget#Sidebar {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                                  stop:0 #1a1b26, stop:1 #16161e);
                border-right: 1px solid #2f334d;
                border-bottom-left-radius: 10px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 20)
        
        # Header Area - Fixed width issues
        header = QWidget()
        header.setFixedHeight(70)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(2)
        header_layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("VISION")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 22px; 
            font-weight: 900; 
            color: {Theme.PRIMARY}; 
            letter-spacing: 3px;
        """)
        
        title_label2 = QLabel("OPTIMIZER")
        title_label2.setAlignment(Qt.AlignCenter)
        title_label2.setStyleSheet(f"""
            font-size: 14px; 
            font-weight: bold; 
            color: {Theme.TEXT_PRIMARY}; 
            letter-spacing: 5px;
        """)
        
        subtitle_label = QLabel("SYSTEM CORE")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            font-size: 9px; 
            color: {Theme.SURFACE_HOVER}; 
            letter-spacing: 3px;
            margin-top: 3px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(title_label2)
        header_layout.addWidget(subtitle_label)
        layout.addWidget(header)
        
        # Divider
        line = QLabel()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 transparent, stop:0.5 #2f334d, stop:1 transparent);")
        layout.addWidget(line)
        layout.addSpacing(10)
        
        # Nav Container
        nav_container = QVBoxLayout()
        nav_container.setSpacing(8)
        nav_container.setContentsMargins(0, 0, 0, 0)
        
        self.btns = []
        
        # Creating buttons
        self.btn_dashboard = self.add_nav_btn(nav_container, "📊  儀表板", True)
        self.btn_boost = self.add_nav_btn(nav_container, "🚀  一鍵加速")
        self.btn_cleaner = self.add_nav_btn(nav_container, "🗑️  垃圾清理")
        self.btn_startup = self.add_nav_btn(nav_container, "⚡  啟動管理")
        self.btn_hardware = self.add_nav_btn(nav_container, "💻  硬體資訊")
        self.btn_scanner = self.add_nav_btn(nav_container, "📁  檔案掃描")
        
        layout.addLayout(nav_container)
        layout.addStretch()
        
        # Footer
        ver_label = QLabel("V1.0.0 PRO")
        ver_label.setAlignment(Qt.AlignCenter)
        ver_label.setStyleSheet(f"color: #3a3f5c; font-weight: bold; font-size: 10px;")
        layout.addWidget(ver_label)

    def add_nav_btn(self, layout, text, active=False):
        btn = QPushButton(text)
        btn.setObjectName("TechNavButton")
        if active:
            btn.setChecked(True)
            
        # Extract page name from button text (remove emoji)
        page_name = text.split("  ")[-1] if "  " in text else text
        btn.clicked.connect(lambda: self.handle_click(btn, page_name))
        
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(48)
        
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.TEXT_SECONDARY};
                border: none;
                border-radius: 10px;
                text-align: left;
                padding-left: 20px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #24283b;
                color: white;
            }}
            QPushButton:checked {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {Theme.SURFACE}, stop:1 transparent);
                color: {Theme.PRIMARY};
                border-left: 4px solid {Theme.PRIMARY};
                font-weight: bold;
            }}
        """)
        
        self.btns.append(btn)
        layout.addWidget(btn)
        return btn

    def handle_click(self, clicked_btn, text):
        for b in self.btns:
            b.setChecked(False)
        clicked_btn.setChecked(True)
        self.page_changed.emit(text)
