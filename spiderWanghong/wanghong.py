import requests
from bs4 import BeautifulSoup
import re
import json
import sys
import time
from mysql import Model
from mysql import Mysql

"""
class Cache():
    '''
    将_csrf的值存储到文件
    '''
    cacheFile = './csrf.cache'
    fileObj = ''

    def read(self):
        if os.path.isfile(self.cacheFile):
            self.fileObj = open(self.cacheFile, 'r')
            return self.fileObj.read()
        else:
            return ''

    def write(self, string):
        self.fileObj = open(self.cacheFile, 'w')
        self.fileObj.write(string)

    def __del__(self):
        if self.fileObj != '':
            self.fileObj.close()
"""


def get_current_time():

    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


class Website:
    session = requests.session()

    htmlParser = BeautifulSoup

    jsonParser = json

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                      '54.0.2840.98 Safari/537.36'
    }

    def get(self, url, params=None):
        if params is None:
            params = {}
        return self.session.get(url, params=params, headers=self.headers)

    def get_html(self, url, params=None):
        """
        GET请求, 用于网站返回html时
        """
        r = self.get(url, params)
        return self.htmlParser(r.text, 'html.parser')

    def get_json(self, url, params=None):
        """
        GET请求, 用于网站返回json时
        """

        r = self.get(url, params)

        return self.jsonParser.loads(r.text)

    def post_url_encoded(self, url, params):
        """
        POST方式：Content-Type: application/x-www-form-urlencoded
        """
        pass

    def post_multi_part(self, url, params):
        """
        POST方式：Content-Type:multipart/form-data
        """

        kwargs = dict()
        for (k, v) in params.items():
            kwargs.setdefault(k, (None, v))
        r = self.session.post(url, files=kwargs, headers=self.headers)

        return self.htmlParser(r.text, "html.parser")


