# -*- coding: utf-8 -*-

import time
import datetime
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

import download_comments as dc
import download_lyric as dl

reload(sys)
sys.setdefaultencoding( "utf-8" )

client=pm.MongoClient('192.168.1.109',27017)

db=client.cloudmusic
coll=db.toplists


def deal_song(sid):
    dc.download_by_sid(sid)
    print sid,"'s comments is saved"
    dl.download_by_sid(sid)
    print sid,"'s lyrics is saved"


def down_his():
    print "history"
    _ids = []
    for _item in coll.find({}):
        for _song in _item['result']['tracks']:
            _ids.append(_song['id'])
    _ids_new = list(set(_ids))
    f_top = open('topsongs_ids_0828.txt','w')
    index = 0
    for item in _ids_new:
        print index,str(item)
        f_top.write(str(item)+'\n')
        index+=1
    f_top.close()

def down_today():
    print "today is "
    _today = datetime.date.today().strftime('%Y%m%d')
    print _today
    for index in range(22):
        _id = _today + '-'+str(index)    
        _data = coll.find_one({'_id':_id})
        if _data:
            print _id
            for _song in _data['result']['tracks']:
                try:
                    deal_song(_song['id'])
                except Exception,e:
                    print e
                    continue
                    


if __name__  =="__main__":
    down_today()
