#coding:utf8
from ncmbot.core import play_list_detail,song_detail

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
import datetime
import send_email
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

client = pm.MongoClient('192.168.1.109',27017)

db=client.cloudmusic
coll=db.toplists

data_addr = '/home/wengyutao/data_collect/allData_toplists/'

Toplists = [
	  {'name':u'云音乐新歌榜','weekly':False,'idx':0,'id':'3779629'},
          {'name':u'云音乐热歌榜','weekly':True,'idx':1,'id':'3778678'},
          {'name':u'网易原创歌曲榜','weekly':True,'idx':2,'id':'2884035'},
          {'name':u'云音乐飙升榜','weekly':False,'idx':3,'id':'19723756'},
          {'name':u'云音乐电音榜','weekly':True,'idx':4,'id':'10520166'},
          {'name':u'UK排行榜周榜','weekly':True,'idx':5,'id':'180106'},
          {'name':u'美国Billboard周榜','weekly':True,'idx':6,'id':'60198'},
          {'name':u'KTV嗨榜','weekly':True,'idx':7,'id':'21845217'},
          {'name':u'iTunes榜','weekly':True,'idx':8,'id':'11641012'},
          {'name':u'Hit FM Top榜','weekly':True,'idx':9,'id':'120001'},
          {'name':u'日本Oricon周榜','weekly':True,'idx':10,'id':'60131'},
          {'name':u'韩国Melon排行榜周榜','weekly':True,'idx':11,'id':'3733003'},
          {'name':u'韩国Mnet排行榜周榜','weekly':True,'idx':12,'id':'60255'},
          {'name':u'韩国Melon原声周榜,','weekly':True,'idx':13,'id':'46772709'},
          {'name':u'中国TOP排行榜(港台榜)','weekly':True,'idx':14,'id':'112504'},
          {'name':u'中国TOP排行榜(内地榜)','weekly':True,'idx':15,'id':'64016'},
          {'name':u'香港电台中文歌曲龙虎榜','weekly':True,'idx':16,'id':'10169002'},
          {'name':u'华语金曲榜','weekly':True,'idx':17,'id':'4395559'},
          {'name':u'中国嘻哈榜','weekly':True,'idx':18,'id':'1899724'},
          {'name':u'法国 NRJ EuroHot 30周榜','weekly':True,'idx':19,'id':'27135204'},
          {'name':u'台湾Hito排行榜','weekly':True,'idx':20,'id':'112463'},
          {'name':u'Beatport全球电子舞曲榜','weekly':True,'idx':21,'id':'3812895'}
]


def get_toplist_data():
    error = False
    day = datetime.datetime.now()
    weekday=day.weekday()
    print 'today is :', weekday
    
    for _toplist in Toplists:
        print _toplist['name'],'is crawling...'
        if weekday !=0 and _toplist['weekly']==True:
            print 'It doesn\'t need to crawl today!'
            continue
        time.sleep(10)
        try:
            _return = play_list_detail(_toplist['id'],100)
            #_return = toplist(_toplist['id']) # get_top_list(toplist['idx'])
            data_toplist = json.loads(_return.content, encoding='utf8')
        except Exception,e:
            print _toplist['idx'],e
            continue
        #print len(data_toplist['result']['tracks'])
        if data_toplist['code'] == 200:
            d = data_toplist
            d['_id'] = day.strftime('%Y%m%d') + '-' + str(_toplist['idx'])
            d['result'] = d['playlist']
            del(d['playlist'])
            ids = []
            for _id in d['result']['trackIds']:
                ids.append(_id['id'])
            #print ids
            _details = json.loads(song_detail(ids).content)
            
            if _details['code'] == 200:
                d['result']['tracks'] = _details['songs']
            toplist_path = data_addr + d['_id']+'.json'
            json.dump(d,open(toplist_path,'w'), indent=4, ensure_ascii=False)    
            coll.save(d)
            print 'Data has saved!'
        else:
            print data_toplist
            print 'Data couldn\'t be crawled!'
	    error = True
    if error:
	send_email.alert('获取榜单出错！')
	

if __name__ == '__main__':
    try:
        #print json.loads(toplist('3779629').content)
        get_toplist_data()
    except Exception,e:
    	send_email.alert(str(e)+ '获取榜单出错！')
