# -*- coding: utf-8 -*-
import sys
import uuid
import requests
import hashlib
import time
from importlib import reload
import json
import pymysql


reload(sys)

YOUDAO_URL = 'https://openapi.youdao.com/api'
APP_KEY = '1111316018731097'
APP_SECRET = 'XaeVt4VJKDh4WSPmdnqL4GoCpmJ2A7x2' 

def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


def connect(q_str):
    q = q_str #"Skipping meals could potentially push your blood glucose higher. When you don't eat."

    data = {}
    data['from'] = 'en'
    data['to'] = 'zh-CHS'
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign
    data['vocabId'] = "您的用户词表ID"

    response = do_request(data)
    contentType = response.headers['Content-Type']
    if contentType == "audio/mp3":
        millis = int(round(time.time() * 1000))
        filePath = "合成的音频存储路径" + str(millis) + ".mp3"
        fo = open(filePath, 'wb')
        fo.write(response.content)
        fo.close()
    elif contentType =="translation":
        #print(response.content)
        result_text=json.loads(response.content.decode('utf-8'))['translation'][0]
        #print(result_text)
        return result_text
    else:
        return ""


if __name__ == '__main__':

    #connect()
    # 连接数据库，
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='lsplsp620',
        db='diabetes',
        charset='utf8',
        # autocommit=True,    # 如果插入数据，， 是否自动提交? 和conn.commit()功能一致。
    )
    cur = conn.cursor()
    sql = "select content from external_link"
    cur.execute(sql)

    trans = []
    while True:
        row = cur.fetchone()
        if not row:
            break
        else:
            q_str = row[0]
            trans.append(connect(q_str))
        
    cur.close()

    cs1 = conn.cursor()
    num = 1
    for item in trans:
        item = item.replace('\'','\\\'') # 处理python字符串组成MySql命令时，字符串含有单引号或者双引号导致出错
        item = item.replace('"','\\\"')
        query ="update external_link set content_ch = \"{}\" where id = {}".format(item, num)
        num = num + 1
        cs1.execute(query)

    # 提交之前的操作，如果之前已经执行多次的execute，那么就都进行提交
    conn.commit()

    # 关闭cursor对象
    cs1.close()
    # 关闭connection对象
    conn.close()

