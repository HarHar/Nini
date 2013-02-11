#!/usr/bin/env python
"""
  This is where we listen for connections and pass the welcome message for new clients
"""
import SocketServer
import threading
admin_clients = {}

def setVar(var, value):
	var = value

class SEngine(SocketServer.BaseRequestHandler):
	version = 'HarBot, version 3'
	initmessages = [':HarBot.harh.net 001 %nick% :Welcome to HarBot interface',
		':HarBot.harh.net 002 %nick% :Your host is HarBot, version 3',
		':HarBot.harh.net 003 %nick% :This server was created sometime',
		':HarBot.harh.net 375 %nick% :Welcome to HarBot\'s administration interface',
		':HarBot.harh.net 372 %nick% :You are not authenticated',
		':HarBot.harh.net 376 %nick% :Please type "/msg $admin auth password" to continue']
	def setup(self):
		global admin_clients
		admin_clients[self.request] = {'authenticated': False}
		done = False
		admin_clients[self.request]['nick'] = ''
		admin_clients[self.request]['user'] = ''
		while done == False:
			try:
				data = self.request.recv(1024)
			except:
				return
			for line in data.split('\n'):
				if line.split(' ')[0].lower() == 'nick':
					admin_clients[self.request]['nick'] = line.split(' ')[1].replace('\r', '')
				if line.split(' ')[0].lower() == 'user':
					admin_clients[self.request]['user'] = line.strip('USER ')
				if admin_clients[self.request]['nick'] != '' and admin_clients[self.request]['user'] != '':
					done = True
		for msg in self.initmessages:
			self.request.send(msg.replace('%nick%', admin_clients[self.request]['nick']) + '\r\n')

		#self.clients[self.request]['authenticated'] = True
	def handle(self):
		global admin_clients
		global bot
		data = 'LOL FGT UMAD XD XD'
		while data:
			try:
				data = self.request.recv(4096).replace('\r', '')
			except:
				break
			for line in data.split('\n'):
				if line.split(' ')[0] == 'PING':
					if len(line.split(' ')) > 1:
						self.request.send(':HarBot.harh.net PONG ' + line.split(' ')[1] + '\r\n')
						continue
				#if self.clients[self.request]['authenticated']:
				s = line.split(' ')
				if s[0] == 'PRIVMSG':
					if line.split(':') > 1:
						#self.request.send(':HarBot!~HarBot@services PRIVMSG admin :' + data.split(':')[1] * 10 + '\r\n')		if self.request in self.clients:
						if s[1].startswith('$'):
							msg = ''
							for x in line.split(':')[1:]:
								msg += x + ':'
							msg = msg[:-1]
							try:
								self.handleMsg(msg, admin_clients[self.request]['nick'], self.request, s[1])
							except Exception, e:
								self.request.send(':'+ s[1] + '!~HarBot@harh.net PRIVMSG ' + admin_clients[self.request]['nick'] + ' :Exception! ' + repr(str(e)) + '\r\n')
	def handleMsg(self, msg, selfnick, req, module):
		global admin_clients
		global bot
		s = msg.split(' ')
		parameters = ''
		for x in s[1:]:
			parameters += x + ' '
		parameters = parameters[:-1]

		if admin_clients[self.request]['authenticated'] == False:
			if module.lower() == '$admin':
				if msg == 'auth ' + bot.password:
					req.send(':$admin!~HarBot@harh.net NOTICE ' + selfnick + ' :Authenticated\r\n')
					admin_clients[self.request]['authenticated'] = True
					return
				else:
					#req.send(':$admin!~HarBot@harh.net PRIVMSG ' + selfnick + ' :Wrong password\r\n')
					req.close()
					return
			return

		if module.lower() == '$admin':
			if s[0].lower() == 'help':
				req.send(':$admin!~HarBot@harh.net PRIVMSG '+ selfnick + ' :Sending help \^ ^\r\n')
			else:
				req.send(':$admin!~HarBot@harh.net PRIVMSG '+ selfnick + ' :Unknown command\r\n')
		elif module.lower() == '$eval':
			req.send(':$eval!~HarBot@harh.net PRIVMSG ' + selfnick + ' :' + repr(eval(msg)) + '\r\n')
		elif module.lower() == '$modules':
			if s[0].lower() == 'disable':
				if len(s) > 1:
					try:
						moduleInstances[s[1]]['enabled'] = False
					except:
						req.send(':$modules!~HarBot@harh.net PRIVMSG '+ selfnick + ' :Error! Module not found\r\n')
						return
					req.send(':$modules!~HarBot@harh.net PRIVMSG '+ selfnick + ' :Module '+ s[1] + ' is now ignored\r\n')
				else:
					req.send(':$modules!~HarBot@harh.net PRIVMSG '+ selfnick + ' :Usage: disable [module]\r\n')
			elif s[0].lower() == 'enable':
				if len(s) > 1:
					try:
						moduleInstances[s[1]]['enabled'] = True
					except:
						req.send(':$modules!~HarBot@harh.net PRIVMSG '+ selfnick + ' :Error! Module not found\r\n')
						return
					req.send(':$modules!~HarBot@harh.net PRIVMSG '+ selfnick + ' :Module '+ s[1] + ' is not ignored anymore\r\n')
				else:
					req.send(':$modules!~HarBot@harh.net PRIVMSG '+ selfnick + ' :Usage: enable [module]\r\n')
			else:
				req.send(':$modules!~HarBot@harh.net NOTICE '+ selfnick + ' :Commands: disable / enable\r\n')

		else:
			req.send(':$harbot!~HarBot@harh.net NOTICE '+ selfnick + ' :Unknown module\r\n')
	def finish(self):
		admin_clients.pop(self.request)


def start(botInstance, modules):
	global bot
	global moduleInstances
	moduleInstances = modules
	bot = botInstance

	for module in moduleInstances:
		moduleInstances[module]['instance'].setAdmins(admin_clients)

	print '[\033[94minfo\033[0m] Listening on 6667 for administrators'
	server = SocketServer.ThreadingTCPServer(('', 6667), SEngine)
	server.serve_forever()