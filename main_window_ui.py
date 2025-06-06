# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 500)
        self.verticalLayout = QtWidgets.QVBoxLayout(MainWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(MainWindow)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_adb = QtWidgets.QWidget()
        self.tab_adb.setObjectName("tab_adb")
        self.adb_main_layout = QtWidgets.QHBoxLayout(self.tab_adb)
        self.adb_main_layout.setObjectName("adb_main_layout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_status = QtWidgets.QLabel(self.tab_adb)
        self.label_status.setObjectName("label_status")
        self.verticalLayout_2.addWidget(self.label_status)
        self.label_device_info = QtWidgets.QLabel(self.tab_adb)
        self.label_device_info.setWordWrap(True)
        self.label_device_info.setObjectName("label_device_info")
        self.verticalLayout_2.addWidget(self.label_device_info)
        self.btn_check_device = QtWidgets.QPushButton(self.tab_adb)
        self.btn_check_device.setObjectName("btn_check_device")
        self.verticalLayout_2.addWidget(self.btn_check_device)
        self.btn_reboot_system = QtWidgets.QPushButton(self.tab_adb)
        self.btn_reboot_system.setObjectName("btn_reboot_system")
        self.verticalLayout_2.addWidget(self.btn_reboot_system)
        self.btn_reboot_recovery = QtWidgets.QPushButton(self.tab_adb)
        self.btn_reboot_recovery.setObjectName("btn_reboot_recovery")
        self.verticalLayout_2.addWidget(self.btn_reboot_recovery)
        self.btn_reboot_fastboot = QtWidgets.QPushButton(self.tab_adb)
        self.btn_reboot_fastboot.setObjectName("btn_reboot_fastboot")
        self.verticalLayout_2.addWidget(self.btn_reboot_fastboot)
        self.btn_flash_partition = QtWidgets.QPushButton(self.tab_adb)
        self.btn_flash_partition.setObjectName("btn_flash_partition")
        self.verticalLayout_2.addWidget(self.btn_flash_partition)
        self.adb_main_layout.addLayout(self.verticalLayout_2)
        self.right_panel = QtWidgets.QVBoxLayout()
        self.right_panel.setObjectName("right_panel")
        self.btn_scrcpy = QtWidgets.QPushButton(self.tab_adb)
        self.btn_scrcpy.setObjectName("btn_scrcpy")
        self.right_panel.addWidget(self.btn_scrcpy)
        self.scrcpy_container = QtWidgets.QWidget(self.tab_adb)
        self.scrcpy_container.setMinimumSize(QtCore.QSize(360, 640))
        self.scrcpy_container.setStyleSheet("background-color: #000;")
        self.scrcpy_container.setObjectName("scrcpy_container")
        self.right_panel.addWidget(self.scrcpy_container)
        self.adb_main_layout.addLayout(self.right_panel)
        self.tabWidget.addTab(self.tab_adb, "")
        self.tab_files = QtWidgets.QWidget()
        self.tab_files.setObjectName("tab_files")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_files)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.line_path = QtWidgets.QLineEdit(self.tab_files)
        self.line_path.setObjectName("line_path")
        self.verticalLayout_3.addWidget(self.line_path)
        self.btn_list_files = QtWidgets.QPushButton(self.tab_files)
        self.btn_list_files.setObjectName("btn_list_files")
        self.verticalLayout_3.addWidget(self.btn_list_files)
        self.list_files = QtWidgets.QListWidget(self.tab_files)
        self.list_files.setObjectName("list_files")
        self.verticalLayout_3.addWidget(self.list_files)
        self.btn_pull_file = QtWidgets.QPushButton(self.tab_files)
        self.btn_pull_file.setObjectName("btn_pull_file")
        self.verticalLayout_3.addWidget(self.btn_pull_file)
        self.btn_push_file = QtWidgets.QPushButton(self.tab_files)
        self.btn_push_file.setObjectName("btn_push_file")
        self.verticalLayout_3.addWidget(self.btn_push_file)
        self.tabWidget.addTab(self.tab_files, "")
                        # Nowa zakładka: Terminal
        self.tab_terminal = QtWidgets.QWidget()
        self.tab_terminal.setObjectName("tab_terminal")
        self.verticalLayout_terminal = QtWidgets.QVBoxLayout(self.tab_terminal)
        self.verticalLayout_terminal.setObjectName("verticalLayout_terminal")
        
        self.terminal_output = QtWidgets.QTextEdit(self.tab_terminal)
        self.terminal_output.setReadOnly(True)
        self.verticalLayout_terminal.addWidget(self.terminal_output)
        
        self.terminal_input = QtWidgets.QLineEdit(self.tab_terminal)
        self.verticalLayout_terminal.addWidget(self.terminal_input)
        
        self.btn_send_terminal = QtWidgets.QPushButton(self.tab_terminal)
        self.btn_send_terminal.setText("Wyślij komendę")
        self.verticalLayout_terminal.addWidget(self.btn_send_terminal)
        
        self.tabWidget.addTab(self.tab_terminal, "")
        
        self.verticalLayout.addWidget(self.tabWidget)



        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Flash Tool by Zdartix"))
        self.label_status.setText(_translate("MainWindow", "Status: Not connected"))
        self.label_device_info.setText(_translate("MainWindow", "📱 Device information will appear here..."))
        self.btn_check_device.setText(_translate("MainWindow", "Check device"))
        self.btn_reboot_system.setText(_translate("MainWindow", "Reboot to System"))
        self.btn_reboot_recovery.setText(_translate("MainWindow", "Reboot to Recovery"))
        self.btn_reboot_fastboot.setText(_translate("MainWindow", "Reboot to Fastboot"))
        self.btn_flash_partition.setText(_translate("MainWindow", "Flash partition"))
        self.btn_scrcpy.setText(_translate("MainWindow", "Show device screen"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_adb), _translate("MainWindow", "ADB / Flash"))
        self.line_path.setText(_translate("MainWindow", "/sdcard"))
        self.btn_list_files.setText(_translate("MainWindow", "Get folder contents"))
        self.btn_pull_file.setText(_translate("MainWindow", "Download selected file"))
        self.btn_push_file.setText(_translate("MainWindow", "Upload file to folder"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_files), _translate("MainWindow", "File Explorer"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_terminal), _translate("MainWindow", "Terminal"))

