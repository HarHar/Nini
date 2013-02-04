#!/usr/bin/env python
"""
  This is where we listen for connections and pass the welcome message for new clients
"""
import SocketServer
import socket
import sys
import os
import threading

class SEngine(SocketServer.BaseRequestHandler):
	clients = {}
	version = 'HarBot, version 3'
	initmessages = [':HarBot.harh.net 001 %nick% :Welcome to HarBot interface',
		':HarBot.harh.net 002 %nick% :Your host is HarBot, version 3',
		':HarBot.harh.net 003 %nick% :This server was created sometime',
		':HarBot.harh.net 375 %nick% :Message of the day',
		':HarBot.harh.net 372 %nick% :I wub u',
		':HarBot.harh.net 376 %nick% :so buch']
	def setup(self):
		self.clients[self.request] = {'authenticated': False}
		done = False
		self.clients[self.request]['nick'] = ''
		self.clients[self.request]['user'] = ''
		while done == False:
			try:
				data = self.request.recv(1024)
			except:
				return
			if data.split(' ')[0].lower() == 'nick':
				self.clients[self.request]['nick'] = data.split(' ')[1].replace('\r', '').replace('\n', '')
			if data.split(' ')[0].lower() == 'user':
				self.clients[self.request]['user'] = data.strip('USER ')
			if self.clients[self.request]['nick'] != '' and self.clients[self.request]['user'] != '':
				done = True
		for msg in self.initmessages:
			self.request.send(msg.replace('%nick%', self.clients[self.request]['nick']) + '\r\n')
		self.clients[self.request]['authenticated'] = True
	def handle(self):
		data = 'LOL FGT UMAD XD XD'
		while data:
			try:
				data = self.request.recv(4096).replace('\r', '').replace('\n', '')
			except:
				continue
			if data.split(' ')[0] == 'PING':
				if len(data.split(' ')) > 1:
					self.request.send(':HarBot.harh.net PONG ' + data.split(' ')[1] + '\r\n')
					continue
			if self.clients[self.request]['authenticated']:
				s = data.split(' ')
				if s[0] == 'PRIVMSG':
					if data.split(':') > 1:
						#self.request.send(':HarBot!~HarBot@services PRIVMSG admin :' + data.split(':')[1] * 10 + '\r\n')		if self.request in self.clients:
						if s[1].lower() == '$admin':
							self.handleMsg(data.split(':')[1], self.clients[self.request]['nick'], self.request)
	def handleMsg(self, msg, selfnick, req):
		s = msg.split(' ')
		if s[0].lower() == 'help':
			req.send(':$admin!~HarBot@offline PRIVMSG '+ selfnick + ' :Sending help \^ ^\r\n')
		else:
			req.send(':$admin!~HarBot@offline PRIVMSG '+ selfnick + ' :Unknown command\r\n')
	def finish(self):
		self.clients.pop(self.request)