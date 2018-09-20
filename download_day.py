#coding:utf8

import json
import multiprocessing
import os
import random
import time
import datetime
from Queue import Queue
from concurrent.futures import ThreadPoolExecutor

import pymongo
import requests
from ncmbot.core import user_record

import send_email
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

coll = pymongo.MongoClient('192.168.1.109', 27017).cloudmusic.day
data_addr = '/home/kayzhou/data_collect/allData_day/'

uid_queue = Queue()
for line in open('data/uids.txt'):
    uid = line.strip().split(',')[0]
    uid_queue.put(uid)


def get_listen_count(uid):
    r = requests.get('http://192.168.1.151:40002/get_nums?uid={}'.format(uid))
    return r.json()['result']


def get_week(uid):
    r = user_record(uid, type=1)
    return json.loads(r.content, encoding='utf8')


def get_uids():
    return [ line.strip().split(',')[0] for line in open('data/uids.txt') ]


def download_by_uid(dt, sid):

    _id = str(dt) + '-' + str(sid)
    data_path = data_addr + _id + '.txt'
    if os.path.exists(data_path) and os.path.getsize(data_path) > 1:
        return 0

    if coll.find_one({'_id': _id}, {'_id': 1}):
        return 0

    data_path = data_addr + _id + '.txt'
    try:
        data = get_week(sid)
    except:
        print sid, 'should crawl it again'
        time.sleep(10)
        return -1

    data['_id'] = _id
    data['update_time'] = datetime.datetime.today().strftime('%c')
    # data['listen_count'] = get_listen_count(sid) 该接口目前有问题

    if data['code'] == 200:
        # json.dump(data, open(data_path, 'w'), indent=4, ensure_ascii=False)
        time.sleep(3)
        coll.save(data)
        print _id, "获取成功"
    else:
        print _id, "获取失败"


def task():
    dt = datetime.datetime.today().strftime('%Y%m%d')
    while True:
        left = uid_queue.qsize()
        print '剩余用户:', left
        if left == 0:
            break
        uid = uid_queue.get()
        download_by_uid(dt, uid)


def main():
    thread_count = 8
    pool = ThreadPoolExecutor(max_workers=thread_count)
    for i in range(thread_count):
        pool.submit(task)


if __name__=='__main__':
    try:
        # download_by_uid('20180322', '49862001')
        main()
    except Exception,e:
        print e
        send_email.alert('获取每日听歌数据：' + str(e))
