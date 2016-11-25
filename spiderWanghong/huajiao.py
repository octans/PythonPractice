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

def getMysqlConn():
    conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root', passwd='123456', db='wanghong', charset='utf8')
    return conn


# get user counts
def getUserCount():
    conn = getMysqlConn()
    cur = conn.cursor()
    cur.execute("USE wanghong")
    cur.execute("set names utf8mb4")
    cur.execute("SELECT count(FUserId) FROM Tbl_Huajiao_User")
    ret = cur.fetchone()
    return ret[0]

# get live counts
def getLiveCount():
    conn = getMysqlConn()
    cur = conn.cursor()
    cur.execute("USE wanghong")
    cur.execute("set names utf8mb4")
    cur.execute("SELECT count(FLiveId) FROM Tbl_Huajiao_Live")
    ret = cur.fetchone()
    return ret[0]

# select user ids
def selectUserIds(num):
    conn = getMysqlConn()
    cur = conn.cursor()
    try:
        cur.execute("USE wanghong")
        cur.execute("set names utf8mb4")
        cur.execute("SELECT FUserId FROM Tbl_Huajiao_User ORDER BY FScrapedTime DESC LIMIT " + str(num))
        ret = cur.fetchall()
        return ret
    except:
        print("selectUserIds except")
        return 0

# update user data
def replaceUserData(data):
    conn = getMysqlConn()
    cur = conn.cursor()
    try:
        cur.execute("USE wanghong")
        cur.execute("set names utf8mb4")
        cur.execute("REPLACE INTO Tbl_Huajiao_User(FUserId,FUserName, FLevel, FFollow,FFollowed,FSupported,FExperience,FAvatar,FScrapedTime) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (int(data['FUserId']), data['FUserName'],int(data['FLevel']),int(data['FFollow']),int(data['FFollowed']), int(data['FSupported']), int(data['FExperience']), data['FAvatar'],getNowTime())
        )
        conn.commit()
    except pymysql.err.InternalError as e:
        print(e)
    except:
        print("replaceUserData except, userId=" + str(data['FUserId']))

# update user live data
def replaceUserLive(data):
    conn = getMysqlConn()
    cur = conn.cursor()
    try:
        print(data)
        cur.execute("USE wanghong")
        cur.execute("set names utf8mb4")
        cur.execute("REPLACE INTO Tbl_Huajiao_Live(FLiveId,FUserId,FWatches,FPraises,FReposts,FReplies,FPublishTimestamp,FTitle,FImage,FLocation,FScrapedTime) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s )", (int(data['relateid']),int(data['FUserId']), int(data['watches']),int(data['praises']),int(data['reposts']),int(data['replies']),int(data['publishtimestamp']),data['title'], data['image'], data['location'],getNowTime())
        )
        conn.commit()
    except pymysql.err.InternalError as e:
        print(e)

# spider user ids
def spiderUserDatas():
    for liveId in getLiveIdsFromRecommendPage():
        userId = getUserId(liveId)
        userData = getUserData(userId)
        if userData:
            replaceUserData(userData)
    return 1

# spider user lives
def spiderUserLives():
    userIds = selectUserIds(100)
    for userId in userIds:
        liveDatas = getUserLives(userId[0])
        for liveData in liveDatas:
            liveData['feed']['FUserId'] = userId[0]
            replaceUserLive(liveData['feed'])

    return 1

def main(argv):
    if len(argv) < 2:
        print("Usage: python3 huajiao.py [spiderUserDatas|spiderUserLives]")
        exit()
    if (argv[1] == 'spiderUserDatas'):
        spiderUserDatas()
    elif (argv[1] == 'spiderUserLives'):
        spiderUserLives()
    elif (argv[1] == 'getUserCount'):
        print(getUserCount())
    elif (argv[1] == 'getLiveCount'):
        print(getLiveCount())
    else:
        print("Usage: python3 huajiao.py [spiderUserDatas|spiderUserLives|getUserCount|getLiveCount]")

if __name__ == '__main__':
    main(sys.argv)


