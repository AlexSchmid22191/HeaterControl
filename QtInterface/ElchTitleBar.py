from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QToolButton, QHBoxLayout, QDialog, QLabel, QVBoxLayout, QPushButton, QTextBrowser


class ElchTitlebar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumHeight(50)
        buttons = {key: QToolButton(self, objectName=key) for key in ['About', 'Minimize', 'Close']}

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addStretch(10)
        for key in buttons:
            buttons[key].setFixedSize(50, 50)
            hbox.addWidget(buttons[key])

        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        self.setLayout(hbox)

        self.dragPosition = None
        buttons['Minimize'].clicked.connect(self.minimize)
        buttons['Close'].clicked.connect(self.close)
        buttons['About'].clicked.connect(self.show_about)

    def mouseMoveEvent(self, event):
        # Enable mouse dragging
        if event.buttons() == Qt.LeftButton:
            self.parent().move(event.globalPos() - self.dragPosition)
            event.accept()

    def mousePressEvent(self, event):
        # Enable mouse dragging
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.parent().frameGeometry().topLeft()
            event.accept()

    def minimize(self):
        self.parent().showMinimized()

    def close(self):
        self.parent().close()

    def show_about(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('About')
        dlg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.setSpacing(10)
        vbox.addWidget(QLabel('ElchiTools 2.8', objectName='Header'), alignment=Qt.AlignHCenter)

        license_label = QLabel()
        license_label.setText('License: GPL 3.0')
        license_label.setOpenExternalLinks(True)
        vbox.addWidget(license_label, alignment=Qt.AlignHCenter)

        vbox.addWidget(QLabel('Maintainer: Alex Schmid'), alignment=Qt.AlignHCenter)
        vbox.addWidget(QLabel('Contact: alex.schmid91@gmail.com'), alignment=Qt.AlignHCenter)

        source_label = QLabel()
        source_label.setText('Source: https://github.com/AlexSchmid22191/HeaterControl')
        source_label.setOpenExternalLinks(True)
        vbox.addWidget(source_label, alignment=Qt.AlignHCenter)
        vbox.addWidget(button2 := QPushButton('View GPL3'))
        vbox.addWidget(button3 := QPushButton('View license info'))
        vbox.addWidget(button := QPushButton('Close'))
        button.clicked.connect(dlg.close)
        button2.clicked.connect(self.show_gpl)
        button3.clicked.connect(self.show_license_info)

        dlg.setLayout(vbox)
        dlg.exec_()

    def show_gpl(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('License')
        dlg.setSizeGripEnabled(True)
        dlg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        dlg.text_browser = QTextBrowser()
        try:
            with open('License/gpl-3.0.md', "r", encoding="utf-8") as file:
                content = file.read()
                dlg.text_browser.setMarkdown(content)
        except Exception as e:
            dlg.text_browser.setText(f"Error loading license file: {e}")

        layout = QVBoxLayout()
        layout.addWidget(dlg.text_browser)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dlg.close)
        layout.addWidget(close_button)

        dlg.setLayout(layout)
        dlg.exec_()

    def show_license_info(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('License')
        dlg.setSizeGripEnabled(True)
        dlg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        dlg.text_browser = QTextBrowser()
        try:
            with open('License/License.md', "r", encoding="utf-8") as file:
                content = file.read()
                dlg.text_browser.setMarkdown(content)
        except Exception as e:
            dlg.text_browser.setText(f"Error loading license file: {e}")

        layout = QVBoxLayout()
        layout.addWidget(dlg.text_browser)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dlg.close)
        layout.addWidget(close_button)

        dlg.setLayout(layout)
        dlg.exec_()