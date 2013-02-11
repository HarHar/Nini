#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Sends events to the admins

class BotModule(object):
	def __init__(self, storage):
		self.storage = storage
		self.admins = {}
	def setBot(self, bot):
		self.bot = bot
	def setAdmins(self, admins):
		self.admins = admins
	def event(self, ev):
		for admin in self.admins:
			admin.send(':$event!HarBot@harh.net PRIVMSG ' + self.admins[admin]['nick'] + ' :' + repr(ev) + '\r\n')