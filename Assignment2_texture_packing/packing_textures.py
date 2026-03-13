import sys
import os
from fileinput import filename

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidgetItem, QAbstractItemView, QPushButton, \
    QLineEdit, QPlainTextEdit, QListWidget

from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

from utils.ui_loader import load_ui
from core import config_manager
from core.worker import DownloadWorker

# TODO: create pyside for UE5 that allows the user to load all textures from a selected folder
# TODO: have dropdown menu that suggests presets based off naming conventions (eg. _AO)
# TODO: "no match found" if no conventions can be found to pack with (allow user to do manually)
# TODO: default packing standard (eg. _RMA or _ORM)


class TexturePacker(QMainWindow):
    def __init__(self):
        super().__init__()

        # load ui
        self.ui = load_ui("Resources/main_window.ui", self)
        self.setCentralWidget(self.ui)
        self.setWindowTitle("Texture Packer")

        # init all parts of widget
        self.btn_browse_folder: QPushButton = self.btn_browse_folder
        self.btn_browse_save: QPushButton = self.btn_browse_save
        self.btn_apply: QPushButton = self.btn_apply
        self.btn_cancel: QPushButton = self.btn_cancel
        self.line_texture_path: QLineEdit = self.line_texture_path
        self.line_save_path: QLineEdit = self.line_save_path
        self.text_texture_files: QPlainTextEdit = self.text_texture_files
        self.text_texture_made: QPlainTextEdit = self.text_texture_made

        # connect to function
        self.btn_browse_folder.clicked.connect(self.browse_folder("texture", QLineEdit(self.btn_browse_folder)))
        self.btn_browse_save.clicked.connect(self.browse_folder("save", QLineEdit(self.btn_browse_save)))

    def browse_folder(self, selection_name: str, path: QLineEdit):

        folder = QFileDialog.getExistingDirectory(self, f"Select {selection_name} Directory")
        if folder:
            path.setText(folder)
        config_manager.save_config({f"last_{selection_name}_path": folder})
