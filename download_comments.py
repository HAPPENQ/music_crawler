# -*- coding: utf-8 -*-
from ncmbot.core import music_comment
import time
import random
import json
import urllib2
import urllib
import requests
import csv
import os
import multiprocessing
import pymongo as pm
import send_email
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
client=pm.MongoClient('192.168.1.109',27017)
db=client.cloudmusic
coll=db.comments
data_addr='/home/wengyutao/data_collect/allData_comments/'


have_songs=set()
have_songs_ids=coll.find({},{'_id':1})
for _sid in have_songs_ids:
    have_songs.add(str(_sid[u'_id']))


def download_all_comments(sid):
    
    comments_path=data_addr+str(sid)+'.json'
    limit=100
    offset=0
    bingo=False
    data={}
    comments_1000 = []
    while True:
        try:
            _return=music_comment(sid,offset,limit)
            d = json.loads(_return.content, encoding='utf8')
            time.sleep(7)
        except Exception,e:
            print sid,e
            continue
        offset+=limit
        if d['code']!=200:
            break
        if data.has_key('code'):
            data['comments'].extend(d['comments'])
        else:
            data=d
            data['_id']=int(sid)
        if d['more']==False:
            bingo=True
            break
        if len(data['comments'])<=1000:
            comments_1000 = data['comments']
        #if len(data['comments'])>10000:
        #    bingo = True
        #    break
    if bingo:
        data['my_total'] = len(data['comments'])
        json.dump(data,open(comments_path,'w'),ensure_ascii=False)
        data_save = data
        data_save['comments'] = comments_1000
        coll.save(data_save)
        print sid, " has been saved."


def download_by_sid(sid):
    if sid in have_songs:
        return 0
    
    comments_path=data_addr+str(sid)+'.json'
    limit=100
    offset=0
    bingo=False
    data={}
    comments_1000 = []
    comment_data=coll.find_one({'_id':int(sid)})
    if comment_data==None:
        if os.path.exists(comments_path):
            comment_data=json.loads(open(comments_path))
            coll.save(comment_data)
        else:
            while True:
                try:
                    _return=music_comment(sid,offset,limit)
                    d = json.loads(_return.content, encoding='utf8')
                    time.sleep(7)
                except Exception,e:
                    print sid,e
                    continue
                offset+=limit
                if d['code']!=200:
                    break
                if data.has_key('code'):
                    data['comments'].extend(d['comments'])
                else:
                    data=d
                    data['_id']=int(sid)
                if d['more']==False:
                    bingo=True
                    break
                if len(data['comments'])<=1000:
                    comments_1000 = data['comments']
                if len(data['comments'])>10000:
                    bingo = True
                    break
            if bingo:
	        data['my_total'] = len(data['comments'])
                json.dump(data,open(comments_path,'w'),ensure_ascii=False)
                data_save = data
                data_save['comments'] = comments_1000
                coll.save(data_save)
                print sid, " has been saved."


def task(sids):
    for sid in sids:
        print sid
        if sid in have_songs:
            continue
        #download_by_sid(sid)
        download_all_comments(sid)

def main():
    sids=[]
    f=open('user-like-songs-20170825.txt')
    for line in f:
        sids.append(line.strip())
    task(sids)
    return 0

    task_cnt=3
    step=int(len(sids)/3)
    for i in range(task_cnt):
        if i ==task_cnt-1:
            slice_sids=sids[i*step:]
        else:
            slice_sids=sids[i*step:(i+1)*step]
        t=multiprocessing.Process(target=task,args=(slice_sids,))
        t.start()


if __name__=='__main__':
    try:
        main()
    except Exception,e:
        print e
        send_email.alert('获取评论数据：' + str(e))
