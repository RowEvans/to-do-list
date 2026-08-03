import sys
import os
import sqlite3
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *

DB_FILE = os.path.join(os.path.dirname(__file__), "tasks.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        done INTEGER NOT NULL DEFAULT 0,
        position INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

class TaskWidget(QWidget):

    text_changed = Signal(int, str)
    done_changed = Signal(int, bool)
    delete_requested = Signal(int)

    def __init__(self, text, done=False, task_id=None):
        super().__init__()

        font_path = os.path.join(os.path.dirname(__file__), "assets/fonts/Roboto-VariableFont_wdth,wght.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        families = QFontDatabase.applicationFontFamilies(font_id)
        self.task_font = QFont(families[0], 10) if families else QFont()

        self.task_id = task_id
        self.button = QCheckBox()
        self.button.stateChanged.connect(self.cross_out)
        self.label = QLabel(text)
        self.label.setFont(self.task_font)
        self.edit = QLineEdit(text)
        self.edit.setFont(self.task_font)
        self.edit.hide()
        self.delete_button = QPushButton("x")
        self.delete_button.setFixedSize(20, 20)
        self.delete_button.setStyleSheet("border: none; background: transparent;")
        self.delete_button.clicked.connect(lambda: self.delete_requested.emit(self.task_id))

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
        layout.addWidget(self.delete_button)
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
            self.text_changed.emit(self.task_id, new_text)
        self.edit.hide()
        self.label.show()

    def cross_out(self, state):
        checked = self.button.isChecked()
        font = self.label.font()
        font.setStrikeOut(checked)
        self.label.setFont(font)
        self.done_changed.emit(self.task_id, checked)


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
        self.resize(350,500)
        self.move(QPoint(1920-375, 25))
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnBottomHint)

        init_db()
        self.conn = sqlite3.connect(DB_FILE)
        self.init_tray()

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
        self.load_tasks()
        
        self.add_task_row = AddTaskWidget()
        self.add_task_row.task_added.connect(self.add_new_task)
        self.task_layout.addWidget(self.add_task_row)

        self.task_layout.addStretch()

        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)
        self.layout.addWidget(self.top_widget)
        self.layout.addWidget(self.scroll_area)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "assets", "icons", "close.png")))
        self.tray_icon.setToolTip("To Do")

        tray_menu = QMenu()

        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()
            self.activateWindow()
    
    def quit_app(self):
        self.conn.close()
        QApplication.quit()
    

    def load_tasks(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, text, done FROM tasks ORDER BY position ASC")
        rows = cur.fetchall()

        if not rows:
            self.insert_task_db("Finish Homework", done=False)
            self.insert_task_db("Finish EE", done=False)
            cur.execute("SELECT id, text, done FROM tasks ORDER BY position ASC")
            rows = cur.fetchall()

        for task_id, text, done in rows:
            widget = TaskWidget(text, bool(done), task_id=task_id)
            widget.text_changed.connect(self.update_task_text)
            widget.done_changed.connect(self.update_task_done)
            widget.delete_requested.connect(self.delete_task)
            self.task_layout.addWidget(widget)

    def insert_task_db(self, text, done=False):
        cur = self.conn.cursor()
        cur.execute("SELECT COALESCE(MAX(position), -1) + 1 FROM tasks")
        next_pos = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO tasks (text, done, position) VALUES (?, ?, ?)",
            (text, int(done), next_pos)
        )
        self.conn.commit()
        return cur.lastrowid

    def add_new_task(self, text):
        cur = self.conn.cursor()
        cur.execute("UPDATE tasks SET position = position + 1")
        cur.execute(
            "INSERT INTO tasks (text, done, position) VALUES (?, 0, 0)",
            (text,)
        )
        self.conn.commit()

        task_id = cur.lastrowid
        widget = TaskWidget(text, done=False, task_id=task_id)
        widget.text_changed.connect(self.update_task_text)
        widget.done_changed.connect(self.update_task_done)
        widget.delete_requested.connect(self.delete_task)
        self.task_layout.insertWidget(0, widget)

    def update_task_text(self, task_id, text):
        cur = self.conn.cursor()
        cur.execute("UPDATE tasks SET text = ? WHERE id = ?", (text, task_id))
        self.conn.commit()

    def update_task_done(self, task_id, done):
        cur = self.conn.cursor()
        cur.execute("UPDATE tasks SET done = ? WHERE id = ?", (int(done), task_id))
        self.conn.commit()

    def delete_task(self, task_id):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

        for i in range(self.task_layout.count()):
            item = self.task_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, TaskWidget) and widget.task_id == task_id:
                widget.deleteLater()
                break


    def closeEvent(self, event):
        event.ignore()
        self.hide()

    #def add_new_task(self, text):
    #   self.task_layout.insertWidget(0, TaskWidget(text))

    def close_window(self, _):
        self.hide()



if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MainWindow()

    window.show()

    sys.exit(app.exec())

