import sys
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import json
import pymysql
import time
import datetime
from mysql import Model
from mysql import Mysql


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
    print('getUserData: userId=' + userId )
    html = urlopen("http://www.huajiao.com/user/" + str(userId))
    bsObj = BeautifulSoup(html, "html.parser")
    data = dict()
    try:
        userInfoObj = bsObj.find("div", {"id":"userInfo"})
        data['FAvatar'] = userInfoObj.find("div", {"class": "avatar"}).img.attrs['src']
        userId = userInfoObj.find("p", {"class":"user_id"}).get_text()
        data['FUserId'] = re.findall("[0-9]+", userId)[0]
        tmp = userInfoObj.h3.get_text('|', strip=True).split('|')
        data['FUserName'] = tmp[0]
        data['FLevel'] = tmp[1]
        tmp = userInfoObj.find("ul", {"class":"clearfix"}).get_text('|', strip=True).split('|')
        data['FFollow'] = tmp[0]
        data['FFollowed'] = tmp[2]
        data['FSupported'] = tmp[4]
        data['FExperience'] = tmp[6]

        return data
    except AttributeError:
        #traceback.print_exc()
        print(str(userId) + ":html parse error in getUserData()")
        return 0

# get user history lives
def getUserLives(userId):
    print('getUserLives: userId=' + str(userId))
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
        try:
            if userData:
                User().insert(userData, 1)
        except pymysql.err.InternalError as e:
            print(e)
            print(userData)

    return 1

# spider user lives
def spiderUserLives():
    userIds = User().select("FUserId").limit(100).fetch_all()
    for userId in userIds:
        liveDatas = getUserLives(userId[0])
        try:
            for liveData in liveDatas:
                liveData['feed']['FUserId'] = userId[0]
                replaceUserLive(liveData['feed'])
        except Exception as e:
            print(e)

    return 1


class BoseModel(Model):
    conn = Mysql(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root', passwd='123456', db='wanghong', charset='utf8')


class User(BoseModel):
    tbl = "Tbl_Huajiao_User"


class Live(BoseModel):
    tbl = "Tbl_Huajiao_Live"


def main(argv):
    if len(argv) < 2:
        print("Usage: python3 huajiao.py [spiderUserDatas|spiderUserLives]")
        exit()
    if argv[1] == 'spiderUserDatas':
        spiderUserDatas()
    elif argv[1] == 'spiderUserLives':
        spiderUserLives()
    elif argv[1] == 'getUserCount':
        count = User().select("count(\"FUserId\")").fetch_one()
        print(count[0])
    elif argv[1] == 'getLiveCount':
        count = Live().select("count(\"FLiveId\")").fetch_one()
        print(count[0])
    else:
        print("Usage: python3 huajiao.py [spiderUserDatas|spiderUserLives|getUserCount|getLiveCount]")

if __name__ == '__main__':
    main(sys.argv)

