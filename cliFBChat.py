# -*- coding: utf-8 -*-
import fbchat
from termcolor import colored
from threading import Thread
from sys import exit,exc_info,stdout
from getpass import getpass
import time
import re
import os

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
    roster = dict()
    last_mid = ""
    def on_message(self,mid, author_id, author_name, imessage, metadata):
        if author_id == self.uid : self.roster[author_id] = 'me'
        if mid == self.last_mid: return ## do not print duplicate message.
        self.last_mid = mid
        print author_name.isdigit()
        if author_name.isdigit() and author_name in self.roster.keys():
            author_name = self.roster[author_id]

        self.markAsDelivered(author_id, mid)
        self.markAsRead(author_id)
        open("msg.txt","a").write(str(metadata)+"\n")
        #print("set last_tid = "+mid)
        ## sometimes message will return with wrong code...
        ##                   in each character......
        message = try_bad_encode_to_unicode(imessage)

        ## group chat use another kind of json.
        try:   ## if group chat
            if 'messaging' ==  metadata['type']:
                fbid = metadata['message']['thread_fbid']
                self.last_tid = fbid
                self.last_tname = metadata['message']['group_thread_info']['name']
                self.last_isgroup = True
                sender_fbid = metadata['message']['sender_fbid']
                sender_name = metadata['message']['sender_name']
                self.roster[fbid] = self.last_tname
                self.roster[sender_fbid] = sender_name
            if 'delta' ==  metadata['type']:
                fbid = metadata['delta']['messageMetadata']['threadKey']['threadFbId']
                self.last_tid = fbid
                sender_fbid = metadata['delta']['messageMetadata']['actorFbId']
                if fbid in self.roster.keys(): 
                    self.last_tname = self.roster[fbid]
                    sender_name = self.roster[fbid]
                else:
                    self.last_tname = fbid
                    sender_name = fbid
                self.last_isgroup = True
        except: ## if personal chat
            #print(exc_info())
            if not author_id == self.uid and author_id:
                self.last_tid = author_id
                self.last_tname = author_name
                self.last_isgroup = False
        try:   ## add time msg time
            if 'message' in metadata.keys(): ## full msg json
                msgtime = metadata['message']['timestamp']
            else:                            ## delta msg
                msgtime = metadata['delta']['messageMetadata']['timestamp']

            msgtime = int(msgtime)/1000
            timestamp = time.strftime("%H:%M",time.localtime(msgtime))
            timestamp  = "%s"%(colored('['+timestamp+']','blue'))
        except:
            print("add timestamp failed")
            timestamp = u'' ## avoid error...
            print(exc_info())
        if not message:  ## for 貼圖
            try:
                url = metadata['message']['attachments'][0]['url']
                message = u":"
                if self.last_isgroup :
                    print("%s%s in %s %s"%(colored(timestamp,'blue'),colored(author_name,'green'),colored(author_name,"yellow"),colored(url,"cyan")))
                else:
                    print("%s%s%s %s"%(colored(timestamp,'blue'),colored(author_name,'green'),message,colored(url,"cyan")))
            except:
                print(exc_info())
                pass
        else:
            if self.last_isgroup :
                tt = "%s%s in %s: %s"%(colored(timestamp,'blue'),colored(author_name,'green')
                    ,colored(sender_name,"yellow"),message)
                print(tt)
            else:
                tt = "%s%s: %s"%(colored(timestamp,'blue'),colored(author_name,'green'),message)
                print(tt)

    def on_notify(self,text,metadata):
        print(colored(re.sub("\n",'',text),"cyan"))
        
def do_cmd(a,fbid,fbname,c):
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
                c.roster[users[i].uid] = users[i].name
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
        for t in threads: 
            if not t.name: t.name = t.other_user_name
        for t in threads: t.uid = t.thread_fbid
        for t in threads: t.isgroup = not t.is_canonical
        nthreads = len(threads)
        c.last_users = threads
        if threads:
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
            print("%s : %s"%
                (colored(c.roster[i],'yellow')
                  ,colored(i,'cyan') ))
        return
    if re.match("^\/clear",a):
        print("")
        print("")
        print("")
        print("")
        print("")
        print("")
        print("")
        print("")
        return
        
    if fbid and a:
        print(colored("[%s] send %s to %s "%(('ok' if c.send(fbid,a) else 'failed'),a,fbname),"blue"))
        return

    if not fbid:
        print(colored("Talk to who? Try use /history or /whois find someone","red"))
        return

    if not a:
        print("say something to %s ? %s"%(colored(fbname,"yellow"),
            colored(fbid,"blue")))
        return

if __name__ == '__main__':
    if os.path.isfile("account.txt"):
        f = open("account.txt","r")
        USERNAME =  f.readline().rstrip()
        PASSWD   =  f.readline().rstrip()
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
        c.stop_listen()
        exit()
