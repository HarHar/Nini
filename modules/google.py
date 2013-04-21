#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib2 import urlopen, Request
from urllib import quote
import json

class BotModule(object):
    """ Provides access to various Google services """
    def __init__(self, storage):
        self.storage = storage
        self.admins = {}
        self.bot = None
        self.apiKey = "AIzaSyBCJciReska7RcTlpOLen7rSrxXmSOVBA4"
        self.gbooksQueryUrl = "https://www.googleapis.com/books/v1/volumes?q="
        self.ytQueryUrl = "http://gdata.youtube.com/feeds/api/videos?alt=json&q="

    def register(self):
        return {'functions': [{'gbooks': self.gbooks}, {'shorten': self.shorten}, {'youtube': self.youtube}], 'aliases': {'gb': 'gbooks', 'gbook': 'gbooks', 'short': 'shorten', 'yt': 'youtube', 'y': 'youtube'}}

    def gbooks(self, args, receiver, sender):
        """ gbooks [book title or author] | True | Searchs Google Books for the arguement and displays info about the results. """
        if args == self.bot.cmd_char + "next":
            self.gbResultNum = self.gbResultNum + 1
            result = self.gbResults['items'][self.gbResultNum]
        else:
            self.gbResultNum = 0
            args = args.replace(' ', '+')
            args = quote(args)
            self.gbResults = json.load(urlopen(self.gbooksQueryUrl + args + '&key=' + self.apiKey))
            result = self.gbResults['items'][0]
        title = result['volumeInfo']['title']
        if "authors" not in result['volumeInfo']:
            author = "Unavailable"
        elif len(result['volumeInfo']['authors']) == 1:
            author = result['volumeInfo']['authors'][0]
        else:
            temp = []
            for a in result['volumeInfo']['authors']:
                if a == result['volumeInfo']['authors'][-1]:
                    temp.append(a)
                else:
                    temp.append(a + ', ')
            author = ''.join(temp)
        link = self.shortenUrl(result['volumeInfo']['infoLink'])
        self.bot.msg(receiver.name, chr(2) + 'Title: ' + chr(15) + title + 
                    chr(2) + ' Author(s): ' + chr(15) + author + chr(2) + ' Link: ' + chr(15) + link)
        if self.gbResultNum == 0:
            self.bot.msg(receiver.name, "For the next result use '" + self.bot.cmd_char + "gbooks " + self.bot.cmd_char + "next'")

    def shorten(self, args, reciever, sender):
        """ shorten [url] | True | Takes a url and provides a shortened goo.gl link. """
        link = self.shortenUrl(args)
        self.bot.msg(reciever.name, sender.nick + ': ' + link)

    def youtube(self, args, receiver, sender):
        """ youtube [query] | True | Searchs Youtube for the argument and displays info about the results. """
        if args == "$next":
            self.ytResultNum = self.ytResultNum + 1
            result = self.ytResults[self.ytResultNum]
        else:
            self.ytResultNum = 0
            args = args.replace(' ', '+')
            args = quote(args)
            try:
                self.ytResults = json.load(urlopen(self.ytQueryUrl + args + '&key=' + self.apiKey))["feed"]["entry"]
            except KeyError:
                receiver.msg(chr(3) + '04Error ' + chr(15) + ' no results found')
                return
            result = self.ytResults[0]
        title = result["title"]["$t"]
        link = self.shortenUrl(result["link"][0]["href"])
        self.bot.msg(receiver.name, chr(2) + u'Title: ' + chr(15) + title + chr(2) + ' Link: ' + chr(15) + link)
        if self.ytResultNum == 0:
            self.bot.msg(receiver.name, "For the next result use '" + self.bot.cmd_char + "youtube " + self.bot.cmd_char + "next'")

    def shortenUrl(self, url):
        data = json.dumps({'longUrl': url})
        apiUrl = 'https://www.googleapis.com/urlshortener/v1/url' + '?key=' + self.apiKey
        header = {'Content-Type': 'application/json'}
        r = Request(apiUrl, data, header)
        reponse = json.load(urlopen(r))
        return reponse['id']
