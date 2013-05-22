#!/usr/bin/env python
"""
wikipedia.py - Phenny Wikipedia Module
Copyright 2008-9, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

http://inamidst.com/phenny/
"""

import re, urllib, gzip, StringIO

import httplib2
from htmlentitydefs import name2codepoint

class Grab(urllib.URLopener): 
   def __init__(self, *args): 
      self.version = 'Mozilla/5.0 (Phenny)'
      urllib.URLopener.__init__(self, *args)
   def http_error_default(self, url, fp, errcode, errmsg, headers): 
      return urllib.addinfourl(fp, [headers, errcode], "http:" + url)
urllib._urlopener = Grab()

def get(uri): 
   if not uri.startswith('http'): 
      return
   #u = urllib.urlopen(uri)
   #bytes = u.read()
   #u.close()

   conn = httplib2.Http()
   (response, bytes) = conn.request(uri)
 
   return bytes

def head(uri): 
   if not uri.startswith('http'): 
      return
   u = urllib.urlopen(uri)
   info = u.info()
   u.close()
   return info

def post(uri, query): 
   if not uri.startswith('http'): 
      return
   data = urllib.urlencode(query)
   u = urllib.urlopen(uri, data)
   bytes = u.read()
   u.close()
   return bytes

r_entity = re.compile(r'&([^;\s]+);')

def entity(match): 
   value = match.group(1).lower()
   if value.startswith('#x'): 
      return unichr(int(value[2:], 16))
   elif value.startswith('#'): 
      return unichr(int(value[1:]))
   elif name2codepoint.has_key(value): 
      return unichr(name2codepoint[value])
   return '[' + value + ']'

def decode(html): 
   return r_entity.sub(entity, html)

r_string = re.compile(r'("(\\.|[^"\\])*")')
r_json = re.compile(r'^[,:{}\[\]0-9.\-+Eaeflnr-u \n\r\t]+$')
env = {'__builtins__': None, 'null': None, 'true': True, 'false': False}

def json(text): 
   """Evaluate JSON text safely (we hope)."""
   if r_json.match(r_string.sub('', text)): 
      text = r_string.sub(lambda m: 'u' + m.group(1), text)
      return eval(text.strip(' \t\r\n'), env, {})
   raise ValueError('Input must be serialised JSON.')



class dummy():
	def __init__(self):
		self.res = ''
	def say(self, res):
		self.res = res

class BotModule(object):
    def __init__(self, storage):
        self.storage = storage
        self.admins = {}
        self.bot = None
        self.ph = dummy()
    def register(self):
        return {'functions': [{'wiki': self.cmd_wiki}], 'aliases': {}}

    def cmd_wiki(self, args, receiver, sender):
        """wiki [entry] | {'public': True, 'admin_only': False} | Fetches an entry from Wikipedia"""
        if args.replace(' ', '') == '': return receiver.msg('Arguments: [text] ')

        wik(self.ph, args)
        if self.ph.res != '':
          receiver.msg('{0}~ {1}'.format(sender.nick, self.ph.res))
          self.ph.res = ''
        else:
          receiver.msg(chr(3) + '5Error!' + chr(15) + ' Something wrong happened :<')

wikiuri = 'http://%s.wikipedia.org/wiki/%s'
# wikisearch = 'http://%s.wikipedia.org/wiki/Special:Search?' \
#                     + 'search=%s&fulltext=Search'

r_tr = re.compile(r'(?ims)<tr[^>]*>.*?</tr>')
r_paragraph = re.compile(r'(?ims)<p[^>]*>.*?</p>|<li(?!n)[^>]*>.*?</li>')
r_tag = re.compile(r'<(?!!)[^>]+>')
r_whitespace = re.compile(r'[\r\n ]+')
r_redirect = re.compile(
   r'(?ims)class=.redirectText.>\s*<a\s*href=./wiki/([^"/]+)'
)

abbrs = ['etc', 'ca', 'cf', 'Co', 'Ltd', 'Inc', 'Mt', 'Mr', 'Mrs', 
         'Dr', 'Ms', 'Rev', 'Fr', 'St', 'Sgt', 'pron', 'approx', 'lit', 
         'syn', 'transl', 'sess', 'fl', 'Op', 'Dec', 'Brig', 'Gen'] \
   + list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') \
   + list('abcdefghijklmnopqrstuvwxyz')
t_sentence = r'^.{5,}?(?<!\b%s)(?:\.(?=[\[ ][A-Z0-9]|\Z)|\Z)'
r_sentence = re.compile(t_sentence % r')(?<!\b'.join(abbrs))

