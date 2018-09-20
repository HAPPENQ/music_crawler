#coding:utf8

from core import music_comment 
import json

re = music_comment('408055514')
print(json.loads(re.content, encoding='utf8'))
