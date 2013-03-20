NiNi
====

Python IRC Bot (continued from HarBot)

The bot is constituted of four parts: an irc client, local server for stand-alone plugins, set of plugins and a irc server, each of them on their own thread.

Specifications
====
The IRC client is implemented using sockets.

Plugins have their own "persistent variable", so that they can store/read data in an organized way. They can register commands (which will be triggered by a combination of fantasy character and prefix/affix (user set)), modifiers (so that they can easily modify/block what is sent) and events (join/part/quit/mode/kick/nick/message).

The IRC server listens on port 6262, and upon connecting you need to send "/msg $admin auth password", keep in mind that the password *MUST* be secure, if the password is wrong the connection is closed. After authenticating, a plugin (events.py) will relay all events to all connected admins, you will have access to $modules $eval and $admin (all of which you /msg inside of your IRC client of choice). The $eval is exceptionally practical: if you want to make the bot say something, you do "/msg $eval bot.say('#channel', 'Hello there')", if you want it to join a channel "/msg $eval bot.join('#channel')", you also can modify persistent variables, manage modules and so on...

It listens on the port 60981 (only locally) for stand-alone plugins, the connection is entirely based on JSON and its documentation will be written soon.

Usage
====
Simply execute main.py, the first time it will ask for settings such as channel/command prefix/etc, if you want to change those use the --config argument. It will then proceed to load modules, if the module is loaded correctly, it will show "[done]", if it does not appear to be a Nini plugin it will show "[warn]", if the module has thrown an exception it will show "[error]".

DEVELOPERS DEVELOPERS DEVELOPERS
====
An example of module is located on modules/example.py, use it.

whoami
====
HarHar @ irc.rizon.net
