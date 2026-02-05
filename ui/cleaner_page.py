from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                                 QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QFrame)
from PySide6.QtCore import Qt, QThread, Signal
from ui.theme import Theme
from core.cleaner import JunkCleaner

class ScanWorker(QThread):
    finished = Signal(list)
    
    def run(self):
        junk = JunkCleaner.scan_junk()
        self.finished.emit(junk)

class CleanWorker(QThread):
    finished = Signal(tuple) # (success, fail, size)
    
    def __init__(self, files):
        super().__init__()
        self.files = files
        
    def run(self):
        result = JunkCleaner.clean_files(self.files)
        self.finished.emit(result)

class CleanerPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        title = QLabel("系統垃圾清理")
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {Theme.TEXT_PRIMARY};")
        layout.addWidget(title)
        
        desc = QLabel("掃描並清除系統暫存檔案與垃圾，釋放磁碟空間。")
        desc.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 14px;")
        layout.addWidget(desc)
        
        # Action Buttons Container
        btn_container = QFrame()
        btn_container.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.SURFACE};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setSpacing(20)
        
        # Scan Button (Big & Prominent)
        self.btn_scan = QPushButton("🔍 開始掃描")
        self.btn_scan.setFixedHeight(60)
        self.btn_scan.setCursor(Qt.PointingHandCursor)
        self.btn_scan.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: #15161e;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                padding: 15px 30px;
            }}
            QPushButton:hover {{
                background-color: #89b4fa;
            }}
            QPushButton:pressed {{
                background-color: #6d91de;
            }}
            QPushButton:disabled {{
                background-color: {Theme.SURFACE_HOVER};
                color: {Theme.TEXT_SECONDARY};
            }}
        """)
        self.btn_scan.clicked.connect(self.start_scan)
        
        # Clean Button (Red for danger)
        self.btn_clean = QPushButton("🗑️ 清理全部")
        self.btn_clean.setFixedHeight(60)
        self.btn_clean.setCursor(Qt.PointingHandCursor)
        self.btn_clean.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.ERROR};
                color: white;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                padding: 15px 30px;
            }}
            QPushButton:hover {{
                background-color: #ff6b6b;
            }}
            QPushButton:pressed {{
                background-color: #e55555;
            }}
            QPushButton:disabled {{
                background-color: {Theme.SURFACE_HOVER};
                color: {Theme.TEXT_SECONDARY};
            }}
        """)
        self.btn_clean.setEnabled(False)
        self.btn_clean.clicked.connect(self.start_clean)
        
        btn_layout.addWidget(self.btn_scan, 1)
        btn_layout.addWidget(self.btn_clean, 1)
        layout.addWidget(btn_container)
        
        # Summary Label
        self.lbl_summary = QLabel("📂 準備開始掃描")
        self.lbl_summary.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 16px; font-weight: bold; padding: 10px 0;")
        layout.addWidget(self.lbl_summary)
        
        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["檔案路徑", "類型", "大小"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 100)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Theme.SURFACE};
                border: 1px solid #1f2335;
                border-radius: 10px;
                color: {Theme.TEXT_SECONDARY};
                gridline-color: transparent;
            }}
            QHeaderView::section {{
                background-color: {Theme.SURFACE};
                color: {Theme.TEXT_SECONDARY};
                border: none;
                padding: 10px;
                font-weight: bold;
                border-bottom: 1px solid #2f334d;
            }}
            QTableWidget::item {{
                padding: 5px;
                background-color: transparent;
                border-bottom: 1px solid #1a1b26;
            }}
            QTableWidget::item:hover {{
                background-color: #24283b;
            }}
            QTableWidget::item:selected {{
                background-color: {Theme.PRIMARY};
                color: #15161e;
            }}
        """)
        layout.addWidget(self.table)
        
        self.scanned_items = []

    def start_scan(self):
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText("⏳ 掃描中...")
        self.lbl_summary.setText("🔍 正在掃描系統垃圾...")
        self.table.setRowCount(0)
        
        self.scan_worker = ScanWorker()
        self.scan_worker.finished.connect(self.on_scan_finished)
        self.scan_worker.start()
        
    def on_scan_finished(self, items):
        self.scanned_items = items
        self.table.setRowCount(len(items))
        
        total_size = 0
        for i, item in enumerate(items):
            path_item = QTableWidgetItem(item.get('path', '未知'))
            path_item.setToolTip(item.get('path', ''))
            self.table.setItem(i, 0, path_item)
            self.table.setItem(i, 1, QTableWidgetItem(item.get('type', '其他')))
            
            size_bytes = item.get('size', 0)
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes/1024:.1f} KB"
            else:
                size_str = f"{size_bytes/(1024*1024):.2f} MB"
            self.table.setItem(i, 2, QTableWidgetItem(size_str))
            total_size += size_bytes
            
            self.table.setRowHeight(i, 40)
            
        total_mb = round(total_size / (1024*1024), 2)
        self.lbl_summary.setText(f"✅ 找到 {len(items)} 個項目，共 {total_mb} MB 可清理")
        self.lbl_summary.setStyleSheet(f"color: {Theme.SUCCESS}; font-size: 16px; font-weight: bold; padding: 10px 0;")
        
        self.btn_scan.setEnabled(True)
        self.btn_scan.setText("🔍 開始掃描")
        self.btn_clean.setEnabled(len(items) > 0)
        
    def start_clean(self):
        self.btn_clean.setEnabled(False)
        self.btn_clean.setText("⏳ 清理中...")
        self.lbl_summary.setText("🗑️ 正在清理垃圾檔案...")
        
        self.clean_worker = CleanWorker(self.scanned_items)
        self.clean_worker.finished.connect(self.on_clean_finished)
        self.clean_worker.start()
        
    def on_clean_finished(self, result):
        success, fail, size = result
        size_mb = round(size / (1024*1024), 2)
        
        self.lbl_summary.setText(f"🎉 已清理 {success} 個檔案，釋放 {size_mb} MB！" + (f" ({fail} 個失敗)" if fail > 0 else ""))
        self.lbl_summary.setStyleSheet(f"color: {Theme.SUCCESS}; font-size: 16px; font-weight: bold; padding: 10px 0;")
        
        self.table.setRowCount(0)
        self.scanned_items = []
        self.btn_clean.setEnabled(False)
        self.btn_clean.setText("🗑️ 清理全部")
