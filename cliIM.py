#!/usr/bin/python3
# -*- coding: utf-8 -*-

import fbchat ## github fbchat python 
from threading import Thread
import sys,time,termios,tty,re,os
import logging
try:
    from termcolor import colored
except:
    def colored(text,color):
        return text
    

class dummyExample(): # module example
    last_tid = '' ## current talkto tid/uid
    last_tname = '' ## current talkto thread
    def __init__(self):
        ## include login
        pass
        self._roster = dict() ## {id : name}

    def roster(self,uid): # get name of user/thread id
        return self._roster.get(str(uid))
    def listen(self):
        while self.listening:
            time.sleep(60)
            ## receive messages
        ## TBD
    def searchUser(self,user):
        ''' for /whois'''
        pass
    def recentChats(self,limit=5):
        ''' for /history'''
        pass


class FBChat(fbchat.Client):
    savepath = './'
    fbcookiefile = savepath+'/'+'fbcookies.txt'
    fbrosterfile = savepath+'/'+'fbroster.txt'

    last_tid = ''
    last_tname = ''
    last_mid = ""
    name_color = "yellow"
    thread_color = "green"
    time_color = "blue"
    _roster = dict()

    def __init__(self,USERNAME,PASSWD):
        ''' login or read cookies, and read roster'''
        fbcookiefile = self.fbcookiefile
        if os.path.isfile(fbcookiefile):
            fbcookies = eval(open(fbcookiefile,'r').read())
        else:
            fbcookies = dict()
        print('[fb] '+USERNAME+' logging in...')
        if fbcookies:
            super().__init__(USERNAME, PASSWD, session_cookies=fbcookies, logging_level=logging.WARNING)
        else:
            super().__init__(USERNAME, PASSWD, logging_level=logging.WARNING)

        fbcookies = self.getSession()
        open(fbcookiefile,'w').write(str(fbcookies))

        ## read saved roster
        try:
            if os.path.isfile(self.fbrosterfile): self._roster= eval(open(self.fbrosterfile,'r').read())
        except:
            print('[fb] read roster file failed: '+self.fbrosterfile)

        self.prompt = colored('[fb] ','red')

    def roster(self,itid):
        tid = str(itid)
        name = self._roster.get(tid)
        if name: return name
        thread = self.fetchThreadInfo(itid)
        name = thread.get('name')
        if name: 
            self._roster.update({tid : name})
            return name
        thread = self.fetchUserInfo(itid)
        name = thread.get('name')
        if name: 
            self._roster.update({tid : name})
            return name
        return str(tid)
    def roster_add(self,uid,name):
        self._roster.update({str(uid) : name})
        open(self.fbrosterfile,'w').write(str(self._roster))

    def onMessage(self, mid=None, author_id=None, message=None, message_object=None, thread_id=None, thread_type=fbchat.ThreadType.USER, ts=None, metadata=None, msg=None):
        timestamp = time.strftime('%H:%M',time.localtime(ts/1000.))
        msgtext = message

        tid = thread_id or author_id
        self.markAsDelivered(tid, mid)
        #self.markAsRead(tid)
        
        sender_name = colored(self.roster(author_id),self.name_color)
        thread_name = colored(self.roster(thread_id),self.thread_color)
        msgtime = colored('['+timestamp+']',self.time_color)
        if thread_id or str(author_id) != str(self.uid) :
            self.last_tid = thread_id or author_id
            self.last_tname = self.roster(self.last_tid)
            self.prompt = colored('[fb]','red')+colored('['+self.last_tname+'] ',self.name_color)
        if not message:  ## for 貼圖
            msgtext = colored("送出貼圖","cyan")

        try:
            if not sender_name == thread_name:
                tt = "%s %s to %s: %s"%(msgtime,sender_name,thread_name,msgtext)
            else:
                tt = "%s %s: %s"%(msgtime,sender_name,msgtext)
            self.output(tt) ## self.output() is assigned in cliInterface
        except UnicodeDecodeError:
            pass


