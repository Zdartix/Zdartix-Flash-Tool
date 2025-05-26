from PyQt5 import QtWidgets, QtCore
import subprocess
import os
import sys

class FlashWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-family: Consolas, monospace;
                font-size: 13px;
            }
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a3a3a, stop:1 #2a2a2a);
                color: white;
                border: 1px solid #444;
                padding: 8px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4a4a4a, stop:1 #3a3a3a);
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #1e1e1e;
                border: 1px solid #444;
                padding: 6px;
                color: white;
                border-radius: 4px;
            }
            QLabel {
                font-weight: normal;
                color: #ccc;
            }
        """)  
        self.current_process = None
        self.setWindowTitle("Partition Flashing")
        self.resize(600, 500)

        layout = QtWidgets.QVBoxLayout(self)

        self.partitions = ["boot", "recovery", "vbmeta", "system", "vendor", "dtbo", "userdata"]
        self.combo_partitions = QtWidgets.QComboBox()
        self.combo_partitions.addItems(self.partitions)
        layout.addWidget(QtWidgets.QLabel("Select partition:"))
        layout.addWidget(self.combo_partitions)

        file_layout = QtWidgets.QHBoxLayout()
        self.line_img_path = QtWidgets.QLineEdit()
        self.btn_browse_img = QtWidgets.QPushButton("Choose IMG")
        self.btn_browse_img.clicked.connect(self.select_img)
        file_layout.addWidget(self.line_img_path)
        file_layout.addWidget(self.btn_browse_img)
        layout.addLayout(file_layout)

        buttons_layout = QtWidgets.QHBoxLayout()
        self.btn_flash = QtWidgets.QPushButton("FLASH")
        self.btn_flash.clicked.connect(self.start_flash)
        self.btn_reboot = QtWidgets.QPushButton("REBOOT TO SYSTEM")
        self.btn_reboot.clicked.connect(self.reboot_device)
        # self.btn_reboot.setEnabled(False)  
        buttons_layout.addWidget(self.btn_flash)
        buttons_layout.addWidget(self.btn_reboot)
        layout.addLayout(buttons_layout)

        # Console
        self.console_output = QtWidgets.QTextEdit()
        self.console_output.setReadOnly(True)
        layout.addWidget(QtWidgets.QLabel("Console:"))
        layout.addWidget(self.console_output)

        
       # --- NEW BUTTONS ---

        self.btn_fastboot_info = QtWidgets.QPushButton("Get Info")
        self.btn_fastboot_info.clicked.connect(self.get_fastboot_info)
        layout.addWidget(self.btn_fastboot_info)
        
        self.btn_reboot_recovery = QtWidgets.QPushButton("Reboot to Recovery")
        self.btn_reboot_recovery.clicked.connect(self.reboot_to_recovery)
        layout.addWidget(self.btn_reboot_recovery)

        self.btn_reboot_system = QtWidgets.QPushButton("Reboot to System")
        self.btn_reboot_system.clicked.connect(self.reboot_to_system)
        layout.addWidget(self.btn_reboot_system)
 

    @staticmethod
    def get_adb():
        return os.path.join(os.getcwd(), "platform-tools", "adb.exe")
    @staticmethod
    def get_fastboot():
        return os.path.join(os.getcwd(), "platform-tools", "fastboot.exe")

    def select_img(self):
        img_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose .img file", "", "Images (*.img)")
        if img_file:
            self.line_img_path.setText(img_file)

    def start_flash(self):
        partition = self.combo_partitions.currentText()
        img_path = self.line_img_path.text()

        if not img_path or not os.path.isfile(img_path):
            QtWidgets.QMessageBox.warning(self, "Error", "Select a valid IMG file!")
            return

        command = [self.get_fastboot(), "flash", partition, img_path]
        flags = subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0
        subprocess.run(command, creationflags=flags)

        self.console_output.append(f"➔ {command}\n")

        self.current_process = QtCore.QProcess(self)
        self.current_process.readyReadStandardOutput.connect(self.update_console)
        self.current_process.readyReadStandardError.connect(self.update_console)
        self.current_process.finished.connect(self.flash_finished)
        
        self.current_process.start(command[0], command[1:])


        self.btn_flash.setEnabled(False)  

    def update_console(self):
        if self.current_process:
            output = self.current_process.readAllStandardOutput().data().decode()
            error = self.current_process.readAllStandardError().data().decode()

            def colorize(text):
                colored = ""

                lines = text.strip().splitlines()
                for line in lines:
                    if "unlocked: yes" in line.lower():
                        colored += f'<span style="color: #00FF00;">{line}</span><br>'
                    elif "warranty: no" in line.lower():
                        colored += f'<span style="color: #FF5555;">{line}</span><br>'
                    elif "secure: no" in line.lower():
                        colored += f'<span style="color: #FFFF00;">{line}</span><br>'
                    elif any(keyword in line.lower() for keyword in ["serialno", "product", "version"]):
                        colored += f'<span style="color: #00BFFF;">{line}</span><br>'
                    else:
                        colored += f'<span style="color: #CCCCCC;">{line}</span><br>'
                return colored

            if output.strip():
                self.console_output.insertHtml(colorize(output))
                self.console_output.insertPlainText("\n")

            if error.strip():
                self.console_output.insertHtml(colorize(error))
                self.console_output.insertPlainText("\n")

    def flash_finished(self):
        self.console_output.append("\n✅ Flashing finished!")
        self.btn_reboot.setEnabled(True)
        self.btn_flash.setEnabled(True)

    def reboot_device(self):
        command = [self.get_fastboot(), "reboot"]
        self.console_output.append(f"\n➔ {' '.join(command)}\n")
        flags = subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0
        subprocess.run(command, creationflags=flags)
        self.console_output.append("✅ Device rebooted.")

    def get_fastboot_info(self):
        command = [self.get_fastboot(), "getvar", "all"]
        self.console_output.append(f"\n➔ {' '.join(command)}\n")
        self.current_process = QtCore.QProcess(self)
        self.current_process.readyReadStandardOutput.connect(self.update_console)
        self.current_process.readyReadStandardError.connect(self.update_console)
        self.current_process.start(command[0], command[1:])

    def reboot_to_recovery(self):
        command = [self.get_fastboot(), "reboot", "recovery"]
        self.console_output.append(f"\n➔ {' '.join(command)}\n")

        self.current_process = QtCore.QProcess(self)
        self.current_process.readyReadStandardOutput.connect(self.update_console)
        self.current_process.readyReadStandardError.connect(self.update_console)
        self.current_process.finished.connect(lambda: self.console_output.append("✅ Rebooted to Recovery"))
        self.current_process.start(command[0], command[1:])


    def reboot_to_system(self):
        command = [self.get_fastboot(), "reboot"]
        self.console_output.append(f"\n➔ {' '.join(command)}\n")
    
        self.current_process = QtCore.QProcess(self)
        self.current_process.readyReadStandardOutput.connect(self.update_console)
        self.current_process.readyReadStandardError.connect(self.update_console)
        self.current_process.finished.connect(lambda: self.console_output.append("✅ Device rebooted to system"))
        self.current_process.start(command[0], command[1:])

