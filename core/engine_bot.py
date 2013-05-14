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
			try:
				modules[module]['instance'].event(event)
			except AttributeError:
				continue

class user():
	""" Dummy class to make it easier to deal with users."""
	nick = ''
	host = ''
	bot = None
	def msg(self, text):
		if self.bot != None:
			self.bot.msg(self.nick, text)
	def notice(self, text):
		if self.bot != None:
			self.bot.notice(self.nick, text)
	def __repr__(self):
		return '<User ' + self.nick + '>'

class receiver():
	""" Dummy class to make it easier to deal with who is receiving what """
	name = ''
	ischannel = False
	bot = None
	def msg(self, text):
		if self.bot != None:
			self.bot.msg(self.name, text)
	def notice(self, text):
		if self.bot != None:
			self.bot.notice(self.name, text)
	def part(self):
		if self.bot != None:
			self.bot.part(self.name)
	def join(self):
		if self.bot != None:
			self.bot.join(self.name)
	def __repr__(self):
		return '<Receiver ' + self.name + '>'


class Bot(object):
	def __init__(self, server='localhost', serverPassword='', port=6667, nick='KB', nickservPass='', channel='', channelPassword='', modules={}, adminPassword='default', cmd_type=0, cmd_char='$', admin=user(), loadModules_func=None, persVars=None):
		self.modules = modules
		self.server = server
		self.serverPassword = serverPassword
		self.port = port
		self.nick = nick
		self.nickservPass = nickservPass
		self.channel = channel
		self.channelPassword = channelPassword
		self.password = adminPassword
		self.commands = {}
		self.modifiers = {}
		self.aliases = {}
		self.cmd_type = cmd_type
		self.cmd_char = cmd_char
		self.joinedChannels = []
		self.ignores = {}
		self.admin = admin
		self.loadModules_func = loadModules_func
		self._persVars = persVars

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

		for module in modules:
			modules[module]['instance'].bot = self

		self.registerCommands()

	def onWelcome(self):
		sleep(1)
		if self.nickservPass != '':
			self.msg('NickServ', 'IDENTIFY ' + self.nickservPass)

		if self.channel != '':
			self.join(self.channel)
			self.joinedChannels = self.channel.replace(' ', '').split(',')

	def unloadModules(self):
		pushEvent(self.modules, {'name': 'unload'})

		del self.modules, self.commands, self.modifiers, self.aliases
		self.modules, self.commands, self.modifiers, self.aliases = {}, {}, {}, {}

	def loadModules(self):
		self.modules = self.loadModules_func(self._persVars)
		for module in self.modules:
			self.modules[module]['instance'].bot = self

		self.registerCommands()
		pushEvent(self.modules, {'name': 'loadComplete'})

	def reloadModules(self):
		self.unloadModules()
		self.loadModules()

	def registerCommands(self):
		del self.commands, self.modifiers, self.aliases
		self.commands, self.modifiers, self.aliases  = {}, {}, {}

		for instance in self.modules:
			if self.modules[instance]['enabled']:
				try:
					toRegister = self.modules[instance]['instance'].register()
				except AttributeError:
					toRegister = None

				if toRegister != None:
					if toRegister.get('functions') != None:
						for cmd in toRegister['functions']:
							for cc in cmd:
								self.commands[cc] = {'func': cmd[cc], 'module': self.modules[instance]}
					if toRegister.get('modifiers') != None:
						for mod in toRegister['modifiers']:
							for cc in mod:
								self.modifiers[cc] = {'func': mod[cc], 'module': self.modules[instance]}
					if toRegister.get('aliases') != None:
						for alias in toRegister['aliases']:
							self.aliases[alias] = {'target': toRegister['aliases'][alias], 'module': self.modules[instance]}
	def sockSend(self, s):
		self.sock.send(s.encode('utf-8') + '\r\n')
	def msg(self, who, message):
		for mod in self.modifiers:
			if self.modifiers[mod]['module']['enabled']:
				res = self.modifiers[mod]['func']({'name': 'msg', 'who': who, 'message': message})
				who = res['who']
				message = res['message']
				if res.get('block') != None: return

		self.sockSend('PRIVMSG ' + who + ' :' + message)

		pushEvent(self.modules, {'name': 'selfmsg', 'who': who, 'message': message})
		sleep(1)
	def notice(self, who, message):
		for mod in self.modifiers:
			if self.modifiers[mod]['module']['enabled']:
				res = self.modifiers[mod]['func']({'name': 'notice', 'who': who, 'message': message})
				who = res['who']
				message = res['message']
				if res.get('block') != None: return

		self.sockSend('NOTICE ' + who + ' :' + message)

		pushEvent(self.modules, {'name': 'selfnotice', 'who': who, 'message': message})
		sleep(1)
	def join(self, channel, passw=''):
		for mod in self.modifiers:
			if self.modifiers[mod]['module']['enabled']:
				res = self.modifiers[mod]['func']({'name': 'join', 'channel': channel, 'password': passw})
				channel = res['channel']
				passw = res['password']

		if passw != '': passw = ' ' + passw
		self.sockSend('JOIN ' + channel + passw)

		pushEvent(self.modules, {'name': 'selfjoin', 'channel': channel})
	def kick(self, channel, who, reason):
		for mod in self.modifiers:
			if self.modifiers[mod]['module']['enabled']:
				res = self.modifiers[mod]['func']({'name': 'selfkick', 'channel': channel, 'who': who, 'reason': reason})
				channel = res['channel']
				who = res['who']
				reason = res['reason']
				if res.get('block') != None: return

		self.sockSend('KICK ' + channel + ' ' + who + ' :' + reason)
	def mode(self, mode):
		for mod in self.modifiers:
			if self.modifiers[mod]['module']['enabled']:
				res = self.modifiers[mod]['func']({'name': 'selfmode', 'mode': mode})
				mode = res['mode']
				if res.get('block') != None: return

		self.sockSend('MODE ' + mode)
	def part(self, channel, reason=''):
		for mod in self.modifiers:
			if self.modifiers[mod]['module']['enabled']:
				res = self.modifiers[mod]['func']({'name': 'part', 'channel': channel, 'reason': reason})
				channel = res['channel']
				reason = res['reason']
				if res.get('block') != None: return

		self.sockSend('PART ' + channel + ' :' + reason)

		pushEvent(self.modules, {'name': 'selfpart', 'channel': channel})
	def quit(self, reason='Leaving'):
		for mod in self.modifiers:
			if self.modifiers[mod]['module']['enabled']:
				res = self.modifiers[mod]['func']({'name': 'quit', 'reason': reason})
				reason = res['reason']
				if res.get('block') != None: return

		self.active = False
		self.sockSend('QUIT :' + reason)
		self.sock.close()

		pushEvent(self.modules, {'name': 'quit', 'reason': reason})
	def chnick(newnick):
		for mod in self.modifiers:
			if self.modifiers[mod]['module']['enabled']:
				res = self.modifiers[mod]['func']({'name': 'nick', 'newnick': newnick})
				newnick = res['newnick']
				if res.get('block') != None: return

		self.sockSend('NICK ' + newnick)
		oldnick = self.nick
		self.nick = newnick

		pushEvent(self.modules, {'name': 'selfnick', 'old': oldnick, 'new': newnick})
	def irc_onMsg(self, nickFrom, host, to, msg):
		if nickFrom in self.ignores:
			if self.ignores[nickFrom] == '*': return
			if self.ignores[nickFrom] == to: return

		#Dummy user object
		usr = user()
		usr.nick = nickFrom
		usr.host = host
		usr.bot = self

		#Dummy receiver object
		rcv = receiver()
		rcv.name = to
		rcv.ischannel = True if to[0] == '#' or to[2:] in ['+#', '%#', '@#', '&#', '~#', '#'] else False
		rcv.bot = self

		#Dispatch
		pushEvent(self.modules, {'name': 'msg', 'from': usr, 'admin': self.admin, 'to': rcv, 'msg': msg})

		split = msg.split(' ')
		args = ''
		for word in split[1:]:
			args += word + ' '
		args = args[:-1]

		
		for cmd in self.commands:
			try:
				try:
					doc = self.commands[cmd]['func'].__doc__.split('|')
					assert(isinstance(eval(doc[1]), dict))
				except:
					doc = ['', "{'public': True, 'admin_only': False}", '']

				if eval(doc[1])['admin_only'] and usr.host != self.admin.host:
					continue

				if self.commands[cmd]['module']['enabled']:
					if self.cmd_type == 0:
						if split[0].lower() == self.cmd_char + cmd.lower():							self.commands[cmd]['func'](args, rcv, usr)
					elif self.cmd_type == 1:
						if split[0].lower() == cmd.lower() + self.cmd_char:
							self.commands[cmd]['func'](args, rcv, usr)
			except KeyError: #necessary because when we unload modules it may bitch about not finding them
				break


		
		for alias in self.aliases:
			try:
				if self.aliases[alias]['module']['enabled']:
					if self.commands.get(self.aliases[alias]['target']) != None:
						if self.cmd_type == 0:
							if split[0].lower() == self.cmd_char + alias.lower():									self.commands[self.aliases[alias]['target']]['func'](args, rcv, usr)
						elif self.cmd_type == 1:
							if split[0].lower() == alias.lower() + self.cmd_char:
								self.commands[self.aliases[alias]['target']]['func'](args, rcv, usr)
			except KeyError: 
					break

	def irc_onInvite(self, nick, host, channel):
		if nick in self.ignores:
			if self.ignores[nickFrom] == '*': return
			if self.ignores[nickFrom] == channel: return
		usr = user()
		usr.nick = nick
		usr.host = host
		pushEvent(self.modules, {'name': 'invite', 'from': usr, 'channel': channel})

def handlingThread(sock, bot):
	while bot.active:
		rcvd = sock.recv(4096)
		try:
			rcvd = rcvd.decode('utf-8')
		except UnicodeDecodeError:
			pass
		rcvd = rcvd.split('\n')
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
					elif csplit[1].lower() == 'invite':
						bot.irc_onInvite(lsplit[1].split('!')[0].strip('\r').strip('\n'), lsplit[1].split('!')[1].strip('\r').strip('\n'), lsplit[2])
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
