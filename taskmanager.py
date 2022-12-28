import sys
import time
import speech_recognition as sr
from PyQt5 import QtGui
from PyQt5.QtSql import QSqlDatabase,QSqlQuery
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QHBoxLayout, QListWidget, QLineEdit, QTextEdit,
                             QLabel, QListWidgetItem, QMessageBox,QSystemTrayIcon,QStyle,QAction, qApp, QMenu)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.tasks_list = QListWidget(self)
        self.button_all_tasks = QPushButton("Все задачи", self)
        self.button_active_tasks = QPushButton("Активные задачи", self)
        self.button_done_tasks = QPushButton("Выполненные задачи", self)
        self.task_name = QLineEdit(self)
        self.task_description = QTextEdit(self)
        self.button_add_task = QPushButton("Добавить задачу", self)
        self.button_edit_task = QPushButton("Изменить задачу", self)
        self.button_delete_task = QPushButton("Удалить задачу", self)
        self.categories_list = QListWidget(self)
        self.category_name = QLineEdit(self)
        self.button_add_category = QPushButton("Добавить категорию", self)
        self.button_edit_category = QPushButton("Изменить категорию", self)
        self.button_delete_category = QPushButton("Удалить категорию", self)
        self.button_speech = QPushButton("голосовой ввод", self)

        # ...
        self.init_ui()
        self.create_db()
        self.load_categories()
        self.load_tasks()
        self.tasks_list.itemClicked.connect(self.task_detail)
        self.categories_list.itemClicked.connect(self.category_detail)
        self.button_add_task.clicked.connect(self.add_tasks)
        self.button_add_category.clicked.connect(self.add_category)
        self.button_delete_task.clicked.connect(self.delete_task)
        self.button_delete_category.clicked.connect(self.delete_category)
        self.button_edit_task.clicked.connect(self.edit_task)
        self.button_edit_category.clicked.connect(self.edit_category)
        self.button_active_tasks.clicked.connect(self.load_undone_tasks)
        self.button_done_tasks.clicked.connect(self.load_done_tasks)
        self.tasks_list.itemDoubleClicked.connect(self.update_status)
        self.button_speech.clicked.connect(self.speech_input)
        self.button_all_tasks.clicked.connect(self.load_tasks)
    def init_ui(self):
        self.setWindowIcon(QtGui.QIcon('icons8-форма-48.png'))

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon("icons8-форма-48.png"))
        show_action = QAction("show", self)
        quit_action = QAction("exit", self)
        hide_action = QAction("hide", self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(qApp.quit)
        hide_action.triggered.connect(self.hide)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setVisible(True)
        self.tray_icon.show()

        self.setStyleSheet("background-color: rgb(222, 184, 135);")
        
        self.task_description.setStyleSheet("background-color: #FFF8DC;")
        self.task_name.setStyleSheet("background-color: #FFF8DC;")
        self.tasks_list.setStyleSheet("background-color: #FFF8DC;")
        self.categories_list.setStyleSheet("background-color: #FFF8DC;")
        self.category_name.setStyleSheet("background-color: #FFF8DC;")

        self.button_speech.setStyleSheet("background-color: #BDB76B;")
        self.button_add_task.setStyleSheet("background-color: #BDB76B;")
        self.button_add_category.setStyleSheet("background-color: #BDB76B;")
        self.button_delete_task.setStyleSheet("background-color: #BDB76B;")
        self.button_delete_category.setStyleSheet("background-color: #BDB76B;")
        self.button_edit_task.setStyleSheet("background-color: #BDB76B;")
        self.button_edit_category.setStyleSheet("background-color: #BDB76B;")
        self.button_active_tasks.setStyleSheet("background-color: #BDB76B;")
        self.button_done_tasks.setStyleSheet("background-color: #BDB76B;")
        self.button_speech.setStyleSheet("background-color: #BDB76B;")
        self.button_all_tasks.setStyleSheet("background-color: #BDB76B;")

        self.resize(400, 500)
        self.setWindowTitle("Список задач")
        vbox = QVBoxLayout()
        self.name1 = QLabel('Список задач:', self)
        vbox.addWidget(self.name1)
        vbox.addWidget(self.tasks_list)
        hbox = QHBoxLayout()
        hbox.addWidget(self.button_all_tasks)
        hbox.addWidget(self.button_active_tasks)
        hbox.addWidget(self.button_done_tasks)
        vbox.addLayout(hbox)
        hbox = QHBoxLayout()
        self.name2 = QLabel('Название задачи:', self)
        hbox.addWidget(self.name2)
        hbox.addWidget(self.task_name)
        vbox.addLayout(hbox)
        hbox = QHBoxLayout()
        self.name3 = QLabel('Описание задачи:', self)
        hbox.addWidget(self.name3)
        hbox.addWidget(self.task_description)
        vbox.addLayout(hbox)
        hbox = QHBoxLayout()
        self.name4 = QLabel('Категория:', self)
        hbox.addWidget(self.name4)
        hbox.addWidget(self.category_name)
        vbox.addLayout(hbox)
        self.name5 = QLabel('Список категорий:', self)
        vbox.addWidget(self.name5)
        vbox.addWidget(self.categories_list)
        hbox = QHBoxLayout()
        hbox.addWidget(self.button_add_task)
        hbox.addWidget(self.button_edit_task)
        hbox.addWidget(self.button_delete_task)
        vbox.addLayout(hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(self.button_add_category)
        hbox.addWidget(self.button_edit_category)
        hbox.addWidget(self.button_delete_category)
        vbox.addLayout(hbox)
        vbox.addWidget(self.button_speech)
        self.setLayout(vbox)


    def create_db(self):
        query = QSqlQuery()
        query.exec(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                name VARCHAR(64) NOT NULL
            )
            """
        )

        query.exec(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                name VARCHAR(255) NOT NULL,
                description VARCHAR(255) NOT NULL,
                active BOOL NOT NULL DEFAULT TRUE,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
            """
        )

    def load_categories(self):
        query = QSqlQuery()
        query.exec(
            """SELECT * 
            FROM categories;""")
        self.categories = []
        count = query.record().count()
        while query.next():
            temp = []
            for i in range(count):
                temp.append(query.value(i))
            self.categories.append(temp)
            print(self.categories)
            self.categories_list.clear()
            for category in self.categories:
                self.categories_list.addItem(QListWidgetItem(category[1]))

    def load_tasks(self):
        query = QSqlQuery()
        query.exec(
            """SELECT *
            FROM tasks
            LEFT JOIN categories
            ON category_id=categories.id;"""
        )
        self.tasks =[]
        count = query.record().count()
        print(count)
        while query.next():
            temp = []
            for i in range(count):
                temp.append(query.value(i))
            self.tasks.append(temp)
        print(self.tasks)
        self.tasks_list.clear()
        for task in self.tasks:
                self.tasks_list.addItem(QListWidgetItem(task[1]))

    def load_done_tasks(self):
        query = QSqlQuery()
        query.exec(
            """SELECT *
            FROM tasks
            LEFT JOIN categories
            ON category_id=categories.id
            WHERE active = FALSE;"""
        )
        self.tasks =[]
        count = query.record().count()
        print(count)
        while query.next():
            temp = []
            for i in range(count):
                temp.append(query.value(i))
            self.tasks.append(temp)
        print(self.tasks)
        self.tasks_list.clear()
        for task in self.tasks:
                self.tasks_list.addItem(QListWidgetItem(task[1]))

    def load_undone_tasks(self):
        query = QSqlQuery()
        query.exec(
            """SELECT *
            FROM tasks
            LEFT JOIN categories
            ON category_id=categories.id
            WHERE active = TRUE;"""
        )
        self.tasks =[]
        count = query.record().count()
        print(count)
        while query.next():
            temp = []
            for i in range(count):
                temp.append(query.value(i))
            self.tasks.append(temp)
        print(self.tasks)
        self.tasks_list.clear()
        for task in self.tasks:
                self.tasks_list.addItem(QListWidgetItem(task[1]))




    def add_tasks(self):
        name = self.task_name.text()
        description = self.task_description.toPlainText()
        row = self.categories_list.currentRow()
        category_id = self.categories[row][0]
        query = QSqlQuery()
        query.exec(
            f"""INSERT INTO tasks (name, description, category_id) 
            VALUES ('{name}', '{description}', '{category_id}');"""
        )
        self.load_tasks()


    def add_category(self):
        name = self.category_name.text()
        query = QSqlQuery()
        query.exec(
            f"""INSERT INTO categories (name) 
            VALUES ('{name}');"""
        )
        self.load_categories()


    def task_detail(self):
        row = self.tasks_list.currentRow()
        self.task_name.setText(self.tasks[row][1])
        self.task_description.setText(self.tasks[row][2])
        self.category_name.setText(self.tasks[row][6])
        print(self.tasks[row])

    def category_detail(self):
        row = self.categories_list.currentRow()
        self.category_name.setText(self.categories[row][1])
    
    def delete_category(self):
        row = self.categories_list.currentRow()
        category_id = self.categories[row][0]
        query = QSqlQuery()
        query.exec(
            f"""DELETE FROM categories
            WHERE id={category_id};"""
        )
        self.load_categories()

    def delete_task(self):
        row = self.tasks_list.currentRow()
        task_id = self.tasks[row][0]
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Warning)
        message_box.setText(f"Вы точно хотите удалить задачу: {self.tasks[row][1]}?")
        message_box.setWindowTitle("Удалить категорию?")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.show()
        result = message_box.exec()
        if result == QMessageBox.Yes:
            query = QSqlQuery()
            query.exec(
                f"""DELETE FROM tasks 
                WHERE id={task_id};"""
            )
            self.load_tasks()

    def update_status(self):
        row = self.tasks_list.currentRow()
        task_id = self.tasks[row][0]
        if self.tasks[row][3] == 1:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Warning)
            message_box.setText(f"Вы точно хотите сделать задачу выполненной: {self.tasks[row][1]}?")
            message_box.setWindowTitle("Удалить категорию?")
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.show()
            result = message_box.exec()
            if result == QMessageBox.Yes:
                query = QSqlQuery()
                query.exec(
                    f"""UPDATE tasks
                    SET active = FALSE
                    WHERE id={task_id};"""
                )
        if self.tasks[row][3] == 0:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Warning)
            message_box.setText(f"Вы точно хотите сделать задачу активной: {self.tasks[row][1]}?")
            message_box.setWindowTitle("Удалить категорию?")
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.show()
            result = message_box.exec()
            if result == QMessageBox.Yes:
                query = QSqlQuery()
                query.exec(
                    f"""UPDATE tasks
                    SET active = TRUE
                    WHERE id={task_id};"""
                )

    def edit_task(self):
        row = self.tasks_list.currentRow()
        task_id = self.tasks[row][0]
        name = self.task_name.text()
        description = self.task_description.toPlainText()
        cat_row = self.categories_list.currentRow()
        category_id = self.categories[cat_row][0]
        query = QSqlQuery()
        query.exec(
            f"""UPDATE tasks 
            SET name='{name}', description='{description}', category_id='{category_id}'
            WHERE id={task_id};"""
        )
        self.load_tasks()

    def edit_category(self):
        row = self.tasks_list.currentRow()
        category_id = self.categories[row][0]
        name = self.category_name.text()
        query = QSqlQuery()
        query.exec(
            f"""UPDATE categories 
            SET name='{name}',
            WHERE id={category_id};"""
        )
        self.load_tasks()


    def speech_input(self):
        r = sr.Recognizer()        
        with sr.Microphone(device_index=1) as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)        
        try:
            query = r.recognize_google(audio, language="ru-RU")
        except sr.UnknownValueError:
            pass
        else:
            self.task_description.setText(self.task_description.toPlainText() + " " + str(query).lower())


if __name__ == '__main__':
    con = QSqlDatabase.addDatabase("QSQLITE")
    con.setDatabaseName("tasks.sqlite")

    if not con.open():
        print("Database Error: %s" % con.lastError().databaseText())
        sys.exit(1)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