def unescape(s): 
   s = s.replace('&gt;', '>')
   s = s.replace('&lt;', '<')
   s = s.replace('&amp;', '&')
   s = s.replace('&#160;', ' ')
   return s

def text(html): 
   html = r_tag.sub('', html)
   html = r_whitespace.sub(' ', html)
   return unescape(html).strip()

def search(term): 
   try: import search
   except ImportError, e: 
      print e
      return term

   if isinstance(term, unicode): 
      term = term.encode('utf-8')
   else: term = term.decode('utf-8')

   term = term.replace('_', ' ')
   try: uri = search.google_search('site:en.wikipedia.org %s' % term)
   except IndexError: return term
   if uri: 
      return uri[len('http://en.wikipedia.org/wiki/'):]
   else: return term

def wikipedia(term, language='en', last=False): 
   global wikiuri
   if not '%' in term: 
      if isinstance(term, unicode): 
         t = term.encode('utf-8')
      else: t = term
      q = urllib.quote(t)
      u = wikiuri % (language, q)
      bytes = get(u)
   else: bytes = get(wikiuri % (language, term))

   if bytes.startswith('\x1f\x8b\x08\x00\x00\x00\x00\x00'): 
      f = StringIO.StringIO(bytes)
      f.seek(0)
      gzip_file = gzip.GzipFile(fileobj=f)
      bytes = gzip_file.read()
      gzip_file.close()
      f.close()

   bytes = r_tr.sub('', bytes)

   if not last: 
      r = r_redirect.search(bytes[:4096])
      if r: 
         term = urllib.unquote(r.group(1))
         return wikipedia(term, language=language, last=True)

   paragraphs = r_paragraph.findall(bytes)

   if not paragraphs: 
      if not last: 
         term = search(term)
         return wikipedia(term, language=language, last=True)
      return None

   # Pre-process
   paragraphs = [para for para in paragraphs 
                 if (para and 'technical limitations' not in para 
                          and 'window.showTocToggle' not in para 
                          and 'Deletion_policy' not in para 
                          and 'Template:AfD_footer' not in para 
                          and not (para.startswith('<p><i>') and 
                                   para.endswith('</i></p>'))
                          and not 'disambiguation)"' in para) 
                          and not '(images and media)' in para
                          and not 'This article contains a' in para 
                          and not 'id="coordinates"' in para
                          and not 'class="thumb' in para]
                          # and not 'style="display:none"' in para]

   for i, para in enumerate(paragraphs): 
      para = para.replace('<sup>', '|')
      para = para.replace('</sup>', '|')
      paragraphs[i] = text(para).strip()

   # Post-process
   paragraphs = [para for para in paragraphs if 
                 (para and not (para.endswith(':') and len(para) < 150))]

   para = text(paragraphs[0])
   m = r_sentence.match(para)

   if not m: 
      if not last: 
         term = search(term)
         return wikipedia(term, language=language, last=True)
      return None
   sentence = m.group(0)

   maxlength = 275
   if len(sentence) > maxlength: 
      sentence = sentence[:maxlength]
      words = sentence[:-5].split(' ')
      words.pop()
      sentence = ' '.join(words) + ' [...]'

   if (('using the Article Wizard if you wish' in sentence)
    or ('or add a request for it' in sentence)
    or ('in existing articles' in sentence)): 
      if not last: 
         term = search(term)
         return wikipedia(term, language=language, last=True)
      return None

   sentence = sentence.replace('"', "'")
   sentence = sentence.decode('utf-8').encode('utf-8')
   wikiuri = wikiuri.decode('utf-8').encode('utf-8')
   term = term.decode('utf-8').encode('utf-8')
   #return sentence + ' - ' + (wikiuri % (language, term))
   return sentence

def wik(phenny, input): 
   #origterm = input.groups()[1]
   origterm = input
   if not origterm: 
      return phenny.say('Perhaps you meant ".wik Zen"?')
   origterm = origterm.encode('utf-8')

   term = urllib.unquote(origterm)
   language = 'en'
   if term.startswith(':') and (' ' in term): 
      a, b = term.split(' ', 1)
      a = a.lstrip(':')
      if a.isalpha(): 
         language, term = a, b
   term = term[0].upper() + term[1:]
   term = term.replace(' ', '_')

   try: result = wikipedia(term, language)
   except IOError: 
      args = (language, wikiuri % (language, term))
      error = "Can't connect to %s.wikipedia.org (%s)" % args
      return phenny.say(error)

   if result is not None: 
      phenny.say(result)
   else: phenny.say('Can\'t find anything in Wikipedia for "%s".' % origterm)

wik.commands = ['wik']
wik.priority = 'high'
