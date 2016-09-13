# -*- coding: utf-8 -*-
import fbchat
from termcolor import colored
from threading import Thread
from sys import exit,exc_info,stdout
from getpass import getpass
import time,re,os

enablexmpp = 0  
try:             ## xmpp listen
    from xmpp import cliXMPP
    enablexmpp = 1
except ImportError:
    pass


USERNAME = ""
PASSWD = ""

def try_bad_encode_to_unicode(text):
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
    last_isgroup = False
    last_mid = ""
    name_color = "yellow"
    thread_color = "green"
    time_color = "blue"
    def on_message(self,mid, imessage, author_id, thread_id, timestamp, stickurl=''):
        tid = thread_id or author_id
        self.markAsDelivered(tid, mid)
        self.markAsRead(tid)
        
        #open("msg.txt","a").write(str(metadata)+"\n")
        if imessage: 
            message = try_bad_encode_to_unicode(imessage)
        else:
            message = imessage[:]

        ## group chat use another kind of json.
        sender_name = colored(self._roster(str(author_id)),self.name_color)
        thread_name = colored(self._roster(str(thread_id)),self.thread_color)
        msgtime = colored('['+timestamp+']',self.time_color)
        if thread_id or str(author_id) != str(self.uid) :
            self.last_tid = thread_id or author_id
            self.last_tname = self._roster(self.last_tid)
            self.last_isgroup = False
            if thread_id :self.last_isgroup = True
        if not message:  ## for 貼圖
            message = colored("送出貼圖","cyan")

        if thread_id :
            tt = "%s%s in %s: %s"%(msgtime,sender_name,thread_name,message)
        else:
            tt = "%s%s: %s"%(msgtime,sender_name,message)
        print(tt)

    def on_notify(self,text,metadata):
        print(colored(re.sub("\n",'',text),"cyan"))
        
def do_cmd(a,fbid,fbname,c):
    if fbname.isdigit(): fbname = c._roster(fbid)
    if re.match("^\/whois ",a):
        users = c.getUsers(a[7:])
        for u in users: u.isgroup = False
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
            c.last_isgroup = c.last_users[i].isgroup
        else:
            print(colored("Find no user",'red'))
        return
    if re.match("^\/set ",a):
        indata = a[5:].split(" ")
        if len(indata) < 2: print('\/set [fbid] [isgroup(1 or 0)]')
        c.last_tid = indata[0]
        c.last_tname = indata[0]
        c.last_isgroup = indata[1]
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
        threads = c.getThreadList(0,end=i)
        
        if threads:
            for t in threads: 
                if not t.name: t.name = t.other_user_name
            for t in threads: t.uid = t.thread_fbid
            for t in threads: t.isgroup = not t.is_canonical
            nthreads = len(threads)
            c.last_users = threads
            for i in range(nthreads):
                print("  %s : %s "%
                    (i,colored(threads[i].name,'yellow')))
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
        print(colored("[%s] send %s to %s "%(('ok' if c.send(fbid,a) else 'failed'),a,fbname),"blue"))
        return

    if not fbid:
        print(colored("Talk to who? Try use /history or /whois find someone","red"))
        return

    if not a:
        print("say something to %s ?" %(colored(fbname,"yellow")))
            #,colored(fbid,"blue"))),colored(str(c.last_isgroup),"blue")))
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
        c = myfb(USERNAME, PASSWD)
        th = Thread(target=c.listen)
        th.start()
        while 1 :
            aa = raw_input("")
            a = aa.decode("utf-8")
            do_cmd(a,c.last_tid,c.last_tname,c)
    except (KeyboardInterrupt,EOFError):
        print("exiting")
        if enablexmpp: xmpp.disconnect()
        if c :c.stop_listen()
        exit()
    except :
        print("Error exit")
        e = exc_info()
        print(e)
        if enablexmpp: xmpp.disconnect()
        if c :c.stop_listen()
        exit()
