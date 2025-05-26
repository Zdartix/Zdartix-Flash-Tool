import sys
import os
import subprocess
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QListWidgetItem, QCheckBox, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QIcon
from main_window_ui import Ui_MainWindow
from PyQt5 import QtCore
import time
import ctypes
import win32gui
import win32con
import win32process
import win32api
import mimetypes
from flash_window import FlashWindow
import threading
from PyQt5.QtCore import QObject, pyqtSignal
import tempfile




class Signals(QObject):
    append_text = pyqtSignal(str)
    show_message = pyqtSignal(str, str)

class FlashApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.terminal_input = self.ui.terminal_input
        self.terminal_output = self.ui.terminal_output
        self.btn_send_terminal = self.ui.btn_send_terminal
        self.btn_send_terminal.clicked.connect(self.start_terminal)

        # Layout poziomy na górze pod tabami
        top_buttons_layout = QtWidgets.QHBoxLayout()
        self.ui.verticalLayout.insertLayout(1, top_buttons_layout)
        
        # Przycisk Backup Partycji
        self.btn_backup_partition = QPushButton("📦 Partition backup")
        top_buttons_layout.addWidget(self.btn_backup_partition)
        self.btn_backup_partition.clicked.connect(self.open_backup_window)

        # === STYL ===
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-family: Consolas, monospace;
                font-size: 13px;
            }

            QPushButton {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a3a3a,
                    stop:1 #2a2a2a
                );
                color: white;
                border: 1px solid #444;
                padding: 8px;
                border-radius: 6px;
            }

            QPushButton:hover {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a4a,
                    stop:1 #3a3a3a
                );
            }

            QLineEdit, QListWidget, QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #444;
                padding: 6px;
                color: white;
                border-radius: 4px;
            }

            QTabWidget::pane {
                border: 1px solid #555;
                background: #1e1e1e;
            }

            QTabBar::tab {
                background: #2c2c2c;
                padding: 8px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                color: white;
            }

            QTabBar::tab:selected {
                background: #3a3a3a;
                font-weight: bold;
            }

            QLabel {
                font-weight: normal;
                color: #ccc;
            }

            QMessageBox {
                background-color: #2c2c2c;
                color: white;
            }
        """)

        # === SYGNAŁY ===
        self.ui.btn_check_device.clicked.connect(self.check_device)
        self.ui.btn_reboot_system.clicked.connect(lambda: self.run_cmd([self.get_adb(), "reboot"]))
        self.ui.btn_reboot_recovery.clicked.connect(lambda: self.run_cmd([self.get_adb(), "reboot", "recovery"]))
        self.ui.btn_reboot_fastboot.clicked.connect(lambda: self.run_cmd([self.get_adb(), "reboot", "bootloader"]))
        self.ui.btn_flash_partition.clicked.connect(self.open_flash_window)

        self.ui.btn_list_files.clicked.connect(self.list_files)
        self.ui.btn_pull_file.clicked.connect(self.pull_file)
        self.ui.btn_push_file.clicked.connect(self.push_file)

        # === DRAG & DROP + DWUKLIK W FOLDER ===
        self.ui.list_files.setAcceptDrops(True)
        self.ui.list_files.dragEnterEvent = self.dragEnterEvent
        self.ui.list_files.dropEvent = self.dropEvent
        self.ui.list_files.itemDoubleClicked.connect(self.enter_directory)
        self.ui.list_files.installEventFilter(self)

        # === ROOT SWITCH & BACK BUTTON ===
        self.cb_root = QCheckBox("mode root", self)
        self.ui.verticalLayout.addWidget(self.cb_root)
        self.cb_root.stateChanged.connect(self.toggle_root_mode)

        self.btn_back_folder = QPushButton("⬅ Return to previous folder", self)
        self.ui.verticalLayout.addWidget(self.btn_back_folder)
        self.btn_back_folder.clicked.connect(self.go_back)

        self.current_path = "/sdcard"
        
        self.ui.btn_scrcpy.clicked.connect(self.run_scrcpy)

        self.ui.list_files.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.list_files.customContextMenuRequested.connect(self.show_context_menu)

        self.ui.btn_send_terminal.setText("Launch Terminal")
        self.ui.btn_send_terminal.clicked.connect(self.start_terminal)

        # === OPTYMALIZACJA === 
        self.signals = Signals()
        self.signals.append_text.connect(self.safe_append_text)
        self.signals.show_message.connect(self.safe_message_box)

    @staticmethod
    def get_adb():
        return os.path.join(os.getcwd(), "platform-tools", "adb.exe")

    @staticmethod
    def get_fastboot():
        return os.path.join(os.getcwd(), "platform-tools", "fastboot.exe")

    def safe_message_box(self, title, msg):
        QMessageBox.information(self, title, msg)
    
    def safe_append_text(self, text):
        if hasattr(self, "backup_console") and self.backup_console.isVisible():
            self.backup_console.append(text)
        else:
            self.ui.terminal_output.append(text)

    def toggle_root_mode(self, state):
        adb = self.get_adb()
        if state == QtCore.Qt.Checked:
            subprocess.run([adb, "root"], creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(1)
            subprocess.run([adb, "wait-for-device"], creationflags=subprocess.CREATE_NO_WINDOW)
            QMessageBox.information(self, "Tryb root", "Switched ADB to root mode.")
        else:
            subprocess.run([adb, "unroot"], creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(1)
            subprocess.run([adb, "wait-for-device"], creationflags=subprocess.CREATE_NO_WINDOW)
            QMessageBox.information(self, "Non-root mode", "Switched to non-root ADB mode.")
      
    def check_device(self):
        adb = self.get_adb()
        result = subprocess.run([adb, "get-state"], stdout=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if "device" in result.stdout:
            self.ui.label_status.setText("✅ Device connected")

            def get_prop(prop):
                try:
                    out = subprocess.run([adb, "shell", f"getprop {prop}"], stdout=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    return out.stdout.strip()
                except:
                    return "Nieznane"

            model = get_prop("ro.product.model")
            manufacturer = get_prop("ro.product.manufacturer")
            android_ver = get_prop("ro.build.version.release")
            build_id = get_prop("ro.build.display.id")

            root_check = subprocess.run(
                [adb, "shell", "which su"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            has_root = "✅ YES" if root_check.stdout.strip() else "❌ NIE"

            info = f"""📱 Info device :
