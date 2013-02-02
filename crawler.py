#!/usr/bin/env python
# coding:utf-8

import os
from spider.spider import route, Handler, spider
from spider.extract import extract
from os.path import abspath, dirname, join
from operator import itemgetter
from bs4 import BeautifulSoup

PREFIX = join(dirname(abspath(__file__))) 

site = 'frostyplanet.blogbus.com'

@route('/logs/(.+)')
class blog_post (Handler):

    posts = []

    def get (self, _id):
        soup = BeautifulSoup (self.html)
        body = soup.find ('div', {'class': 'postBody'})
        if body:
            category = soup.find ('span', {'class': 'category'})
            if category:
                category = category.find ('a')
                if category:
                    category = category.string
            body = str(body)
            if body.find ('html</a><br/><br/>') != -1 and body.find ('div class="relpost"') != -1:
                body = extract ('html</a><br/><br/>', '<div class="relpost"', body)
            self.posts.append ((_id, category, body))
           
        
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

if __name__ == '__main__':
    spider.put ("http://%s/index_1.html" % (site))
#    spider.put ("http://frostyplanet.blogbus.com/c1566502/")
    spider.run (3, 5)
        
    if not os.path.exists (os.path.join (PREFIX, "output")):
        os.mkdir ("output")
    for _id, category, html in blog_post.posts:
        file_path = os.path.join (os.path.join (PREFIX, "output", str(category) + "_" + str(_id)))
        f = open (file_path, "w")
        try:
            f.write (html)
        finally:
            f.close ()
        print "wrote", file_path
    


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 :
