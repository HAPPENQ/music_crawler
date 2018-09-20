#coding:utf8
import pymongo as pm
import separate as sp
import datetime
import json
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

client = pm.MongoClient('192.168.1.109',27017)

db = client.cloudmusic
coll_tp = db.toplists
coll_lrc = db.lyrics
coll_sf = db.song_features
coll_comments = db.comments

feature_dir = '/home/wengyutao/data_collect/allData_features/'

have_ids = set()
have_songs_ids=coll_sf.find({},{'_id':1})
for _sid in have_songs_ids:
    have_ids.add(str(_sid['_id']))
#print "have_ids is saved",have_ids

def ex_today():
    print "today is "
    _today = datetime.date.today().strftime('%Y%m%d')
    print _today
    for index in range(22):
        _id = _today + '-'+str(index)
        _data = coll_tp.find_one({'_id':_id})
        if _data:
            print _id
            ex_toplist(_data)
            #print 'have_ids:',have_ids


def ex_all_toplists():
    _toplists = coll_tp.find({})
    for _toplist in _toplists:
        print 'id!!!!!!!!!!!!!!!!!!!!!!!!!!!!!:',_toplist['_id']
        ex_toplist(_toplist)
        print 'have_ids:',have_ids


def ex_toplist(songs):
    #songs = coll_tp.find_one({'_id':'20170914-0'})
    for song in songs['result']['tracks']:
        if str(song['id']) in have_ids:
            continue
        print song['id'],' is dealing...'
        feature = {}
        feature['name'] = song['name']
        feature['popularity'] = song['popularity']
        feature['duration'] = song['duration']
        feature['artist'] = song['artists'][0]['name']
        feature['album'] = song['album']['name']
        
        _lrc = ex_lyric(song)
        feature['lrc_tags'] = _lrc['lrc_tags']
        feature['tlrc_tags'] = _lrc['tlrc_tags']
        
        _comment = ex_comment(song)
        if len(_comment['tags'])>100:
            save_tags = _comment['tags'][0:100]
        feature['comments'] = save_tags
        
        coll_sf.update({'_id':song['id']},{'$setOnInsert': feature},True)
        #files
        #feature['comments'] = _comment['tags']
        feature['lrc'] = _lrc['lrc']
        feature['tlrc'] = _lrc['tlrc']
        feature['hotComments'] = _comment['hot']
        feature['comments'] = _comment['comment']
        json.dump(feature,open(feature_dir+str(song['id'])+'.json','w'),ensure_ascii=False)       
        have_ids.add(song['id'])
        print song['id'],'is saved'

def ex_lyric(song):
    _lrcdata = coll_lrc.find_one({'_id':int(song['id'])})
    if _lrcdata:
        if _lrcdata['ifDownload'] ==True:
            _lrc = sp.deal_lyric(str(song['id']))
            return _lrc
    return {'lrc':[],'tlrc':[],'lrc_tags':[],'tlrc_tags':[]}


def ex_comment(song):
    _commentdata = coll_comments.find_one({'_id':int(song['id'])})
    if _commentdata:
        return sp.deal_comment(str(song['id']))
    return {'hot':[],'comment':[],'tags':[]}



if __name__ =="__main__":
    #ex_all_toplists()
    ex_today()
    #print have_ids
