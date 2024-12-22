import psycopg2
from psycopg2 import sql
# Параметры подключения к базе данных
DB_NAME = "postgres"
DB_USER = "postgres"  # Замените на вашего пользователя
DB_PASSWORD = "password"  # Замените на ваш пароль
DB_HOST = "localhost"
DB_PORT = "5432"

class App:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                dbname = DB_NAME,
                user = DB_USER,
                password = DB_PASSWORD,
                host = DB_HOST
            )
            #self.connection.autocommit = True
            self.cur = self.connection.cursor()
            print('Успешное подключение к БД')
        except Exception as e:
            print('Ошибка при подключении базы данных:', e)
    def create_db(self):
        try:
            with open('setup_db.sql') as f:
                sql_commands = f.read()
            self.cur.execute(sql_commands)
            print('База данных успешно создана!')
        except Exception as e:
            print('Возникла ошибка при создании базы данных:' , e)


App = App()
App.create_db()