from bs4 import BeautifulSoup
import os
import sqlite3
import string

try:
    os.remove('weibo.db')
except:
    pass

con = sqlite3.connect('weibo.db')

class Table(object):
    key = []
    schema = {}

    @classmethod
    def getKeys(cls):
        return ','.join(cls.key)

    @classmethod
    def getSchema(cls):
        return ','.join('%s %s' % (k, cls.schema.get(k)) for k in cls.key)

    @classmethod
    def create_db(cls):
        print 'CREATE TABLE %s(%s)' % (cls.name, cls.getSchema())
        con.cursor().execute('CREATE TABLE %s ( %s )' % (cls.name, cls.getSchema()))

    @classmethod
    def insert(cls, *args, **kargs):
        val = {}
        parameters = []
        placeholder = []
        for k in cls.key:
            v = kargs.get(k, None)
            if v is None:
                continue
            val[k] = v
            parameters.append(k)
            placeholder.append(':' + k)

        cursor = con.cursor()
        cursor.execute('INSERT INTO %s(%s) VALUES(%s)' % \
                (cls.name, ','.join(parameters), ','.join(placeholder)), val)
        return cursor.lastrowid

class Weibo(Table):
    key = [
        'keyword', 
        'nick', 
        'content', 
        'post_time', 
        'post_from', 
        'collect_cnt', 
        'forward_cnt', 
        'like_cnt', 
        'comment_cnt', 
        'forward_from'
    ]

    schema = {
        'keyword'     : 'TEXT',
        'nick'        : 'TEXT',
        'content'     : 'TEXT',
        'post_time'   : 'TEXT',
        'post_from'   : 'TEXT',
        'collect_cnt' : 'INTEGER',
        'forward_cnt' : 'INTEGER',
        'like_cnt'    : 'INTEGER',
        'comment_cnt' : 'INTEGER',
        'forward_from': 'INTEGER'
    }

    name = 'weibo'

class Face(Table):
    key = ['fromid', 'face']

    schema = {
        'fromid': 'INTEGER',
        'face' : 'TEXT'
    }
    
    name = 'face'

def get_pub_from(node):
    if node is None:
        return ''

    if node.string is None:
        return ' '.join(node.strings)

    return repr(node.string)

def get_action(node):
    key = ['conllect_cnt', 'forward_cnt', 'like_cnt', 'comment_cnt']
    action = {
        'collect_cnt' : 0,
        'forward_cnt' : 0,
        'like_cnt'    : 0,
        'comment_cnt' : 0
    }
    if node is None:
        return action

    li = node.find_all('li')
    i = 0
    if len(li) > 3:
        i = 1
    while i < len(li):
        num = li[i].find('em')
        if num is not None:
            cnt_str = ''.join(num.strings)
            print i, cnt_str

        if cnt_str.isdigit():
            action[key[i]] = string.atoi(cnt_str)

        i = i + 1

    return action

def create_db():
    Weibo.create_db()
    Face.create_db()

def parse_weibo(node, keyword):
    weibo = {
        'keyword': keyword
    }

    a = node.find('a', attrs={'class': 'W_fb'})
    weibo['nick'] = a['nick-name']

    p = node.find('p', attrs={
        'class': 'comment_txt'
    })
    weibo['content'] = ' '.join(p.strings)

    weibo['post_time'] = node.find('a', attrs={'class': 'W_textb'})['date']

    weibo['post_from'] = get_pub_from(node.find('a', attrs={'rel': 'nofollow'}))

    ul = node.find_all('ul', attrs={
        'class': 'feed_action_info'
    })

    action = {
        'collect_cnt' : 0,
        'forward_cnt' : 0,
        'like_cnt'    : 0,
        'comment_cnt' : 0
    }
    if ul is not None:
        if len(ul) > 1:
            action = get_action(ul[1])
        elif len(ul) > 0:
            action = get_action(ul[0])

    for k, v in action.items():
        weibo[k] = v

    return weibo

def parse_face(node, lastrowid):
    faces = node.find_all('img', attrs={'type': 'face'})
    for face in faces:
        f = {}
        f['fromid'] = lastrowid
        f['face'] = face['alt']

        Face.insert(**f)

def parse(filename):
    bs = BeautifulSoup(open(filename))
    res = bs.find_all('div', attrs={
        'action-type': 'feed_list_item'
    })

    count = 1
    for node in res:
        print 'parsing %s' % count
        weibo = parse_weibo(node, 'duang')

        comment = node.find('div', attrs={'class': 'comment'})
        if comment is not None:
            origin_weibo = parse_weibo(comment, 'duang')
            lastrowid = Weibo.insert(**origin_weibo)
            parse_face(comment, lastrowid)
            weibo['forward_from'] = lastrowid
        else:
            weibo['forward_from'] = 0

        lastrowid = Weibo.insert(**weibo)
        parse_face(node, lastrowid)

        count = count + 1

if __name__ == '__main__':
    create_db()
    parse('tmp')

    con.commit()
    con.close()
