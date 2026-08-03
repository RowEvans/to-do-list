import sys
import os
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *

class TaskWidget(QWidget):
    def __init__(self, text):
        super().__init__()

        font_path = os.path.join(os.path.dirname(__file__), "assets/fonts/Roboto-VariableFont_wdth,wght.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        families = QFontDatabase.applicationFontFamilies(font_id)
        self.task_font = QFont(families[0], 10) if families else QFont()

        self.button = QCheckBox()
        self.button.stateChanged.connect(self.cross_out)
        self.label = QLabel(text)
        self.label.setFont(self.task_font)
        self.edit = QLineEdit(text)
        self.edit.setFont(self.task_font)
        self.edit.hide()

        self.label.setStyleSheet("background: transparent; border: none")
        self.label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.edit.setStyleSheet("background: transparent; border: none")

        self.label.mousePressEvent = self.edit_label

        layout = QHBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10,0,0,0)
        layout.addWidget(self.button)
        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        layout.addStretch()
        self.setLayout(layout)

        self.edit.editingFinished.connect(self.finish_edit)

    def edit_label(self, event):
        self.label.hide()
        self.edit.setText("")
        self.edit.show()
        self.edit.setFocus()
        self.edit.selectAll()

    def finish_edit(self):
        new_text = self.edit.text().strip()
        if new_text:
            self.label.setText(new_text)
        self.edit.hide()
        self.label.show()

    def cross_out(self, state):
        font = self.label.font()
        font.setStrikeOut(state == Qt.Checked.value)
        self.label.setFont(font)


class AddTaskWidget(QWidget):

    task_added = Signal(str)

    def __init__(self):
        super().__init__()

        font_path = os.path.join(os.path.dirname(__file__), "assets/fonts/Roboto-VariableFont_wdth,wght.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        families = QFontDatabase.applicationFontFamilies(font_id)
        self.task_font = QFont(families[0], 10) if families else QFont()

        self.label = QLabel("Add task... ")
        self.edit = QLineEdit()
        self.edit.hide()

        self.label.setStyleSheet("background: transparent; border: none")
        self.label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.label.setFont(self.task_font)

        self.edit.setStyleSheet("background: transparent; border: none")
        self.edit.setFont(self.task_font)

        self.label.mousePressEvent = self.start_editing

        layout = QHBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10,0,0,0)
        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        layout.addStretch()
        self.setLayout(layout)

        self.edit.editingFinished.connect(self.finish_edit)

    def start_editing(self, _):
        self.label.hide()
        self.edit.setText("")
        self.edit.show()
        self.edit.setFocus()

    def finish_edit(self):
        text = self.edit.text().strip()
        self.edit.hide()
        self.label.show()

        if text:
            self.task_added.emit(text)

        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To Do")
        self.resize(350,500)

        self.setWindowFlags(Qt.FramelessWindowHint)

        font_path = os.path.join(os.path.dirname(__file__), "assets/fonts/ArchivoBlack-Regular.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        families = QFontDatabase.applicationFontFamilies(font_id)
        self.title_font = QFont(families[0], 12) if families else QFont()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.top_widget = QWidget()
        self.top_layout = QHBoxLayout()
        self.top_widget.setLayout(self.top_layout)
        self.main_label = QLabel("Today's Tasks")
        self.main_label.setFont(self.title_font)
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_label.setStyleSheet("font-size: 18px; font-weight: bold; border: 2px")
        self.top_layout.addWidget(self.main_label)
        self.top_layout.addStretch()
        self.exit_button = QPushButton()
        self.exit_button.setStyleSheet("background: transparent; border: none")
        self.exit_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "assets", "icons", "close.png")))
        self.exit_button.clicked.connect(self.close_window)
        self.exit_button.setIconSize(QSize(10, 10))
        self.top_layout.addWidget(self.exit_button)
        

        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_area.setStyleSheet("background: transparent; border: none")
        self.scroll_widget.setStyleSheet("background: transparent; border: none")
        self.task_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.task_layout)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.task_layout.addWidget(TaskWidget("Finish Homework"))
        self.task_layout.addWidget(TaskWidget("Finish EE"))
        
        self.add_task_row = AddTaskWidget()
        self.add_task_row.task_added.connect(self.add_new_task)
        self.task_layout.addWidget(self.add_task_row)

        self.task_layout.addStretch()

        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)
        self.layout.addWidget(self.top_widget)
        self.layout.addWidget(self.scroll_area)

    def add_new_task(self, text):
        self.task_layout.insertWidget(0, TaskWidget(text))

    def close_window(self, _):
        sys.exit()



if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()

    sys.exit(app.exec())

