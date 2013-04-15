#!/usr/bin/env python
# -*- coding: utf-8 -*-
##Functions that do not really provides more features to the end-users
##but nonetheless are useful as a module
import os, inspect

def fuzzyTail():
	pass

class BotModule(object):
	def __init__(self, storage):
		self.storage = storage
		self.admins = {}
		self.bot = None
	def register(self):
		return {'functions': [{'help': self.cmd_help}], 'aliases': {'commands': 'help', 'cmds': 'help'}}
	def event(self, ev):
		pass
	def cmd_help(self, args, receiver, sender):
		"""help | True | shows where to get a list of commands"""
		baseURL = ''
		if (self.storage['config'].get('customURL') in [None, '']) == False:
			baseURL = self.storage['config']['customURL']
		else:
			baseURL = 'http://' + self.storage['config']['domain'] + ':' + str(self.storage['config']['webport']) + '/'
		URL = baseURL + os.path.basename(inspect.getsourcefile(fuzzyTail)).split('.')[0] + '/commands'

		if receiver.ischannel:
			receiver.msg('I am hosting my command list at ' + chr(2) + URL)
		else:
			sender.msg('I am hosting my command list at ' + chr(2) + URL)


	def http(self, path):
		p = path.split('/')
		#p[0] == '', p[1] == 'core', p[2] == 'SOMEPAGE', p[3] == '' <-- example

		out = ''
		if len(p) >= 2:
			if p[2].lower() == 'commands':
				for cmd in self.bot.commands:
					try:
						doc = self.bot.commands[cmd]['func'].__doc__.split('|')
						if bool(doc[1]):
							if self.bot.cmd_type == 0:
								out += '<p><span class="lead">' + self.bot.cmd_char + doc[0].strip() + '</span> '+ doc[2] + '</p>'
							else:
								out += '<p><span class="lead">' + doc[0].strip() + self.bot.cmd_char + '</span> '+ doc[2] + '</p>'
					except:
						continue
				return {'title': 'Commands', 'content': out}
			else:
				return {'title': 'Core', 'content': 'Provides some cool stuff'}

		#return {'title': 'Example web page', 'content': '<p class="lead">This is a cute example page :3</p><p>It looks like you are on the page ' + path + '..</p>'}