======
cliFBChat
======

Receive and reply facebook messages with terminal.

Powered by fbchat python lib.

**No API key is needed**. Just use your ID and PASSWORD.


Updates
============
01Nov2018
    Catch up fbchat updates.
    Keep previous login session in fbcookie.txt


Installation
============

.. code-block:: console

    $ git clone https://github.com/blcc/cliFBChat.git


Dependence
-------
fbchat (https://github.com/carpedm20/fbchat/).

termcolor (optional)

Setting
--------

account.txt  # optional, line 1 is FB userid, line 2 is password.



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

Facebook often change format.

Takes time to exit.


Author
=======
blc
