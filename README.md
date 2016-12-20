# PythonPractice

### 使用说明
* 1. 使用db.sql建立mysql数据库
* 2. 在wanghong.py的BoseModel定义里设置mysql的连接参数
* 3. 安装python库pymysql, requests, BeautifulSoup
* 4. 运行以下命令, 会提示支持的操作
```
# python3 wanghong.py
Usage: python3 wanghong.py [spider_womiyouxuan_actors|spider_yixia_videos|spider_yixia_follows|womiyouxuan_actors_count|yixia_videos_count|yixia_actors_count]
```
* 5. 运行某一个命令，比如：
```
# python3 wanghong.py spider_yixia_follows
```
| 命令       | 含义          | 逻辑  |
| :------------- |:-------------|:-----|
| spider_womiyouxuan_actors      | 爬取沃米优选的主播信息 | 遍历每个分页并将主播信息写入数据表Tbl_WMYX_Actor |
| spider_yixia_videos      | 爬取一下网的视频     |  从数据库中取出最新爬取的主播数据，进而爬取每个主播的视频数据，写入数据表Tbl_YiXia_Video |
| spider_yixia_follows | 爬取一下网的主播     |  从数据库中取出最新爬取的主播数据，进而爬取每个主播关注的人的数据，写入数据表Tbl_YiXia_Actor |
|yixia_videos_count|查看爬取的一下网视频总数|
|yixia_actors_count|查看爬取的一下网主播总数|

