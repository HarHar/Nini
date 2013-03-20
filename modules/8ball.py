#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random

class BotModule(object):
	def __init__(self, storage):
		self.storage = storage
		self.answers = [chr(3) + '04Of course not!', chr(3) + '05No', 'Mayhaps', chr(3) + '03Yes', chr(3) + '02Sure!']
	def register(self):
		return {'functions': [{'8ball': self.cmd_8ball}, {'choose': self.cmd_choose}]}
	def cmd_8ball(self, args, receiver, sender):
		"""8ball [question] | True | Answers a yes/no question"""
		if args == '':
			self.bot.msg(receiver.name, 'Need a question, sly')
			return
			
		if receiver.ischannel:
			fixed = args
			if fixed[0].isupper() == False: fixed = fixed[0].upper() + fixed[1:]
			if fixed[-1] != '?': fixed = fixed + '?'

			self.bot.msg(receiver.name, chr(2) + 'Question: ' + chr(15) + fixed)
			self.bot.msg(receiver.name, chr(2) + 'Answer: ' + chr(15) + random.choice(self.answers))
	def cmd_choose(self, args, receiver, sender):
		"""choose one, two or three | True | Picks one of the items you give"""
		if receiver.ischannel:
			if args.find('or') != -1:
				s = args.split(' or ')
				if len(s) == 2:
					if len(s[0].split(',')) > 1:
						s = s[0].split(',') + [s[1]]
				self.bot.msg(receiver.name, sender.nick + ', ' + random.choice(s).strip(',').lstrip().rstrip())
				return
			self.bot.msg(receiver.name, sender.nick + ', ' + random.choice(args.split(' ')).strip(','))