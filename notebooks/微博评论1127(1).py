# _*_ conding : utf-8 _*_
# @Time : 2023/11/27 17:13
# @File : 微博评论1127
# @Project : pachong
import csv
import time

import requests


def get_req(url,headers):
    reqtimes = 0
    while True:
        try:
            reqtimes += 1
            req = requests.get(url=url,headers=headers)
            time.sleep(1)
            if req.status_code == 200:
                return req
        except Exception as e:
            time.sleep(3)
            if reqtimes > 20:
                return None
            if "HTTPSConnectionPool(host='s.weibo.com', port=443)" in str(e):
                continue

def get_plUrl(mid,uid):
    count = 1
    pl_url = f'https://weibo.com/ajax/statuses/buildComments?is_reload=1&id={mid}&is_show_bulletin=2&is_mix=0&count=10&uid={uid}&fetch_level=0&locale=zh-CN'
    while 1:
        # 拿评论, 同时拿到下一页的max_id,
        max_id = get_comment(pl_url)
        print(max_id)
        if max_id == 0:
            print('=========爬取完毕==========')
            break
        print(f'第{count}页完成')
        # 构建下一页的url
        count += 1
        pl_url =f"https://weibo.com/ajax/statuses/buildComments?flow=0&is_reload=1&id={mid}&is_show_bulletin=3&is_mix=0&max_id={max_id}&count=20&uid={uid}&fetch_level=0&locale=zh-CN"
        print(pl_url)
        time.sleep(1)

def get_comment(pl_url):
    """一级评论"""
    r = get_req(pl_url,headers).json()
    # max_id的值
    max_id = r['max_id']
    # 所有的评论
    data = r['data']

    # 遍历得到每一条评论
    for i in data:
        # 评论内容
        comment = i['text_raw']
        # 当前评论的id
        level_id = i['idstr']
        print(comment)
        with open('./微博评论5.csv',mode='a',encoding='utf-8-sig',newline='')as fp:
            csv_writer = csv.writer(fp)
            csv_writer.writerow([comment])
        time.sleep(5)
        # 二级评论的url
        level_url = "https://weibo.com/ajax/statuses/buildComments?is_reload=1&id=%s&is_show_bulletin=2&is_mix=1&fetch_level=1&max_id=0&count=20&uid=%s" % (level_id, uid)
        level_split_url = "https://weibo.com/ajax/statuses/buildComments?flow=1&is_reload=1&id=%s&is_show_bulletin=2&is_mix=1&fetch_level=1&max_id={}&count=20&uid=%s" % (level_id, uid)
        while 1:
            level_max_id = get_level_comment(level_url)
            # 二级评论返回结果是0, 就代表抓取二级评论完毕
            if level_max_id == 0:
                break
            level_url = level_split_url.format(level_max_id)

    return max_id

def get_level_comment(level_url):
    """二级评论"""
    print(level_url)
    r = get_req(level_url,headers).json()
    # max_id的值
    level_max_id = r['max_id']
    # 所有的评论
    data = r['data']
    for i in data:
        comment = i['text_raw']
        print(comment)
        with open('./微博评论5.csv',mode='a',encoding='utf-8-sig',newline='')as fp:
            csv_writer = csv.writer(fp)
            csv_writer.writerow([comment])
        time.sleep(5)
    return level_max_id

if __name__ in '__main__':
    # url示例：https://weibo.com/2144596567/NnGCX8MDx
    url = 'https://weibo.com/1458470903/NnRqOELWR#comment'
    headers = {
        'Cookie': 'SINAGLOBAL=3015057945737.2207.1697207942757; UOR=,,login.sina.com.cn; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5H-EjpOgbAr0liA7ApzHve5JpX5KMhUgL.FoqfSonfShq41Ke2dJLoIEXLxK-L1K2L1hqLxKnL1K5L12eLxKML1K.LB.BLxK-LBo.LB.BLxKML1h2LBo-t; ALF=1703253405; SCF=AtuTjGv7kcFJKnM_Rs3kvEo1MNetNQHYCkON2ovjFGPtAH5YAukLc0har22aoxOnGFez9PXbd44f1n5SdPlaJKE.; SUB=_2A25IWnjODeThGeBL7VoU9CjFwj-IHXVrFvQGrDV8PUNbmtANLXLYkW9NRvJY1WsRVavJ9yqjfEPHXD2FEMKzZJ1z; ULV=1700745073232:17:9:8:4581705907291.285.1700745073179:1700661418044; XSRF-TOKEN=DTVbgXHW7CbNd3-oSQ0hZc_7; WBPSESS=u_to8mj6poWe0i48T87iAJVf9X9pg2t2dTFKQl2WmCYg0FtLyEw3bpRYzQ7DjUnGaquOtewjvEqqpsHCy78fglRqXJbrWZyc4xjptShpcRitXqOeAIYbnf2uxCd_5W3RDkbtQRUew-4CZ-F6Uha2JA==',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
    }
    split_url = url.split('/')
    code = split_url[-1]
    uid = split_url[3]
    print(code)
    print('uid:'+uid)
    codeurl = f'https://weibo.com/ajax/statuses/show?id={code}&locale=zh-CN'
    mid_req = get_req(codeurl,headers)
    mid_json = mid_req.json()
    mid = mid_json['mid']
    print('mid:'+mid)
    get_plUrl(mid, uid)
