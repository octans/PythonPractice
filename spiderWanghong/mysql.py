import pymysql


def addslashes(s):
    try:
        d = {'"': '\\"', "'": "\\'", "\0": "\\\0", "\\": "\\\\"}
        return ''.join(d.get(c, c) for c in s)
    except:
        return s


class Mysql():
    def __new__(cls, **params):
        cls.connect(**params)
        return cls

    def __del__(cls):
        cls.close()

    @classmethod
    def connect(cls, **params):
        cls.conn = pymysql.connect(**params)
        cls.cursor = cls.conn.cursor()
        cls.cursor.execute("set names utf8mb4")

    @classmethod
    def close(cls):
        cls.cursor.close()
        cls.conn.close()

    @classmethod
    def query(cls, sql, is_dict=0):
        if is_dict:
            cls.cursor = cls.conn.cursor(pymysql.cursors.DictCursor)
        cls.cursor.execute(sql)
        return cls


class Model:
    sql = ''

    def select(self, select_str):
        if select_str.find(",") == -1:
            select_str = select_str
        else:
            fields = list()
            for f in select_str.split(","):
                if f.find('as') > 0:
                    p = f.split(" as ")
                    fields.append(p[0].strip() + ' as `' + p[1].strip() + '`')
                else:
                    fields.append('`' + f.strip() + '`')
                select_str = ",".join(fields)
        self.sql = "SELECT " + select_str + " FROM " + self.tbl
        return self

    def where(self, string):
        self.sql = self.sql + " WHERE " + string
        return self

    def order_by(self, string):
        self.sql = self.sql + " ORDER BY " + string
        return self

    def limit(self, num):
        self.sql = self.sql + " LIMIT " + str(num)
        return self

    def fetch_all(self, is_dict=0):
            return self.conn.query(self.sql, is_dict).cursor.fetchall()

    def fetch_one(self):
        return self.conn.query(self.sql).cursor.fetchone()

    def insert(self, data, replace=None):
        fields = list()
        for a in data.keys():
            fields.append('`' + a + '`')
        sqlFields = ",".join(fields)

        values = list()
        for v in data.values():
            v = addslashes(v)
            v = "\"" + v + "\"" if type(v) is type("a") else str(v)
            values.append(v)
        sqlValues = ",".join(values)

        action = "INSERT" if replace is None else "REPLACE"
        sql = action + " INTO " + self.tbl + " (" + sqlFields + ") VALUES (" + sqlValues + ")"
        self.conn.query(sql).conn.commit()

    def update(self, where, **data):
        pass

    def delete(self, where='1'):
        sql = "DELETE FROM " + self.tbl + " WHERE " + where
        self.conn.query(sql).conn.commit()
