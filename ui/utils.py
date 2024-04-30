import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2.QtWidgets import QWidget
import os


def maya_main_window():
    """Return the Maya main window widget as a Python object."""

    main_window_pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_pointer), QWidget)

ui_folder: str = os.path.dirname(__file__)
ICON_PATH = os.path.join(ui_folder, 'project_files/ncloth.svg')
STYLE_PATH = os.path.join(ui_folder,'project_files/style.css')
