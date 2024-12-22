import psycopg2
from PyQt5 import QtWidgets, QtCore
import sys

DB_NAME = "online_school"
DB_USER = "user_name"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"

class DatabaseApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.connection = None
        self.cursor = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Database Manager")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)

        self.create_db_button = QtWidgets.QPushButton("Создать базу данных")
        self.delete_db_button = QtWidgets.QPushButton("Удалить базу данных")
        self.connect_db_button = QtWidgets.QPushButton("Подключиться к базе данных")

        self.create_db_button.setFixedWidth(200)
        self.delete_db_button.setFixedWidth(200)
        self.connect_db_button.setFixedWidth(200)

        self.layout.addWidget(self.create_db_button)
        self.layout.addWidget(self.delete_db_button)
        self.layout.addWidget(self.connect_db_button)

        self.create_db_button.clicked.connect(self.create_database)
        self.delete_db_button.clicked.connect(self.delete_database)
        self.connect_db_button.clicked.connect(self.go_to_database)

    def connect_to_server(self):
        try:
            if self.connection:
                self.connection.close()
            self.connection = psycopg2.connect(
                dbname="postgres",
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST
            )
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
        except Exception as e:
            self.show_error(f"Ошибка при подключении к серверу: {e}")

    def load_procedures(self):
        try:
            self.cursor.execute("SELECT current_database();")
            current_db = self.cursor.fetchone()[0]
            print(f"Процедуры загружаются в базу данных: {current_db}")

            with open('procedures.sql', 'r', encoding='utf-8') as file:
                sql = file.read()
                self.cursor.execute(sql)
                print("Процедуры успешно загружены!")
        except Exception as e:
            self.show_error(f"Ошибка при загрузке хранимых процедур: {e}")

    def create_database(self):
        self.connect_to_server()
        if not self.cursor:
            return
        try:
            # Создание базы данных выполняется напрямую в Python, а не через хранимую процедуру
            self.cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
            self.cursor.execute(f"CREATE DATABASE {DB_NAME};")
            self.connect_to_database()
            self.create_tables()
            self.load_procedures()
            self.show_message("Успех", f"База данных {DB_NAME} успешно создана.")
        except Exception as e:
            self.show_error(f"Ошибка при создании базы данных: {e}")

    def create_tables(self):
        try:
            with open('setup_db.sql') as f:
                sql_commands = f.read()
            self.cursor.execute(sql_commands)
            print('Таблицы успешно созданы!')

        except Exception as e:
            print('Возникла ошибка при создании таблиц:', e)

    def delete_database(self):
        self.connect_to_server()
        if not self.cursor:
            return
        try:
            # Удаление базы данных выполняется напрямую в Python, а не через хранимую процедуру
            self.cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{DB_NAME}' AND pid <> pg_backend_pid();
            """)
            self.cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
            self.show_message("Успех", f"База данных {DB_NAME} успешно удалена.")
        except Exception as e:
            self.show_error(f"Ошибка при удалении базы данных: {e}")

    def connect_to_database(self):
        try:
            if self.connection:
                self.connection.close()
            self.connection = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST
            )
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            # Не загружаем процедуры и таблицы, если они уже есть
        except Exception as e:
            self.show_error(f"Ошибка при подключении к базе данных: {e}")

    def go_to_database(self):
        try:
            if self.connection:
                self.connection.close()
            self.connection = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST
            )
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            self.show_tables_window()
        except Exception as e:
            self.show_error(f"Ошибка при подключении к базе данных: {e}")

    def show_tables_window(self):
        self.tables_window = TablesWindow(self.connection)
        self.tables_window.show()
        self.close()

    def show_message(self, title, message):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def show_error(self, message):
        error_box = QtWidgets.QMessageBox(self)
        error_box.setIcon(QtWidgets.QMessageBox.Critical)
        error_box.setWindowTitle("Ошибка")
        error_box.setText(message)
        error_box.exec_()

class TablesWindow(QtWidgets.QMainWindow):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.cursor = connection.cursor()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Управление таблицами")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.tables_list = QtWidgets.QListWidget()
        self.layout.addWidget(self.tables_list)

        self.view_table_button = QtWidgets.QPushButton("Просмотреть содержимое")
        self.clear_table_button = QtWidgets.QPushButton("Очистить таблицу")
        self.clear_all_tables_button = QtWidgets.QPushButton("Очистить все таблицы")

        self.layout.addWidget(self.view_table_button)
        self.layout.addWidget(self.clear_table_button)
        self.layout.addWidget(self.clear_all_tables_button)

        self.view_table_button.clicked.connect(self.view_table_content)
        self.clear_table_button.clicked.connect(self.clear_table)
        self.clear_all_tables_button.clicked.connect(self.clear_all_tables)

        self.load_tables()  # Загружаем таблицы сразу при старте

    def load_tables(self):
        try:
            self.tables_list.clear()
            self.cursor.execute("SELECT * FROM load_tables_proc();")
            tables = self.cursor.fetchall()

            for table in tables:
                self.tables_list.addItem(table[0])
        except Exception as e:
            self.show_error(f"Ошибка при загрузке таблиц: {e}")

    def view_table_content(self):
        selected_table = self.tables_list.currentItem()
        if not selected_table:
            self.show_error("Выберите таблицу для просмотра.")
            return
        try:
            table_name = selected_table.text()
            self.open_table_content_window(table_name)
        except Exception as e:
            self.show_error(f"Ошибка при просмотре таблицы: {e}")

    def open_table_content_window(self, table_name):
        self.table_content_window = TableContentWindow(self.connection, table_name, self)  # Передаем TablesWindow
        self.table_content_window.show()
        self.close()  # Закрываем текущий виджет при открытии нового

    def clear_table(self):
        selected_table = self.tables_list.currentItem()
        if not selected_table:
            self.show_error("Выберите таблицу для очистки.")
            return
        try:
            table_name = selected_table.text()
            self.cursor.execute(f"CALL clear_table_proc('{table_name}');")
            self.show_message("Успех", f"Таблица {table_name} успешно очищена.")
        except Exception as e:
            self.show_error(f"Ошибка при очистке таблицы: {e}")

    def clear_all_tables(self):
        try:
            self.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = self.cursor.fetchall()
            for table in tables:
                self.cursor.execute(f"CALL clear_table_proc('{table[0]}');")
            self.show_message("Успех", "Все таблицы успешно очищены.")
        except Exception as e:
            self.show_error(f"Ошибка при очистке всех таблиц: {e}")

    def show_message(self, title, message):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def show_error(self, message):
        error_box = QtWidgets.QMessageBox(self)
        error_box.setIcon(QtWidgets.QMessageBox.Critical)
        error_box.setWindowTitle("Ошибка")
        error_box.setText(message)
        error_box.exec_()


class TableContentWindow(QtWidgets.QMainWindow):
    def __init__(self, connection, table_name, parent_window):
        super().__init__()
        self.connection = connection
        self.cursor = connection.cursor()
        self.table_name = table_name
        self.parent_window = parent_window  # Сохраняем ссылку на родительский виджет
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"Содержимое таблицы: {self.table_name}")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.table_view = QtWidgets.QTableWidget(self)
        self.layout.addWidget(self.table_view)

        self.load_table_content()

        # Кнопки
        self.back_button = QtWidgets.QPushButton("Назад к таблицам")
        self.add_record_button = QtWidgets.QPushButton("Добавить запись")

        self.layout.addWidget(self.back_button)
        self.layout.addWidget(self.add_record_button)

        self.back_button.clicked.connect(self.back_to_tables)
        self.add_record_button.clicked.connect(self.add_record)

    def load_table_content(self):
        try:
            self.cursor.execute(f"SELECT * FROM {self.table_name}")
            rows = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]

            self.table_view.setColumnCount(len(columns))
            self.table_view.setRowCount(len(rows))
            self.table_view.setHorizontalHeaderLabels(columns)

            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    self.table_view.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(value)))

        except Exception as e:
            self.show_error(f"Ошибка при загрузке содержимого таблицы: {e}")

    def add_record(self):
        dialog = AddRecordDialog(self, self.table_name)
        dialog.exec_()

    def back_to_tables(self):
        self.parent_window.show()  # Показываем основной виджет
        self.close()  # Закрываем текущий виджет

    def show_message(self, title, message):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def show_error(self, message):
        error_box = QtWidgets.QMessageBox(self)
        error_box.setIcon(QtWidgets.QMessageBox.Critical)
        error_box.setWindowTitle("Ошибка")
        error_box.setText(message)
        error_box.exec_()


class AddRecordDialog(QtWidgets.QDialog):
    def __init__(self, parent, table_name):
        super().__init__(parent)
        self.table_name = table_name
        self.cursor = parent.cursor
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"Добавить запись в таблицу: {self.table_name}")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QtWidgets.QFormLayout(self)

        self.fields = {}

        # Получаем описание колонок таблицы
        self.cursor.execute(f"SELECT * FROM {self.table_name} LIMIT 1;")
        columns = [desc[0] for desc in self.cursor.description]

        for column in columns:
            self.fields[column] = QtWidgets.QLineEdit(self)
            self.layout.addRow(f"{column}: ", self.fields[column])

        self.submit_button = QtWidgets.QPushButton("Добавить", self)
        self.cancel_button = QtWidgets.QPushButton("Отмена", self)

        self.layout.addRow(self.submit_button, self.cancel_button)

        self.submit_button.clicked.connect(self.submit_record)
        self.cancel_button.clicked.connect(self.reject)

    def submit_record(self):
        try:
            values = [self.fields[column].text() for column in self.fields]
            query = f"INSERT INTO {self.table_name} ({', '.join(self.fields.keys())}) VALUES ({', '.join(['%s'] * len(values))})"
            self.cursor.execute(query, values)
            self.accept()
            self.parent().load_table_content()
            self.parent().show_message("Успех", "Запись успешно добавлена!")
        except Exception as e:
            self.show_error(f"Ошибка при добавлении записи: {e}")

    def show_error(self, message):
        error_box = QtWidgets.QMessageBox(self)
        error_box.setIcon(QtWidgets.QMessageBox.Critical)
        error_box.setWindowTitle("Ошибка")
        error_box.setText(message)
        error_box.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DatabaseApp()
    window.show()
    sys.exit(app.exec_())
