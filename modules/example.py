#!/usr/bin/env python
# -*- coding: utf-8 -*-

class BotModule(object):
	def __init__(self, storage):
		self.storage = storage
		self.admins = {}
		print 'Example module loaded'
	def setBot(self, bot):
		self.bot = bot
	def setAdmins(self, admins):
		self.admins = admins
	def event(self, ev):
		for admin in self.admins:
			admin.send(':$event!HarBot@harh.net PRIVMSG ' + self.admins[admin]['nick'] + ' :' + repr(ev) + '\r\n')

		if ev['name'] == 'msg':
			split = ev['msg'].split(' ')

			if split[0].lower() == '$test':
				self.bot.msg(ev['to'], 'It works .‿.')