#!/usr/bin/env python
import urllib
import httplib2
from BeautifulSoup import BeautifulSoup

def urbandict(search, limit=5, cutafter=256):
    query = urllib.urlencode(dict(term=search))
    url = 'http://www.urbandictionary.com/define.php?' + query
    conn = httplib2.Http()
    (response, content) = conn.request(url)
 
    soup = BeautifulSoup(content)

    fix = lambda item: item.replace('\r', '').replace('\n', '')
    cut = lambda item: len(item) > cutafter and item[:cutafter] + '(...)' or item
    extract = lambda item: isinstance(item, unicode) and item or \
        (item.name == 'a' and item.contents[0] or '')

    for item, count in zip(soup.findAll('div', attrs={'class':'definition'}), range(limit)):
        yield cut(' '.join([fix(extract(k)) for k in item.contents])).encode('utf-8')

class BotModule(object):
    def __init__(self, storage):
        self.storage = storage
        self.admins = {}
        self.bot = None
    def register(self):
        return {'functions': [{'urbandictionary': self.cmd_ud}], 'aliases': {'ud': 'urbandictionary', 'urb': 'urbandictionary', 'urbandict': 'urbandictionary'}}

    def cmd_ud(self, args, receiver, sender):
        """ud [entry] | {'public': True, 'admin_only': False} | Fetches an entry on Urban Dictionary"""
        if args.replace(' ', '') == '': return receiver.msg('Arguments: [text] ')

        found = False
        for entry in urbandict(args, 1, 256):
            found = True
            receiver.msg(chr(2) + args + chr(15) + ' ' + entry)

        if not found:
            receiver.msg(chr(15) + 'Entry ' + chr (2) + args + chr(15) + ' not found')
