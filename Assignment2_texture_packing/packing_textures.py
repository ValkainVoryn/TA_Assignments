import sys
import os
from fileinput import filename

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidgetItem, QAbstractItemView, QPushButton, \
    QLineEdit, QPlainTextEdit, QListWidget

from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

from utils.ui_loader import load_ui
from core import config_manager
from PIL import Image
from pathlib import Path
from core.worker import DownloadWorker

# TODO: create pyside for UE5 that allows the user to load all textures from a selected folder
# filter files only for images
# TODO: have dropdown menu that suggests presets based off naming conventions (eg. _AO)
# TODO: "no match found" if no conventions can be found to pack with (allow user to do manually)
# TODO: default packing standard (eg. _RMA or _ORM)


class TexturePackerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # load ui
        self.ui = load_ui("resources/main_window.ui", self)
        self.setCentralWidget(self.ui)
        self.setWindowTitle("Texture Packer")

        # init all parts of widget
        self.btn_browse_folder: QPushButton = self.ui.btn_browse_folder
        self.btn_browse_save: QPushButton = self.ui.btn_browse_save
        self.btn_apply: QPushButton = self.ui.btn_apply
        self.btn_cancel: QPushButton = self.ui.btn_cancel

        self.line_texture_path: QLineEdit = self.ui.line_texture_path
        self.line_save_path: QLineEdit = self.ui.line_save_path

        self.text_texture_files: QPlainTextEdit = self.ui.text_texture_files
        self.text_texture_made: QPlainTextEdit = self.ui.text_texture_made

        # connect to function
        self.btn_browse_folder.clicked.connect(self.browse_folder_for_textures)
        self.btn_browse_save.clicked.connect(self.browse_folder_for_save)

        # Load saved path from config_manager

        config = config_manager.load_config()
        saved_path = config.get("last_save_path", "")
        if saved_path and os.path.isdir(saved_path):
            self.line_save_path.setText(saved_path)

    def browse_folder_for_textures(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Texture Directory")
        # this is a folder picker
        if folder:
            self.line_texture_path.setText(folder)
            config_manager.save_config({"last_texture_path": folder})
        src_path = Path(folder)

        extensions = Image.registered_extensions().keys()
        l_img_paths: list[Path] = []
        for path in src_path.rglob("*"):
            if path.suffix.lower() in extensions:
                l_img_paths.append(path)
        return l_img_paths

    def browse_folder_for_save(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        # this is a folder picker
        if folder:
            self.line_save_path.setText(folder)
            config_manager.save_config({"last_save_path": folder})


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TexturePackerApp()
    window.show()
    sys.exit(app.exec())
