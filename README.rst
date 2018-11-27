======
cliIM
======

Receive and reply facebook messages with terminal.

Powered by fbchat python lib.

**No API key is needed**. Just use your ID and PASSWORD.


Updates
============
27Nov2018
    Fetch history message when /talkto someone.

08Nov2018 Big change!
    Rename to cliIM.
    Remove XMPP module.
    Cmd-line style. (command line at bottom)
        Terminal style shortcut support.(C-a,C-e,C-u... etc.)
        Simple 'loading animation'.
    Save/load login session automatically.
    

01Nov2018
    Catch up fbchat updates.
    Keep previous login session in fbcookie.txt


Installation
============

.. code-block:: console

    $ git clone https://github.com/blcc/cliFBChat.git


Dependence
-------
python3

fbchat (https://github.com/carpedm20/fbchat/).

termcolor (optional)

Setting
--------

account.txt  # required, line 1 is FB userid, line 2 is password.



Usage
=======

.. code-block:: console

    $ python cliIM.py

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


    /quit

Leave cliIM.


Trick
=======
    You can modify fbroster.txt file to give someone alias.


Known issue
=======

Takes time to exit after /quit or Ctrl-C.
    Or press Ctrl-C one more time, it will leave with error (but ok).

Author
=======
blc
