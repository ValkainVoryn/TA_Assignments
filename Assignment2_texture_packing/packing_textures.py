import sys
import os
import re
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
from repack import load_json, parse_name

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
        self.config_repack = load_json("config_lab.json")

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

        if saved_texture_path is not None:
            self.open_texture_folder_at_start()

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

    def open_texture_folder_at_start(self):
        folder = self.line_texture_path.text()

        # this is a folder picker
        if folder:
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
        """
        after btn is clicked opens file dialog for user to select folder from to which it saves
        :return: None
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        # this is a folder picker
        if folder:
            self.line_save_path.setText(folder)
            config_manager.save_config({"last_save_path": folder})

        self.check_if_apply_is_valid()

    def check_if_apply_is_valid(self):
        """
        checks if both texture folder and save folder have been selected and sets btn_apply to enabled if true
        :return: None
        """
        valid_texture_dir = os.path.isdir(self.line_texture_path.text().strip())
        valid_save_dir = os.path.isdir(self.line_save_path.text().strip())
        self.btn_apply.setEnabled(valid_save_dir and valid_texture_dir)

    def apply_and_export(self):
        paths = []
        for i in range(self.list_texture_files.count()):
            item = self.list_texture_files.item(i)
            temp_path = item.data(Qt.ItemDataRole.UserRole)
            paths.append(temp_path)
        if self.cb_export.currentIndex() == 0:
            print("RMA")
            self.process_images(paths, self.config_repack)
        elif self.cb_export.currentIndex() == 1:
            print("ORM")
        else:
            print("option doesn't exist yet")
            # I know I could just do else instead of elif, but this could be handy if you want-
            # to add more options later

    def process_images(self, list_image_path: list[Path], config: dict) -> None:
        """
        process images rename and repack
        :param list_image_path: paths of image
        :param config: .json config file
        :return: None
        """
        for img_path in list_image_path:
            prefix, name, suffix, ext = parse_name(img_path.name, config)

            if suffix in config["suffix"]["Base"]["naming_conventions"]:
                print(f"File is in color: {img_path}")
                pass
            elif suffix in config["suffix"]["packing"]["naming_conventions"].keys():
                # print(f"File is a channel/grey packed image {img_path}")
                pass
            elif suffix in config["suffix"]["packing"]["separate_maps"].keys():
                # print(f"Files is an single channel image: {img_path}")
                pass
            else:
                # print(f"OTHER: File is something else: {img_path}")
                pass

    def prefix_based_packing(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TexturePackerApp()
    window.show()
    sys.exit(app.exec())
