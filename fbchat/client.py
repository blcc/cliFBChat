"""
    fbchat
    ~~~~~~

    Facebook Chat (Messenger) for Python

    :copyright: (c) 2015 by Taehoon Kim.
    :license: BSD, see LICENSE for more details.
"""

import requests
from uuid import uuid1
from random import random, choice
import time
from datetime import datetime
from bs4 import BeautifulSoup as bs
from sys import exc_info

from .utils import *
from .models import *
from .stickers import *

# URLs
LoginURL     ="https://m.facebook.com/login.php?login_attempt=1"
SearchURL    ="https://www.facebook.com/ajax/typeahead/search.php"
SendURL      ="https://www.facebook.com/ajax/mercury/send_messages.php"
ThreadsURL   ="https://www.facebook.com/ajax/mercury/threadlist_info.php"
ThreadSyncURL="https://www.facebook.com/ajax/mercury/thread_sync.php"
MessagesURL  ="https://www.facebook.com/ajax/mercury/thread_info.php"
ReadStatusURL="https://www.facebook.com/ajax/mercury/change_read_status.php"
DeliveredURL ="https://www.facebook.com/ajax/mercury/delivery_receipts.php"
MarkSeenURL  ="https://www.facebook.com/ajax/mercury/mark_seen.php"
BaseURL      ="https://www.facebook.com"
MobileURL    ="https://m.facebook.com/"
StickyURL    ="https://0-edge-chat.facebook.com/pull"
PingURL      ="https://0-channel-proxy-06-ash2.facebook.com/active_ping"

