import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To Do")
        self.resize(350,500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_label = QLabel("Today's Tasks")

        self.scroll_area = QScrollArea()

        self.add_task = QWidget()
        self.add_button = QPushButton("Add task...")
        self.mic_button = QPushButton("Microphone")
        
        self.bottom_bar_layout = QHBoxLayout()
        self.add_task.setLayout(self.bottom_bar_layout)
        self.bottom_bar_layout.addWidget(self.add_button)
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

