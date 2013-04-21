#!/usr/bin/env python
import os
import sys
import json

#Persistent variables
class persVars(object):
	def __init__(self):
		self.vardir = os.path.dirname(os.path.realpath(__file__)) + '/'
	def __getitem__(self, item):
		if isinstance(item, str) == False:
			print '[NON-FATAL] ' + repr(item) + ' is not a string'
			return None

		varfile = os.path.join(self.vardir + item + '.var')
		if os.path.exists(varfile):
			return json.load(open(varfile, 'r'))
		else:
			return {}
	def __setitem__(self, item, content):
		if isinstance(item, str) == False:
			print '[NON-FATAL] ' + repr(item) + ' is not a string'
			return None

		varfile = os.path.join(self.vardir + item + '.var')
		json.dump(content, open(varfile, 'w'))