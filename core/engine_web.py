import tornado.ioloop
import tornado.web
import threading
import os, inspect

def fuzzyTail():
	pass

class MainHandler(tornado.web.RequestHandler):
	def initialize(self, config, bot, pvar):
		self.mainPage = {'title': 'Welcome', 'content': 'This is ##BOTNAME##\'s web server, how may I serve you?'}
		self.noReturn = {'title': 'Oops', 'content': 'This module seems to exist, but did not return a (valid) HTTP response'}
		self.noExist = {'title': 'Oops', 'content': 'This module does not exists'}
		self.path = os.path.dirname(os.path.abspath(inspect.getsourcefile(fuzzyTail)))

		self.bot = bot
		self.config = config
		self.pvar = pvar
	def get(self, path):
		if path == '/Saber':
			self.write(open(os.path.join(self.path, 'web/Saber.jpg'), 'r').read())
			return
		else:
			#Render
			template = open(os.path.join(self.path, 'web/template.html'), 'r').read()
			rendered = ''

			if path == '/':
				renderWith = self.mainPage
			else:
				if self.bot.modules.get(path[1:].split('/')[0]) != None:
					try:
						renderWith = self.bot.modules[path[1:].split('/')[0]]['instance'].http(path)
						assert(renderWith.get('title') != None)
						assert(renderWith.get('content') != None)
					except Exception, e:
						renderWith = self.noReturn
				else:
					renderWith = self.noExist

			rendered = unicode(template).replace('##TITLE##', renderWith['title']).replace('##CONTENT##', renderWith['content']).replace('##BOTNAME##', self.bot.nick)
			self.write(rendered)


def start(port, config, botInstance, pvar):
	print '[\033[94minfo\033[0m] Listening on '+ str(port) +' for HTTP requests'	
	application = tornado.web.Application([
		(r"(.*)", MainHandler, dict(config=config, bot=botInstance, pvar=pvar)),
	])	
	application.listen(port)
	tornado.ioloop.IOLoop.instance().start()
