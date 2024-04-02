from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QGridLayout
)

from maya import cmds

from ..funcs import set_preroll


class PrerollWidget(QWidget):
    

    def __init__(self, parent=None):
        super(PrerollWidget, self).__init__(parent)

        self.init_ui()
        self.create_widgets()
        self.create_layout()
        self.create_connections()


    def init_ui(self):
        size = (300, 400)
        self.setMinimumSize(*size)


    def create_widgets(self):
        start_frame: float = cmds.playbackOptions(query = True, minTime = True)
        self.start_frame_label = QLabel(f'Start frame')
        self.start_frame_lineedit = QLineEdit(f'{start_frame}')

        self.start_pose_offset_label = QLabel('Start pose offset')
        self.start_pose_offset_lineedit = QLineEdit(f'{-5.0}')
        
        self.inter_pose_offset_label = QLabel('Inter pose offset')
        self.inter_pose_offset_lineedit = QLineEdit(f'{-25.0}')
        
        self.bind_pose_offset_label = QLabel('Bind pose offset')
        self.bind_pose_offset_lineedit = QLineEdit(f'{-30.0}')

        self.info_label = QLabel('Select controlers')
        self.run_button = QPushButton('Preroll')


    def create_layout(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)
        self.main_layout.addWidget(self.grid_widget)

        self.grid_layout.addWidget(self.start_frame_label, 0, 0)
        self.grid_layout.addWidget(self.start_frame_lineedit, 0, 1)
        self.grid_layout.addWidget(self.start_pose_offset_label, 1, 0)
        self.grid_layout.addWidget(self.start_pose_offset_lineedit, 1, 1)
        self.grid_layout.addWidget(self.inter_pose_offset_label, 2, 0)
        self.grid_layout.addWidget(self.inter_pose_offset_lineedit, 2, 1)
        self.grid_layout.addWidget(self.bind_pose_offset_label, 3, 0)
        self.grid_layout.addWidget(self.bind_pose_offset_lineedit, 3, 1)

        self.main_layout.addWidget(self.info_label)
        self.main_layout.addWidget(self.run_button)


    def create_connections(self):
        self.run_button.clicked.connect(self.preroll)


    def preroll(self):
        start_frame = float(self.start_frame_lineedit.text())
        start_pose_offset = float(self.start_pose_offset_lineedit.text())
        inter_pose_offset = float(self.inter_pose_offset_lineedit.text())
        bind_pose_offset = float(self.bind_pose_offset_lineedit.text())

        preroll_values = [start_frame, start_pose_offset, inter_pose_offset, bind_pose_offset]

        controlers: list = cmds.ls(selection = True)
        set_preroll(controlers, preroll_values)
