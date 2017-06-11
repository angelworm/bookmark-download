#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import urllib
import urlparse
import re
import lxml.html
import cookielib
import mechanize
import requests

class Illust:
    def __init__(self, id_, dom):
        
        def ectractAuthor():
            userlink = dom.xpath('//a[@calss="user-link"]')
            return {
                id:   userlink.attrib['href'],
                name: userlink.xpath(".//h1")[0].text,
                img:  userlink.xpath(".//img")[0].attrib['src']
                }

        self.id      = id_
        self.title   = title_
        self.author  = author_
        self.imgURL  = imgURL_
        self.pageURL = pageURL_
        
    def __str__(self):
        return "id: " + str(self.id) + ", img: " + self.imgURL

    def description(self):
        return "id: " + str(self.id) + ", img: " + self.imgURL + ", title: " + u"「" + self.title + u"」 / " + self.author

class Thumbnail:
    """pixiv thumbnails and some information"""
    
    def __init__(self, id_, title_, author_, pageURL_, imgURL_, multiple_ = False):
        self.id       = id_
        self.title    = title_
        self.author   = author_
        self.imgURL   = imgURL_
        self.pageURL  = pageURL_
        self.multiple = multiple_
        
    def __str__(self):
        return "id: " + str(self.id) + ", img: " + self.imgURL + ", multiple: " + str(self.multiple)

    def description(self):
        return "id: " + str(self.id) + ", img: " + self.imgURL + ", title: " + u"「" + self.title + u"」 / " + self.author

def openI(url, referer = 'https://www.pixiv.net'):

    return requests.get(url,headers= {
        'referer': referer,
        'user-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    })
    
def openP(url, cj = None, referer = 'https://www.pixiv.net'):
    if cj is not None:
        cp = urllib2.HTTPCookieProcessor(cj)
        opener = urllib2.build_opener(cp)
    else:
        opener = urllib2.build_opener()
        
    req = urllib2.Request(url)
    req.add_header('referer', referer)
    req.add_header('accept-Language', 'ja')
    req.add_header('user-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
    
    return opener.open(url)
    
def getPage(url, cj = None):
    res = openP(url, cj)
    return unicode(res.read(), "utf-8")

def getIllust(id_):
    """ this function is broken! """
    url = "http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+id_
    root = lxml.html.fromstring(getPage(url)).xpath('//div[@class="front-content"]/*')
    mainT = root[0]
    sideT = root[1]

    authorT = sideT.xpath('//h2')[0]
    title = mainT.xpath('//h1')[0].text
    author_img  = authorT.xpath('//a[1]/img[1]/@src')[0]
    author_url  = authorT.xpath('//a[1]/@href')[0]
    author_name = authorT.xpath('//a[1]/img/@title')[0]

    print author_name

    return [title, author_img, author_url, author_name]

def getLargeMangaImage(id_, page, cj = None):
    url = "http://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=" + str(id_) + "&page=" + str(page)

    path = lxml.html.fromstring(getPage(url, cj))

    cands = path.xpath('//img')

    if len(cands):
        return (cands[0].attrib['src'], url)
    else:
        return None

def getMangaImages(id_, cj = None):
    url = "http://www.pixiv.net/member_illust.php?mode=manga&illust_id="+str(id_)

    path = lxml.html.fromstring(getPage(url, cj))

    cands = path.xpath('//img[@data-index]')
    return list(c.attrib['data-src'] for c in cands)
    
def getLargeImage(id_, cj = None):
    url = "http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+str(id_)

    path = lxml.html.fromstring(getPage(url, cj))

    cands = path.xpath('//img[contains(@class, "original-image")]')
    if (len(cands) !=  0):
        return list(c.attrib['data-src'] for c in cands)
        
    cands = path.xpath('//img[@border=\"0\"]')
    if len(cands) != 0:
        return [cands[0].attrib['src']]

    return []

def makeImageData_(tags):
    a   = tags.xpath(".//a")
    h2  = tags.xpath(".//h1")[0].text
    img = tags.xpath(".//img[1]/@src")[0]
    p   = re.compile('.*/member_illust\.php\?mode=medium&illust_id=(\d+)')
    mul  = tags.xpath('.//a[contains(@class, "multiple")]')
    
    pageURL= urlparse.urljoin("http://www.pixiv.net/", a[0].attrib['href'])
    id_ = int(p.match(pageURL).group(1))
    title = h2
    author = a[2].text
    imgURL = img
    multiple = len(mul) != 0
        
    return Thumbnail(id_, title, author, pageURL, imgURL, multiple)

def searchTag(word, full=True):    
    
    #部分一致
    qword = urllib.quote_plus(word.encode('utf-8'))
    if full:
        smode = "s_tag_full"
    else:
        smode = "s_tag"
    
    url = "http://www.pixiv.net/search.php?s_mode=" + smode + "&word="+qword

    dom = lxml.html.fromstring(getPage(url))
    return map(makeImageData_, dom.xpath('//li[@class="image-item "]'))

def bookmark(cj, page=1, hidden=True):
    if hidden:
        rest = 'hide'
    else:
        rest = 'show'
    
    
    url = "https://www.pixiv.net/bookmark.php?rest=" + rest + "&p=" + str(page)

    txt = getPage(url, cj)
    
    dom = lxml.html.fromstring(txt)
    return map(makeImageData_, dom.xpath('//li[@class="image-item"]'))

def browser(cj):
    br = mechanize.Browser()

    br.set_cookiejar(cj)

    return br
    
def login(cj, username, password):
    br = browser(cj)
    br.set_handle_robots( False )

    br.open("https://accounts.pixiv.net/login")
    br.select_form(nr=0)
    br.form['pixiv_id'] = username
    br.form['password'] = password
    br.submit()

    return br
    
def test():
    return searchTag(u"雀")

def pr(img):
    print img

if __name__ == '__main__':
    print "loading"
    # print searchTag(u"10点じゃ足りない")

    # print getLargeImage("62231195")

    with open('hoge.jpg', 'w') as f:
        res = openI('https://i.pximg.net/img-original/img/2017/05/30/19/33/53/63143848_p0.png', referer='https://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=63143848&page=0')
        
        for chunk in res.iter_content(1024*1024):
            f.write(chunk)
    
    #images = getLargeImage("63143848")

    # print images
    # print len(images)

