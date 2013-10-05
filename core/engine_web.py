import tornado.ioloop
import tornado.web
import threading
import os, inspect
import traceback

def fuzzyTail():
	pass

class MainHandler(tornado.web.RequestHandler):
	def initialize(self, config, bot, pvar):
		if 'mascot' in pvar['config']:
			mascot = pvar['config']['mascot']
		else:
			mascot = 'Saber'
		self.mainPage = {'title': 'Welcome', 'content': 'This is ##BOTNAME##\'s web server, how may I serve you?', 'mascot': mascot}
		self.noReturn = {'title': 'Oops', 'content': 'This module seems to exist, but did not return a (valid) HTTP response', 'mascot': mascot}
		self.noExist = {'title': 'Oops', 'content': 'This module does not exists', 'mascot': mascot}
		self.path = os.path.dirname(os.path.abspath(inspect.getsourcefile(fuzzyTail)))

		self.bot = bot
		self.config = config
		self.pvar = pvar
		self.mascot = mascot
	def get(self, path):
		if path == '/bootstrap.css':
			self.set_header('Content-Type', 'text/css')
			self.write(open(os.path.join(self.path, 'web/bootstrap.css'), 'r').read())
			return
		if path.endswith('.msct'):
			p = path[:-5]
			if os.path.exists(os.path.join(self.path, 'web/'+ p +'.jpg')):
				self.write(open(os.path.join(self.path, 'web/'+ p +'.jpg'), 'r').read())
				return
			elif os.path.exists(os.path.join(self.path, 'web/'+ p +'.png')):
				self.write(open(os.path.join(self.path, 'web/'+ p +'.png'), 'r').read())
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
						renderWith = self.bot.modules[path[1:].split('/')[0]]['instance'].http(path, self)
						if renderWith.get('mascot') in ['', None]:
							renderWith['mascot'] = self.mascot
						assert(renderWith.get('content') != None)
					except Exception, e:
						renderWith = self.noReturn
						renderWith['content'] += '<br /><pre>' + traceback.format_exc() + '</pre>'
				else:
					renderWith = self.noExist

			if renderWith.get('max-width') == None: renderWith['max-width'] = '680px'

			if renderWith.get('type') != None: self.content_type = renderWith['type']

			if renderWith.get('raw') is None:
				rendered = unicode(template).replace('##TITLE##', renderWith['title']).replace('##CONTENT##', renderWith['content']).replace('##BOTNAME##', self.bot.nick).replace('##MAX-WIDTH##', renderWith['max-width'])
				for key in renderWith:
					rendered = rendered.replace('##' + key.upper() + '##', renderWith[key])
			else:
				rendered = renderWith['content']
			self.write(rendered)

def start(port, config, botInstance, pvar):
	print '[\033[94minfo\033[0m] Listening on '+ str(port) +' for HTTP requests'	
	application = tornado.web.Application([
		(r"(.*)", MainHandler, dict(config=config, bot=botInstance, pvar=pvar)),
	])	
	application.listen(port)
	tornado.ioloop.IOLoop.instance().start()
