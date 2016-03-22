import re
import json
import time
from random import random
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/601.1.10 (KHTML, like Gecko) Version/8.0.5 Safari/601.1.10",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; ; NCT50_AAP285C84A1328) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6"
]

def now():
    return int(time.time()*1000)

def get_json(text):
    #b  =re.sub(r"^[^{]*", '', text.encode('utf-8').decode("unicode-escape"), 1) 
    b  =re.sub(r"^[^{]*", '', text, 1) 
    
    open("json.log","a").write(repr(text)+"\n")
    try:
        a = json.loads(b,encoding='utf-8')
    except: ## someone like your post
        #print("get_json(): error when parser, raise error")
        a = json.loads('{"ms":[{"type":"someone give you a like"}]}')
        #raise "parserError"
    return a
    #return json.loads(re.sub(r"for.*(.*;.*;.*).*;", '', text.encode('utf-8').decode("unicode-escape"), 1))

def digit_to_char(digit):
    if digit < 10:
        return str(digit)
    return chr(ord('a') + digit - 10)

def str_base(number,base):
    if number < 0:
        return '-' + str_base(-number, base)
    (d, m) = divmod(number, base)
    if d > 0:
        return str_base(d, base) + digit_to_char(m)
    return digit_to_char(m)

def generateMessageID(client_id=None):
    k = now()
    l = int(random() * 4294967295)
    return ("<%s:%s-%s@mail.projektitan.com>" % (k, l, client_id));
