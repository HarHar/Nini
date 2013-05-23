#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mega import Mega
import sys
from byteformat import format as fmt

class BotModule(object):
	def __init__(self, storage):
		self.storage = storage
		self.admins = {}
		self.bot = None

		sys.stdout.write(' (logging in to mega.co.nz) ')
		self.mega = Mega({'verbose': True})
		self.mega.login_anonymous()
	def event(self, ev):
		if ev['name'] == 'msg':
			split = ev['msg'].split(' ')

			for word in split:
				if (word.lower().find('https://mega.co.nz/#!') == 0) or (word.lower().find('http://mega.co.nz/#!') == 0):
					try:
						info = self.mega.get_public_url_info(word)
						assert(info.get('name') != None)
						assert(info.get('size') != None)
					except Exception, e:
						ev['to'].msg('There was an error fetching Mega info from that link, it may be private or there may have happened a communication error. Sorry.')
						return

					ev['to'].msg(chr(3)+ '5Mega| ' + chr(15) +chr(2) + info['name'] + chr(15) + ' [' + fmt(info['size']) + ']')
