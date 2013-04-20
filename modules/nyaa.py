#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib2 import urlopen
from urllib import quote
from xml.dom import minidom

class BotModule(object):
    """ Searches torrents on nyaa.eu """
    def __init__(self, storage):
        self.storage = storage
        self.admins = {}
        self.bot = None

    def register(self):
        return {'functions': [{'nyaa' : self.nyaaSearch}]}

    def nyaaSearch(self, args, receiver, sender):
        """ nyaa [search term] | True | Searches nyaa.eu torrents """
        if args == self.bot.cmd_char + "next":
            self.resultNum = self.resultNum + 1
            result = self.results[self.resultNum]
        else:
            self.resultNum = 0
            args = args.replace(' ', '+')
            args = quote(args)
            self.results = self.search(args)
            if len(self.results) == 0:
                receiver.msg(chr(3) + '04Error' + chr(15) + ' no results found')
                return
            result = self.results[0]
        title = result['title']
        url = result['url']
        details = result['description'].replace('Remake', chr(3) + '04Remake' + chr(15))
        details = details.replace('Trusted', chr(3) + '03Trusted' + chr(15))
        self.bot.msg(receiver.name, chr(2) + 'Title: ' + chr(15) + title + chr(2) + ' Link: ' + chr(15) + url + ' ' + chr(2) + 'Details: ' + chr(15) + details)
        if self.resultNum == 0:
            self.bot.msg(receiver.name, "For the next result use '" + self.bot.cmd_char + "nyaa " + self.bot.cmd_char + "next'")
	
    def search(self, term):
        results = []

        rss = minidom.parse(urlopen("http://www.nyaa.eu/?page=rss&term="+quote(term)))
        items = rss.getElementsByTagName('item')

        for item in items:
            title = self.get_tag_value(item.getElementsByTagName('title')[0])
            url = self.get_tag_value(item.getElementsByTagName('link')[0])
            url = url.replace("&amp;", "&")
            description = self.get_tag_value(item.getElementsByTagName('description')[0])
            description = description.replace('<![CDATA[', '')
            description = description.replace(']]>', '')
            results.append({'title': title, 'url': url, 'description': description})
        return results

    def get_tag_value(self, node):
        xml_str = node.toxml()
        start = xml_str.find('>')
        if start == -1:
            return ''
        end = xml_str.rfind('<')
        if end < start:
            return ''
        return xml_str[start + 1:end]	
