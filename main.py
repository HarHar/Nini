#!/usr/bin/python
"""
This is where we instanciate stuff
"""
import threading

import var
import core.engine_bot
import core.engine_botserver
import core.engine_admin

import os
import imp
import traceback

import sys

def massload(folder):
	modls = {}
	from os.path import join
	for root, dirs, files in os.walk(folder):
		for f in files:
			fullname = join(root, f)
			if max(fullname.split('.')) == 'py':
				try:
					ff = open(fullname, 'U')
					modls[fullname.split('/')[-1:][0].split('.')[0]] = imp.load_module(fullname.split('/')[-1:][0].split('.')[0], ff, os.path.realpath(fullname), ('.py', 'U', 1))
				except Exception, info:
					print('Could not load module: ' + fullname)
					print('--- ' + str(info) + ' ---')
					print traceback.format_exc()
					exit()
	return modls

global persistentVariables, bot, srv, admin, modules, modInstances # Lazy
persistentVariables = var.persVars()

config = False
if '--config' in sys.argv:
	config = True

if persistentVariables['config'] == {}:
	config = True

if config:
	#(self, server='localhost', serverPassword='', port=6667, nick='KB', nickservPass='', channel='', channelPassword='', modules={}, adminPassword='default', cmd_type=0, cmd_char='$'):
	print 'Initiating configuration routine...'
	print 'You may access this anytime by using the "--config" parameter'
	newconf = {}
	newconf['server'] = raw_input('IRC Server host/address> ')
	newconf['serverPassword'] = raw_input('Server password [optional]> ')

	p = 'lol'
	while p.isdigit() == False: p = raw_input('Port [number only]> ')
	newconf['port'] = int(p)

	newconf['nick'] = raw_input('Nick> ')
	newconf['nickservPass'] = raw_input('NickServ password [optional]> ')
	newconf['channel'] = raw_input('Channels [separated by comma]> ')
	newconf['adminPassword'] = raw_input('Remote administration password [IMPORTANT!]> ')

	newconf['admin_nick'] = raw_input('Your nick> ')
	newconf['admin_host'] = raw_input('Your ident@host (or VHost)> ')

	t = 'lol'
	while (t in ['0', '1']) == False: t = raw_input('Command type [0 for prefix; 1 for affix]> ')
	newconf['cmd_type'] = int(t)

	newconf['cmd_char'] = raw_input('Command ' + ('prefix' if int(t) == 0 else 'affix') + ' character> ')

	persistentVariables['config'] = newconf

	print 'Saved'
	print 'Continuing boot procedure'

directory = os.path.dirname(os.path.realpath(__file__))
modules = massload(os.path.join(directory, 'modules/'))
modInstances = {}
for module in modules:
	try:
		sys.stdout.write('Loading ' + repr(module) + '... ')
		modInstances[module] = {'instance': modules[module].BotModule(persistentVariables), 'enabled': True}
		sys.stdout.write('[\033[92mdone\033[0m]\n')
	except AttributeError:
		sys.stdout.write('[\033[93mwarning\033[0m]\n')
	except:
		sys.stdout.write('[\033[91merror\033[0m]\n')

config = persistentVariables['config']

adm = core.engine_bot.user()
adm.nick = config['admin_nick']
adm.host = config['admin_host']
bot = core.engine_bot.Bot(server=config['server'], serverPassword=config['serverPassword'], port=config['port'], nick=config['nick'], nickservPass=config['nickservPass'], channel=config['channel'], adminPassword=config['adminPassword'], modules=modInstances, cmd_type=config['cmd_type'], cmd_char=config['cmd_char'], admin=adm) #We need to go wider

srv = threading.Thread(target=core.engine_botserver.start, args=(bot, modInstances))
srv.setDaemon(True)
srv.start()

admin = threading.Thread(target=core.engine_admin.start, args=(bot, modInstances))
admin.setDaemon(True)
admin.start()

#All stuff is threaded so we really don't have to do anything here
#Maybe on the future there'll be a sort of interpretor
from time import sleep
while True:
	try:
		sleep(420)#blazeitfgt
	except:
		os.kill(os.getpid(), 9) #seppuku