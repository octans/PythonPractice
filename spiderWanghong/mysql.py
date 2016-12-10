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
    def query(cls, sql):
        cls.cursor.execute(sql)
        return cls


class Model:

    @classmethod
    def select(cls, selectStr):
        if selectStr.find(",") == -1:
            sqlFields = selectStr
        else:
            fields = list()
            for f in selectStr.split(","):
                fields.append('`' + f.strip() + '`')
            sqlFields = ",".join(fields)
        cls.sql = "SELECT " + sqlFields + " FROM " + cls.tbl
        return cls

    @classmethod
    def where(cls, string):
        cls.sql = cls.sql + " WHERE " + string
        return cls

    @classmethod
    def orderBy(cls, string):
        cls.sql = cls.sql + " ORDER BY " + string
        return cls

    @classmethod
    def limit(cls, num):
        cls.sql = cls.sql + " LIMIT " + str(num)
        return cls

    @classmethod
    def fetchAll(cls):
        return Mysql().query(cls.sql).cursor.fetchall()

    @classmethod
    def fetchOne(cls):
        return Mysql().query(cls.sql).cursor.fetchone()

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

    @classmethod
    def update(cls, where, **data):
        pass

    @classmethod
    def delete(cls, where):
        sql = "DELETE FROM " + cls.tbl + " WHERE " + where
        Mysql().query(sql).conn.commit()
