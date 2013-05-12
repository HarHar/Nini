#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from urllib2 import urlopen
from BeautifulSoup import BeautifulStoneSoup

def HTMLEntitiesToUnicode(text):
    """Converts HTML entities to unicode.  For example '&amp;' becomes '&'."""
    text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
    return text

class BotModule(object):
	def __init__(self, storage):
		self.storage = storage
		self.admins = {}
		self.bot = None

	def register(self):
		return {'functions': [{'4chan': self.search4chan}]}

	def event(self, ev):
		if ev['name'] == 'msg':
			split = ev['msg'].split(' ')

			if split[0].lower() == '$test':
				self.bot.msg(ev['to'].name, u'It works .‿.')
				
	def search4chan(self, args, receiver, sender):
		""" 4chan | True | Searches a specified 4chan board and returns any threads that match."""
		if args == "$next":
			self.printThread(self.results[self.resultNum], receiver.name)
			self.resultNum += 1
			return
		board = args.rsplit(" ")[0]
		self.currentBoard = board
		query = args.rsplit(" ")[1].lower()
		try:
			req = urlopen("https://api.4chan.org/" + board + "/catalog.json")
		except:
			self.bot.msg(receiver.name, "It seems you didn't specify a real board")
			return
		catalog = json.load(req)
		self.results = []
		x = 0
		while x < 10:
			for thread in catalog[x]['threads']:
				try:
					if query in thread['sub'].lower():
						self.results.append(thread)
				except:
					pass
				try:
					if query in thread['com'].lower():
						self.results.append(thread)
				except:
					pass
			x += 1
		self.resultNum = 1
		self.printThread(self.results[0], receiver.name)

	def printThread(self, thread, receiver):
		""" Pretty prints a thread"""
		try:
			subject = thread['sub']
		except:
			subject = "No Subject"
		try:
			comment = thread['com']
			comment = comment.replace('<br><br><br><br>', '<br>').replace('<br><br><br>', '<br>').replace('<br><br>', '<br>') #in case someone uses 4 consecutive newlines or something
			comment = comment.replace('<br>', ' | ')
			comment = comment.replace('</wbr>', '')
			comment = comment.replace('<wbr>', '')
			comment = HTMLEntitiesToUnicode(comment)
		except:
			comment = "No Comment"
		name = thread['name']
		# these guys count from zero so we gotta increment them
		replyNum = str(thread['replies']+1)
		imageNum = str(thread['images']+1)
		link = "https://boards.4chan.org/" + self.currentBoard + "/res/" + str(thread['no'])
		try:
			link = self.bot.modules['google']['instance'].shortenUrl(link)
		except:
			pass
			
		self.bot.msg(receiver, chr(3) + '12' + name + chr(15) + " >>> " + chr(3) + '13' + subject + chr(15) + " >>> " + chr(3) + '12' + comment + chr(15) + " >>> " + chr(3) + '13' + replyNum + "/" + imageNum + chr(15) + " >>> " + chr(3) + '2' + link)
