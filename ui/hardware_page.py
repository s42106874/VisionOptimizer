from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QFrame, QGridLayout, QScrollArea, QProgressBar)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from ui.theme import Theme
from core.hardware import HardwareInfo

class HardwareCard(QFrame):
    def __init__(self, title, icon="💻", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.SURFACE};
                border-radius: 12px;
                border: 1px solid #1f2335;
            }}
            QFrame:hover {{
                border: 1px solid {Theme.PRIMARY};
                background-color: #1f2335;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 24px; border: none; background: transparent;")
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {Theme.TEXT_PRIMARY}; border: none; background: transparent;")
        
        header.addWidget(icon_lbl)
        header.addWidget(title_lbl)
        header.addStretch()
        
        layout.addLayout(header)
        
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(12)
        layout.addLayout(self.content_layout)
        
    def add_row(self, label, value):
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 14px; border: none; background: transparent;")
        val = QLabel(str(value))
        val.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 14px; font-weight: 500; border: none; background: transparent;")
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(val)
        self.content_layout.addLayout(row)
        
    def add_progress_row(self, label, percent, total_text):
        container = QWidget()
        container.setStyleSheet("border: none; background: transparent;")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(8)
        
        # Text line
        hbox = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 14px; border: none;")
        val = QLabel(total_text)
        val.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: 13px; font-weight: bold; border: none;")
        hbox.addWidget(lbl)
        hbox.addStretch()
        hbox.addWidget(val)
        vbox.addLayout(hbox)
        
        # Progress bar
        bar = QProgressBar()
        bar.setFixedHeight(6)
        bar.setTextVisible(False)
        bar.setRange(0, 100)
        bar.setValue(int(percent))
        
        color = Theme.PRIMARY
        if percent > 80: color = Theme.WARNING
        if percent > 90: color = Theme.ERROR
            
        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #1a1b26;
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        vbox.addWidget(bar)
        
        self.content_layout.addWidget(container)

class HardwarePage(QWidget):
    def __init__(self):
        super().__init__()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: transparent; }}
            QScrollBar:vertical {{
                border: none;
                background: {Theme.BACKGROUND};
                width: 8px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #2f334d;
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        container = QWidget()
        container.setStyleSheet(f"background-color: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(25)
        
        # Header
        header = QLabel("硬體資訊")
        header.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {Theme.TEXT_PRIMARY};")
        layout.addWidget(header)
        
        # Grid Layout for cards
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # System Info
        try:
            sys_info = HardwareInfo.get_system_info()
            sys_card = HardwareCard("系統核心", "🖥️")
            sys_card.add_row("作業系統", sys_info['os'])
            sys_card.add_row("版本", sys_info['os_version'])
            sys_card.add_row("電腦名稱", sys_info['hostname'])
            sys_card.add_row("架構", sys_info['machine'])
            sys_card.setFixedHeight(200)
            grid.addWidget(sys_card, 0, 0)
        except: pass
            
        # CPU Info
        try:
            cpu_info = HardwareInfo.get_cpu_info()
            cpu_card = HardwareCard("處理器", "🧠")
            cpu_card.add_row("型號", cpu_info['name'])
            cpu_card.add_row("核心數", f"{cpu_info['cores']} 核心")
            cpu_card.add_row("基準時脈", cpu_info['frequency'])
            cpu_card.setFixedHeight(200)
            grid.addWidget(cpu_card, 0, 1)
        except: pass
        
        # Memory Info
        try:
            mem_info = HardwareInfo.get_memory_info()
            mem_card = HardwareCard("記憶體", "⚡")
            mem_card.add_row("總容量", f"{mem_info['total']} GB")
            mem_card.add_progress_row("使用率", mem_info['percent'], f"{mem_info['used']} GB / {mem_info['total']} GB")
            mem_card.add_row("可用", f"{mem_info['available']} GB")
            grid.addWidget(mem_card, 1, 0)
        except: pass
        
        # GPU Info
        try:
            gpu_list = HardwareInfo.get_gpu_info()
            if gpu_list:
                gpu_card = HardwareCard("顯示卡", "🎮")
                for i, gpu in enumerate(gpu_list):
                    gpu_card.add_row(f"GPU {i+1}", gpu)
                grid.addWidget(gpu_card, 1, 1)
        except: pass
            
        layout.addLayout(grid)
        
        # Disk Section Title
        disk_title = QLabel("儲存裝置")
        disk_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {Theme.TEXT_PRIMARY}; margin-top: 20px;")
        layout.addWidget(disk_title)
        
        # Disks Layout
        try:
            disks = HardwareInfo.get_disk_info()
            if disks:
                disk_grid = QGridLayout()
                disk_grid.setSpacing(20)
                
                row = 0
                col = 0
                for disk in disks:
                    # Handle missing keys safely
                    device = disk.get('device', 'Unknown')
                    mount = disk.get('mountpoint', '')
                    fstype = disk.get('fstype', 'NTFS') # Fallback
                    
                    disk_card = HardwareCard(f"{device} ({mount})", "💾")
                    
                    # Some partitions might not have usage stats (e.g. DVD drive with no disc)
                    if 'total' in disk:
                        disk_card.add_row("檔案系統", fstype)
                        disk_card.add_progress_row("空間使用", disk['percent'], f"{disk['used']} GB / {disk['total']} GB")
                        disk_card.add_row("剩餘空間", f"{disk['free']} GB")
                    else:
                        disk_card.add_row("狀態", "無法讀取資訊")
                    
                    disk_grid.addWidget(disk_card, row, col)
                    col += 1
                    if col > 1:
                        col = 0
                        row += 1
                
                layout.addLayout(disk_grid)
            else:
                layout.addWidget(QLabel("無法偵測到磁碟裝置", styleSheet=f"color: {Theme.ERROR}"))
        except Exception as e:
            print(f"Error loading disks: {e}")
            layout.addWidget(QLabel(f"讀取磁碟錯誤: {e}", styleSheet=f"color: {Theme.ERROR}"))
            
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
