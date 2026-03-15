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
# DONE
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

        # Load paths from config_manager

        save_config = config_manager.load_save_config()
        saved_save_path = save_config.get("last_save_path", "")
        if saved_save_path and os.path.isdir(saved_save_path):
            self.line_save_path.setText(saved_save_path)
        texture_config = config_manager.load_texture_config()
        saved_texture_path = texture_config.get("last_texture_path", "")
        if saved_texture_path and os.path.isdir(saved_texture_path):
            self.line_texture_path.setText(saved_texture_path)

        # if saved texture path exists already load in textures from folder
        if saved_texture_path is not None:
            self.open_texture_folder_at_start()
            # loads in what texture groups may look like
            for material in self.process_images(self.get_paths_from_list(), self.config_repack):
                self.text_texture_made.appendPlainText(f"{material}_{self.cb_export.currentText()}.png")

        # check if paths to save and texture both exist
        self.check_if_apply_is_valid()

    def browse_folder_for_textures(self):
        """
        after btn is clicked opens file dialog for user to select folder from which to take images from
        :return: None
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Texture Directory")

        # this is a folder picker
        if folder:
            self.line_texture_path.setText(folder)
            config_manager.save_config({"last_texture_path": folder}, 1)

            # checks for legit image extensions (eg .png)
            extensions = Image.registered_extensions().keys()
            src_path = Path(folder)
            for path in src_path.rglob("*"):
                if path.suffix.lower() in extensions:
                    # creates key
                    item = QListWidgetItem(path.name)
                    # sets value for key
                    item.setData(Qt.ItemDataRole.UserRole, path)
                    self.list_texture_files.addItem(item)

        # loads in texture names for preview
        for material in self.process_images(self.get_paths_from_list(), self.config_repack):
            self.text_texture_made.appendPlainText(f"{material}_{self.cb_export.currentText()}.png")

        # if button clicked check if paths to save and texture both exist
        self.check_if_apply_is_valid()

    def open_texture_folder_at_start(self):
        folder = self.line_texture_path.text()

        # this is a folder picker
        if folder:
            config_manager.save_config({"last_texture_path": folder}, 1)

            extensions = Image.registered_extensions().keys()
            src_path = Path(folder)
            for path in src_path.rglob("*"):
                if path.suffix.lower() in extensions:
                    item = QListWidgetItem(path.name)
                    item.setData(Qt.ItemDataRole.UserRole, path)
                    self.list_texture_files.addItem(item)

    def browse_folder_for_save(self):
        """
        after btn is clicked opens file dialog for user to select folder from to which it saves
        :return: None
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        # this is a folder picker
        if folder:
            self.line_save_path.setText(folder)
            config_manager.save_config({"last_save_path": folder}, 0)

        # if button clicked check if paths to save and texture both exist
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
        paths = self.get_paths_from_list()
        materials = self.process_images(paths, self.config_repack)
        self.prefix_based_packing(materials, self.config_repack)

    def get_paths_from_list(self) -> list[Path]:
        """
        get all paths from list_texture_files
        :return: list of Path
        """
        paths = []
        # get all paths stored in Qwidget
        for i in range(self.list_texture_files.count()):
            item = self.list_texture_files.item(i)
            temp_path = item.data(Qt.ItemDataRole.UserRole)

            if Path:
                paths.append(temp_path)
        return paths

    def process_images(self, list_image_path: list[Path], config: dict) -> dict:
        """
        process images rename and repack
        :param list_image_path: paths of image
        :param config: .json config file
        :return: dict of materials
        """
        materials = {}

        for img_path in list_image_path:
            prefix, name, suffix, ext = parse_name(img_path.name, config)

            # if key doesn't exist yet, make new
            if name not in materials:
                materials[name] = {
                    "maps": {}
                }

            # BC, A
            if suffix in config["suffix"]["Base"]["naming_conventions"]:
                materials[name]["base"] = img_path

            # packed
            elif suffix in config["suffix"]["packing"]["naming_conventions"].keys():
                materials[name]["packed"] = img_path

            # needs to be packed
            elif suffix in config["suffix"]["packing"]["separate_maps"].keys():
                map_type = config["suffix"]["packing"]["separate_maps"][suffix]
                materials["name"]["maps"][map_type][suffix] = img_path

            else:
                print(f"OTHER: File is something else: {img_path}")

        return materials

    def prefix_based_packing(self, materials: dict, config: dict):
        # all maps
        for material, data in materials.items():

            # skip if already packed
            if "packed" in data:
                continue

            maps = data["maps"]
            if not maps:
                continue

            ao = Image.open(maps["AO"]).convert("L")
            rough = Image.open(maps["R"]).convert("L")
            metal = Image.open(maps["M"]).convert("L")
            packed = Image

            if self.cb_export.currentText() == "ORM":
                packed = Image.merge("RGB", (ao, rough, metal))
            elif self.cb_export.currentText() == "RMA":
                packed = Image.merge("RGB", (rough, metal, ao))

            safe_folder = Path(self.line_save_path.text())

            save_path = safe_folder / f"{material}_{self.cb_export.currentText()}.png"
            packed.save(save_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TexturePackerApp()
    window.show()
    sys.exit(app.exec())
