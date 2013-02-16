#!/usr/bin/env python
# -*- coding: utf-8 -*-

class BotModule(object):
	def __init__(self, storage):
		self.storage = storage
		self.admins = {}
		self.bot = None
	def register(self):
		return {'functions': [{'test2': self.cmd_test2}], 'modifiers': [{'mod_test': self.mod_replace}]}
	def event(self, ev):
		if ev['name'] == 'msg':
			split = ev['msg'].split(' ')

			if split[0].lower() == '$test':
				self.bot.msg(ev['to'], 'It works .‿.')

	##############
	#Registered command
	##############
	def cmd_test2(self, args, receiver, sender, sender_address):
		self.bot.msg(receiver, 'This works too \\^ ^')

	##############
	#Modifier
	##############
	def mod_replace(self, content):
		if content['name'] == 'msg':
			content['message'] = content['message'].replace('ASSHOLE', '[CENSORED]')
		return content	