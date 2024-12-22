import psycopg2

# Параметры подключения к базе данных
DB_NAME = "online_school"
DB_USER = "postgres"  # Замените на вашего пользователя
DB_PASSWORD = "password"  # Замените на ваш пароль
DB_HOST = "localhost"
DB_PORT = "5432"


class App:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(dbname="postgres", user=DB_USER,password=DB_PASSWORD,host=DB_HOST)
            self.connection.autocommit = True  # Включаем autocommit
            self.cur = self.connection.cursor()
            print('Успешное подключение к БД')
        except Exception as e:
            print('Ошибка при подключении базы данных:', e)

    def create_db(self):
        try:
            # Удаляем базу данных, если она существует
            self.cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
            print(f"База данных {DB_NAME} успешно удалена (если существовала).")

            # Создаем новую базу данных
            self.cur.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"База данных {DB_NAME} успешно создана!")

            self.close_connection()
            self.connection = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
            self.cur = self.connection.cursor()
            print(f"Осуществлен вход в {DB_NAME}")
        except Exception as e:
            print('Возникла ошибка при создании базы данных:', e)

    def create_tables(self):
        try:
            with open('setup_db.sql') as f:
                sql_commands = f.read()
            self.cur.execute(sql_commands)
            print('Таблицы успешно созданы!')
        except Exception as e:
            print('Возникла ошибка при создании таблиц:', e)

    def close_connection(self):
        self.cur.close()
        self.connection.close()
        print("Соединение закрыто.")

    def check_tables(self):
        self.cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = self.cur.fetchall()
        print("Существующие таблицы в базе данных:")
        for table in tables:
            print(table[0])  # Выводим имя таблицы

# Создание базы данных
app = App()
app.create_db()
app.create_tables()
app.check_tables()
app.close_connection()