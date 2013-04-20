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
        """ nyaa [search term] | Searches nyaa.eu torrents """
        if args == self.bot.cmd_char + "next":
            self.resultNum = self.resultNum + 1
            result = self.results[self.resultNum]
        else:
            self.resultNum = 0
            args = args.replace(' ', '+')
            args = quote(args)
            self.results = self.search(args)
            result = self.results[0]
        title = result['title']
        url = result['url']
        self.bot.msg(receiver.name, chr(2) + 'Title: ' + chr(15) + title + chr(2) + ' Link: ' + chr(15) + url)
        if self.resultNum == 0:
            self.bot.msg(receiver.name, "For the next result use '" + self.bot.cmd_char + "nyaa " + self.bot.cmd_char + "next'")
	
    def search(self, term):
        results = []

        rss = minidom.parse(urlopen("http://www.nyaa.eu/?page=rss&term="+term))
        items = rss.getElementsByTagName('item')

        for item in items:
            title = self.get_tag_value(item.getElementsByTagName('title')[0])
            url = self.get_tag_value(item.getElementsByTagName('link')[0])
            results.append({'title':title,'url':url})
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
