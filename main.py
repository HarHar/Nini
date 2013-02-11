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

directory = os.path.dirname(os.path.realpath(__file__))
modules = massload(os.path.join(directory, 'modules/'))
modInstances = {}
for module in modules:
	try:
		modInstances[module] = {'instance': modules[module].BotModule(persistentVariables), 'enabled': True}
	except AttributeError:
		print 'Ignoring ' + module

bot = core.engine_bot.Bot(server='irc.rizon.net', nick='KBlitz', channel='#KBlitz2', adminPassword='lel', modules=modInstances)

srv = threading.Thread(target=core.engine_botserver.start, args=(bot, modInstances))
srv.setDaemon(True)
srv.start()

admin = threading.Thread(target=core.engine_admin.start, args=(bot, modInstances))
admin.setDaemon(True)
admin.start()