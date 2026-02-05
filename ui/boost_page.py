from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                                 QSpinBox, QCheckBox, QGroupBox, QFrame)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from ui.theme import Theme
from core.optimizer import SystemOptimizer
from core.monitor import SystemMonitor
import psutil

class BoostWorker(QThread):
    finished = Signal(dict)

    def run(self):
        result = SystemOptimizer.boost_memory()
        self.finished.emit(result)

class MemoryRing(QWidget):
    """Circular progress ring for memory display"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 180)
        self.value = 0
        self.before_value = 0
        self.show_before = False
        
    def set_value(self, val):
        self.value = val
        self.update()
        
    def set_before(self, val):
        self.before_value = val
        self.show_before = True
        self.update()
        
    def clear_before(self):
        self.show_before = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = QRectF(15, 15, 150, 150)
        
        # Track
        pen = QPen(QColor(Theme.SURFACE_HOVER), 12)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)
        
        # Before value (ghost arc) if showing comparison
        if self.show_before:
            pen_ghost = QPen(QColor(Theme.ERROR), 12)
            pen_ghost.setCapStyle(Qt.RoundCap)
            painter.setPen(pen_ghost)
            span_before = -self.before_value * 3.6 * 16
            painter.drawArc(rect, 90 * 16, span_before)
        
        # Current value
        color = QColor(Theme.SUCCESS) if self.value < 70 else QColor(Theme.WARNING) if self.value < 85 else QColor(Theme.ERROR)
        pen = QPen(color, 12)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        span = -self.value * 3.6 * 16
        painter.drawArc(rect, 90 * 16, span)
        
        # Text
        painter.setPen(QColor(Theme.TEXT_PRIMARY))
        painter.setFont(QFont("Segoe UI", 32, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, f"{int(self.value)}%")
        
        # Label
        painter.setPen(QColor(Theme.TEXT_SECONDARY))
        painter.setFont(QFont("Segoe UI", 11))
        painter.drawText(rect.adjusted(0, 50, 0, 0), Qt.AlignCenter, "記憶體")

class BoostPage(QWidget):
    def __init__(self):
        super().__init__()
        
        # Auto-boost settings
        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self.auto_boost)
        self.threshold_monitor = None
        
        # Live memory monitor
        self.live_monitor = SystemMonitor()
        self.live_monitor.stats_updated.connect(self.update_live_memory)
        self.live_monitor.start()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("一鍵加速")
        header.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {Theme.TEXT_PRIMARY};")
        layout.addWidget(header)
        
        # Main boost section
        boost_section = QFrame()
        boost_section.setStyleSheet(f"background-color: {Theme.SURFACE}; border-radius: 15px; padding: 20px;")
        boost_layout = QVBoxLayout(boost_section)
        boost_layout.setAlignment(Qt.AlignCenter)
        
        # Memory Ring (Live)
        self.mem_ring = MemoryRing()
        boost_layout.addWidget(self.mem_ring, 0, Qt.AlignCenter)
        
        # Status
        self.lbl_status = QLabel("準備就緒")
        self.lbl_status.setStyleSheet(f"font-size: 20px; color: {Theme.TEXT_PRIMARY}; font-weight: bold; margin-top: 10px;")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        boost_layout.addWidget(self.lbl_status)
        
        # Result Details
        self.lbl_result = QLabel("")
        self.lbl_result.setStyleSheet(f"font-size: 14px; color: {Theme.SUCCESS};")
        self.lbl_result.setAlignment(Qt.AlignCenter)
        self.lbl_result.setWordWrap(True)
        boost_layout.addWidget(self.lbl_result)
        
        # Boost Button
        self.btn_boost = QPushButton("立即優化")
        self.btn_boost.setFixedSize(220, 50) 
        self.btn_boost.setCursor(Qt.PointingHandCursor)
        self.btn_boost.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: #15161e;
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }}
            QPushButton:hover {{ background-color: #89b4fa; }}
            QPushButton:pressed {{ background-color: #6d91de; }}
            QPushButton:disabled {{ background-color: {Theme.SURFACE_HOVER}; color: {Theme.TEXT_SECONDARY}; }}
        """)
        self.btn_boost.clicked.connect(self.start_boost)
        
        boost_layout.addSpacing(15)
        boost_layout.addWidget(self.btn_boost, 0, Qt.AlignCenter)
        
        layout.addWidget(boost_section)
        
        # Auto-boost settings section
        settings_group = QGroupBox("自動優化設定")
        settings_group.setStyleSheet(f"""
            QGroupBox {{
                font-size: 16px;
                font-weight: bold;
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.SURFACE_HOVER};
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }}
        """)
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(15)
        
        # Interval auto-boost
        interval_row = QHBoxLayout()
        self.chk_interval = QCheckBox("定時自動優化")
        self.chk_interval.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 14px;")
        self.chk_interval.toggled.connect(self.toggle_interval_boost)
        
        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(1, 60)
        self.spin_interval.setValue(10)
        self.spin_interval.setSuffix(" 分鐘")
        self.spin_interval.setStyleSheet(f"""
            QSpinBox {{
                background-color: {Theme.SURFACE};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.SURFACE_HOVER};
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }}
        """)
        
        interval_row.addWidget(self.chk_interval)
        interval_row.addWidget(QLabel("每"))
        interval_row.addWidget(self.spin_interval)
        interval_row.addStretch()
        settings_layout.addLayout(interval_row)
        
        # Threshold auto-boost
        threshold_row = QHBoxLayout()
        self.chk_threshold = QCheckBox("記憶體使用率超過")
        self.chk_threshold.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 14px;")
        self.chk_threshold.toggled.connect(self.toggle_threshold_boost)
        
        self.spin_threshold = QSpinBox()
        self.spin_threshold.setRange(50, 95)
        self.spin_threshold.setValue(80)
        self.spin_threshold.setSuffix(" %")
        self.spin_threshold.setStyleSheet(self.spin_interval.styleSheet())
        
        threshold_row.addWidget(self.chk_threshold)
        threshold_row.addWidget(self.spin_threshold)
        threshold_row.addWidget(QLabel("時自動優化"))
        threshold_row.addStretch()
        settings_layout.addLayout(threshold_row)
        
        # Status indicator
        self.lbl_auto_status = QLabel("🔴 自動優化已關閉")
        self.lbl_auto_status.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 13px;")
        settings_layout.addWidget(self.lbl_auto_status)
        
        layout.addWidget(settings_group)
        layout.addStretch()
        
        # Stats
        self.boost_count = 0
        self.total_freed = 0
        
        # Animation state
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.animate_ring)
        self.anim_start = 0
        self.anim_end = 0
        self.anim_current = 0
        self.anim_step = 0
        self.boost_result = None
        self.tray_icon = None
        
    def set_tray_icon(self, tray_icon):
        self.tray_icon = tray_icon
        
    def update_live_memory(self, stats):
        """Update ring with live memory data when not animating"""
        if not self.anim_timer.isActive():
            self.mem_ring.set_value(stats['ram_percent'])
        
    def start_boost(self):
        # Capture before state
        mem = psutil.virtual_memory()
        self.before_percent = mem.percent
        
        self.btn_boost.setEnabled(False)
        self.btn_boost.setText("優化中...")
        self.lbl_status.setText("正在釋放記憶體...")
        self.lbl_result.setText("")
        
        # Show "before" ghost on ring
        self.mem_ring.set_before(self.before_percent)
        
        self.worker = BoostWorker()
        self.worker.finished.connect(self.on_boost_finished)
        self.worker.start()
        
    def on_boost_finished(self, result):
        self.boost_result = result
        freed_bytes = result['freed_bytes']
        count = result['processes_count']
        
        # Get actual current memory
        mem = psutil.virtual_memory()
        after_percent = mem.percent
        
        freed_mb = round(freed_bytes / (1024*1024), 2)
        self.boost_count += 1
        self.total_freed += freed_mb
        
        # Setup animation from before to after
        self.anim_start = self.before_percent
        self.anim_end = after_percent
        self.anim_current = self.anim_start
        
        # Calculate step (animate over ~1 second at 30fps)
        diff = self.anim_start - self.anim_end
        if diff > 0:
            self.anim_step = max(0.5, diff / 30)
        else:
            self.anim_step = 0
            self.finish_animation()
            return
            
        self.lbl_status.setText(f"釋放中... ({count} 程序)")
        self.anim_timer.start(33) # ~30 fps
        
    def animate_ring(self):
        if self.anim_current > self.anim_end:
            self.anim_current -= self.anim_step
            if self.anim_current < self.anim_end:
                self.anim_current = self.anim_end
            self.mem_ring.set_value(self.anim_current)
        else:
            self.anim_timer.stop()
            self.finish_animation()
            
    def finish_animation(self):
        result = self.boost_result
        freed_mb = round(result['freed_bytes'] / (1024*1024), 2)
        count = result['processes_count']
        
        # Get final accurate percentage
        mem = psutil.virtual_memory()
        final_percent = mem.percent
        
        self.mem_ring.set_value(final_percent)
        self.mem_ring.clear_before() # Remove ghost
        
        drop = round(self.before_percent - final_percent, 1)
        
        self.lbl_status.setText("優化完成！")
        self.lbl_result.setText(f"✓ 已優化 {count} 個程序 | 釋放 {freed_mb} MB\n系統負載 {self.before_percent:.0f}% → {final_percent:.0f}% (↓{drop}%)")
        self.lbl_result.setStyleSheet(f"font-size: 14px; color: {Theme.SUCCESS};")
        
        self.btn_boost.setText("立即優化")
        self.btn_boost.setEnabled(True)
        
        # Show notification
        if self.tray_icon:
            from PySide6.QtWidgets import QSystemTrayIcon
            self.tray_icon.showMessage(
                "優化完成", 
                f"已釋放 {freed_mb} MB 記憶體此時負載下降 {drop}%",
                QSystemTrayIcon.Information,
                3000
            )
        
    def auto_boost(self):
        if not self.btn_boost.isEnabled():
            return
        self.start_boost()
        
    def toggle_interval_boost(self, enabled):
        if enabled:
            interval_ms = self.spin_interval.value() * 60 * 1000
            self.auto_timer.start(interval_ms)
        else:
            self.auto_timer.stop()
        self.update_auto_status()
        
    def toggle_threshold_boost(self, enabled):
        if enabled:
            if self.threshold_monitor is None:
                self.threshold_monitor = SystemMonitor()
                self.threshold_monitor.stats_updated.connect(self.check_threshold)
                self.threshold_monitor.start()
        else:
            if self.threshold_monitor:
                self.threshold_monitor.stop()
                self.threshold_monitor = None
        self.update_auto_status()
        
    def check_threshold(self, stats):
        if not self.chk_threshold.isChecked():
            return
        if stats['ram_percent'] > self.spin_threshold.value():
            if self.btn_boost.isEnabled():
                self.start_boost()
                
    def update_auto_status(self):
        modes = []
        if self.chk_interval.isChecked():
            modes.append(f"每 {self.spin_interval.value()} 分鐘")
        if self.chk_threshold.isChecked():
            modes.append(f"RAM > {self.spin_threshold.value()}%")
            
        if modes:
            self.lbl_auto_status.setText(f"🟢 自動優化已啟用：{' / '.join(modes)}")
            self.lbl_auto_status.setStyleSheet(f"color: {Theme.SUCCESS}; font-size: 13px;")
        else:
            self.lbl_auto_status.setText("🔴 自動優化已關閉")
            self.lbl_auto_status.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 13px;")
            
    def close_monitor(self):
        if self.live_monitor and self.live_monitor.isRunning():
            self.live_monitor.stop()
        if self.threshold_monitor and self.threshold_monitor.isRunning():
            self.threshold_monitor.stop()
