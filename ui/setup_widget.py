from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout
)

from PySide2.QtCore import (
    Qt
)

from maya import cmds

from funcs import create_full_setup


class SetupWidget(QWidget):


    def __init__(self, parent=None):
        super(SetupWidget, self).__init__(parent)

        self.init_ui()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.collider_dict = {}

    def init_ui(self):
        size = (300, 400)
        self.setMinimumSize(*size)

    def create_widgets(self):
        self.setup_name_label = QLabel('Setup name')
        self.setup_name_lineedit = QLineEdit()

        self.simu_nmesh_button = QPushButton('Simu nMesh')
        self.simu_nmesh_lineedit = QLineEdit()

        self.himesh_button = QPushButton('High Mesh')
        self.himesh_lineedit = QLineEdit()

        self.add_collider_button = QPushButton('Add collider')

        self.collider_mesh_label = QLabel('Collider mesh')
        self.collider_name_label = QLabel('Collider name')

        self.create_setup_button = QPushButton('Create setup')

    def create_layout(self):
        self.main_layout = QVBoxLayout(self)

        self.grid_widget = QWidget()
        self.main_layout.addWidget(self.grid_widget)
        self.grid_layout = QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)
        self.grid_layout.addWidget(self.setup_name_label, 0, 0)
        self.grid_layout.addWidget(self.setup_name_lineedit, 0, 1)
        self.grid_layout.addWidget(self.simu_nmesh_button, 1, 0)
        self.grid_layout.addWidget(self.simu_nmesh_lineedit, 1, 1)
        self.grid_layout.addWidget(self.himesh_button, 2, 0)
        self.grid_layout.addWidget(self.himesh_lineedit, 2, 1)

        # Ajouter le label et le bouton dans un QHBoxLayout
        collider_button_layout = QHBoxLayout()
        collider_button_layout.addWidget(self.add_collider_button)
        self.main_layout.addLayout(collider_button_layout)

        self.collider_widget = QWidget()
        self.main_layout.addWidget(self.collider_widget)
        self.collider_layout = QGridLayout()
        self.collider_widget.setLayout(self.collider_layout)
        self.collider_layout.addWidget(self.collider_mesh_label, 0, 0, Qt.AlignTop)
        self.collider_layout.addWidget(self.collider_name_label, 0, 1, Qt.AlignTop)

        self.main_layout.addWidget(self.create_setup_button)


    def create_connections(self):
        self.simu_nmesh_button.clicked.connect(self.update_lineedit)
        self.himesh_button.clicked.connect(self.update_lineedit)
        self.create_setup_button.clicked.connect(self.create_setup)
        self.add_collider_button.clicked.connect(self.add_collider)


    def add_collider(self):
        collider_mesh_lineedit = QLineEdit()
        collider_name_lineedit = QLineEdit()

        for i in range(1, 10):
            if self.collider_layout.itemAtPosition(i, 0):
                continue

            self.collider_layout.addWidget(collider_mesh_lineedit, i, 0, Qt.AlignTop)
            self.collider_layout.addWidget(collider_name_lineedit, i, 1, Qt.AlignTop)

        self.collider_dict[collider_mesh_lineedit] = collider_name_lineedit


    def update_lineedit(self):
        button_label_dict = {
            self.simu_nmesh_button: self.simu_nmesh_lineedit,
            self.himesh_button: self.himesh_lineedit
        }

        lineedit: QLineEdit = button_label_dict[self.sender()]

        selection = cmds.ls(selection=True)
        if not selection:
            return

        node_name: str = selection[0]
        lineedit.setText(node_name)


    def create_setup(self):
        setup_prefix = self.setup_name_lineedit.text()
        low_mesh = self.simu_nmesh_lineedit.text()
        high_mesh = self.himesh_lineedit.text()

        collider_dict = {}
        for key, value in self.collider_dict.items():
            collider_dict[key.text()] = value.text()

        create_full_setup(setup_prefix, low_mesh, high_mesh, colliders=collider_dict)
