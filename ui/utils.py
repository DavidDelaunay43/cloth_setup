import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2.QtWidgets import QWidget


def maya_main_window():
    """Return the Maya main window widget as a Python object."""

    main_window_pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_pointer), QWidget)


ICON_PATH = 'C:/Users/d.delaunay/Documents/maya_dev/scripts/sun/mayatools/cloth/ncloth.svg'
STYLE_PATH = 'C:/Users/d.delaunay/Documents/maya_dev/scripts/sun/mayatools/cloth/style.css'
