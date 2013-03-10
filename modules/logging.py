#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Logs every event

class BotModule(object):
	def __init__(self, storage):
		self.storage = storage
	def event(self, ev):
		logs = self.storage['logs']
		logs[len(logs) + 1] = ev
		self.storage['logs'] = logs
		del logs