### 已实现对以下直播类网站的数据爬取:
* 花椒(http://www.huajiao.com/)
* 一下(http://www.yixia.com/u/paike_oq7pzk336s)
```
### 访问主播页面，从该页面获取到suid和主播个人信息
uid = 'paike_oq7pzk336s'
ret = YiXia().parse_user_page(uid)
print(ret)
"""
{'relayed': '4', 'avatar': 'http://tp2.sinaimg.cn/2714280233/180/5728135083/0', 'video_count': '140', 'suid': 'ZPWwDeYSvPUb23SL', 'uid': 'paike_oq7pzk336s', 'follow': '13', 'followed': '21031136', 'descr': '微信订阅：dapapi。微博：papi酱。', 'location': '北京 崇文区', 'nickname': 'papi酱', 'praised': '0'}
"""

### 获取某用户的关注列表
suid = 'ZPWwDeYSvPUb23SL'
page = 1
ret = YiXia().get_follow_list(suid, page)
print(ret)
"""
[{'followed': '169054', 'nickname': 'lyxp', 'follow': '3', 'descr': 'ta很懒什么都没有留下', 'uid': 'wxsso_nz297durpu', 'avatar': 'http://wx.qlogo.cn/mmopen/gobtgL6xn9Z6KMsibqkqWeOa8Npickk1XKUbrwIWASjw40vdNWUT74PxVIdFe8FmAQu80Yq01rx4WL74rULianT2iaSz5PKgAedH/0', 'suid': '64tfU0JCV~O2YyFVR7sRGw__', 'video_count': '11'}, {'followed': '6827071', 'nickname': '最神奇的视频', 'follow': '11', 'descr': '搞笑，预告，你的喜怒哀乐这里都能看到，通过视频，让你感', 'uid': 'sina_0udpfn0a2h', 'avatar': 'http://tp4.sinaimg.cn/2141823055/180/5621846443/0', 'suid': 'lfMtGJsFJMlMhYm2', 'video_count': '3455'}, {'followed': '352', 'nickname': '扬名止过', 'follow': '14', 'descr': '波澜不惊，荣辱不争。', 'uid': 'paike_8iqcuo8pko', 'avatar': 'http://tp2.sinaimg.cn/1583429645/180/5621703354/1', 'suid': 'gn2U51iUx4PT6k8-', 'video_count': '0'}, {'followed': '499', 'nickname': '段蓓珊', 'follow': '13', 'descr': '……', 'uid': 'paike_c4i54d6ey2', 'avatar': 'http://tp2.sinaimg.cn/1670302465/180/5632141584/0', 'suid': '1Kev5Dmc1H7SMMnX', 'video_count': '1'}, {'followed': '145', 'nickname': '胖大星Alis', 'follow': '0', 'descr': 'ta很懒什么都没有留下', 'uid': 'paike_76o4l8zotz', 'avatar': 'http://tp3.sinaimg.cn/1760582170/180/5709471341/0', 'suid': 'epu~2vdSHF23E0Q-', 'video_count': '1'}, {'followed': '295', 'nickname': '文史_海巴子', 'follow': '0', 'descr': 'ta很懒什么都没有留下', 'uid': 'paike_7bnuhrz12h', 'avatar': 'http://tp2.sinaimg.cn/2624069177/180/5634691164/1', 'suid': 'CGTQC2jMVAA4Me26', 'video_count': '0'}, {'followed': '5880191', 'nickname': '英国那些事儿', 'follow': '45', 'descr': '一个在英国爱吐槽的主页君.没事爱分享英国最搞最有意思大', 'uid': 'paike_t9y36wkt4c', 'avatar': 'http://tp3.sinaimg.cn/2549228714/180/40021372518/1', 'suid': 'Ii9QcPCa~novHdgc', 'video_count': '744'}, {'followed': '12312', 'nickname': '每天搞笑排行榜', 'follow': '6', 'descr': 'ta很懒什么都没有留下', 'uid': 'paike_oqbmsp87kq', 'avatar': 'http://tp3.sinaimg.cn/2281122894/180/5661656420/0', 'suid': 'PQX0xTUI4fgV~s3v', 'video_count': '0'}, {'followed': '3414317', 'nickname': '史上第一最最搞', 'follow': '7', 'descr': 'ta很懒什么都没有留下', 'uid': 'paike_pomohtzbiw', 'avatar': 'http://tp1.sinaimg.cn/1134796120/180/40069206893/0', 'suid': '3Xlno6tiKcXS6noq', 'video_count': '5000'}, {'followed': '63631', 'nickname': '霍泥芳', 'follow': '8', 'descr': '＜夏天有风吹过＞里，我是内向叛逆的半夏；＜幸福生活在招', 'uid': 'paike_4kf51dy2de', 'avatar': 'http://tp1.sinaimg.cn/1277126544/180/5641596294/0', 'suid': 'yVwNg6clktoWe-Ib', 'video_count': '10'}, {'followed': '20308', 'nickname': 'M大王叫我来巡', 'follow': '0', 'descr': 'ta很懒什么都没有留下', 'uid': 'paike_rx2xp66tks', 'avatar': 'http://tp4.sinaimg.cn/1720173771/180/40048639291/1', 'suid': 'tJ2tClKrqCYm6uDc', 'video_count': '26'}, {'followed': '7195252', 'nickname': 'gogoboi', 'follow': '12', 'descr': '冒着脑残的炮火前进，前进，前进进！工作联系：gogob', 'uid': 'paike_bg95tflssd', 'avatar': 'http://tp2.sinaimg.cn/1706372681/180/40017354355/1', 'suid': 's5u1-93x2yMZx6NM', 'video_count': '20'}, {'followed': '8929355', 'nickname': '秒拍', 'follow': '659', 'descr': '秒拍-10秒拍大片！', 'uid': 'paike_i1dudsh696', 'avatar': 'http://dynimg3.yixia.com/square.124/storage.video.sina.com.cn/user-icon/EfFEP4pOsmYCl0Nf_480__1438164133711.jpg', 'suid': 'EfFEP4pOsmYCl0Nf', 'video_count': '622'}]
"""

### 获取某用户的视频列表
suid = 'ZPWwDeYSvPUb23SL'
page = 1
ret = YiXia().get_video_list(suid, page)
print(ret)
"""
[{'scid': 'Svl4iqHkBsM~DCNCf0WPsQ__', 'detail_page': 'http://www.yixia.com/show/Svl4iqHkBsM~DCNCf0WPsQ__.htm', 'praised': 2321, 'discussed': 3258, 'flash': 'http://wscdn.miaopai.com/splayer2.2.0.swf?scid=Svl4iqHkBsM~DCNCf0WPsQ__&fromweibo=false&fromweibo=false&token=', 'img': 'http://wsacdn4.miaopai.com/stream/Svl4iqHkBsM~DCNCf0WPsQ___tmp_11_409_.jpg', 'title': '“难道只有我一个人觉得吗？”是呀！当然只有你一个人觉得！你多厉害呀！你最与众不同啦！你存在感爆棚！（祝大家一周&周一愉快嗷~比心~最近的雾霾超好吸超带感超咳咳咳咳咳咳咳咳咳', 'pub_date': '17:44', 'watched': 4680000}, {'scid': 'd5xoiWIzy9edsWtNhNZBEw__', 'detail_page': 'http://www.yixia.com/show/d5xoiWIzy9edsWtNhNZBEw__.htm', 'praised': 29000, 'discussed': 4347, 'flash': 'http://wscdn.miaopai.com/splayer2.2.0.swf?scid=d5xoiWIzy9edsWtNhNZBEw__&fromweibo=false&fromweibo=false&token=', 'img': 'http://wsacdn1.miaopai.com/stream/d5xoiWIzy9edsWtNhNZBEw___tmp_11_354_.jpg', 'title': '“现在的观众，根本不知道什么才是好电影”，资深影迷pa某酱表示。近期影片盘点，该看什么？看点在哪儿？pa某酱让你更迷惑。（本视频纯属胡说八道，不接受任何反驳，比心️', 'pub_date': '12-17', 'watched': 8200000}, {'scid': 'd3Ph834EJZtuSNeSL7AJng__', 'detail_page': 'http://www.yixia.com/show/d3Ph834EJZtuSNeSL7AJng__.htm', 'praised': 27000, 'discussed': 56, 'flash': 'http://wscdn.miaopai.com/splayer2.2.0.swf?scid=d3Ph834EJZtuSNeSL7AJng__&fromweibo=false&fromweibo=false&token=', 'img': 'http://wsacdn3.miaopai.com/stream/d3Ph834EJZtuSNeSL7AJng___tmp_11_741_.jpg', 'title': 'papi酱不定期更新的日常——pa老师的英语课。同学们', 'pub_date': '12-16', 'watched': 20240000}, {'scid': 'ZzRKTzzvM6WgNZbLRO2HUg__', 'detail_page': 'http://www.yixia.com/show/ZzRKTzzvM6WgNZbLRO2HUg__.htm', 'praised': 29000, 'discussed': 93, 'flash': 'http://wscdn.miaopai.com/splayer2.2.0.swf?scid=ZzRKTzzvM6WgNZbLRO2HUg__&fromweibo=false&fromweibo=false&token=', 'img': 'http://qncdn.miaopai.com/stream/ZzRKTzzvM6WgNZbLRO2HUg___qnweb_14818081966424.jpg', 'title': '“爱所有人，信任一些人，不伤害任何人。”这句莎剧的台词，是我在自己的视频中一直想要传达的，也是我静下来的时候不断回想的。不知多少人能接受这个视频里这样的我，希望你们看完后能认识并且接受一个或许不太熟悉的papi。（实不相瞒，这个视频，我是捂着眼睛看的（评论里不要截图给我（我羞赧...', 'pub_date': '12-15', 'watched': 21190000}]
"""
```
* 沃米优选(http://video.51wom.com/)

### TODO:
* 映客(http://www.inke.cn/hotlive_list.html)
* 斗鱼(https://www.douyu.com/)
* 微信公众号

### 代码逻辑请参考以下文章：
#####[Python初学者之网络爬虫](http://mp.weixin.qq.com/s/vNcQtXWjGHnc6JMjt_vWiQ "Python初学者之网络爬虫")
#####[Python初学者之网络爬虫(二)](http://mp.weixin.qq.com/s/WoLKDnaFBcJ-u3msAqtDNw "Python初学者之网络爬虫(二)")