class YiXia(Website):

    def parse_user_page(self, uid):
        """
        访问主播页面，也是视频列表页，从该页面获取到suid和主播个人信息
        """

        print(get_current_time() + ':' + self.__class__.__name__ + ':parse_user_page, uid=' + uid)
        user = dict()
        user['uid'] = uid
        url = 'http://www.yixia.com/u/' + uid
        bs = self.get_html(url)

        div = bs.find('div', {'class': 'box1'})
        user['nickname'] = div.h1.a.get_text(strip=True)  # 昵称

        stat = div.ol.get_text(strip=True)
        stat = re.split('关注\||粉丝', stat)
        user['follow'] = stat[0].strip()  # 关注数
        user['followed'] = stat[1].strip()  # 粉丝数

        user['avatar'] = bs.find('div', {'class': 'nav_div1'}).a.img.attrs['src']  # 头像

        user['suid'] = bs.find('div', {'class': 'nav_div1'}).find('button').attrs['suid']  # suid

        tmp = bs.find('div', {'class': 'nav_div3'}).get_text('@#$%', strip=True).split('@#$%')
        user['location'] = tmp[0]
        user['descr'] = tmp[1]

        tmp = bs.find('div', {'class': 'n_b_con'}).get_text(strip=True)
        tmp = re.split('视频|转发|赞', tmp)
        user['video_count'] = tmp[0]  # 视频数
        user['relayed'] = tmp[1]  # 转发数
        user['praised'] = tmp[2]  # 被赞数

        return user

    def get_follow_list(self, suid, page=1):
        """
        获取某用户的关注列表
        页面地址：http://www.yixia.com/u/$uid/relation/follow.htm 瀑布流展示关注列表，
        ajax接口地址：http://www.yixia.com/gu/follow?page=1&suid=$suid
        """

        print(get_current_time() + ':' + self.__class__.__name__ + ':get_follow_list, suid=' + suid + ' page=' + str(page))

        url = 'http://www.yixia.com/gu/follow'  # ajax接口
        params = {
            'page': page,
            'suid': suid,
        }
        res = self.get_json(url, params)
        if res['msg'] == '':
            return list()

        res = BeautifulSoup(res['msg'], 'html.parser')
        boxs = res.findAll('div', {'class': 'box'})
        users = list()
        for box in boxs:
            user = dict()
            user['suid'] = suid
            top = box.find('div', {'class': 'box_top'})
            user['avatar'] = top.img.attrs['src']
            user['uid'] = top.a.attrs['href']
            user['uid'] =re.split('http://www.yixia.com/u/', user['uid'])
            user['uid'] = user['uid'][1]
            user['suid'] = top.div.h2.button.attrs['suid']
            user['nickname'] = box.find('div', {'class': 'top_txt'}).a.get_text(strip=True)

            center = box.find('div', {'class': 'box_center'}).get_text(strip=True)
            center = re.split('视频|关注|粉丝', center)
            user['video_count'] = center[0]  # 视频数
            user['follow'] = center[1]  # 关注数
            user['followed'] = center[2]  # 粉丝数
            user['descr'] = box.find('p', {'class': 'box_bottom'}).b.get_text(strip=True)
            users.append(user)
        return users

    def get_video_list(self, suid, page=1):
        """
        AJAX请求视频列表
        """

        url = 'http://www.yixia.com/gu/u'
        payload = {
            'page': page,
            'suid': suid,
            'fen_type': 'channel'
        }
        json_obj = self.get_json(url, params=payload)
        msg = json_obj['msg']
        msg = BeautifulSoup(msg, 'html.parser')

        '''
        解析视频标题
        '''
        titles = list()
        ps = msg.findAll('p')
        for p in ps:
            titles.append(p.get_text(strip=True))  # 视频标题

        '''
        解析视频赞和评论数
        '''
        stats = list()
        divs = msg.findAll('div', {'class': 'list clearfix'})
        for div in divs:
            tmp = div.ol.get_text(strip=True)
            tmp = re.split('赞|\|评论', tmp)
            stats.append(tmp)

        '''
        解析视频其他数据
        '''
        videos = list()
        divs = msg.findAll('div', {'class': 'D_video'})
        for (k, div) in enumerate(divs):
            video = dict()
            video['scid'] = div.attrs['data-scid']
            video['img'] = div.find('div', {'class': 'video_img'}).img.attrs['src']  # 视频封面
            video['flash'] = div.find('div', {'class': 'video_flash'}).attrs['va']  # 视频flash地址
            intro = div.find('div', {'class': 'introduction'})
            head_area = intro.find('div', {'class': 'D_head_name'}).h2
            video['detail_page'] = head_area.a.attrs['href']  # 视频详情地址
            video['pub_date'] = head_area.b.get_text(strip=True)  # 视频日期
            head_area.a.decompose()
            tmp = head_area.get_text(strip=True)
            tmp = re.split('观看', tmp)

            def format_num(string):

                # 判断是否有逗号，比如8,189
                try:
                    index = string.index(',')
                    string = string.replace(',', '')
                except ValueError:
                    string = string

                # 判断是否有小数点
                try:
                    index = string.index('.')
                    is_float = True
                except ValueError:
                    is_float = False

                # 是否有万字
                t = string[len(string)-1]
                if t == '万':
                    num = string.replace('万', '')
                    if is_float:
                        ret = int(float(num) * 10000)
                    else:
                        ret = int(num) * 10000
                else:
                    if is_float:
                        ret = float(string)
                    else:
                        ret = int(string)

                return ret

            try:
                video['watched'] = format_num(tmp[0])  #观看量
                video['title'] = titles[k]  # 标题
                video['praised'] = format_num(stats[k][1])  # 赞
                video['discussed'] = format_num((stats[k][2]))  # 评论
            except (ValueError, IndexError) as e:
                print(e)
            else:
                videos.append(video)

        return videos

    def spider_videos(self, suid, video_count):
        page = 1
        current = 0
        tbl_video = YiXiaVideo()
        while current < int(video_count):
            print(get_current_time() + ':' + 'spider_videos: suid=' + suid + ', page=' + str(page))
            videos = self.get_video_list(suid, page)
            for video in videos:
                tbl_video.insert(video, replace=True)
            current += len(videos)
            page += 1
        return True

    def spider_follows(self, suid):
        page = 1
        tbl_user = YiXiaActor()
        while True:
            users = self.get_follow_list(suid, page)
            if len(users) <= 0:
                break;
            for user in users:
                tbl_user.insert(user, replace=True)
            page += 1

        return True



