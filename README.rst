======
cliFBChat
======

Receive and reply facebook messages with terminal.

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
=======

.. code-block:: console
    /whois [username]
Find user

.. code-block:: console
    /talkto [number]
Set message send destination. User only.

.. code-block:: console
    [enter]
Show who talk to now.


.. code-block:: console
    /set [FB id with long number] [is group chat(1) or no(0)]
Same as /talkto, but use user id if already know.

Author
=======

blc
