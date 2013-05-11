#!/usr/bin/env python
# -*- coding: utf-8 -*-

class BotModule(object):
	def __init__(self, storage):
		self.storage = storage
		self.admins = {}
		self.bot = None
	def event(self, ev):
		if ev['name'] == 'msg':
			if ev['from'].nick == self.bot.nick: return
			split = ev['msg'].split(' ')

			if (ev['to'].ischannel == False) and (ev['from'].host == ev['admin'].host):
				if split[0].lower() == 'afk':
					if (self.storage['afk'].get(ev['from'].nick) in ['off', None]) == False:
						self.bot.msg(ev['from'].nick, 'AFK off')

						tmp = self.storage['afk']
						tmp[ev['from'].nick] = 'off'
						self.storage['afk'] = tmp
					else:
						self.bot.msg(ev['from'].nick, 'AFK set')
						if len(split) == 1: split = ['afk', 'away']

						a = ''
						for x in split[1:]:
							a += x + ' '
						a = a[:-1]
						tmp = self.storage['afk']
						tmp[ev['from'].nick] = a
						self.storage['afk'] = tmp

						del a 
						del x

			for usr in self.storage['afk']:
				if self.storage['afk'][usr] != 'off':
					if usr in ev['msg']:
						if self.storage['afk'][usr] == 'away':
							p = ''
						else:
							p = ' [' + self.storage['afk'][usr] + chr(15) + ']'
						self.bot.msg(ev['to'].name, usr + ' is away' + p + ' :C')

						del p