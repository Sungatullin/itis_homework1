import math
import sqlite3
import time


class FlaskDataBase:
    def __init__(self, db) -> None:
        self.__db = db
        self.__cur = db.cursor()

    def get_menu(self):
        """Returns all menu items from mainmenu table."""
        query = "SELECT * from mainmenu"
        try:
            self.__cur.execute(query)
            res = self.__cur.fetchall()
            if res:
                return res
        except Exception as e:
            print(f"Unexpected exception {e}")
        return []

    def add_user(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                com = "Пользователь с таким email уже существует"
                return False, com
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, ?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            com = "Ошибка добавления пользователя в БД" + str(e)
            return False, com
        return True, "Вы успешно зарегистрированы"

    def get_user(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = '{user_id}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД" + str(e))

        return False

    def get_user_by_email(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД" + str(e))

        return False
