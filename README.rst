======
cliFBChat
======

Receive and reply facebook messages with terminal.

It's also print notification of facebook.

Powered by (modified) fbchat python lib(https://github.com/carpedm20/fbchat/).

**No XMPP or API key is needed**. Just use your ID and PASSWORD.


Installation
============

.. code-block:: console

    $ git clone https://github.com/blcc/cliFBChat.git

Usage
=======

.. code-block:: console

    $ python cliFBChat.py

And input FB username(email) and password.

If someone send you a message, you can just type to reply.

Or send message to someone with following command.

Commands
--------

    /whois [username]

Find user

    /history [number]

Show [number] historical chats. Default is 5.


    /talkto [number]

Set message send destination.


    [enter]

Show who talk to now.


    /set [FB id with long number] [is group chat(1) or no(0)]

Same as /talkto, but use user id if already know.

    [Other things]

Send message to user/group chat.

Known issue
=======
Needs re-login after long time(over night) idle to send message.

Occasional encoding error.
(ex. chinese(UTF-8) name and send pure ascii message.)

Lost message when mass chatting.

Author
=======
blc
