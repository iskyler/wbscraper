from time import sleep
import requests

cookie_str = '' # add cookie str

def parse_cookie_str():
    kv_list = cookies_str.split('; ')
    
    d = dict()
    for kv in kv_list:
        kv_pair = kv.split('=')
        d[kv_pair[0]] = kv_pair[1]
    return d

if __name__ == '__main__':
    url = 'http://s.weibo.com/weibo/duang&b=1&page='
    headers = {
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'zh-CN',
        'User-Agent': 'Mozilla/5.0 (MSIE 9.0; Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Referer': 'http://s.weibo.com/weibo/duang?topnav=1&wvr=6&b=1'
    }
    params = {
        'b': 1,
        'page': 2
    }
    cookies = parse_cookie_str()
    print cookies

    for i in range(38, 51):
        r = requests.get(url + str(i), cookies=cookies, headers=headers)
        f = open('html/%s.html' % str(i), 'w')
        f.write(r.text.encode('utf-8'))
        f.close()
        sleep(3)

