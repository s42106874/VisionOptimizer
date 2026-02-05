from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame)
from PySide6.QtCore import Qt
from ui.theme import Theme
from ui.widgets import CircularProgress, StatCard, NetworkWaveform
from core.monitor import SystemMonitor

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        
        # Start Monitor
        self.monitor = SystemMonitor()
        self.monitor.stats_updated.connect(self.update_stats)
        self.monitor.start()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("系統戰情室")
        header.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {Theme.TEXT_PRIMARY}; font-family: 'Segoe UI Black'; letter-spacing: 1px;")
        layout.addWidget(header)
        
        # Progress Ring Section
        rings_layout = QHBoxLayout()
        rings_layout.setSpacing(30)
        
        self.cpu_ring = CircularProgress("CPU 負載", Theme.PRIMARY)
        self.ram_ring = CircularProgress("記憶體", Theme.SECONDARY)
        self.disk_ring = CircularProgress("系統碟", Theme.WARNING)
        
        rings_layout.addWidget(self.cpu_ring)
        rings_layout.addWidget(self.ram_ring)
        rings_layout.addWidget(self.disk_ring)
        rings_layout.addStretch()
        
        layout.addLayout(rings_layout)
        
        # Network Waveform Section (New Tech Feature)
        net_label = QLabel("網路流量監控")
        net_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Theme.TEXT_SECONDARY}; margin-top: 10px;")
        layout.addWidget(net_label)
        
        self.net_waveform = NetworkWaveform()
        layout.addWidget(self.net_waveform)
        
        # Detail Cards Grid
        cards_layout = QGridLayout()
        cards_layout.setSpacing(20)
        
        self.card_ram_details = StatCard("可用記憶體", "載入中...")
        self.card_disk_details = StatCard("可用磁碟空間", "載入中...")
        
        cards_layout.addWidget(self.card_ram_details, 0, 0)
        cards_layout.addWidget(self.card_disk_details, 0, 1)
        
        layout.addLayout(cards_layout)
        
        # Tech Fillers (Bottom status bar)
        status_bar = QHBoxLayout()
        
        lbl_system_status = QLabel("● SYSTEM OPTIMAL")
        lbl_system_status.setStyleSheet(f"color: {Theme.SUCCESS}; font-weight: bold; letter-spacing: 2px;")
        
        lbl_mode = QLabel("MODE: PERFORMANCE")
        lbl_mode.setStyleSheet(f"color: {Theme.PRIMARY}; font-weight: bold; letter-spacing: 2px;")
        
        status_bar.addWidget(lbl_system_status)
        status_bar.addStretch()
        status_bar.addWidget(lbl_mode)
        
        # Container for status bar with border
        status_container = QFrame()
        status_container.setStyleSheet(f"border-top: 1px solid {Theme.SURFACE_HOVER}; border-bottom: 1px solid {Theme.SURFACE_HOVER}; padding: 10px 0;")
        status_container.setLayout(status_bar)
        
        layout.addWidget(status_container)
        layout.addStretch()

    def update_stats(self, stats):
        self.cpu_ring.set_value(stats['cpu'])
        self.ram_ring.set_value(stats['ram_percent'])
        self.disk_ring.set_value(stats['disk_percent'])
        
        self.card_ram_details.lbl_value.setText(f"{stats['ram_used']} GB / {stats['ram_total']} GB")
        self.card_disk_details.lbl_value.setText(f"{stats['disk_free']} GB 可用")
        
        # Update Network Graph
        self.net_waveform.push_data(stats['net_recv'], stats['net_sent'])
        
    def close_monitor(self):
        """Safely stop the monitor thread"""
        if self.monitor.isRunning():
            self.monitor.stop()
