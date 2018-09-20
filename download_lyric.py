# -*- coding: utf-8 -*-
#from cloudmusic_new import *
from ncmbot.core import lyric
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
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

client=pm.MongoClient('192.168.1.109',27017)

db=client.cloudmusic
coll=db.lyrics

data_addr='/home/wengyutao/data_collect/allData_lyrics/'
user_addr='/home/wengyutao/data_collect/user_record/'

'''
proxyHost = "proxy.abuyun.com"
proxyPort = "9020"

proxyUser = "H0714433900N52ZD"
proxyPass = "C39EAC44A6405179"

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host" : proxyHost,
    "port" : proxyPort,
    "user" : proxyUser,
    "pass" : proxyPass,
}

proxies = {
    "http"  : proxyMeta,
    "https" : proxyMeta,
}
'''

def download_by_sid(sid):
    print sid,"is dealing"
    lrc_path=data_addr+str(sid)+'.json'
    lrc_data=coll.find_one({'_id':int(sid)})
    if lrc_data==None:
        if os.path.exists(lrc_path):
            coll.save({'_id':int(sid),'ifDownload':True})
        else:
            song_lrc= json.loads(lyric(sid).content, encoding='utf8')#get_lyric(sid)
            #print song_lrc
            time.sleep(0.5)
            if song_lrc['code']==200 and song_lrc.has_key('lrc'):
                if song_lrc['lrc'].has_key('lyric'):
                    if song_lrc['lrc']['lyric']!=None and song_lrc['lrc']['lyric']!='':
                        json.dump(song_lrc,open(lrc_path,'w'),indent=4,ensure_ascii=False)
            if os.path.exists(lrc_path):
                coll.save({'_id':int(sid),'ifDownload':True})
                print sid,"is saving"
            else:
                coll.save({'_id':int(sid),'ifDownload':False})
    else:
        print sid,"is saved"


def task(sids):
    for sid in sids:
        download_by_sid(sid)
        #print sid,' is done'


def main():
    sids=[]
    f=open('user-like-songs-20170825.txt')
    f_lines=f.readlines()
    for line in f_lines[1:]:
        line_str=line.split(',')
        sids.append(line_str[0].strip())
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
        send_email.alert('获取歌词数据：' + str(e))
    #get_urls()
    #cutFiles()
    #print json.loads(lyric('193473').content, encoding='utf8')
    #url='http://m10.music.126.net/20170615165458/5d50583ae0565bdbc6d54bda3067fef9/ymusic/629e/da85/36aa/2de7e2ece7df32ef2aa8abd5c1f45ed4.mp3'
    
