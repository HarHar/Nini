#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, inspect
import sys

def fuzzyTail():
	pass

class BotModule(object):
	def __init__(self, storage):
		self.storage = storage
		self.admins = {}
		self.bot = None
	def register(self):
		return {'functions': [{'help': self.cmd_help}, {'quit': self.quit}, {'modules': self.modules}, {'chnick': self.chnick}, {'join': self.join}, {'part': self.part}, {'mode': self.mode}, {'kick': self.kick}, {'msg': self.msg}, {'notice': self.notice}, {'say': self.say}], 'aliases': {'commands': 'help', 'cmds': 'help'}}
	def event(self, ev):
		pass
	def cmd_help(self, args, receiver, sender):
		"""help | {'public': True, 'admin_only': False} | shows where to get a list of commands"""
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

	def quit(self, args, receiver, sender):
		"""quit | {'public': False, 'admin_only': True} | quits bot """
		self.bot.msg(receiver.name, "Exiting on user command")
		self.bot.quit()

	def chnick(self, args, receiver, sender):
		"""chnick [new nick] | {'public': False, 'admin_only': True} | changes nick """
		if args == '':
			receiver.msg('Arguments: [new nick]')
			return

		receiver.msg('Trying to change nick..')
		self.bot.chnick(args)


	def join(self, args, receiver, sender):
		"""join #[channel] | {'public': False, 'admin_only': True} | joins channel """
		if args == '':
			receiver.msg('Arguments: #[channel]')
			return

		receiver.msg('Joining ' + args.split(' ')[0])
		self.bot.join(args.split(' ')[0])


	def part(self, args, receiver, sender):
		"""part #[channel] | {'public': False, 'admin_only': True} | parts channel """
		if args == '':
			receiver.msg('Arguments: #[channel]')
			return

		receiver.msg('Parting ' + args.split(' ')[0])
		self.bot.part(args.split(' ')[0])

	def mode(self, args, receiver, sender):
		"""mode [channel/user] [modes] [extra] | {'public': False, 'admin_only': True} | sets mode """
		if args == '':
			receiver.msg('Arguments: [channel/user] [modes] [extra]')
			return

		self.bot.mode(args)

	def kick(self, args, receiver, sender):
		"""kick [channel] [nick] [reason] | {'public': False, 'admin_only': True} | kicks a user from a channel """
		s = args.split(' ')
		if len(s) < 3:
			receiver.msg('Arguments: [channel] [nick] [reason]')
			return

		x = ''
		for y in s[2:]:
			x += y + ' '
		x = x[:-1]
		self.bot.kick(s[0], s[1], x)

	def msg(self, args, receiver, sender):
		"""msg [nick/channel] [message] | {'public': False, 'admin_only': True} | sends a user/channel a message """
		s = args.split(' ')
		if len(s) < 2:
			receiver.msg('Arguments: [nick/channel] [message]')
			return

		x = ''
		for y in s[1:]:
			x += y + ' '
		x = x[:-1]
		self.bot.msg(s[0], x)

	def notice(self, args, receiver, sender):
		"""msg [nick/channel] [message] | {'public': False, 'admin_only': True} | sends a user/channel a message """
		s = args.split(' ')
		if len(s) < 2:
			receiver.msg('Arguments: [nick/channel] [message]')
			return

		x = ''
		for y in s[1:]:
			x += y + ' '
		x = x[:-1]
		self.bot.notice(s[0], x)

	def modules(self, args, receiver, sender):
		"""modules [unload/reload] | {'public': False, 'admin_only': True} | controls modules """
		s = args.lower().split()

		if len(s) == 0: return

		if s[0] == 'unload':
			receiver.msg('Unloading modules...')
			self.bot.unloadModules()
			receiver.msg('Done')
		elif s[0] == 'reload':
			receiver.msg('Reloading modules...')
			try:
				self.bot.reloadModules()
			except Exception, e:
				receiver.msg(chr(3) + '5Error!'+ chr(15) + ' ' + str(e))
				return
			receiver.msg('Done')
		elif s[0] == 'load':
			receiver.msg('This command is not implemented since it wouldn\'t be possible for it to be usable')
			receiver.msg('If you wish to load all modules you should go to the admin interface and type "/msg $eval bot.loadModules()"')
		else:
			receiver.msg('Arguments: [unload/reload]')

	def say(self, args, receiver, sender):
		"""say [text] | {'public': False, 'admin_only': True} | sends the current channel a message """
		if args == '':
			receiver.msg('Arguments: [text]')
			return

		if receiver.ischannel:
			receiver.msg(args)
		else: sender.msg(args)

	def http(self, path, handler):
		p = path.split('/')
		#p[0] == '', p[1] == 'core', p[2] == 'SOMEPAGE', p[3] == '' <-- example

		out = ''
		if len(p) >= 2:
			if p[2].lower() == 'commands':
				for cmd in self.bot.commands:
					try:
						doc = self.bot.commands[cmd]['func'].__doc__.split('|')
						if eval(doc[1])['public'] == True:
							if self.bot.cmd_type == 0:
								out += '<p><span class="lead">' + self.bot.cmd_char + doc[0].strip() + '</span> '+ doc[2] + '</p>'
							else:
								out += '<p><span class="lead">' + doc[0].strip() + self.bot.cmd_char + '</span> '+ doc[2] + '</p>'
					except:
						continue
				return {'title': 'Commands', 'content': out, 'mascot': 'Saber2'}
			else:
				return {'title': 'Core', 'content': 'Provides some cool stuff'}
