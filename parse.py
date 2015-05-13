from bs4 import BeautifulSoup
import sqlite3
import string

con = sqlite3.connect('weibo.db')

class blog(object):
    key = ['nick', 'content', 'post_time', 'post_from',
            'collect_cnt', 'forward_cnt', 'like_cnt', 'comment_cnt']

    schema = {
        'nick'       : 'TEXT',
        'content'    : 'TEXT',
        'post_time'  : 'TEXT',
        'post_from'  : 'TEXT',
        'collect_cnt': 'INTEGER',
        'forward_cnt': 'INTEGER',
        'like_cnt'   : 'INTEGER',
        'comment_cnt': 'INTEGER'
    }

    @staticmethod
    def getKeys():
        return ','.join(blog.key)

    @staticmethod
    def getSchema():
        return ','.join('%s %s' % (k, blog.schema.get(k)) for k in blog.key)

    @staticmethod
    def new(nick, content, post_time, post_from, action):
        # val = '%s, %s, %s, %s, %s, %s, %s, %s' % \
        #         (nick, content, post_time, post_from, \
        #         action[0], action[1], action[2], action[3])
        # val = val.decode('unicode-escape').encode('utf-8')

        val = (nick, content, post_time, post_from, \
                action[0], action[1], action[2], action[3])
        con.cursor().execute( \
                'INSERT INTO blog VALUES(?, ?, ?, ?, ?, ?, ?, ?)', val)

def create_db():
    con.cursor().execute('CREATE TABLE blog (%s)' % blog.getSchema())
    print blog.getSchema()

def get_pub_from(node):
    if node is None:
        return ''

    if node.string is None:
        return ' '.join(node.strings)

    return repr(node.string)

def get_action(node):
    action = [0, 0, 0, 0]
    if node is None:
        return action

    li = node.find_all('li')
    for i in range(4):
        num = li[i].find('em')
        if num is None:
            continue
        else:
            cnt_str = ''.join(num.strings)
            print i, cnt_str

        if cnt_str.isdigit():
            action[i] = string.atoi(cnt_str)

    return action

def parse(filename):
    bs = BeautifulSoup(open(filename))
    res = bs.find_all('div', attrs={
        'action-type': 'feed_list_item'
    })

    count = 1
    for node in res:
        print 'parsing %s of %s' % (count, len(res))

        p = node.find('p', attrs={
            'class': 'comment_txt'
        })

        nickname = p['nick-name']
        content = ' '.join(p.strings)
        time = node.find('a', attrs={'class': 'W_textb'})['date']

        pub_from = get_pub_from(node.find('a', attrs={'rel': 'nofollow'}))

        action = get_action(node.find('ul', attrs={
            'class': 'feed_action_info feed_action_row4'
        }))

        blog.new(nickname, content, time, pub_from, action)

        count = count + 1

if __name__ == '__main__':
    create_db()
    parse('tmp')
    con.commit()
    con.close()
