#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib2 import urlopen
from urllib import quote
from xml.dom import minidom
import libtorrent as lt
from byteformat import format as fmt
from time import sleep
import os, inspect

def fuzzyTail():
    pass

class BotModule(object):
    """ Searches torrents on nyaa.eu """
    def __init__(self, storage):
        self.storage = storage
        self.admins = {}
        self.bot = None
        self.resultNum = 'apparently zero is false too so I gotta fill this up with something else, such is life'
        self.results = []
        self.torrentInfo = None

    def register(self):
        return {'functions': [{'nyaa' : self.nyaaSearch}]}

    def nyaaSearch(self, args, receiver, sender):
        """ nyaa [search term] | True | Searches nyaa.eu torrents """
        if args == self.bot.cmd_char + "next":
            self.resultNum = self.resultNum + 1
            result = self.results[self.resultNum]
        elif args in [self.bot.cmd_char + "details", self.bot.cmd_char + "detail"]:
            if isinstance(self.resultNum, str) == False and self.results != []:
                entry = self.results[self.resultNum]
                e = lt.bdecode(urlopen(entry['url']).read())
                info = lt.torrent_info(e)

                self.torrentInfo = info
                #maxfiles = 3

                baseURL = ''
                if (self.storage['config'].get('customURL') in [None, '']) == False:
                    baseURL = self.storage['config']['customURL']
                else:
                    baseURL = 'http://' + self.storage['config']['domain'] + ':' + str(self.storage['config']['webport']) + '/'
                URL = baseURL + os.path.basename(inspect.getsourcefile(fuzzyTail)).split('.')[0] + '/torrentInfo'

                trackers = []
                for x in info.trackers():
                    trackers.append(x)
                comment = ' | ' + chr(3) + '14Comment "' + info.comment() + '" ' + chr(15) if info.comment() != '' else ' '

                msg = []
                msg.append((chr(3) + '14{5} files, {1} in total' + chr(15) + ' | ' + chr(3) + '14Created on {2}' + chr(15) +' | ' + chr(3) + '14Announce on {3}' + chr(15) +' | ' + chr(3) + '14{6} pieces ({7} per piece)' + chr(15) +'{4}' + '| More information (such as file list) on ' + chr(3) + '2' + URL).format(info.name(), fmt(info.total_size()), str(info.creation_date()), trackers[0].url.replace('udp://', '').replace('http://', '').split('/')[0], comment, str(info.num_files()), str(info.num_pieces()), fmt(info.piece_length())))
                #if info.num_files() != 0:
                #    if info.files()[0].path != info.name():
                #        for f in info.files()[:maxfiles]:
                #            msg.append(('{0}' + chr(15) + ' [' + chr(3) + '14{1}' + chr(15) + ']').format(os.path.basename(f.path), fmt(f.size)))
                #
                #if info.num_files() > maxfiles:
                #    msg.append('Omitted {0} files'.format(str(info.num_files()-maxfiles)))
                for message in msg:
                    receiver.msg(message)
                    sleep(1)

                return
            else:
                receiver.msg('You need to search for something first')
                return
        else:
            self.resultNum = 0
            args = quote(args)
            self.results = self.search(args)
            if len(self.results) == 0:
                receiver.msg(chr(3) + '04Error' + chr(15) + ' no results found')
                return
            result = self.results[0]
        title = result['title']
        category = result['category']
        try:
            url = self.bot.modules['google']['instance'].shortenUrl(result['url'])
        except:
            url = result['url']
        details = result['description'].replace('Remake', chr(15) + chr(3) + '04Remake' + chr(15))
        details = details.replace('Trusted', chr(15) + chr(3) + '03Trusted' + chr(15))
        self.bot.msg(receiver.name, chr(3) + '13[' + category + '] ' + chr(15) + title + ' [' + chr(3) + '14' + details + ']' + chr(15) + ' - ' + chr(2) +  url)
        if self.resultNum == 0:
            self.bot.msg(receiver.name, "For details use '" + chr(3) + '03' + self.bot.cmd_char + "nyaa " + self.bot.cmd_char + "details" + chr(15) + "', for the next result use '" + chr(3) + '03' + self.bot.cmd_char + "nyaa " + self.bot.cmd_char + "next" + chr(15) + "'")
	
    def search(self, term):
        results = []

        rss = minidom.parse(urlopen("http://www.nyaa.eu/?page=rss&term="+term))
        items = rss.getElementsByTagName('item')

        for item in items:
            title = self.get_tag_value(item.getElementsByTagName('title')[0])
            url = self.get_tag_value(item.getElementsByTagName('link')[0])
            url = url.replace("&amp;", "&")
            description = self.get_tag_value(item.getElementsByTagName('description')[0])
            description = description.replace('<![CDATA[', '')
            description = description.replace(']]>', '')
            category = self.get_tag_value(item.getElementsByTagName('category')[0])
            results.append({'title': title, 'url': url, 'description': description, 'category': category})
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

    def http(self, path, handler):
        p = path.split('/')
        #p[0] == '', p[1] == 'core', p[2] == 'SOMEPAGE', p[3] == '' <-- example

        if len(p) >= 2:
            if p[2].lower() == 'torrentinfo':
                if self.torrentInfo != None:
                    trackers = []
                    for x in self.torrentInfo.trackers():
                        trackers.append(x)
                    comment = '<br />' + self.torrentInfo.comment() + '' if self.torrentInfo.comment() != '' else ''

                    out = ('<h4>{5} files, {1} in total<br />{6} pieces, {7} per piece<br />Created on {2}<br />Announce on {3} {4}').format(self.torrentInfo.name(), fmt(self.torrentInfo.total_size()), str(self.torrentInfo.creation_date()), trackers[0].url.replace('udp://', '').replace('http://', '').split('/')[0], comment, str(self.torrentInfo.num_files()), self.torrentInfo.num_pieces(), fmt(self.torrentInfo.piece_length()))
                    if self.torrentInfo.creator() != '':
                        out += '<br />Created by ' + self.torrentInfo.creator()
                    out += '</h4><br />'
                    for f in self.torrentInfo.files():
                        out += ('{0} [{1}]').format(os.path.basename(f.path), fmt(f.size)) + '<br />'

                    return {'title': self.torrentInfo.name(), 'content': out, 'mascot': 'Saber'}
                else:
                    return {'title': 'No torrent selected', 'content': 'Please use the nyaa search command and refresh this page', 'mascot': 'Saber'}
            
        return {'title': 'Nyaa search and torrent parser', 'content': 'Searches on <a href="http://nyaa.eu" target="_BLANK">nyaa.eu</a> and optionally gives more information on the .torrent file', 'mascot': 'Saber'}