class Spinner():
    Box1 = u'⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    Box2 = u'⠋⠙⠚⠞⠖⠦⠴⠲⠳⠓'
    Box3 = u'⠄⠆⠇⠋⠙⠸⠰⠠⠰⠸⠙⠋⠇⠆'
    Box4 = u'⠋⠙⠚⠒⠂⠂⠒⠲⠴⠦⠖⠒⠐⠐⠒⠓⠋'
    Box5 = u'⠁⠉⠙⠚⠒⠂⠂⠒⠲⠴⠤⠄⠄⠤⠴⠲⠒⠂⠂⠒⠚⠙⠉⠁'
    Box6 = u'⠈⠉⠋⠓⠒⠐⠐⠒⠖⠦⠤⠠⠠⠤⠦⠖⠒⠐⠐⠒⠓⠋⠉⠈'
    Box7 = u'⠁⠁⠉⠙⠚⠒⠂⠂⠒⠲⠴⠤⠄⠄⠤⠠⠠⠤⠦⠖⠒⠐⠐⠒⠓⠋⠉⠈⠈'
    Spin1 = u'|/-\\'
    Spin2 = u'◴◷◶◵'
    Spin3 = u'◰◳◲◱'
    Spin4 = u'◐◓◑◒'
    Spin5 = u'▉▊▋▌▍▎▏▎▍▌▋▊▉'
    Spin6 = u'▌▄▐▀'
    Spin7 = u'╫╪'
    Spin8 = u'■□▪▫'
    Spin9 = u'←↑→↓'
    default = Spin2
    running = 0
    text = ''
    def spinning(self):
        spinstring = self.default
        slen = len(spinstring)
        i = 0
        while self.running:
            sys.stdout.write("\r"+self.text+' '+spinstring[(i%slen)])
            sys.stdout.flush()
            time.sleep(0.1)
            i = i+1
        #sys.stdout.write("\r")
        #sys.stdout.flush()
    def start_spin(self,text):
        if text : self.text = text
        self.running = 1
        #self.spinning() ## should use threading
        a = Thread(target=self.spinning)
        a.start()
    def stop_spin(self):
        self.running = 0

