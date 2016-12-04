import sys
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import json
import pymysql
import time
import datetime
#import traceback


def getNowTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

# filter out live ids from a url
def filterLiveIds(url):
    html = urlopen(url)
    liveIds = set()
    bsObj = BeautifulSoup(html, "html.parser")
    for link in bsObj.findAll("a", href=re.compile("^(/l/)")):
        if 'href' in link.attrs:
            newPage = link.attrs['href']
            liveId = re.findall("[0-9]+", newPage)
            liveIds.add(liveId[0])
    return liveIds

# get live ids from recommand page
def getLiveIdsFromRecommendPage():
    liveIds = set()
    liveIds = filterLiveIds("http://www.huajiao.com/category/1000") | filterLiveIds("http://www.huajiao.com/category/1000?pageno=2")
    return liveIds

# get user id from live page
def getUserId(liveId):
    html = urlopen("http://www.huajiao.com/" + "l/" + str(liveId))
    bsObj = BeautifulSoup(html, "html.parser")
    text = bsObj.title.get_text()
    res = re.findall("[0-9]+", text)
    return res[0]


# get user data from user page
def getUserData(userId):
    html = urlopen("http://www.huajiao.com/user/" + str(userId))
    bsObj = BeautifulSoup(html, "html.parser")
    data = dict()
    try:
        userInfoObj = bsObj.find("div", {"id":"userInfo"})
        data['FAvatar'] = userInfoObj.find("div", {"class": "avatar"}).img.attrs['src']
        userId = userInfoObj.find("p", {"class":"user_id"}).get_text()
        data['FUserId'] = re.findall("[0-9]+", userId)[0]
        tmp = userInfoObj.h3.get_text('|', strip=True).split('|')
        #print(tmp[0].encode("utf-8"))
        data['FUserName'] = tmp[0]
        data['FLevel'] = tmp[1]
        tmp = userInfoObj.find("ul", {"class":"clearfix"}).get_text('|', strip=True).split('|')
        data['FFollow'] = tmp[0]
        data['FFollowed'] = tmp[2]
        data['FSupported'] = tmp[4]
        data['FExperience'] = tmp[6]
        '''
        metrics = userInfoObj.find("ul", {"class":"clearfix"}).findAll("li")
        i = 0
        for li in metrics:
            if i == 0:
                data['FFollow'] = li.p.get_text()
            elif i == 1:
                data['FFollowed'] = li.p.get_text()
            elif i == 2:
                data['FSupported'] = li.p.get_text()
            elif i == 3:
                data['FExperience'] = li.p.get_text()
            else:
                break;
            i += 1
        '''

        return data
    except AttributeError:
        #traceback.print_exc()
        print(str(userId) + ":html parse error in getUserData()")
        return 0

# get user history lives
def getUserLives(userId):
    try:
        url = "http://webh.huajiao.com/User/getUserFeeds?fmt=json&uid=" + str(userId)
        html = urlopen(url).read().decode('utf-8')
        jsonData = json.loads(html)
        if jsonData['errno'] != 0:
            print(str(userId) + "error occured in getUserFeeds for: " + jsonData['msg'])
            return 0

        return jsonData['data']['feeds']
    except Exception as e:
        print(e)
        return 0


def getTimestamp():
    return (time.mktime(datetime.datetime.now().timetuple()))

# update user live data
def replaceUserLive(data):
    try:
        kvs = dict()
        kvs['FLiveId'] = int(data['relateid'])
        kvs['FUserId'] = int(data['FUserId'])
        kvs['FWatches'] = int(data['watches'])
        kvs['FPraises'] = int(data['praises'])
        kvs['FReposts'] = int(data['reposts'])
        kvs['FReplies'] = int(data['replies'])
        kvs['FPublishTimestamp'] = int(data['publishtimestamp'])
        kvs['FTitle'] = data['title']
        kvs['FImage'] = data['image']
        kvs['FLocation'] = data['location']
        kvs['FScrapedTime'] = getNowTime()
        Live().insert(kvs, 1)
    except pymysql.err.InternalError as e:
        print(e)

# spider user ids
def spiderUserDatas():
    for liveId in getLiveIdsFromRecommendPage():
        userId = getUserId(liveId)
        userData = getUserData(userId)
        if userData:
            User().insert(userData, 1)
    return 1

# spider user lives
def spiderUserLives():
    userIds = User().select("FUserId").limit(100).fetchAll()
    for userId in userIds:
        liveDatas = getUserLives(userId[0])
        for liveData in liveDatas:
            liveData['feed']['FUserId'] = userId[0]
            replaceUserLive(liveData['feed'])

    return 1

class Mysql():
    def __new__(cls):
        cls.connect()
        return cls
    def __del__(cls):
        cls.close()

    @classmethod
    def connect(cls):
        cls.conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root', passwd='123456', db='wanghong', charset='utf8')
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

class Model():
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

    @classmethod
    def insert(cls, data, replace=None):
        fields = list()
        for a in data.keys():
            fields.append('`' + a + '`')
        sqlFields = ",".join(fields)

        values = list()
        for v in data.values():
            v = "\"" + v + "\"" if type(v) is type("a") else str(v)
            values.append(v)
        sqlValues = ",".join(values)

        action = "INSERT" if replace is None else "REPLACE"
        sql = action + " INTO " + cls.tbl + " (" + sqlFields + ") VALUES (" + sqlValues + ")"
        print(sql)
        Mysql().query(sql).conn.commit()

    @classmethod
    def update(cls, where, **data):
        pass

    @classmethod
    def delete(cls, where):
        sql = "DELETE FROM " + cls.tbl + " WHERE " + where
        Mysql().query(sql).conn.commit()

# ORM User -> Tbl_Huajiao_User
class User(Model):
    tbl = "Tbl_Huajiao_User"

class Live(Model):
    tbl = "Tbl_Huajiao_Live"

def main(argv):
    if len(argv) < 2:
        print("Usage: python3 huajiao.py [spiderUserDatas|spiderUserLives]")
        exit()
    if (argv[1] == 'spiderUserDatas'):
        spiderUserDatas()
    elif (argv[1] == 'spiderUserLives'):
        spiderUserLives()
    elif (argv[1] == 'getUserCount'):
        count = User().select("count(\"FUserId\")").fetchOne()
        print(count[0])
    elif (argv[1] == 'getLiveCount'):
        count = Live().select("count(\"FLiveId\")").fetchOne()
        print(count[0])
    else:
        print("Usage: python3 huajiao.py [spiderUserDatas|spiderUserLives|getUserCount|getLiveCount]")

if __name__ == '__main__':
    main(sys.argv)

