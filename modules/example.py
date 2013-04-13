#!/usr/bin/env python
# -*- coding: utf-8 -*-

class BotModule(object):
	def __init__(self, storage):
		self.storage = storage
		self.admins = {}
		self.bot = None
	def register(self):
		return {'functions': [{'test2': self.cmd_test2}], 'aliases': {'ts2': 'test2'}}
	def event(self, ev):
		if ev['name'] == 'msg':
			split = ev['msg'].split(' ')

			if split[0].lower() == '$test':
				self.bot.msg(ev['to'].name, 'It works .‿.')

	##############
	#Registered command
	##############
	def cmd_test2(self, args, receiver, sender):
		"""test2 | True | Ping-pong"""
		self.bot.msg(receiver.name, 'This works too \\^ ^')

	##############
	#Modifier
	##############
	def mod_replace(self, content):
		if content['name'] == 'msg':
			content['message'] = content['message'].replace('ASSHOLE', '[CENSORED]')
		return content	