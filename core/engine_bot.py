#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import socket
import threading
from time import sleep

def pushEvent(modules, event):
	for module in modules:
		if modules[module]['enabled']:
			modules[module]['instance'].event(event)

class Bot(object):
	def __init__(self, server='localhost', serverPassword='', port=6667, nick='KB', nickservPass='', channel='', channelPassword='', modules={}, adminPassword='default'):
		self.modules = modules
		self.server = server
		self.serverPassword = serverPassword
		self.port = port
		self.nick = nick
		self.nickservPass = nickservPass
		self.channel = channel
		self.channelPassword = channelPassword
		self.password = adminPassword

		#Connection/authentication routine
		self.sock = socket.socket()
		self.sock.connect((server, port))

		if serverPassword != '':
			self.sockSend('PASS ' + serverPassword)
		self.sockSend('NICK ' + nick)
		self.sockSend('USER ' + nick + ' ' + nick + ' ' + nick + ' :HarBot v3')

		self.active = True
		self.thread = threading.Thread(target=handlingThread, args=(self.sock, self))
		self.thread.setDaemon(True)
		self.thread.start()

	def onWelcome(self):
		sleep(1)
		if self.nickservPass != '':
			self.msg('NickServ', 'IDENTIFY ' + self.nickservPass)

		if self.channel != '':
			self.join(self.channel)

		for instance in self.modules:
			if self.modules[instance]['enabled']:
				self.modules[instance]['instance'].setBot(self)
	def sockSend(self, s):
		self.sock.send(s + '\r\n')
	def msg(self, who, message):
		self.sockSend('PRIVMSG ' + who + ' :' + message)
	def join(self, channel, passw=''):
		if passw != '': passw = ' ' + passw
		self.sockSend('JOIN ' + channel + passw)

		pushEvent(self.modules, {'name': 'selfjoin', 'channel': channel})
	def part(self, channel, reason=''):
		self.sockSend('PART ' + channel + ' :' + reason)

		pushEvent(self.modules, {'name': 'selfpart', 'channel': channel})
	def quit(self, reason='Leaving'):
		self.active = False
		self.sockSend('QUIT :' + reason)
		self.sock.close()

		pushEvent(self.modules, {'name': 'quit', 'reason': reason})
	def nick(newnick):
		self.sockSend('NICK ' + newnick)
		oldnick = self.nick
		self.nick = newnick

		pushEvent(self.modules, {'name': 'selfnick', 'old': oldnick, 'new': newnick})
	def irc_onMsg(self, nickFrom, host, to, msg):
		pushEvent(self.modules, {'name': 'msg', 'from': nickFrom, 'from_host': host, 'to': to, 'msg': msg})

		if to[0] == '#':
			split = msg.split(' ')

def handlingThread(sock, bot):
	while bot.active:
		rcvd = sock.recv(4096).split('\n')
		for line in rcvd:
			line = line.replace('\r', '')

			if line.split(' ')[0] == 'PING':
				try:
					sock.send('\r\nPONG ' + line.split(' ')[1].replace(':', '') + '\r\n')
				except:
					sock.send('\r\nPONG\r\n')

			lsplit = line.split(':')
			try:
				csplit = lsplit[1].split(' ')
			except:
				csplit = []
			#print repr(csplit) + ' - ' + repr(lsplit) +# ' - ' + repr(line)
			if len(lsplit) >= 2:
				if len(csplit) >= 2:
					if csplit[1] == '001':
						bot.onWelcome()
				if 'PRIVMSG' in lsplit[1] or 'NOTICE' in lsplit[1]:
					# ---BEGIN WTF BLOCK---
					lsplit = line.split(':')
					addrnfrom = ''
					if '~' in lsplit[1]:
						addrnfrom = lsplit[1].split('~')[1].split(' ')[0]
						nfrom = lsplit[1].split('!')[0]
					else:
						nfrom = lsplit[1].split('!')[0]

					if len(lsplit[1].split()) >= 3:
						to = lsplit[1].split()[2]
					msg = ''
					for brks in lsplit[2:]:
						msg += brks + ':'
					msg = msg[:-1].lstrip()
					# ---END WTF BLOCK- --
					bot.irc_onMsg(nfrom, addrnfrom, to, msg)