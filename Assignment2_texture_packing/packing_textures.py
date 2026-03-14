import sys
import os
from fileinput import filename

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidgetItem, QAbstractItemView, QPushButton, \
    QLineEdit, QPlainTextEdit, QListWidget, QComboBox

from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

from utils.ui_loader import load_ui
from core import config_manager
from PIL import Image
from pathlib import Path
from core.worker import DownloadWorker

# TODO: create pyside for UE5 that allows the user to load all textures from a selected folder
# DONE
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
        self.cb_export: QComboBox = self.ui.cb_export

        self.line_texture_path: QLineEdit = self.ui.line_texture_path
        self.line_save_path: QLineEdit = self.ui.line_save_path

        self.list_texture_files: QListWidget = self.ui.list_texture_files
        self.text_texture_made: QPlainTextEdit = self.ui.text_texture_made

        # connect to function
        self.btn_browse_folder.clicked.connect(self.browse_folder_for_textures)
        self.btn_browse_save.clicked.connect(self.browse_folder_for_save)
        self.btn_apply.clicked.connect(self.apply_and_export)

        # Load saved path from config_manager

        config = config_manager.load_config()
        saved_save_path = config.get("last_save_path", "")
        if saved_save_path and os.path.isdir(saved_save_path):
            self.line_save_path.setText(saved_save_path)

        saved_texture_path = config.get("last_texture_path", "")
        if saved_texture_path and os.path.isdir(saved_texture_path):
            self.line_texture_path.setText(saved_texture_path)

    def browse_folder_for_textures(self):
        """
        after btn is clicked opens file dialog for user to select folder from which to take images from
        :return: None
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Texture Directory")

        # this is a folder picker
        if folder:
            self.line_texture_path.setText(folder)
            config_manager.save_config({"last_texture_path": folder})

            extensions = Image.registered_extensions().keys()
            src_path = Path(folder)
            for path in src_path.rglob("*"):
                if path.suffix.lower() in extensions:
                    item = QListWidgetItem(path.name)
                    item.setData(Qt.ItemDataRole.UserRole, path)
                    self.list_texture_files.addItem(item)

        self.check_if_apply_is_valid()

    def browse_folder_for_save(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        # this is a folder picker
        if folder:
            self.line_save_path.setText(folder)
            config_manager.save_config({"last_save_path": folder})

        self.check_if_apply_is_valid()

    def apply_and_export(self):
        if self.cb_export.currentIndex() == 0:
            print("RMA")
        elif self.cb_export.currentIndex() == 1:
            print("ORM")
        else:
            print("option doesn't exist yet")
            # I know I could just do else instead of elif, but this could be handy if you want-
            # to add more options later

    def check_if_apply_is_valid(self):
        valid_texture_dir = os.path.isdir(self.line_texture_path.text().strip())
        valid_save_dir = os.path.isdir(self.line_save_path.text().strip())
        self.btn_apply.setEnabled(valid_save_dir and valid_texture_dir)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TexturePackerApp()
    window.show()
    sys.exit(app.exec())
