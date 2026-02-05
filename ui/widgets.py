from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect, 
                                 QDialog, QPushButton, QHBoxLayout)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPainterPath, QLinearGradient, QBrush
from ui.theme import Theme
import collections

class CustomDialog(QDialog):
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        
        # Container
        container = QWidget()
        container.setObjectName("DialogContainer")
        container.setStyleSheet(f"""
            QWidget#DialogContainer {{
                background-color: {Theme.SURFACE};
                border: 1px solid {Theme.PRIMARY};
                border-radius: 15px;
            }}
        """)
        
        cont_layout = QVBoxLayout(container)
        cont_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {Theme.PRIMARY}; margin-bottom: 10px;")
        cont_layout.addWidget(lbl_title)
        
        # Message
        lbl_msg = QLabel(message)
        lbl_msg.setStyleSheet(f"font-size: 14px; color: {Theme.TEXT_PRIMARY}; margin-bottom: 20px;")
        lbl_msg.setWordWrap(True)
        cont_layout.addWidget(lbl_msg)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_minimize = QPushButton("縮小至托盤")
        self.btn_minimize.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.SURFACE_HOVER};
                color: {Theme.TEXT_PRIMARY};
                padding: 8px 15px;
                border-radius: 8px;
            }}
            QPushButton:hover {{ background-color: {Theme.SECONDARY}; color: #fff; }}
        """)
        self.btn_minimize.clicked.connect(lambda: self.done(101)) # Custom code
        
        self.btn_quit = QPushButton("結束程式")
        self.btn_quit.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.ERROR};
                color: white;
                padding: 8px 15px;
                border-radius: 8px;
            }}
            QPushButton:hover {{ background-color: #ff6b6b; }}
        """)
        self.btn_quit.clicked.connect(lambda: self.done(102)) # Custom code
        
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.TEXT_SECONDARY};
                padding: 8px 15px;
            }}
            QPushButton:hover {{ color: {Theme.TEXT_PRIMARY}; }}
        """)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_minimize)
        btn_layout.addWidget(self.btn_quit)
        
        cont_layout.addLayout(btn_layout)
        layout.addWidget(container)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        container.setGraphicsEffect(shadow)

class CircularProgress(QWidget):
    def __init__(self, title, color_hex, parent=None):
        super().__init__(parent)
        self.value = 0
        self.title = title
        self.color = QColor(color_hex)
        self.setFixedSize(200, 200)
        
    def set_value(self, value):
        self.value = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Dimensions
        width = self.width()
        height = self.height()
        rect = QRectF(10, 10, width - 20, height - 20)
        
        # Draw Track
        pen = QPen(QColor(Theme.SURFACE_HOVER), 10)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, -90 * 16, 360 * 16) # Full circle
        
        # Draw Progress
        pen.setColor(self.color)
        # Angle is in 1/16th of a degree. 
        # Start at 90 degrees (top) -> 90 * 16
        # Span is negative for clockwise
        span = -self.value * 3.6 * 16
        painter.setPen(pen)
        painter.drawArc(rect, 90 * 16, span)
        
        # Draw Text
        painter.setPen(QColor(Theme.TEXT_PRIMARY))
        painter.setFont(QFont("Segoe UI", 24, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, f"{int(self.value)}%")
        
        # Draw Title
        painter.setPen(QColor(Theme.TEXT_SECONDARY))
        painter.setFont(QFont("Segoe UI", 12))
        painter.drawText(rect.adjusted(0, 40, 0, 0), Qt.AlignCenter, self.title)

class StatCard(QWidget):
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setObjectName("Card") # Setup for stylesheet
        layout = QVBoxLayout(self)
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setObjectName("CardTitle")
        
        self.lbl_value = QLabel(value)
        self.lbl_value.setObjectName("CardValue")
        
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

class NetworkWaveform(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(200)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.SURFACE};
                border-radius: 15px;
                border: 1px solid #1f2335;
            }}
        """)
        
        # Data storage (store last 60 points)
        self.recv_data = collections.deque([0]*60, maxlen=60)
        self.sent_data = collections.deque([0]*60, maxlen=60)
        self.max_val = 100 * 1024 # Initial scale 100 KB
        
        # Labels for current speed
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        
        self.lbl_recv = QLabel("⬇ 0 KB/s")
        self.lbl_recv.setStyleSheet(f"color: {Theme.SUCCESS}; font-weight: bold; background: transparent; margin-right: 15px;")
        
        self.lbl_sent = QLabel("⬆ 0 KB/s")
        self.lbl_sent.setStyleSheet(f"color: {Theme.SECONDARY}; font-weight: bold; background: transparent;")
        
        layout.addWidget(self.lbl_recv)
        layout.addWidget(self.lbl_sent)
        
    def push_data(self, recv_bytes, sent_bytes):
        self.recv_data.append(recv_bytes)
        self.sent_data.append(sent_bytes)
        
        # Update text
        self.lbl_recv.setText(f"⬇ {self.format_speed(recv_bytes)}")
        self.lbl_sent.setText(f"⬆ {self.format_speed(sent_bytes)}")
        
        # Dynamic scaling
        current_max = max(max(self.recv_data), max(self.sent_data))
        if current_max > self.max_val:
            self.max_val = current_max * 1.2
        elif current_max < self.max_val * 0.5 and self.max_val > 100*1024:
            self.max_val = max(100*1024, current_max * 1.5)
            
        self.update()
        
    def format_speed(self, bytes_sec):
        if bytes_sec < 1024:
            return f"{int(bytes_sec)} B/s"
        elif bytes_sec < 1024**2:
            return f"{bytes_sec/1024:.1f} KB/s"
        else:
            return f"{bytes_sec/(1024**2):.1f} MB/s"

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # 1. Draw Grid Background
        painter.setPen(QPen(QColor("#2f334d"), 1, Qt.DotLine))
        # Horizontal lines
        for i in range(1, 4):
            y = i * (h / 4)
            painter.drawLine(0, y, w, y)
        # Vertical lines
        for i in range(1, 10):
            x = i * (w / 10)
            painter.drawLine(x, 0, x, h)
            
        # 2. Draw Graphs
        self.draw_graph(painter, self.recv_data, QColor(Theme.SUCCESS)) # Green for Download
        self.draw_graph(painter, self.sent_data, QColor(Theme.SECONDARY)) # Purple for Upload
        
    def draw_graph(self, painter, data, color):
        w = self.width()
        h = self.height()
        
        path = QPainterPath()
        # Start bottom left
        path.moveTo(0, h)
        
        # Calculate points
        step_x = w / (len(data) - 1)
        for i, val in enumerate(data):
            x = i * step_x
            # Normalize height (0 to h)
            # Higher value = lower y (screen coords)
            normalized = max(0, min(1, val / self.max_val))
            y = h - (normalized * h)
            path.lineTo(x, y)
            
        # Close path for fill
        path.lineTo(w, h)
        path.closeSubpath()
        
        # Draw Fill (Gradient)
        grad = QLinearGradient(0, 0, 0, h)
        c_top = QColor(color)
        c_top.setAlpha(150)
        c_bottom = QColor(color)
        c_bottom.setAlpha(10)
        grad.setColorAt(0, c_top)
        grad.setColorAt(1, c_bottom)
        
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)
        
        # Draw Line (Top stroke)
        stroke_path = QPainterPath()
        stroke_path.moveTo(0, h - (max(0, min(1, data[0] / self.max_val)) * h))
        for i, val in enumerate(data):
             x = i * step_x
             normalized = max(0, min(1, val / self.max_val))
             y = h - (normalized * h)
             stroke_path.lineTo(x, y)
             
        pen = QPen(color, 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(stroke_path)
