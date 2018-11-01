# -*- coding: utf-8 -*-
import fbchat
from termcolor import colored
from threading import Thread
from sys import exit,exc_info,stdout
from getpass import getpass
import time,re,os
import logging

enablexmpp = 0  
try:             ## xmpp listen
    from xmpp import cliXMPP
    enablexmpp = 1
except ImportError:
    pass


USERNAME = ""
PASSWD = ""

def try_bad_encode_to_unicode(text):
    return text # try not encode
    encs = ['iso-8859-1','iso-8859-2']
    #print("try: "+repr(text))
    for i in encs:
        try:
            t = text.encode(i).decode('utf-8')
        except UnicodeEncodeError:
            continue
        #print("    "+i+" is right code")
        return t
    return text

class myfb(fbchat.Client):
    last_tid = ''
    last_tname = ''
    last_mid = ""
    name_color = "yellow"
    thread_color = "green"
    time_color = "blue"
    roster = dict()
    def on_message(self,mid, imessage, author_id, thread_id, timestamp, stickurl=''):
        ## obsoleted
        pass
    def onMessage(self, mid=None, author_id=None, message=None, message_object=None, thread_id=None, thread_type=fbchat.ThreadType.USER, ts=None, metadata=None, msg=None):
        timestamp = str(ts)
        msgtext = message

        tid = thread_id or author_id
        self.markAsDelivered(tid, mid)
        self.markAsRead(tid)
        
        #open("msg.txt","a").write(str(metadata)+"\n")
        #if imessage: 
        #    message = try_bad_encode_to_unicode(imessage)
        #else:
        #    message = imessage[:]

        ## group chat use another kind of json.
        sender_name = colored(self.roster.get(str(author_id)),self.name_color)
        thread_name = colored(self.roster.get(str(thread_id)),self.thread_color)
        msgtime = colored('['+timestamp+']',self.time_color)
        if thread_id or str(author_id) != str(self.uid) :
            self.last_tid = thread_id or author_id
            self.last_tname = self.roster.get(self.last_tid)
        if not message:  ## for 貼圖
            msgtext = colored("送出貼圖","cyan")

        if thread_id :
            tt = "%s%s in %s: %s"%(msgtime,sender_name,thread_name,msgtext)
        else:
            tt = "%s%s: %s"%(msgtime,sender_name,msgtext)
        print(tt)

    def on_notify(self,text,metadata):
        print(colored(re.sub("\n",'',text),"cyan"))
        
def do_cmd(a,fbid,fbname,c):
    if fbname.isdigit(): fbname = c.roster.get(fbid)
    if re.match("^\/whois ",a):
        users = c.searchForUsers(a[7:],limit=5)
        c.last_users = users
        nuser = len(users)
        if users:
            for i in range(nuser):
                print("  %s : %s %s"%
                    (i,colored(users[i].name,'cyan')
                    ,colored(re.sub("www\.","m.",users[i].url),'blue')))
            print(colored("/talkto [number]",'red'))
        else:
            print(colored("Find no user",'red'))
        return
    if re.match("^\/talkto ",a):
        try:
            i = int(a[8:])
        except:
            print(colored("/talkto [number]",'red'))
            return
            
        if c.last_users:
            print(colored("talk to ","red")+colored(c.last_users[i].name,"yellow"))
            c.last_tid = c.last_users[i].uid
            c.last_tname = c.last_users[i].name
        else:
            print(colored("Find no user",'red'))
        return
    if re.match("^\/set ",a):
        indata = a[5:].split(" ")
        c.last_tid = indata[0]
        c.last_tname = indata[0]
        print(colored("set id to %s"%(str(indata)),'red'))
        return
    if re.match("^\/history",a):
        i = 5
        if len(a) > 8:
            try:
                i = int(a[8:])
            except:
                print(colored("/history [number]",'red'))
                return
        threads = c.fetchThreadList(limit=i)
        
        if threads:
            '''
            for t in threads: 
                if not t.name: t.name = t.other_user_name
            for t in threads: 
                t.uid = t.thread_fbid
            '''
            nthreads = len(threads)
            c.last_users = threads
            for i in range(nthreads):
                print("  %s : %s "%
                    (i,colored(threads[i].name,'yellow')))
                c.roster[threads[i].uid] = threads[i].name
            #print("use /talkto [number]  ")
            print(colored("use /talkto [number] ",'red'))
        else:
            print(colored("Find no chat",'red'))
        return
    if re.match("^\/roster",a):
        for i in c.roster.keys():
            print("%s : %s "%
                (colored(c.roster[i],'yellow')
                  ,colored(i,'cyan') ))
        return
    if re.match("^\/clear",a):
        print(chr(27) + "[2J")
        return
    if re.match("^\/cls",a):
        print(chr(27) + "[2J")
        return
    if re.match("^\/",a):
        print("%s"%(colored("Want to use command? ","red")))
        return
        
    if fbid and a:
        print(colored("[%s] send %s to %s "%(('ok' if c.send(thread_id=fbid,message=fbchat.Message(text=a)) else 'failed'),a,fbname),"blue"))
        return

    if not fbid:
        print(colored("Talk to who? Try use /history or /whois find someone","red"))
        return

    if not a:
        print("say something to %s ?" %(colored(fbname,"yellow")))
        return

if __name__ == '__main__':
    c = ""
    if os.path.isfile("account.txt"):
        f = open("account.txt","r")
        USERNAME =  f.readline().rstrip()
        PASSWD   =  f.readline().rstrip()
    if enablexmpp and os.path.isfile("xmppaccount.txt"):
        f = open("xmppaccount.txt","r")
        xmppUSERNAME =  f.readline().rstrip()
        xmppPASSWD   =  f.readline().rstrip()
        xmpp = cliXMPP.xmpp_client(xmppUSERNAME, xmppPASSWD) 
        
        if xmpp.connect():
            xmpp.process(threaded=True)
            print("XMPP, listen only")
        else:
            print("xmpp unable to connect.")
    try:
        if not USERNAME:
            USERNAME = raw_input("FB username: ")
            PASSWD = getpass("FB password: ")
        fbcookiefile = 'fbcookies.txt'
        if os.path.isfile(fbcookiefile):
            fbcookies = eval(open(fbcookiefile,'r').read())
        else:
            fbcookies = dict()

        print(fbcookies)
        c = myfb(USERNAME, PASSWD, session_cookies=fbcookies, logging_level=logging.WARNING)
        fbcookies = c.getSession()
        open(fbcookiefile,'w').write(str(fbcookies))
        ## test load cookie
        fbcookies = eval(open(fbcookiefile,'r').read())
        print("Listening")
        th = Thread(target=c.listen)
        th.start()
        while 1 :
            aa = raw_input("")
            a = aa.decode("utf-8")
            try:
                do_cmd(a,c.last_tid,c.last_tname,c)
            except:
                print("cmd error")
                print(exc_info())
                pass
    except (KeyboardInterrupt,EOFError):
        print("exiting")
        if enablexmpp: xmpp.disconnect()
        if c :c.stopListening()
        exit()
    except :
        print("Error exit")
        exc_type, exc_obj, exc_tb = exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(exc_tb)

        if enablexmpp: xmpp.disconnect()
        if c :c.stopListening()
        exit()