class WoMiYouXuan(Website):
    """
    网红数据分析平台：沃米优选 http://www.51wom.com/
    """

    csrf = ''

    def __init__(self):
        self.first_kiss()

    def first_kiss(self):
        """
        首次请求获取cookies和csrf, 将cookies和csrf放入后续每次发请求的头信息里；
        其中cookies由requests.session()自动处理
        """

        url = 'http://video.51wom.com/'
        html = self.get_html(url)
        self.csrf = html.find('meta', {'name': 'csrf-token'}).attrs['content']

    def parse_actor_list_page(self, page=1):
        """
        从主播列表页获取主播信息
        """

        '''
        构造参数->发送请求
        '''
        url = 'http://video.51wom.com/media/' + str(page) + '.html'
        keys = ('_csrf', 'stage-name', 'platform', ' industry', 'price', 'follower_num', 'follower_area',
                'page', 'is_video_platform', 'sort_by_price', 'type_by_price')
        params = dict()
        for key in keys:
            params.setdefault(key, '')
        params['_csrf'] = self.csrf
        params['page'] = str(page)
        html = self.post_multi_part(url, params)

        '''
        总条目数
        '''
        total = int(html.find('div', {'id': 'w0'}).find('span', {'class': 'gross'}).i.get_text(strip=True))

        '''
        解析主播列表
        '''
        trs = html.find('div', {'id': 'table-list'}).table.findAll('tr')
        trs.pop(0)  # 去除标题行
        actor_list = list()
        for tr in trs:
            actor_dict = dict()

            tds = tr.find_all('td')

            actor_dict['address'] = tds[0].span.attrs['data-address']
            actor_dict['uuid'] = tds[0].span.attrs['data-uuid']

            def format_price(price_str):
                p = price_str.split('.')
                p = 0 if p[0] == '' else p[0]
                return p
            actor_dict['max_price'] = format_price(tds[0].span.attrs['data-max-price'])
            actor_dict['min_price'] = format_price(tds[0].span.attrs['data-min-price'])

            as_ = tds[1].find_all('a')
            actor_dict['avatar'] = as_[0].img.attrs['src']  # 头像
            actor_dict['nickname'] = as_[1].get_text(strip=True)  # 昵称
            sex = tds[1].find('i', {'class': 'note'}).img.attrs['src']
            index_tmp = sex.find('.png')
            actor_dict['sex'] = sex[index_tmp - 1:index_tmp]  # 性别：1-男，2-女
            actor_dict['geo_range'] = tds[1].find('span', {'class': 'name synopsis'}).get_text(strip=True)  # 地域范围
            actor_dict['type_label'] = tds[1].li.get_text(strip=True)  # 资源分类

            platform = tds[2].img.attrs['src']
            index_tmp = platform.find('.png')
            actor_dict['platform'] = platform[index_tmp - 1:index_tmp]  # 平台：5-秒拍，

            user_id = tds[3].span.get_text(strip=True).split('ID:')
            actor_dict['user_id'] = user_id[1].strip()  # 用户在平台的user id

            actor_dict['followed'] = tds[4].span.get_text(strip=True)  # 粉丝数

            prices = tds[5].find_all('p', {'class', 'p-price'})  # 报价方式，比如"视频原创+发布"，"线上直播"，"线下直播"
            price_dict = dict()
            for price in prices:
                price = price.get_text(strip=True).split('：')
                try:
                    price_dict[price[0]] = price[1]
                except IndexError:
                    pass
            actor_dict['price_dict'] = price_dict

            avg_watched = tds[6].get_text(strip=True)  # 平均观看人数
            mode = re.compile(r'\d+')
            tmp = mode.findall(avg_watched)
            try:
                avg_watched = tmp[0]
            except IndexError:
                pass
            actor_dict['avg_watched'] = avg_watched
            actor_list.append(actor_dict)

        return {'total': total, 'page': page, 'items_count': len(actor_list), 'items': actor_list}

    def spider_actors(self):
        page = 1
        tbl_actor = WMYXActor()
        while True:
            ret = self.parse_actor_list_page(page)
            for actor in ret['items']:
                actor['price_dict'] = json.dumps(actor['price_dict'])
                tbl_actor.insert(actor, replace=True)
            if ret['items_count'] * ret['page'] < ret['total']:
                page += 1
            else:
                break


