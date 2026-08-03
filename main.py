import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *

class TaskWidget(QWidget):
    def __init__(self, text):
        super().__init__()

        self.button = QCheckBox()
        #self.button.stateChanged.connect()
        self.label = QLabel(text)

        layout = QHBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10,0,0,0)
        layout.addWidget(self.button)
        layout.addWidget(self.label)
        layout.addStretch()
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To Do")
        self.resize(350,500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_label = QLabel("Today's Tasks")

        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.task_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.task_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.task_layout.addWidget(TaskWidget("Finish Homework"))
        self.task_layout.addWidget(TaskWidget("Finish EE"))
        self.task_layout.addStretch()
        

        self.add_task = QWidget()
        self.add_button = QPushButton("Add task...")
        self.mic_button = QPushButton("Microphone")
        
        self.bottom_bar_layout = QHBoxLayout()
        self.add_task.setLayout(self.bottom_bar_layout)
        self.bottom_bar_layout.addWidget(self.add_button)
        self.bottom_bar_layout.addStretch()
        self.bottom_bar_layout.addWidget(self.mic_button)


        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)
        self.layout.addWidget(self.main_label)
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.add_task)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()

    sys.exit(app.exec())

