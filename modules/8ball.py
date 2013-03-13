#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

class BotModule(object):
	def __init__(self, storage):
		self.storage = storage
		self.answers = [chr(3) + '04Of course not!', chr(3) + '05No', 'Mayhaps', chr(3) + '03Yes', chr(3) + '02Sure!']
	def register(self):
		return {'functions': [{'8ball': self.cmd_8ball}]}
	def cmd_8ball(self, args, receiver, sender, sender_address):
		"""test2 [question] | True | Ping-pong"""
		if receiver[0] == '#':
			self.bot.msg(receiver, chr(2) + 'Question: ' + chr(15) + args)
			self.bot.msg(receiver, chr(2) + 'Answer: ' + chr(15) + random.choice(self.answers))