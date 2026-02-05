from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                                 QTreeWidget, QTreeWidgetItem, QHeaderView, QComboBox,
                                 QFrame, QMenu)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QAction
from ui.theme import Theme
import os
import string
import ctypes

class DiskAnalyzerWorker(QThread):
    """Fast disk analyzer - single pass algorithm"""
    progress = Signal(int)
    finished = Signal(dict, dict)  # folder_sizes, children_map
    
    SKIP_DIRS = {'$Recycle.Bin', 'System Volume Information', 'Recovery', '$WinREAgent', 
                 'Config.Msi', '$SysReset'}
    
    def __init__(self, drive):
        super().__init__()
        self.drive = drive
        self.running = True
        # Create/Clear log file
        self.log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scan_log.txt')
        with open(self.log_path, "w", encoding="utf-8") as f:
            f.write("Scan Started\n")
            
    def log(self, message):
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(message + "\n")
        except: pass
        
    def stop(self):
        self.running = False
        
    def run(self):
        root_path = f"{self.drive}\\"
        folder_sizes = {}
        children_map = {}  # parent -> [(name, path, size, is_dir)]
        scan_count = 0
        
        # Priority skip list (only skip if we are sure doing so wont miss user data)
        # We should NOT skip 'Users' or 'Documents and Settings'
        SKIP_DIRS = {'$Recycle.Bin', 'System Volume Information', 'Recovery', '$WinREAgent', 
                     'Config.Msi', '$SysReset'}
        
        # First pass: Recursively calculate sizes using a safe stack approach
        # We manually implement walk to ensure we catch hidden items and handle errors gracefully
        
        # Stack: (path)
        stack = [root_path]
        
        # Post-process stack for size aggregation: (path, list_of_children_files, list_of_children_dirs)
        aggregation_stack = []
        
        while stack and self.running:
            current_path = stack.pop()
            scan_count += 1
            if scan_count % 1000 == 0:
                self.progress.emit(scan_count)
                
            try:
                files = []
                dirs = []
                
                # Use scandir for performance
                with os.scandir(current_path) as entries:
                    for entry in entries:
                        try:
                            if entry.is_file(follow_symlinks=False):
                                size = entry.stat(follow_symlinks=False).st_size
                                files.append((entry.name, entry.path, size))
                            elif entry.is_dir(follow_symlinks=False):
                                # Debug specific paths
                                if "Desktop" in entry.name or "Users" in entry.name or "Jack_Liu" in entry.name:
                                    self.log(f"[SCAN] Found interesting folder: {entry.path}")
                                    
                                if entry.name not in SKIP_DIRS and not entry.name.startswith('$'):
                                    dirs.append((entry.name, entry.path))
                                else:
                                    self.log(f"[SKIP] Skipping: {entry.path}")
                        except (PermissionError, OSError) as e:
                            # Log individual file error but continue scanning directory
                            # self.log(f"[ERROR] Access denied scanning item {entry.path}: {e}")
                            continue
                
                # Push back to aggregator
                # self.log(f"[VISIT] Scanned: {current_path} | Found {len(dirs)} subdirs") # Comment out to reduce noise
                aggregation_stack.append((current_path, files, dirs))
                
                # Push children to processing stack
                for dname, dpath in dirs:
                    stack.append(dpath)
                    
            except (PermissionError, OSError) as e:
                self.log(f"[ERROR] Failed to open dir {current_path}: {e}")
                # Only if the DIRECTORY ITSELF cannot be opened do we skip it
                aggregation_stack.append((current_path, [], []))
                continue
                
        if not self.running:
            return

        # Second pass: Aggregate sizes from bottom up
        # aggregation_stack has parents visited before children.
        # reversing it ensures children are processed before parents.
        
        for path, files, dirs in reversed(aggregation_stack):
            current_size = 0
            file_items = []
            dir_items = []
            
            # Sum files
            for fname, fpath, fsize in files:
                current_size += fsize
                file_items.append((fname, fpath, fsize, False))
                
            # Sum directories
            for dname, dpath in dirs:
                dsize = folder_sizes.get(dpath, 0)
                current_size += dsize
                dir_items.append((dname, dpath, dsize, True))
                
            folder_sizes[path] = current_size
            
            # Combine and sort for UI
            all_items = dir_items + file_items
            all_items.sort(key=lambda x: x[2], reverse=True)
            children_map[path] = all_items
            
        self.finished.emit(folder_sizes, children_map)

class FileScannerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.folder_sizes = {}
        self.children_map = {}
        self.drive_root = ""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Header
        title = QLabel("磁碟空間分析")
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {Theme.TEXT_PRIMARY};")
        layout.addWidget(title)
        
        desc = QLabel("展開資料夾查看子項目大小，右鍵可開啟檔案總管")
        desc.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 14px;")
        layout.addWidget(desc)
        
        # Legend
        legend_frame = QFrame()
        legend_frame.setStyleSheet(f"background-color: {Theme.SURFACE}; border-radius: 8px; padding: 5px;")
        legend_layout = QHBoxLayout(legend_frame)
        legend_layout.setContentsMargins(10, 5, 10, 5)
        legend_layout.setSpacing(20)
        
        legends = [
            ("📦 >1GB", Theme.ERROR),
            ("📁 >100MB", Theme.WARNING),
            ("✅ 垃圾/暫存檔", Theme.SUCCESS),
            ("⚠️ 應用程式資料", Theme.WARNING),
            ("🔒 系統保護", "#666666"),
            ("📌 個人檔案", Theme.TEXT_PRIMARY)
        ]
        
        for text, color in legends:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px; border: none;")
            legend_layout.addWidget(lbl)
            
        legend_layout.addStretch()
        layout.addWidget(legend_frame)
        
        # Controls
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet(f"background-color: {Theme.SURFACE}; border-radius: 10px; padding: 15px;")
        ctrl_layout = QHBoxLayout(ctrl_frame)
        ctrl_layout.setSpacing(15)
        
        ctrl_layout.addWidget(QLabel("磁碟："))
        self.combo_drive = QComboBox()
        self.combo_drive.setFixedWidth(80)
        self.combo_drive.setStyleSheet(f"""
            QComboBox {{
                background-color: {Theme.SURFACE_HOVER};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid #2f334d;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }}
        """)
        self.populate_drives()
        ctrl_layout.addWidget(self.combo_drive)
        
        ctrl_layout.addStretch()
        
        self.btn_scan = QPushButton("📊 開始分析")
        self.btn_scan.setFixedSize(140, 45)
        self.btn_scan.setCursor(Qt.PointingHandCursor)
        self.btn_scan.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: #15161e;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #89b4fa; }}
            QPushButton:disabled {{ background-color: {Theme.SURFACE_HOVER}; }}
        """)
        self.btn_scan.clicked.connect(self.start_scan)
        ctrl_layout.addWidget(self.btn_scan)
        
        layout.addWidget(ctrl_frame)
        
        # Status
        self.lbl_status = QLabel("📂 選擇磁碟並開始分析")
        self.lbl_status.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 14px;")
        layout.addWidget(self.lbl_status)
        
        # Tree View
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["名稱", "大小", "完整路徑"])
        self.tree.setColumnWidth(0, 400)
        self.tree.setColumnWidth(1, 100)
        self.tree.header().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tree.setAlternatingRowColors(False)  # Disable to avoid color conflicts
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemExpanded.connect(self.on_item_expanded)
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                background-color: {Theme.SURFACE};
                border: 1px solid #1f2335;
                border-radius: 10px;
                color: {Theme.TEXT_PRIMARY};
            }}
            QHeaderView::section {{
                background-color: {Theme.SURFACE};
                color: {Theme.TEXT_SECONDARY};
                border: none;
                padding: 10px;
                font-weight: bold;
                border-bottom: 1px solid #2f334d;
            }}
            QTreeWidget::item {{
                padding: 5px;
                background-color: transparent;
            }}
            QTreeWidget::item:hover {{
                background-color: #24283b;
            }}
            QTreeWidget::item:selected {{
                background-color: {Theme.PRIMARY};
                color: #15161e;
            }}
            QTreeWidget::branch {{
                background-color: transparent;
            }}
        """)
        layout.addWidget(self.tree)
        
        self.scan_worker = None
        
    def populate_drives(self):
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                self.combo_drive.addItem(f"{letter}:")
            bitmask >>= 1
            
    def start_scan(self):
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.stop()
            self.btn_scan.setText("📊 開始分析")
            return
            
        self.tree.clear()
        self.folder_sizes = {}
        self.children_map = {}
        
        drive = self.combo_drive.currentText()
        self.drive_root = f"{drive}\\"
            
        self.btn_scan.setText("⏹️ 停止")
        self.lbl_status.setText(f"🔍 正在分析 {drive}\\ ...")
        self.lbl_status.setStyleSheet(f"color: {Theme.TEXT_SECONDARY}; font-size: 14px;")
        
        self.scan_worker = DiskAnalyzerWorker(drive)
        self.scan_worker.progress.connect(self.on_progress)
        self.scan_worker.finished.connect(self.on_scan_finished)
        self.scan_worker.start()
        
    def on_progress(self, count):
        self.lbl_status.setText(f"🔍 已掃描 {count} 個資料夾...")
        
    def on_scan_finished(self, folder_sizes, children_map):
        self.btn_scan.setText("📊 開始分析")
        self.folder_sizes = folder_sizes
        self.children_map = children_map
        
        total_scanned = len(folder_sizes)
        
        # Calculate total size by summing first level items
        # The children_map stores items as (name, full_path, size, is_dir)
        top_level_items = self.children_map.get(self.drive_root, [])
        total_size = sum(item[2] for item in top_level_items)
        
        self.lbl_status.setText(f"✅ 完成！{total_scanned} 個資料夾，總計 {self.format_size(total_size)}")
        self.lbl_status.setStyleSheet(f"color: {Theme.SUCCESS}; font-size: 14px;")
        
        # Populate root level folders (only direct children of drive)
        self.populate_children(None, self.drive_root)
        
    def populate_children(self, parent_item, folder_path):
        """Add child items to a tree item"""
        items = self.children_map.get(folder_path, [])
        
        for name, fpath, size, is_dir in items:
            if size < 1024 * 100:  # Skip < 100KB
                continue
                
            item = QTreeWidgetItem()
            
            # Get safety info
            safety_emoji, safety_color, tooltip = self.get_safety_info(fpath, is_dir)
            
            # Icon based on type and size
            if is_dir:
                if self.is_system_path(fpath):
                    icon = "🔒"
                    item.setForeground(0, QColor("#666"))
                elif size > 1024 * 1024 * 1024:  # > 1GB
                    icon = "📦"
                    item.setForeground(0, QColor(Theme.ERROR))
                elif size > 100 * 1024 * 1024:  # > 100MB
                    icon = "📁"
                    item.setForeground(0, QColor(Theme.WARNING))
                else:
                    icon = "📂"
                    item.setForeground(0, QColor(Theme.TEXT_PRIMARY))
            else:
                # Files: show safety indicator
                icon = safety_emoji
                item.setForeground(0, safety_color)
            
            item.setText(0, f"{icon} {name}")
            item.setText(1, self.format_size(size))
            item.setText(2, fpath)
            item.setToolTip(0, tooltip)
            item.setToolTip(2, fpath)
            item.setData(0, Qt.UserRole, fpath)
            item.setData(0, Qt.UserRole + 1, is_dir)
            
            # Add dummy child for expandable folders
            if is_dir and fpath in self.children_map and self.children_map[fpath]:
                dummy = QTreeWidgetItem()
                dummy.setText(0, "載入中...")
                item.addChild(dummy)
            
            if parent_item is None:
                self.tree.addTopLevelItem(item)
            else:
                parent_item.addChild(item)
                
    def on_item_expanded(self, item):
        """Lazy load children when item is expanded"""
        # Check if it has a dummy child
        if item.childCount() == 1 and item.child(0).text(0) == "載入中...":
            item.takeChildren()  # Remove dummy
            folder_path = item.data(0, Qt.UserRole)
            self.populate_children(item, folder_path)
            
    def is_system_path(self, path):
        """Check if path is a system/protected location"""
        path_lower = path.lower()
        protected = [
            'windows', 'program files', 'program files (x86)', 'programdata',
            'users\\default', 'users\\public', 'users\\all users',
            'boot', 'recovery', 'system volume information',
            'perflogs', 'intel', 'amd', 'nvidia'
        ]
        for p in protected:
            if p in path_lower:
                return True
        return False
        
    def get_safety_info(self, path, is_dir):
        """Return (emoji, color, tooltip) based on safety"""
        path_lower = path.lower()
        name = os.path.basename(path).lower()
        
        # Definitely protected
        if self.is_system_path(path):
            return ("🔒", QColor("#ff6b6b"), "系統檔案，請勿刪除")
        
        # Safe to delete patterns
        safe_patterns = ['temp', 'tmp', 'cache', 'log', '.log', '.tmp', '.bak', 
                         'thumbs.db', 'desktop.ini', '.ds_store']
        if any(p in name for p in safe_patterns):
            return ("✅", QColor(Theme.SUCCESS), "垃圾/暫存檔案 (通常可安全刪除)")
        
        # User folders - be careful
        if 'users' in path_lower and 'appdata' in path_lower:
            return ("⚠️", QColor(Theme.WARNING), "應用程式資料，刪除可能導致軟體重設")
        
        # Downloads, temp folders
        if any(x in path_lower for x in ['downloads', 'desktop', 'documents', 'music', 'pictures', 'videos']):
            return ("📌", QColor(Theme.TEXT_PRIMARY), "您的個人檔案 (刪除後系統不會壞，但檔案會消失)")
            
        # Classify by extension
        ext = os.path.splitext(name)[1].lower()
        if ext in ['.exe', '.msi', '.dll', '.sys', '.bat', '.cmd']:
            return ("⚙️", QColor(Theme.TEXT_SECONDARY), "應用程式/系統檔案")
        elif ext in ['.txt', '.log', '.ini', '.cfg', '.xml', '.json']:
            return ("📝", QColor(Theme.TEXT_SECONDARY), "文字/設定檔")
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg']:
            return ("🖼️", QColor(Theme.TEXT_PRIMARY), "圖片")
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.mp3', '.wav', '.flac']:
            return ("🎬", QColor(Theme.TEXT_PRIMARY), "影音檔案")
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return ("📦", QColor(Theme.TEXT_SECONDARY), "壓縮檔")
        elif ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h']:
            return ("💻", QColor(Theme.TEXT_PRIMARY), "程式碼")
        
        return ("❓", QColor(Theme.TEXT_SECONDARY), "一般檔案 (請自行確認用途)")
            
    def show_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
            
        path = item.data(0, Qt.UserRole)
        is_dir = item.data(0, Qt.UserRole + 1)
        
        if not path or not os.path.exists(path):
            return
        
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {Theme.SURFACE};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid #2f334d;
                border-radius: 5px;
                padding: 5px;
            }}
            QMenu::item {{
                padding: 8px 20px;
            }}
            QMenu::item:selected {{
                background-color: {Theme.PRIMARY};
                color: #15161e;
            }}
            QMenu::separator {{
                height: 1px;
                background: #2f334d;
                margin: 5px 10px;
            }}
        """)
        
        # Open in Explorer
        action_open = menu.addAction("📂 在檔案總管中開啟")
        action_open.triggered.connect(lambda: os.startfile(path if is_dir else os.path.dirname(path)))
        
        menu.addSeparator()
        
        # Check if system path
        is_protected = self.is_system_path(path)
        
        if is_protected:
            action_warn = menu.addAction("🔒 系統保護項目，無法刪除")
            action_warn.setEnabled(False)
        else:
            # Delete option
            if is_dir:
                action_delete = menu.addAction("🗑️ 刪除資料夾")
                action_delete.triggered.connect(lambda: self.delete_item(item, path, True, False))
                
                action_force = menu.addAction("💀 強制刪除（含子項目）")
                action_force.triggered.connect(lambda: self.delete_item(item, path, True, True))
            else:
                action_delete = menu.addAction("🗑️ 刪除檔案")
                action_delete.triggered.connect(lambda: self.delete_item(item, path, False, False))
        
        menu.exec(self.tree.viewport().mapToGlobal(pos))
        
    def delete_item(self, item, path, is_dir, force):
        from PySide6.QtWidgets import QMessageBox
        import shutil
        
        name = os.path.basename(path)
        
        if force:
            msg = f"⚠️ 確定要強制刪除？\n\n{name}\n\n這將刪除資料夾內所有檔案，無法復原！"
        else:
            msg = f"確定要刪除？\n\n{name}"
            
        reply = QMessageBox.question(self, "確認刪除", msg,
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
            
        try:
            if is_dir:
                if force:
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    os.rmdir(path)  # Only works if empty
            else:
                os.remove(path)
                
            # Remove from tree
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                idx = self.tree.indexOfTopLevelItem(item)
                self.tree.takeTopLevelItem(idx)
                
            self.lbl_status.setText(f"🗑️ 已刪除: {name}")
            self.lbl_status.setStyleSheet(f"color: {Theme.SUCCESS}; font-size: 14px;")
            
        except PermissionError:
            QMessageBox.warning(self, "權限不足", "無法刪除，請確認檔案未被使用中，或以系統管理員身分執行。")
        except OSError as e:
            if "not empty" in str(e).lower() or "目錄不是空的" in str(e):
                QMessageBox.warning(self, "資料夾不為空", "資料夾內還有檔案。\n請使用「強制刪除」來刪除整個資料夾。")
            else:
                QMessageBox.warning(self, "錯誤", f"無法刪除：{e}")
            
    def format_size(self, size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size/(1024*1024):.1f} MB"
        else:
            return f"{size/(1024*1024*1024):.2f} GB"