class BoseModel(Model):
    conn = Mysql(host='127.0.0.1', user='root', passwd='123456', db='wanghong', charset='utf8')


class WMYXActor(BoseModel):
    tbl = "Tbl_WMYX_Actor"


class YiXiaActor(BoseModel):
    tbl = "Tbl_YiXia_Actor"


class YiXiaVideo(BoseModel):
    tbl = "Tbl_YiXia_Video"

class HuaJiaoActor(BoseModel):
    tbl = "Tbl_Huajiao_User"

class Actor(BoseModel):
    tbl = "Tbl_Actor"


def agg_actors():
    Actor().delete()

    # 一下网
    actors = YiXiaActor().select('uid, nickname, follow, followed, praised, avatar, 2 as pid')\
        .order_by('followed desc').limit(500).fetch_all(is_dict=1)
    try:
        for actor in actors:
            Actor().insert(actor)
    except Exception as e:
        print(e)

    # 花椒网
    actors = HuaJiaoActor().select('FUserId as uid, FUserName as nickname, FFollow as follow, FFollowed as followed,\
                                   FSupported as praised, FAvatar as avatar, 1 as pid').order_by('FFollowed')\
        .limit(500).fetch_all(is_dict=1)
    try:
        for actor in actors:
            Actor().insert(actor)
    except Exception as e:
        print(e)

def spider_yixia_videos():
    # yixia_actors = WMYXActor().select('user_id').where('platform=5').order_by('scraped_time desc').fetch_all()
    yixia_actors = YiXiaActor().select('uid').order_by('scraped_time desc').limit(100).fetch_all()
    y = YiXia()
    for actor in yixia_actors:
        uid = actor[0]
        actor = y.parse_user_page(uid)
        YiXiaActor().insert(actor, replace=True)
        y.spider_videos(actor['suid'], actor['video_count'])


def spider_womiyouxuan_actors():
    WoMiYouXuan().spider_actors()


def spider_yixia_follows():
    suids = YiXiaActor().select('suid').order_by('scraped_time desc, id desc').limit(20).fetch_all()
    if len(suids) <= 0:
        suids = [{'ZPWwDeYSvPUb23SL'}]
    for suid in suids:
        YiXia().spider_follows(suid[0])

def main(argv):
    useage = "Usage: python3 wanghong.py [spider_womiyouxuan_actors|spider_yixia_videos|spider_yixia_follows|" \
             "womiyouxuan_actors_count|" \
             "yixia_videos_count|yixia_actors_count" \
             "|agg_actors]"
    if len(argv) < 2:
        print(useage)
        exit()

    if argv[1] == 'spider_womiyouxuan_actors':
        spider_womiyouxuan_actors()
    elif argv[1] == 'spider_yixia_videos':
        print(get_current_time() + ':' + 'spider_yixia_videos start')
        spider_yixia_videos()
        print(get_current_time() + ':' + 'spider_yixia_videos end')
    elif argv[1] == 'spider_yixia_follows':
        print(get_current_time() + ':' + 'spider_yixia_follows start')
        spider_yixia_follows()
        print(get_current_time() + ':' + 'spider_yixia_follows end')
    elif argv[1] == 'womiyouxuan_actors_count':
        count = WMYXActor().select("count(\"id\")").fetch_one()
        print(count[0])
    elif argv[1] == 'yixia_videos_count':
        count = YiXiaVideo().select("count(\"id\")").fetch_one()
        print(count[0])
    elif argv[1] == 'yixia_actors_count':
        count = YiXiaActor().select("count(\"id\")").fetch_one()
        print(count[0])
    elif argv[1] == 'agg_actors':
        agg_actors()
    else:
        print(useage)

if __name__ == '__main__':
    main(sys.argv)






