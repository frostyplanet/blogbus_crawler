#!/usr/bin/env python
# coding:utf-8

import os
from spider.spider import route, Handler, spider
from spider.extract import extract
from os.path import abspath, dirname, join
from operator import itemgetter
from bs4 import BeautifulSoup
import datetime

PREFIX = join(dirname(abspath(__file__))) 

site = 'frostyplanet.blogbus.com'

@route('/logs/(.+)')
class blog_post (Handler):

    posts = []

    def get (self, _id):
        soup = BeautifulSoup (self.html)
        header = soup.find ('div', {'class': 'postHeader'})

        title = header.find ('h2').string
        date = header.find ('span', {'class': 'date'}).string
        date = date.encode ('utf-8').strip ().strip ('日期：')
        dt = datetime.datetime.strptime (date, '%Y-%m-%d')
        times = dt.strftime ('%Y/%m/%d 00:00:00')
        category = header.find ('span', {'class': 'category'})

        body = soup.find ('div', {'class': 'postBody'})
        if body:
            if category:
                category = category.find ('a')
                if category:
                    category = category.string
            body = str(body)
            if body.find ('html</a><br/><br/>\n</p>') != -1 and body.find ('div class="relpost"') != -1:
                body = extract ('html</a><br/><br/>\n</p>', '<div class="relpost"', body)
            elif body.find ('html</a><br/><br/>\n</p>') != -1 and body.find ('div class="addfav"') != -1:
                body = extract ('html</a><br/><br/>\n</p>', '<div class="addfav"', body)
            self.posts.append ((_id, title, times, category, body))
           
        
@route('/')
@route('/index_\d+.html')
@route('/(c\w+)/?(.+)?')
class post_list (Handler):

    indexes = dict ()

    def get (self, category=None, _x=None):
        soup = BeautifulSoup (self.html)
        links = soup.find_all ('a', {'class':'readmore'})
        for link_e in links:
            link = link_e.get ('href')
            print 'link', link
            spider.put (link)
        page_index = soup.find ('div', {'class': 'pageNavi'})
        if page_index:
            for link_e in page_index.find_all ('a'):
                link = link_e.get ('href')
                if link:
                    if link.find (site) == -1:
                        link = "http://%s%s" % (site, link)
                    if not self.indexes.has_key (link):
                        print 'link_index', link
                        self.indexes[link] = None
                        spider.put (link)

template = unicode("""---
title: %s
date: %s
categories: %s
---
""", 'utf-8')

if __name__ == '__main__':
    spider.put ("http://%s/index_1.html" % (site))
#    spider.put ("http://frostyplanet.blogbus.com/c1566502/")
    spider.run (5, 5)
        
    if not os.path.exists (os.path.join (PREFIX, "output")):
        os.mkdir ("output")
    for _id, title, times, category, html in blog_post.posts:
        file_path = os.path.join (os.path.join (PREFIX, "output", str(category) + "_" + str(_id)))
        content = template % (title, times, category) + unicode(html, 'utf-8')
        f = open (file_path, "w")
        try:
            f.write (content.encode ('utf-8'))
        finally:
            f.close ()
        print "wrote", file_path
    


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 :
