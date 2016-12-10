import requests
from bs4 import BeautifulSoup
import os
import re
import json
import sys
from mysql import Model
from mysql import Mysql


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


class Website:
    session = requests.session()

    htmlParser = BeautifulSoup

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                      '54.0.2840.98 Safari/537.36'
    }

    def get(self, url):
        """
        GET请求
        """

        r = self.session.get(url, headers=self.headers)
        return self.htmlParser(r.text, "html.parser")

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
        html = self.get(url)
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
            actor_dict['type_label'] = tds[1].li.get_text(strip=True)  # 标签

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
            print(page)
            ret = self.parse_actor_list_page(page)
            print(ret)
            for actor in ret['items']:
                actor['price_dict'] = json.dumps(actor['price_dict'])
                tbl_actor.insert(actor, replace=True)
            if ret['items_count'] * ret['page'] < ret['total']:
                page += 1
            else:
                break


class BoseModel(Model):
    conn = Mysql(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root', passwd='123456', db='wanghong', charset='utf8')


class WMYXActor(BoseModel):
    tbl = "Tbl_WMYX_Actor"


def main(argv):
    useage = 'Usage: python3 wanghong.py [spider_actors]'
    if len(argv) < 2:
        print(useage)
        exit()

    if argv[1] == 'spider_actors':
        w = WoMiYouXuan()
        w.spider_actors()
    else:
        print(useage)

if __name__ == '__main__':
    main(sys.argv)





