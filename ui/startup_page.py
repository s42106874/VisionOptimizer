from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                                 QTableWidgetItem, QHeaderView, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, Slot, QRectF, Signal, Property, QTimer
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont
from ui.theme import Theme
from core.startup import StartupManager

class ToggleSwitch(QWidget):
    toggled = Signal(bool)

    def __init__(self, checked=True, enabled=True, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 26)
        self.setCursor(Qt.PointingHandCursor if enabled else Qt.ForbiddenCursor)
        self._checked = checked
        self._enabled = enabled
        
        # Animation
        self._thumb_pos = 22.0 if checked else 2.0
        self.anim = QPropertyAnimation(self, b"thumb_pos", self)
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)

    def isChecked(self):
        return self._checked

    def setChecked(self, checked):
        if self._checked != checked:
            self._checked = checked
            self.anim.setStartValue(self._thumb_pos)
            self.anim.setEndValue(22.0 if checked else 2.0)
            self.anim.start()
            self.update()

    # Property for animation
    def get_thumb_pos(self):
        return self._thumb_pos
        
    def set_thumb_pos(self, pos):
        self._thumb_pos = pos
        self.update()
        
    thumb_pos = Property(float, get_thumb_pos, set_thumb_pos)

    def mouseReleaseEvent(self, event):
        if self._enabled and event.button() == Qt.LeftButton:
            self.setChecked(not self._checked)
            self.toggled.emit(self._checked)
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Track
        track_rect = QRectF(1, 1, 48, 24)
        
        track_color = QColor(Theme.SUCCESS) if self._checked else QColor(Theme.SURFACE_HOVER)
        if not self._enabled:
            track_color = QColor("#333")
            
        painter.setBrush(QBrush(track_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(track_rect, 12, 12)
        
        # Thumb
        thumb_color = QColor("#ffffff")
        if not self._enabled:
            thumb_color = QColor("#666")
            
        painter.setBrush(QBrush(thumb_color))
        painter.drawEllipse(QRectF(self._thumb_pos, 3, 20, 20))

class StartupPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("啟動項管理")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {Theme.TEXT_PRIMARY};")
        
        self.btn_refresh = QPushButton(" 重新整理")
        self.btn_refresh.setObjectName("ActionButton")
        self.btn_refresh.setFixedWidth(120)
        self.btn_refresh.clicked.connect(self.reload_logic)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_refresh)
        layout.addLayout(header_layout)
        
        desc = QLabel("管理系統開機時自動執行的程式。 (部分項目需要管理員權限)")
        desc.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 14px; margin-bottom: 20px;")
        layout.addWidget(desc)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["來源", "程式名稱", "詳細路徑", "狀態", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 70) 
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 70)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Theme.SURFACE};
                border: 1px solid #1f2335;
                border-radius: 10px;
                color: {Theme.TEXT_SECONDARY};
                padding: 5px;
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
        
        self.items_data = [] 
        self.load_items()

    def reload_logic(self):
        self.table.setRowCount(0)
        self.btn_refresh.setText("讀取中...")
        QTimer.singleShot(100, self.load_items)

    def load_items(self):
        self.items_data = StartupManager.get_startup_items()
        self.table.setRowCount(len(self.items_data))
        
        for i, item in enumerate(self.items_data):
            # 1. Source
            src_lbl = QLabel(item['root'])
            src_lbl.setAlignment(Qt.AlignCenter)
            src_lbl.setStyleSheet(f"color: {Theme.SECONDARY if item['root']=='HKCU' else Theme.WARNING}; font-weight: bold; font-size: 11px; background: #2f334d; border-radius: 4px; padding: 2px;")
            src_container = self.create_centered_widget(src_lbl)
            self.table.setCellWidget(i, 0, src_container)
            
            # 2. Name
            name_item = QTableWidgetItem(item['name'])
            name_item.setForeground(QColor(Theme.TEXT_PRIMARY))
            name_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table.setItem(i, 1, name_item)
            
            # 3. Command
            cmd_item = QTableWidgetItem(item['command'])
            cmd_item.setToolTip(item['command'])
            self.table.setItem(i, 2, cmd_item)
            
            # 4. Toggle
            toggle = ToggleSwitch(checked=item['enabled'], enabled=item['can_toggle'])
            toggle.toggled.connect(lambda c, idx=i: self.on_toggle(idx, c))
            self.table.setCellWidget(i, 3, self.create_centered_widget(toggle))
            
            # 5. Delete
            if item['can_toggle']:
                del_btn = QPushButton()
                del_btn.setText("×")
                del_btn.setFixedSize(30, 30)
                del_btn.setCursor(Qt.PointingHandCursor)
                del_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {Theme.ERROR};
                        font-size: 20px;
                        font-weight: bold;
                        border-radius: 15px;
                    }}
                    QPushButton:hover {{
                        background-color: rgba(247, 118, 142, 0.2);
                    }}
                """)
                del_btn.clicked.connect(lambda _, idx=i: self.on_delete(idx))
                self.table.setCellWidget(i, 4, self.create_centered_widget(del_btn))
            
            self.table.setRowHeight(i, 55)
            
        self.btn_refresh.setText(" 重新整理")
    
    def create_centered_widget(self, widget):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(widget)
        return container

    def on_toggle(self, index, enabled):
        item = self.items_data[index]
        success = StartupManager.set_startup_enabled(item, enabled)
        
        if not success:
            QMessageBox.warning(self, "權限不足", f"無法修改 {item['name']}。\n若此項目位於 HKLM，請以系統管理員身分執行此程式。")
            cell_widget = self.table.cellWidget(index, 3) 
            switch = cell_widget.findChild(ToggleSwitch)
            if switch:
                switch.blockSignals(True)
                switch.setChecked(not enabled)
                switch.blockSignals(False)

    def on_delete(self, index):
        item = self.items_data[index]
        reply = QMessageBox.question(self, "刪除確認", 
                                     f"確定要永久刪除「{item['name']}」嗎？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            success = StartupManager.delete_startup_item(item)
            if success:
                self.reload_logic()
            else:
                QMessageBox.warning(self, "錯誤", "刪除失敗，請確認權限。")