Model: {model}
Producent: {manufacturer}
Android: {android_ver}
Build: {build_id}
Root: {has_root}"""

            self.ui.label_device_info.setText(info)

        else:
            self.ui.label_status.setText("❌ Devices missing")
            self.ui.label_device_info.setText("")

    def run_command_live(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        while True:
            output = process.stdout.readline()
            if output:
                self.signals.append_text.emit(output.strip())
                QtWidgets.QApplication.processEvents()
            if process.poll() is not None:
                break

        stderr_output = process.stderr.read()
        if stderr_output:
            if "KB/s" in stderr_output or "bytes" in stderr_output:
                self.backup_console.append(stderr_output.strip())
            else:
                self.backup_console.append(f"❌ Error: {stderr_output.strip()}")
     
    def start_backup(self):
        thread = threading.Thread(target=self._do_backup, daemon=True)
        thread.start()

    def _do_backup(self):
        adb = self.get_adb()
        partitions = []
        if self.cb_system.isChecked():
            partitions.append("system")
        if self.cb_vendor.isChecked():
            partitions.append("vendor")
        if self.cb_boot.isChecked():
            partitions.append("boot")
        if self.cb_dtbo.isChecked():
            partitions.append("dtbo")
        if self.cb_recovery.isChecked():
            partitions.append("recovery")
        if self.cb_userdata.isChecked():
            partitions.append("userdata")

        if not partitions:
            self.signals.show_message.emit("No choice", "Select at least one partition to backup.")
            return

        folder = QFileDialog.getExistingDirectory(self, "Select backup folder")
        if not folder:
            return

        for part in partitions:
            local_path = os.path.join(folder, f"{part}.img")
            remote_partition = f"/dev/block/bootdevice/by-name/{part}"
            remote_tmp = f"/data/local/tmp/{part}.img"

            self.signals.append_text.emit(f"📦 Create backup: {part}")


            result = subprocess.run(
                [adb, "shell", "su", "-c", f"dd if={remote_partition} of={remote_tmp}"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            self.signals.append_text.emit(result.stdout + result.stderr)


            check = subprocess.run(
                [adb, "shell", f"ls {remote_tmp}"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if "No such file" in check.stderr:
                self.signals.append_text.emit(f"❌ Failed to create backup of {part}\n")
                continue


            self.run_command_live([adb, "pull", remote_tmp, local_path])
            subprocess.run([adb, "shell", "rm", remote_tmp])
            self.signals.append_text.emit(f"✅ Backup completed {part}\n")

        self.signals.append_text.emit("🎉 Backup of all partitions completed!")
        self.signals.show_message.emit("Backup completed", "✅ All partitions saved")
    
    def run_cmd(self, cmd):
        adb = self.get_adb()
        fastboot = self.get_fastboot()
        
        if cmd and cmd[0] == "adb":
            cmd[0] = adb
        elif cmd and cmd[0] == "fastboot":
            cmd[0] = fastboot

        if hasattr(self, 'cb_root') and self.cb_root.isChecked() and cmd[0] == adb and "shell" in cmd:
            idx = cmd.index("shell") + 1
            shell_cmd = " ".join(cmd[idx:])
            cmd = [adb, "shell", "su", "-c", shell_cmd]

        try:
            flags = subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0
            subprocess.run(cmd, check=True, creationflags=flags)
            QMessageBox.information(self, "OK", f"command completed:\n{' '.join(cmd)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def list_files(self):
        adb = self.get_adb()
        path = self.ui.line_path.text()
        cmd = [adb, "shell"]
        ls_cmd = f"ls -p {path}"
        if self.cb_root.isChecked():
            ls_cmd = f"su -c \"{ls_cmd}\""
        cmd.append(ls_cmd)

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

        self.ui.list_files.clear()

        if result.stderr.strip():
            error_item = QListWidgetItem(f"❌ {result.stderr.strip()}")
            error_item.setForeground(QtGui.QColor("red"))
            error_item.setFlags(QtCore.Qt.NoItemFlags)  
            self.ui.list_files.addItem(error_item)
            return

        items = result.stdout.replace("\n", " ").replace("\t", " ").replace("\r", "").split()
        for item_name in items:
            item = QListWidgetItem(item_name)
            if item_name.endswith("/"):
                item.setIcon(QIcon.fromTheme("folder"))
            else:
                item.setIcon(QIcon.fromTheme("text-x-generic"))
            self.ui.list_files.addItem(item)

    def enter_directory(self, item):
        if item is None:
            return  

        if not item.text().endswith("/"):
            return  

        current_path = self.ui.line_path.text().rstrip("/")
        new_path = f"{current_path}/{item.text().rstrip('/')}"
        self.ui.line_path.setText(new_path)
        self.list_files()

    def go_back(self):
        current_path = self.ui.line_path.text().rstrip("/")
        if "/" in current_path:
            parent_path = "/".join(current_path.split("/")[:-1]) or "/"
            self.ui.line_path.setText(parent_path)
            self.list_files()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        adb = self.get_adb()
        for url in event.mimeData().urls():
            local_path = url.toLocalFile()
            remote_path = self.ui.line_path.text()
            if local_path:
                subprocess.run([adb, "push", local_path, remote_path], creationflags=subprocess.CREATE_NO_WINDOW)
                QMessageBox.information(self, "Push", f"Send: {local_path}")
        self.list_files()

    def pull_file(self):
        adb = self.get_adb()
        selected = self.ui.list_files.currentItem()
        if selected:
            remote = f"{self.ui.line_path.text()}/{selected.text().rstrip('/')}"
            local = QFileDialog.getExistingDirectory(self, "Where to save")
            if local:
                subprocess.run([adb, "pull", remote, local], creationflags=subprocess.CREATE_NO_WINDOW)
                self.signals.show_message.emit("OK", "Downloaded file")

    def push_file(self):
        adb = self.get_adb()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select file to pysh")
        if file_path:
            remote = self.ui.line_path.text()
            subprocess.run([adb, "push", file_path, remote], creationflags=subprocess.CREATE_NO_WINDOW)
            QMessageBox.information(self, "OK", "File pushed successfully")

    def run_scrcpy(self):
        scrcpy_dir = os.path.join(os.getcwd(), "scrcpy")
        scrcpy_path = os.path.join(scrcpy_dir, "scrcpy.exe")

        if not os.path.exists(scrcpy_path):
            QMessageBox.critical(self, "Błąd", f"scrcpy.exe not found :\n{scrcpy_path}")
            return

        container = self.ui.scrcpy_container
        if container is None:
            QMessageBox.critical(self, "Błąd", "Not found scrcpy_container!")
            return

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        proc = subprocess.Popen([
            scrcpy_path,
            "--window-borderless",
            "--max-size=650",
            "--always-on-top"  
        ], cwd=scrcpy_dir, startupinfo=startupinfo)
        pid = proc.pid

        hwnd = None
        for _ in range(50):
            def enum_handler(handle, _):
                nonlocal hwnd
                _, found_pid = win32process.GetWindowThreadProcessId(handle)
                if found_pid == pid and win32gui.IsWindowVisible(handle):
                    hwnd = handle

            win32gui.EnumWindows(enum_handler, None)
            if hwnd:
                break
            time.sleep(0.1)

        if not hwnd:
            QMessageBox.critical(self, "Błąd", "Not found window scrcpy.")
            return

        win32gui.SetParent(hwnd, container.winId())

        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style = style & ~win32con.WS_POPUP | win32con.WS_CHILD | win32con.WS_VISIBLE
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

        rect = container.geometry()
        win32gui.MoveWindow(hwnd, 0, 0, rect.width(), rect.height(), True)

    def is_editable(self, filename):
        editable_exts = [".sh", ".txt", ".conf", ".rc", ".log"]
        return any(filename.endswith(ext) for ext in editable_exts)

    def show_context_menu(self, position):
        adb = self.get_adb()
        self.ui.list_files.blockSignals(True) 

        menu = QtWidgets.QMenu()

        action_new_folder = menu.addAction("📁 Create folder")
        action_new_file = menu.addAction("📄  Add file")
        action_rename = menu.addAction("✏️ Rename")

        menu.addSeparator()

        selected_item = self.ui.list_files.itemAt(position)
        current_path = self.ui.line_path.text().rstrip("/")

        action_edit = None
        if selected_item and not selected_item.text().endswith("/"):
            action_edit = menu.addAction("✍️ Edit file")

        action_copy = menu.addAction("📋 Copy")
        action_paste = menu.addAction("📥 Paste")
        action_delete = menu.addAction("🗑️ Delete")
        
        menu.addSeparator()
        action_info = menu.addAction("ℹ️ Info device")

        selected_action = menu.exec_(self.ui.list_files.viewport().mapToGlobal(position))

        self.ui.list_files.blockSignals(False) 

        if selected_action == action_new_folder:
            name, ok = QtWidgets.QInputDialog.getText(self, "New folder", "Name folder:")
            if ok and name:
                cmd = [adb, "shell", f"mkdir '{current_path}/{name}'"]
                if self.cb_root.isChecked():
                    cmd = [adb, "shell", f"su -c \"mkdir '{current_path}/{name}'\""]
                flags = subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0    
                subprocess.run(cmd, creationflags=flags)
                self.list_files()

        elif selected_action == action_new_file:
            name, ok = QtWidgets.QInputDialog.getText(self, "New file", "Name file:")
            if ok and name:
                cmd = [adb, "shell", f"touch '{current_path}/{name}'"]
                if self.cb_root.isChecked():
                    cmd = [adb, "shell", f"su -c \"touch '{current_path}/{name}'\""]
                flags = subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0      
                subprocess.run(cmd, creationflags=flags)
                self.list_files()

        elif selected_action == action_rename and selected_item:
            old_name = selected_item.text().rstrip("/")
            new_name, ok = QtWidgets.QInputDialog.getText(self, "Rename", f"New name for: {old_name}")
            if ok and new_name:
                old_path = f"{current_path}/{old_name}"
                new_path = f"{current_path}/{new_name}"
                cmd = [adb, "shell", f"mv '{old_path}' '{new_path}'"]
                if self.cb_root.isChecked():
                    cmd = [adb, "shell", f"su -c \"mv '{old_path}' '{new_path}'\""]
                flags = subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0     
                subprocess.run(cmd, creationflags=flags)
                self.list_files()

        elif selected_item and selected_action:
            file_path = f"{current_path}/{selected_item.text().rstrip('/')}"

            if selected_action == action_edit:
                self.edit_file(file_path)
                return

            elif selected_action == action_copy:
                self.clipboard_path = file_path
                return

            elif selected_action == action_paste and hasattr(self, 'clipboard_path'):
                cmd = [adb, "shell", f"cp '{self.clipboard_path}' '{current_path}'"]
                if self.cb_root.isChecked():
                    cmd = [adb, "shell", f"su -c \"cp '{self.clipboard_path}' '{current_path}'\""]
                flags = subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0      
                subprocess.run(cmd, creationflags=flags)
                self.list_files()
                return

            elif selected_action == action_delete:
                cmd = [adb, "shell", f"rm -rf '{file_path}'"]
                if self.cb_root.isChecked():
                    cmd = [adb, "shell", f"su -c \"rm -rf '{file_path}'\""]
                flags = subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0      
                subprocess.run(cmd, creationflags=flags)
                self.list_files()
                return

            elif selected_action == action_info:
                self.show_file_info(file_path)
                return

    def edit_file(self, remote_path):
        adb = self.get_adb()
        if remote_path.endswith("/"):
            QMessageBox.warning(self, "Error", "You cannot edit a folder.")
            return

        result = subprocess.run([adb, "shell", f"if [ -d '{remote_path}' ]; then echo folder; else echo file; fi"], 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

        if "folder" in result.stdout:
            QMessageBox.warning(self, "Error", "This is a folder, not a file.")
            return

        

        local_tmp = os.path.join(tempfile.gettempdir(), "temp_edit_file.txt")

        subprocess.run([adb, "pull", remote_path, local_tmp], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)

        if not os.path.exists(local_tmp):
            QMessageBox.critical(self, "Error", "file was not downloaded")
            return

        try:
            with open(local_tmp, "rb") as f:
                raw = f.read()
                try:
                    content = raw.decode("utf-8")
                except UnicodeDecodeError:
                    QMessageBox.critical(self, "Error", "The file is not a text file.")
                    return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"File cannot be opened:\n{e}")
            return

        text, ok = QtWidgets.QInputDialog.getMultiLineText(self, "Edit file", remote_path.split("/")[-1], content if raw else "")

        if ok:
            with open(local_tmp, "w", encoding="utf-8") as f:
                f.write(text)
            subprocess.run([adb, "push", local_tmp, remote_path], creationflags=subprocess.CREATE_NO_WINDOW)
            QMessageBox.information(self, "Save", "The changes file have been saved successfully.")
            
    def flash_finished(self):
        self.console_output.append("\n✅ Flashing completed!")
        self.reboot_button.setEnabled(True)
    
    def open_flash_window(self):
        self.flash_window = FlashWindow()
        self.flash_window.show()

    def open_backup_window(self):
      self.backup_window = QtWidgets.QDialog(self)
      self.backup_window.setWindowTitle("Partition Backup")
      self.backup_window.resize(500, 400)
  
      layout = QtWidgets.QVBoxLayout(self.backup_window)
  
      # Checkboxy partycji
      self.cb_system = QtWidgets.QCheckBox("system")
      self.cb_vendor = QtWidgets.QCheckBox("vendor")
      self.cb_boot = QtWidgets.QCheckBox("boot")
      self.cb_dtbo = QtWidgets.QCheckBox("dtbo")
      self.cb_recovery = QtWidgets.QCheckBox("recovery")
      self.cb_userdata = QtWidgets.QCheckBox("userdata")
  
      layout.addWidget(self.cb_system)
      layout.addWidget(self.cb_vendor)
      layout.addWidget(self.cb_boot)
      layout.addWidget(self.cb_dtbo)
      layout.addWidget(self.cb_recovery)
      layout.addWidget(self.cb_userdata)
  
      self.backup_console = QtWidgets.QTextEdit()
      self.backup_console.setReadOnly(True)
      layout.addWidget(self.backup_console)

      btn_start_backup = QPushButton("📦 Start Backup")
      layout.addWidget(btn_start_backup)
      btn_start_backup.clicked.connect(self.run_backup_thread)
  
      self.backup_window.show()

    def run_backup_thread(self):
     thread = threading.Thread(target=self.start_backup, daemon=True)
     thread.start()

    def eventFilter(self, source, event):
        if source == self.ui.list_files:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                if event.button() == QtCore.Qt.RightButton:
                    return True  
        return super().eventFilter(source, event)
    
    def show_file_info(self, remote_path):
     adb = self.get_adb()
     try:
         cmd = [adb, "shell", f"ls -l '{remote_path}'"]
         if self.cb_root.isChecked():
             cmd = [adb, "shell", f"su -c \"ls -l '{remote_path}'\""]
         result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
         
         if result.stderr.strip():
             QMessageBox.critical(self, "Błąd", result.stderr.strip())
             return
 
         info = result.stdout.strip()
         QMessageBox.information(self, "ℹ️ Properties", info)
 
     except Exception as e:
         QMessageBox.critical(self, "Error", f"Unable to retrieve information:\n{e}")
      
    def start_terminal(self):
        adb = self.get_adb()
        if hasattr(self, "adb_process") and self.adb_process and self.adb_process.poll() is None:
            return  
    
        cb_root = self.findChild(QtWidgets.QCheckBox, "cb_terminal_root")
        shell_cmd = [adb, "shell"]
        if cb_root and cb_root.isChecked():
            shell_cmd = [adb, "shell", "su", "-c", "sh"]
    
        try:
            self.adb_process = subprocess.Popen(
                shell_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        except Exception as e:
            self.signals.show_message.emit("Error", f"Failed to start terminal:\n{e}")
            return
    
        def read_terminal_output():
            while self.adb_process.poll() is None:
                try:
                    line = self.adb_process.stdout.readline()
                    if line:
                        self.signals.append_text.emit(line.strip())
                except Exception as e:
                    self.signals.append_text.emit(f"❌ Terminal error: {e}")
                    break
    
        self.terminal_thread = threading.Thread(target=read_terminal_output, daemon=True)
        self.terminal_thread.start()
    
        try:
            self.ui.terminal_input.returnPressed.disconnect()
        except:
            pass
    
        self.terminal_input.returnPressed.connect(self.send_terminal_command)
        self.ui.btn_send_terminal.setEnabled(False)
      
    def send_terminal_command(self):
        cmd = self.terminal_input.text().strip()
        if cmd and hasattr(self, "adb_process") and self.adb_process and self.adb_process.stdin:
            try:
               
                self.terminal_output.append(f"begonia:/ # {cmd}")
                self.adb_process.stdin.write(cmd + "\n")
                self.adb_process.stdin.flush()
            except Exception as e:
                self.signals.append_text.emit(f"❌ Failed to send command: {e}")
        self.terminal_input.clear()
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = FlashApp()
    window.show()
    sys.exit(app.exec_())
