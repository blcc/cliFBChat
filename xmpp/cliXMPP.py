#!/usr/bin/env python
# -*- coding: utf-8 -*-

## for msgCent
import sys,logging,time,getpass

import sleekxmpp
from termcolor import colored

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')


class xmpp_client(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler("session_start", self.start)

        self.add_event_handler("message", self.message)
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping

    def start(self, event):
        self.send_presence()
        self.get_roster()
        #print(self.roster)

    def message(self, msg):
        self.on_message(msg['body'],self.roster[msg['from']._jid.split("/")[0]]['name'])
        #print(msg['from']._jid.split("/")[0])
        #print(self.roster[msg['from']._jid.split("/")[0]]['name']+": "+msg['body'])
    def on_message(self,message,authorname):
        proc = colored('[xmpp]','cyan')
        name = colored(authorname+": ",'cyan')
        msg =  colored(message,'cyan')
        print(proc+name+msg)
        pass

    def whois(self,jid):
        return self.roster[jid]['name']
    def whoall(self):
        print (self.roster)

if __name__ == '__main__':
    xmpp = xmpp_client(USERNAME, PASSWORD) ## testing

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        xmpp.process(threaded=True)
        while 1:
            a = raw_input()
            print("sending "+a)
            xmpp.send_message(mto=TOJID,mbody=a,mtype='chat')
    else:
        print("Unable to connect.")