class cliInterface(): ## get hotkeys, control cmd line and insert text above it
    def __init__(self,mods):
        self.cmd_prompt = ''
        self.cmd = ''
        self.exitkey = [3] # ord(keys) to exit, [C-c]
        self.curPos = 0 ## cursor position in cmd line
        self.curEOL = 1 ## is cursor follow end of line

        self.actived_mods = list() # modules to operate
        self.threads = list() # module threads
        self.c = None  # current modules to operate
        
        for m in mods:
            th = Thread(target=m.listen)
            th.start()
            self.actived_mods.append(m)
            self.threads.append(th)
        self.c = self.actived_mods[0]

        self.cmd_history = list()
        self.cmd_now = 0  ## 0 means using new cmd, cmd_history is negative
        self.cmd_typing = ''

        # _cmd_actions dict()
        self.cmd_actions = dict()
        for i in dir(self):
            if re.match("^_cmd_[A-Za-z]*",i): self.cmd_actions.update({re.sub(r"^_cmd_",r"/",i,1) : eval("self."+i)})

        # spinner
        self.spinner = Spinner()
    def _cmd_whois(self,a):
        '''  /whois <user name>  : find user'''
        c = self.c
        users = c.searchForUsers(a[7:],limit=5)
        if users:
            c.last_users = users
            nuser = len(users)
            for i in range(nuser):
                c.roster_add(users[i].uid , users[i].name)
                self.output("  %s : %s %s"%
                    (i,colored(users[i].name,'cyan')
                    ,colored(re.sub("www\.","m.",users[i].url),'blue')))
            self.output(colored("/talkto [number]",'red'))
        else:
            pass
        return
    def _cmd_talkto(self,a):
        r'''  /talkto <list number> : set thread to chat'''
        c = self.c
        try:
            i = int(a[8:])
        except:
            self.output(colored("/talkto [number]",'red'))
            return
            
        if c.last_users:
            if i > len(c.last_users)-1:
                self.output(colored("/talkto [0-"+str(len(c.last_users)-1)+"]",'red'))
                return
            self.output(colored("talk to ","red")+colored(c.last_users[i].name,"yellow"))
            c.last_tid = c.last_users[i].uid
            c.last_tname = c.last_users[i].name
            c.prompt = colored('[fb]','red')+colored('['+c.last_tname+'] ','cyan')
        else:
            pass
        return
    def _cmd_history(self,a):
        r'''  /history [n items] : list chat threads '''
        c = self.c
        i = 5
        if len(a) > 8:
            try:
                i = int(a[8:])
            except:
                self.output(colored("/history [number]",'red'))
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
                self.output("  %s : %s "%
                    (i,colored(threads[i].name,'yellow')))
                c.roster_add(threads[i].uid,threads[i].name)
            #self.output("use /talkto [number]  ")
            self.output(colored("use /talkto [number] ",'red'))
        else:
            self.output(colored("Find no chat",'red'))
        return
    def _cmd_roster(self,a):
        r'''  /roster : list roster'''
        c = self.c
        if not c.roster: self.output("no roster yet")
        for i in c._roster.keys():
            self.output("%s : %s "%
                (colored(c.roster(i),'yellow')
                  ,colored(i,'cyan') ))
        return
    def _cmd_clear(self,a):
        '''  /clear, /cls : clear screen '''
        self.output(chr(27) + "[2J")
        return
    def _cmd_cls(self,a):
        '''  /clear, /cls : clear screen '''
        self.output(chr(27) + "[2J")
        return
    def _cmd_quit(self,a):
        '''  /quit : quit cliIM '''
        self._exit()
        return
    def _cmd_help(self,a):
        '''  /help : list commands'''
        for i in sorted(self.cmd_actions.keys()):
            self.output(self.cmd_actions[i].__doc__)

    def _getch(self):  ## grab keycode
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def _do_cmd(self,cmd):
        a = cmd
        c = self.c
        tid = c.last_tid

        firstWord = a.split(' ')[0]
        if firstWord in self.cmd_actions.keys(): 
            self.cmd_actions[firstWord](a)
            return

        if re.match("^\/",a):
            self.output("%s"%(colored("Want to use command? "+a,"red")))
            return
            
        if tid and a:
            self.output(colored("[%s] send %s to %s "%(('ok' if c.send(thread_id=tid,message=fbchat.Message(text=a)) else 'failed'),a,c.roster(tid)),"blue"))
            return

        if not tid:
            self.output(colored("Talk to who? Try use /history or /whois find someone: "+a,"red"))
            return

        if not a:
            self.output("say something to %s ?" %(colored(c.roster(tid),"yellow")))
            return
    def _keyact(self,ch): ## action for keypress
        if ord(ch) in self.exitkey:
            self._exit()
            return
        if ord(ch) in [10,13,15]: ## press enter,C-m,C-o
            cmd = self.cmd[:]
            if cmd: self.cmd_history.append(cmd)
            self.cmd_now = 0
            self.curEOL=1 ## put cursor to end of line
            try:
                self.output(spinner=True)
                self._do_cmd(cmd)
            except:
                self.output(cmd+" error")
                self.output(str(sys.exc_info()))
            finally:
                self.cmd = ''
                pass
                
            self.output() ## refresh cmd_line
            return
        if ord(ch) in [4]: ## press C-d (delete)
            self.cmd = self.cmd[:self.curPos]+self.cmd[self.curPos+1:]
            self.output()
            return
        if ord(ch) in [127,8]: ## press backspace or C-h
            self.cmd = self.cmd[:self.curPos-1]+self.cmd[self.curPos:]
            self.curPos += -1
            self.output()
            return
        if ord(ch) in [2]: ## press C-b
            self.curEOL = 0
            self.curPos += -1
            self.output()
            return
        if ord(ch) in [6]: ## press C-f
            self.curEOL = 0
            self.curPos += 1
            self.output()
            return
        if ord(ch) in [1]: ## press C-a
            self.curEOL = 0
            self.curPos = 0
            self.output()
            return
        if ord(ch) in [5]: ## press C-e
            self.curEOL = 1
            self.output()
            return
        if ord(ch) in [21]: ## press C-u
            self.cmd = self.cmd[self.curPos:]
            self.curPos = 0
            self.output()
            return
        if ord(ch) in [23]: ## press C-w
            self.output('hotkey C-w not done yet')
            return
        if ord(ch) in [16]: ## press C-p
            if self.cmd_now == 0 : self.cmd_typing = self.cmd
            self.cmd_now += -1
            if len(self.cmd_history) + self.cmd_now == 0:self.cmd_now +=1
            self.cmd = self.cmd_history[self.cmd_now]
            self.output()
            return
        if ord(ch) in [14]: ## press C-n
            if not self.cmd_now: 
                self.cmd = self.cmd_typing
                self.output()
                return
            if self.cmd_now: self.cmd_now += 1
            self.cmd = self.cmd_history[self.cmd_now]
            if not self.cmd_now: self.cmd = self.cmd_typing
            self.output()
            return

        ## TBD hotkeys, dict() style keyact 
        #self.output(str(ord(ch)))
        self.cmd = self.cmd[:self.curPos]+ch+self.cmd[self.curPos:]
        self.curPos +=1
        self.output() ## refresh cmd_line

    def _exit(self): ## exit cliIM
        for m in self.actived_mods:
            m.stopListening()
        self.listening = False
        #self.output("exiting...")

        print("\nexiting...")
        sys.exit()

    def cmd_listen(self): ## get user inputs
        self.listening = True
        self.output()
        while self.listening:
            self._keyact(self._getch())
        
    def output(self,text='',move_cursor=0,spinner=False): ## keep cmd line, insert text above it or just refresh cmd_line
        cmd_prompt = self.c.prompt
        cmdlen = len(self.cmd) 

        if spinner : # spinner not done yet
            #self.spinner.text = cmd_prompt+self.cmd
            self.spinner.start_spin(cmd_prompt+self.cmd)
            return
        else:
            self.spinner.stop_spin()

        if text: sys.stdout.write("\r"+text+"\033[K"+"\n")

        if self.curPos == cmdlen: self.curEOL = 1
        if self.curEOL: self.curPos = cmdlen


        if self.curEOL:
            sys.stdout.write("\r"+cmd_prompt+self.cmd+"\033[K")
        else:
            movecur = '\033['+str(cmdlen-self.curPos)+'D'
            sys.stdout.write("\r"+cmd_prompt+self.cmd+"\033[K"+movecur)
        sys.stdout.flush()
        pass
    

if __name__ == '__main__':
    a = open('account.txt',"r").readlines()
    USERNAME = a[0].strip()
    PASSWD = a[1].strip()

    fb = FBChat(USERNAME,PASSWD)
    c = cliInterface([fb])
    fb.output = c.output
    c.cmd_listen()
