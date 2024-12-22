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
            self.load_procedures()
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

    def check_tables(self):
        self.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = self.cursor.fetchall()
        print("Существующие таблицы в базе данных:")
        for table in tables:
            print(table[0])  # Выводим имя таблицы

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
            self.check_tables()
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
            self.cursor = self.connection.cursor()
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
            self.cursor = self.connection.cursor()
            self.load_procedures()
            self.create_tables()
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

        self.load_tables_button = QtWidgets.QPushButton("Загрузить таблицы")
        self.view_table_button = QtWidgets.QPushButton("Просмотреть содержимое")
        self.clear_table_button = QtWidgets.QPushButton("Очистить таблицу")
        self.clear_all_tables_button = QtWidgets.QPushButton("Очистить все таблицы")

        self.layout.addWidget(self.load_tables_button)
        self.layout.addWidget(self.view_table_button)
        self.layout.addWidget(self.clear_table_button)
        self.layout.addWidget(self.clear_all_tables_button)

        self.load_tables_button.clicked.connect(self.load_tables)
        self.view_table_button.clicked.connect(self.view_table_content)
        self.clear_table_button.clicked.connect(self.clear_table)
        self.clear_all_tables_button.clicked.connect(self.clear_all_tables)

    def check_tables(self):
        self.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = self.cursor.fetchall()
        print("Существующие таблицы в базе данных:")
        for table in tables:
            print(table[0])  # Выводим имя таблицы

    def load_tables(self):
        try:
            self.tables_list.clear()

            # Запрос для получения таблиц из базы данных
            self.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            all_tables = self.cursor.fetchall()

            # Выводим все таблицы в базе данных для сравнения
            print("Все таблицы в базе данных:")
            for table in all_tables:
                print(table[0])  # Выводим имя таблицы

            # Загружаем таблицы через хранимую процедуру
            self.cursor.execute("SELECT * FROM load_tables_proc();")
            tables = self.cursor.fetchall()

            # Выводим таблицы, загруженные через хранимую процедуру
            print("Загруженные таблицы через процедуру:")
            for table in tables:
                print(table[0])

            for table in tables:
                self.tables_list.addItem(table[0])
            self.check_tables()
        except Exception as e:
            self.show_error(f"Ошибка при загрузке таблиц: {e}")

    def view_table_content(self):
        selected_table = self.tables_list.currentItem()
        if not selected_table:
            self.show_error("Выберите таблицу для просмотра.")
            return
        try:
            table_name = selected_table.text()
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()
            content = '\n'.join(map(str, rows))
            self.show_message(f"Содержимое таблицы {table_name}", content)
        except Exception as e:
            self.show_error(f"Ошибка при просмотре таблицы: {e}")

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

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DatabaseApp()
    window.show()
    sys.exit(app.exec_())
