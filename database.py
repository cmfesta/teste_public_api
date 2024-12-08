import sqlite3
import datetime


class messageDB:
    def __init__(self, db_path) -> None:
        self.db_path = db_path
        pass

    def connect_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()

    def create_table(self):
        self.connect_db()
        sql = """CREATE TABLE IF NOT EXISTS haircut_agenda (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT,
                    haircut_type TEXT,
                    date TEXT,
                    hour TEXT
                );
              """
        self.cur.execute(sql)
        self.conn.commit()
        self.conn.close()
        return

    def add_haircut_to_agenda(self, user_id, name, haircut_type,haircut_date):
        self.connect_db()
        sql = """INSERT INTO haircut_agenda(user_id,name,haircut_type,haircut_date) VALUES(?,?,?,?) """
        data = [user_id, name, haircut_type, haircut_date]
        self.cur.execute(sql, data)
        self.conn.commit()
        self.conn.close()
        return

    def delete_scheduled_haircut(self,user_id):
        self.connect_db()
        sql = f"""delete from haircut_agenda where user_id = ?"""
        data = [user_id]
        self.cur.execute(sql, data)
        self.conn.commit()
        self.conn.close()

    def all_users(self):
        self.connect_db()
        sql = f"""
                select distinct user_id from messages
               """
        all_users_list = self.cur.execute(sql).fetchall()
        self.conn.close()
        return all_users_list

    def filter_last_10_msgs_all_users(self):
        sql = f"""
                with u as (
                    select * from messages order by insert_date desc limit 10)
                    delete from messages
                    where user_id not in(select user_id from u)
               """
        self.cur.execute(sql)
        self.conn.commit()
        return

    def filter_last_10_msgs(self, user_id):
        self.connect_db()
        sql = f"""
                with user_id_ as (select * from messages where user_id = "{user_id}")
                select * from user_id_ order by insert_date desc limit 10
               """
        msgs = self.cur.execute(sql).fetchall()
        self.conn.close()
        return msgs

    def run(self, user_id, msg_history):
        self.connect_db()
        self.create_table()
        self.add_msg(user_id, msg_history)
        # self.filter_last_10_msgs_all_users()
        self.conn.close()
