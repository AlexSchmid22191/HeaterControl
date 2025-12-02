import sys
import src.appinfo
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QToolButton, QHBoxLayout, QDialog, QLabel, QVBoxLayout, QPushButton, QTextBrowser


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
        # noinspection PyUnresolvedReferences
        buttons['Minimize'].clicked.connect(self.minimize)
        # noinspection PyUnresolvedReferences
        buttons['Close'].clicked.connect(self.close)
        # noinspection PyUnresolvedReferences
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
        vbox.addWidget(l := QLabel(text=f'{src.appinfo.APP_NAME} {src.appinfo.APP_VERSION}'), alignment=Qt.AlignHCenter)
        l.setObjectName('Header')

        license_label = QLabel()
        license_label.setText(f'License: {src.appinfo.APP_LICENSE}')
        license_label.setOpenExternalLinks(True)
        vbox.addWidget(license_label, alignment=Qt.AlignHCenter)

        vbox.addWidget(QLabel(f'Maintainer: {src.appinfo.APP_AUTHOR}'), alignment=Qt.AlignHCenter)
        vbox.addWidget(QLabel(f'Contact: {src.appinfo.APP_CONTACT}'), alignment=Qt.AlignHCenter)

        source_label = QLabel()
        source_label.setText(f'Source: {src.appinfo.APP_SOURCE}')
        source_label.setOpenExternalLinks(True)
        vbox.addWidget(source_label, alignment=Qt.AlignHCenter)
        vbox.addWidget(button3 := QPushButton('View license info'))
        vbox.addWidget(button2 := QPushButton('View GPL3'))
        vbox.addWidget(button := QPushButton('Close'))
        # noinspection PyUnresolvedReferences
        button.clicked.connect(dlg.close)
        # noinspection PyUnresolvedReferences
        button2.clicked.connect(self.show_gpl)
        # noinspection PyUnresolvedReferences
        button3.clicked.connect(self.show_license_info)

        dlg.setLayout(vbox)
        dlg.exec_()

    def show_gpl(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('License')
        dlg.setSizeGripEnabled(True)
        dlg.setMinimumSize(600, 400)
        dlg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        dlg.text_browser = QTextBrowser()
        try:
            if getattr(sys, "frozen", False):
                path = Path(sys.executable).resolve().parent / 'License/gpl-3.0.md'
            else:
                path = Path(__file__).resolve().parents[2] / 'License/gpl-3.0.md'
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
                dlg.text_browser.setMarkdown(content)
        except Exception as e:
            dlg.text_browser.setText(f"Error loading license file: {e}")

        layout = QVBoxLayout()
        layout.addWidget(dlg.text_browser)

        close_button = QPushButton("Close")
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(dlg.close)
        layout.addWidget(close_button)

        dlg.setLayout(layout)
        dlg.exec_()

    def show_license_info(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('License')
        dlg.setSizeGripEnabled(True)
        dlg.setMinimumSize(600, 400)
        dlg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        dlg.text_browser = QTextBrowser()
        try:
            if getattr(sys, "frozen", False):
                path = Path(sys.executable).resolve().parent / 'License/License.md'
            else:
                path = Path(__file__).resolve().parents[2] / 'License/License.md'
            with open(path, "r", encoding="utf-8") as file:
                content = file.read()
                dlg.text_browser.setMarkdown(content)
        except Exception as e:
            dlg.text_browser.setText(f"Error loading license file: {e}")

        layout = QVBoxLayout()
        layout.addWidget(dlg.text_browser)

        close_button = QPushButton("Close")
        # noinspection PyUnresolvedReferences
        close_button.clicked.connect(dlg.close)
        layout.addWidget(close_button)

        dlg.setLayout(layout)
        dlg.exec_()
