from PySide2.QtWidgets import (
    QDialog,
    QPushButton,
    QVBoxLayout,
    QTabWidget,
    QWidget,
    QHBoxLayout
)

from PySide2.QtGui import (
    QIcon
)

def reload_modules():
    from . import preroll_widget, setup_widget, utils
    from importlib import reload
    reload(preroll_widget)
    reload(setup_widget)
    reload(utils)

reload_modules()

from .preroll_widget import PrerollWidget
from .setup_widget import SetupWidget
from .utils import maya_main_window, ICON_PATH


class ClothUi(QDialog):


    def __init__(self, parent = maya_main_window()):
        super(ClothUi, self).__init__(parent)

        self.init_ui()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.show()

    def init_ui(self):
        self.setWindowTitle('Cloth Setup')
        self.setWindowIcon(QIcon(ICON_PATH))


    def create_widgets(self):
        self.add_setup_btn = QPushButton('Add Setup')
        self.pre_roll_widget = PrerollWidget(self)


    def create_layout(self):
        self.main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.cloth_widget = QWidget()
        self.preroll_widget = QWidget()

        self.cloth_layout = QVBoxLayout(self.cloth_widget)
        self.preroll_layout = QVBoxLayout(self.preroll_widget)

        self.tab_widget.addTab(self.cloth_widget, 'Cloth')
        self.tab_widget.addTab(self.preroll_widget, 'Preroll')

        # cloth layout
        self.cloth_layout.addWidget(self.add_setup_btn)
        self.setup_widget = QWidget()
        self.setup_layout = QHBoxLayout(self.setup_widget)
        self.cloth_layout.addWidget(self.setup_widget)

        # preroll layout
        self.preroll_layout.addWidget(self.pre_roll_widget)


    def create_connections(self):
        self.add_setup_btn.clicked.connect(self.add_setup_widget)


    def add_setup_widget(self):
        setup_widget = SetupWidget(self)
        self.setup_layout.addWidget(setup_widget)
        setup_widget.show()
