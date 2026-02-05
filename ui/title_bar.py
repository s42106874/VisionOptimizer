from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton)
from PySide6.QtCore import Qt, QPoint
from ui.theme import Theme

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.parent_window = parent
        self.start_pos = None
        self.is_dragging = False
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 10, 0)
        
        # Title Label
        self.title_label = QLabel("傲視系統優化大師")
        self.title_label.setStyleSheet(f"font-size: 14px; color: {Theme.TEXT_SECONDARY}; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # Window Controls
        btn_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                color: #a9b1d6;
                font-family: Arial;
                font-size: 14px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #2f334d;
                color: white;
            }
        """
        
        close_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                color: #a9b1d6;
                font-family: Arial;
                font-size: 14px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #f7768e;
                color: white;
            }
        """
        
        self.btn_min = QPushButton("─")
        self.btn_min.setStyleSheet(btn_style)
        self.btn_min.clicked.connect(self.parent_window.showMinimized)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setStyleSheet(close_style)
        self.btn_close.clicked.connect(self.parent_window.close)
        
        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_close)
        
        # Styling
        self.setFixedHeight(35)
        self.setStyleSheet(f"""
            QWidget#TitleBar {{
                background-color: {Theme.BACKGROUND};
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom: 1px solid #16161e;
            }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.start_pos = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() & Qt.LeftButton:
            self.parent_window.move(event.globalPosition().toPoint() - self.start_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.is_dragging = False
