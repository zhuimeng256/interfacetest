import pymysql
from warnings import filterwarnings

filterwarnings("ignore", category=pymysql.Warning)

class MysqlDb:
    def __init__(self):
        self.conn = pymysql.connect(host="127.0.0.1", user="root", password="123456", database="intertest", use_unicode=True, charset="utf8")
        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def query(self, sql, state="all"):
        self.cur.execute(sql)
        if state == "all":
            data = self.cur.fetchall()
        else:
            data = self.cur.fetchone()
        return data

    def execute(self, sql):
        try:
            rows = self.cur.execute(sql)
            self.conn.commit()
            return  rows
        except Exception as e:
            print("数据库操作异常 {0}".format(e))
            self.conn.rollback()

if __name__ == '__main__':
    mydb = MysqlDb()
    r = mydb.query("select * from `case`")
    # r = mydb.execute("insert into `case` (`app`) values('xd')")
    print(r)