class Client(object):
    """A client for the Facebook Chat (Messenger).

    See http://github.com/carpedm20/fbchat for complete
    documentation for the API.

    """

    def __init__(self, email, password, debug=True, user_agent=None):
        """A client for the Facebook Chat (Messenger).

        :param email: Facebook `email` or `id` or `phone number`
        :param password: Facebook account password

            import fbchat
            chat = fbchat.Client(email, password)

        """

        if not (email and password):
            raise Exception("id and password or config is needed")

        self.email = email
        self.password = password
        self.debug = debug
        self._session = requests.session()
        self.req_counter = 1
        self.seq = "0"
        self.payloadDefault={}
        self.client = 'mercury'
        self.listening = False
        self.roster = dict()
        self.mid = ''

        if not user_agent:
            user_agent = choice(USER_AGENTS)

        self._header = {
            'Content-Type' : 'application/x-www-form-urlencoded',
            'Referer' : BaseURL,
            'Origin' : BaseURL,
            'User-Agent' : user_agent,
            'Connection' : 'keep-alive',
        }

        self._console("Logging in...")

        if not self.login():
            raise Exception("id or password is wrong")

        self.threads = []

    def _console(self, msg):
        if self.debug: print(msg)

    def _setttstamp(self):
        for i in self.fb_dtsg:
            self.ttstamp += str(ord(i))
        self.ttstamp += '2'

    def _generatePayload(self, query):
        '''
        Adds the following defaults to the payload:
          __rev, __user, __a, ttstamp, fb_dtsg, __req
        '''
        payload=self.payloadDefault.copy()
        if query:
            payload.update(query)
        payload['__req'] = str_base(self.req_counter, 36)
        payload['seq'] = self.seq
        self.req_counter+=1
        return payload

    def _get(self, url, query=None, timeout=30):
        payload=self._generatePayload(query)
        return self._session.get(url, headers=self._header, params=payload, timeout=timeout)

    def _post(self, url, query=None, timeout=30):
        payload=self._generatePayload(query)
        return self._session.post(url, headers=self._header, data=payload, timeout=timeout)

    def _cleanPost(self, url, query=None, timeout=30):
        self.req_counter+=1
        return self._session.post(url, headers=self._header, data=query, timeout=timeout)

    def _roster(self,fbid,name=''):
        try:
            if name and fbid:
                self.roster[int(fbid)] = name
            elif fbid:
                name = self.roster[int(fbid)]
                return name
        except:
            return fbid
    def login(self):
        if not (self.email and self.password):
            raise Exception("id and password or config is needed")

        soup = bs(self._get(MobileURL).text, "lxml")
        data = dict((elem['name'], elem['value']) for elem in soup.findAll("input") if elem.has_attr('value') and elem.has_attr('name'))
        data['email'] = self.email
        data['pass'] = self.password
        data['login'] = 'Log In'

        r = self._cleanPost(LoginURL, data)

        if 'home' in r.url:
            self.client_id = hex(int(random()*2147483648))[2:]
            self.start_time = now()
            self.uid = int(self._session.cookies['c_user'])
            self._roster(self.uid,'me')
            self.user_channel = "p_" + str(self.uid)
            self.ttstamp = ''

            r = self._get(BaseURL)
            soup = bs(r.text, "lxml")
            self.fb_dtsg = soup.find("input", {'name':'fb_dtsg'})['value']
            self._setttstamp()
            # Set default payload
            self.payloadDefault['__rev'] = int(r.text.split('"revision":',1)[1].split(",",1)[0])
            self.payloadDefault['__user'] = self.uid
            self.payloadDefault['__a'] = '1'
            self.payloadDefault['ttstamp'] = self.ttstamp
            self.payloadDefault['fb_dtsg'] = self.fb_dtsg

            self.form = {
                'channel' : self.user_channel,
                'partition' : '-2',
                'clientid' : self.client_id,
                'viewer_uid' : self.uid,
                'uid' : self.uid,
                'state' : 'active',
                'format' : 'json',
                'idle' : 0,
                'cap' : '8'
            }

            self.prev = now()
            self.tmp_prev = now()
            self.last_sync = now()

            return True
        else:
            return False

    def listen(self):
        pass

    def getUsers(self, name):
        """Find and get user by his/her name

        :param name: name of a person
        """
        payload = {
            'value' : name.lower(),
            'viewer' : self.uid,
            'rsp' : "search",
            'context' : "search",
            'path' : "/home.php",
            'request_id' : str(uuid1()),
        }

        r = self._get(SearchURL, payload)
        self.j = j = get_json(r.text)
		
        users = []
        for entry in j['payload']['entries']:
            if entry['type'] == 'user':
                users.append(User(entry))
                self._roster(entry['uid'],entry['text'])

        return users # have bug TypeError: __repr__ returned non-string (type bytes)

    def send(self, thread_id, message=None, like=None):
        """Send a message with given thread id

        :param thread_id: a thread id that you want to send a message
        :param message: a text that you want to send
        :param like: size of the like sticker you want to send
        """

        timestamp = now()
        date = datetime.now()
        ## see https://github.com/Schmavery/facebook-chat-api/blob/master/src/sendMessage.js
        data = {
            'client' : self.client,
            'message_batch[0][action_type]' : 'ma-type:user-generated-message',
            'message_batch[0][author]' : 'fbid:' + str(self.uid),
            #'message_batch[0][specific_to_list][0]' : 'fbid:' + str(thread_id),
            #'message_batch[0][specific_to_list][1]' : 'fbid:' + str(self.uid),
            'message_batch[0][timestamp]' : timestamp,
            'message_batch[0][timestamp_absolute]' : 'Today',
            'message_batch[0][timestamp_relative]' : str(date.hour) + ":" + str(date.minute).zfill(2),
            'message_batch[0][timestamp_time_passed]' : '0',
            'message_batch[0][is_unread]' : False,
            'message_batch[0][is_cleared]' : False,
            'message_batch[0][is_forward]' : False,
            'message_batch[0][is_filtered_content]' : False,
            'message_batch[0][is_spoof_warning]' : False,
            'message_batch[0][source]' : 'source:chat:web',
            'message_batch[0][source_tags][0]' : 'source:chat',
            'message_batch[0][body]' : message,
            'message_batch[0][html_body]' : False,
            'message_batch[0][ui_push_phase]' : 'V3',
            'message_batch[0][status]' : '0',
            'message_batch[0][message_id]' : generateMessageID(self.client_id),
            'message_batch[0][manual_retry_cnt]' : '0',
            'message_batch[0][thread_fbid]' : None,
            'message_batch[0][has_attachment]' : False,
        }
        if self.last_isgroup:
            data['message_batch[0][thread_fbid]'] = thread_id
        else:
            data['message_batch[0][other_user_fbid]'] = thread_id
            data['message_batch[0][specific_to_list][0]'] = 'fbid:' + str(thread_id)
            data['message_batch[0][specific_to_list][1]'] = 'fbid:' + str(self.uid)
            
            
        if like:
            try:
                sticker = LIKES[like.lower()]
            except KeyError:
                # if user doesn't enter l or m or s, then use the large one
                sticker = LIKES['l']
            data["message_batch[0][sticker_id]"] = sticker
            
        open("send_data.txt","a").write(str(data)+"\n")
        r = self._post(SendURL, data)
        return r.ok

    def getThreadInfo(self, userID, start, end=None):
        """Get the info of one Thread

        :param userID: ID of the user you want the messages from
        :param start: the start index of a thread
        :param end: (optional) the last index of a thread
        """
        if not end: end = start + 20
        if end <= start: end=start+end

        data={}
        data['messages[user_ids][%s][offset]'%userID]=    start
        data['messages[user_ids][%s][limit]'%userID]=     end
        data['messages[user_ids][%s][timestamp]'%userID]= now()

        r = self._post(MessagesURL, query=data)
        if not r.ok or len(r.text) == 0:
            return None

        j = get_json(r.text)
        if not j['payload']:
            return None
        messages=[]
        for message in j['payload']['actions']:
            messages.append(Message(**message))
        return list(reversed(messages))

    def getThreadList(self, start, end=None):
        """Get thread list of your facebook account.

        :param start: the start index of a thread
        :param end: (optional) the last index of a thread
        """
        if not end: end = start + 20
        if end <= start: end=start+end

        timestamp = now()
        date = datetime.now()
        data = {
            'client' : self.client,
            'inbox[offset]' : start,
            'inbox[limit]' : end,
        }

        r = self._post(ThreadsURL, data)
        if not r.ok or len(r.text) == 0:
            return None

        j = get_json(r.text)

        # Get names for people
        participants={}
        try:
            for participant in j['payload']['participants']:
                participants[participant["fbid"]] = participant["name"]
                ## include other_user_name in self.roster
                self._roster(participant["fbid"],participant["name"])
        except Exception as e:
          print(j)
          return None

        # Prevent duplicates in self.threads
        threadIDs=[getattr(x, "thread_id") for x in self.threads]
        for thread in j['payload']['threads']:
            if thread["thread_id"] not in threadIDs:
                try:
                    thread["other_user_name"] = participants[int(thread["other_user_fbid"])]
                except:
                    thread["other_user_name"] = ""
                if not thread['name'] and thread["thread_fbid"] in participants.keys(): thread['name'] = participants[thread["thread_fbid"]]
                t = Thread(**thread)
                self._roster(thread["thread_fbid"],thread['name'])
                self.threads.append(t)

        return self.threads


    def getUnread(self):
        form = {
            'client': 'mercury_sync',
            'folders[0]': 'inbox',
            'last_action_timestamp': now() - 60*1000
            #'last_action_timestamp': 0
        }
        r = self._post(ThreadSyncURL, form)
        if not r.ok or len(r.text) == 0:
            return None

        j = get_json(r.text)
        result = {
            "message_counts": j['payload']['message_counts'],
            "unseen_threads": j['payload']['unseen_thread_ids']}
        return result

    def markAsDelivered(self, userID, threadID):
        data={"message_ids[0]": threadID}
        data["thread_ids[%s][0]"%userID] = threadID
        r = self._post(DeliveredURL, data)
        return r.ok

    def markAsRead(self, userID):
        data={
            "watermarkTimestamp": now(),
            "shouldSendReadReceipt": True}
        data["ids[%s]"%userID] = True
        r = self._post(ReadStatusURL, data)
        return r.ok

    def markAsSeen(self):
        r = self._post(MarkSeenURL, {"seen_timestamp": 0})
        return r.ok


    def ping(self, sticky):
        data={
            'channel': self.user_channel,
            'clientid': self.client_id,
            'partition': -2,
            'cap': 0,
            'uid': self.uid,
            'sticky': sticky,
            'viewer_uid': self.uid
        }
        r = self._get(PingURL, data)
        return r.ok

    def _getSticky(self):
        '''
        Call pull api to get sticky and pool parameter,
        newer api needs these parameter to work.
        '''
        data={ "msgs_recv": 0 }

        r = self._get(StickyURL, data)
        j = get_json(r.text)

        if 'lb_info' not in j:
            raise Exception('Get sticky pool error')

        sticky = j['lb_info']['sticky']
        pool = j['lb_info']['pool']
        return sticky, pool


    def _pullMessage(self, sticky, pool):
        '''
        Call pull api with seq value to get message data.
        '''
        data={
            "msgs_recv": 0,
            "sticky_token":sticky,
            "sticky_pool":pool
        }

        r = self._get(StickyURL, data)
        j = get_json(r.text)
        if not j: return j

        self.seq = j.get('seq', '0')
        return j

    def _parseTimeInMessage(self,metadata):
        if 'message' in metadata.keys(): ## full msg json
            msgtime = metadata['message']['timestamp']
        else:                            ## delta msg
            msgtime = metadata['delta']['messageMetadata']['timestamp']

        msgtime = int(msgtime)/1000
        timestamp = time.strftime("%H:%M",time.localtime(msgtime))
        return timestamp

    def _parseGroupMessage(self,metadata):
        #print("_parseGroupMessage(): parsing msg")
        if 'delta' ==  metadata['type']:
            thread_fbid = metadata['delta']['messageMetadata']['threadKey']['threadFbId']
            message=metadata['delta']['body']
            mid = metadata['delta']['messageMetadata']['messageId']
            sender_fbid = metadata['delta']['messageMetadata']['actorFbId']
            thread_name = thread_fbid
            sender_name = sender_fbid
            if thread_fbid in self.roster.keys(): self.last_tname = self._roster(thread_fbid)
            if sender_fbid in self.roster.keys(): sender_name = self._roster(fbid)
        elif 'messaging' ==  metadata['type']:
            thread_fbid = metadata['message']['thread_fbid']
            message=metadata['message']['body']
            mid = metadata['message']['mid']
            thread_name = metadata['message']['group_thread_info']['name']
            sender_fbid = metadata['message']['sender_fbid']
            sender_name = metadata['message']['sender_name']
            self._roster(thread_fbid,thread_name)
            self._roster(sender_fbid,sender_name)
        #print("_parsePersonalMessage(): get "+message)
        #print(mid)
        return message,mid,thread_fbid,sender_fbid
        
    def _parsePersonalMessage(self,metadata):
        #print("_parsePersonalMessage(): parsing msg")
        if metadata['type'] in ['delta']:
            mid =   metadata['delta']['messageMetadata']['messageId']
            message=metadata['delta']['body']
            fbid =  metadata['delta']['messageMetadata']['actorFbId']
        elif metadata['type'] in ['m_messaging', 'messaging']:
            mid =   metadata['message']['mid']
            message=metadata['message']['body']
            fbid =  metadata['message']['sender_fbid']
            name =  metadata['message']['sender_name']
            self._roster(fbid,name)
        #print("_parsePersonalMessage(): get "+message)
        #print(mid)
        return message,mid,fbid

    def _isDeltaMsg(self,m):
        if m['type'] in ['delta'] and 'body' in m['delta'].keys(): return True
        return False
    def _parseMessage(self, content):
        '''
        Get message and author name from content.
        May contains multiple messages in the content.
        '''
        if 'ms' not in content:
            return
        for m in content['ms']:
            if m['type'] in ['m_messaging', 'messaging'] or self._isDeltaMsg(m):
                thread_id = ''
                mid = ''
                sender_fbid = ''
                try:
                    message,mid,thread_id,sender_fbid =  self._parseGroupMessage(m)
                except:
                    #print("_parseGroupMessage():")
                    #print(exc_info())
                    pass

                if not mid:
                    try:
                        message,mid,sender_fbid = self._parsePersonalMessage(m)
                    except:
                        #print("_parsePersonalMessage():")
                        #print(exc_info())
                        pass
                if not mid: # not message
                    #print "not message"
                    return

                stickurl = ""
                if not message:
                    try: 
                        stickurl = metadata['message']['attachments'][0]['url']

                    except:
                        pass
                if mid == self.last_mid:
                    pass
                else:
                    self.last_mid = mid
                    self.on_message(mid,message,sender_fbid,thread_id,self._parseTimeInMessage(m), stickurl)
            elif m['type'] in ['typ']:
                try:
                    fbid =  m["from"]
                    self.on_typing(fbid)
                except:
                    open("log.txt","a").write(str(m)+"\n")
            elif m['type'] in ['m_read_receipt']:
                try:
                    author = m['author']
                    reader = m['reader']
                    msgtime = m['time']
                    self.on_read(author, reader, msgtime)
                except:
                    open("log.txt","a").write(str(m)+"\n")
            elif m['type'] in ['notification_json']:
                try:
                    likemsg = m['nodes'][0]['unaggregatedTitle']['text']
                    #likemsg = m['nodes'][0]['unaggregatedTitle']['text']
                    self.on_notify(likemsg,m)
                except :
                    open("like_err.log","a").write(str(m)+"\n")
                    self.on_notify(u'someone gives you a like',m)
            else:
              open("log.txt","a").write(str(m)+"\n")

    def listen(self, markAlive=True):
        self.listening = True
        sticky, pool = self._getSticky()

        if self.debug:
            print("Listening...")

        while self.listening:
            try:
                if markAlive: self.ping(sticky)
                try:
                    content = self._pullMessage(sticky, pool)
                    self._parseMessage(content)
                except requests.exceptions.RequestException as e:
                    continue
            except KeyboardInterrupt:
                break
            except requests.exceptions.Timeout:
              pass

    def on_message(self,mid, message, author_id, thread_id, timestamp, stickurl):
        tid = thread_id or author_id
        self.markAsDelivered(tid, mid)
        self.markAsRead(tid)

    def on_typing(self, author_id):
        pass

    def on_read(self, author, reader, msgtime):
        pass
    def on_notify(self, text, metadata):
        pass
    def stop_listen(self):
        self.listening = False
