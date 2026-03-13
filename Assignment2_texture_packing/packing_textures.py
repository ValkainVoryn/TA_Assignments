from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidgetItem, QAbstractItemView, QPushButton, \
    QLineEdit, QPlainTextEdit, QListWidget

# TODO: create pyside for UE5 that allows the user to load all textures from a selected folder
# TODO: have dropdown menu that suggests presets based off naming conventions (eg. _AO)
# TODO: "no match found" if no conventions can be found to pack with (allow user to do manually)
# TODO: default packing standard (eg. _RMA or _ORM)


class TexturePacker(QMainWindow):
    def __init__(self):
        super().__init__()
