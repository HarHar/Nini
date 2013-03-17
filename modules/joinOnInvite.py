#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Joins on invite
import threading #1st join-on-invite that needs threading
from time import sleep

def waitAndJoin(bot, channel, tries):
	sleep(tries * 5)
	bot.join(channel)

class BotModule(object):
	def __init__(self, storage):
		self.storage = storage
		self.admins = {}
		self.bot = None
	def event(self, ev):
		if ev['name'] == 'invite':
			tries = self.storage['autojoin'].get(ev['channel'], 1)
			self.bot.notice(ev['from'].nick, 'Joining ' + ev['channel'] + ' in ' + str(tries * 5) + ' seconds')
			thread = threading.Thread(target=waitAndJoin, args=(self.bot, ev['channel'], tries))
			thread.setDaemon(True)
			thread.start()

			tmp = self.storage['autojoin']
			tmp[ev['channel']] = tries + 1
			self.storage['autojoin'] = tmp
			del tmp