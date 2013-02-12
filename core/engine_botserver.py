#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Yeah, yeah, globals

import SocketServer
import socket
import sys
import os
import threading
import json
connections = {}

class botServer(SocketServer.BaseRequestHandler):
	def setup(self):
		global connections

		connections[self.request] = True
	def handle(self):
		global bot
		global connections

		data = 'dummy text'
		while data:
			try:
				data = self.request.recv(4096).replace('\r', '')
			except:
				break

			chunks = data.split('\n')

			for chunk in chunks:
				try:
					cmd = json.loads(chunk)

					if cmd['command'] == 'msg':
						bot.msg(cmd['who'], cmd['message'])
					elif cmd['command'] == 'join':
						bot.join(cmd['channel'], cmd.get('password') if cmd.get('password') != None else '')
					elif cmd['command'] == 'part':
						bot.part(cmd['channel'])
					elif cmd['command'] == 'quit':
						bot.quit(cmd.get('reason') if cmd.get('reason') != None else 'Leaving')
				except:
					continue

	def finish(self):
		global connections
		connections[self.request] = False

def start(botInstance, modules):
	print '[\033[94minfo\033[0m] Listening on 60981 for stand-alone plugins'
	global moduleInstances
	moduleInstances = modules
	global bot
	bot = botInstance
	server = SocketServer.ThreadingTCPServer(('127.0.0.1', 60981), botServer)
	server.allow_reuse_address = True
	server.serve_forever()