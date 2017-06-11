#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import Queue
import base64
import cookielib
import getpass
import os
import os.path
import pixiv
import re
import sys
import time
import traceback
import urllib
import urllib2

def login(username = None, password = None):
    if username is None:
        username = raw_input('pixiv id: ')

    if password is None:
        password = getpass.getpass('password: ')
    
    cj = cookielib.LWPCookieJar()
    pixiv.login(cj, username, password)

    return cj

def loadThumbs(Q, cj, page):
    print "loading bookmark page: " + str(page)
    
    thumbs = pixiv.bookmark(cj, 1)

    for t in thumbs:
        Q.put(('t', t))

    if len(thumbs) != 0:
        Q.put(('p', page + 1))

def makeOutput(dirname):
    suffix = 1
    path = dirname

    while os.path.exists(path) and not os.path.isdir(path):
        path = dirname + '.' + str(suffix)
        suffix = suffix + 1

    if not os.path.exists(path):
        os.mkdir(path)

    return path
    
def resolveImage(Q, cj, thumb):
    print "resolving \"real\" images: " + thumb.title
    id_ = thumb.id
    
    if thumb.multiple:
        imgs = pixiv.getMangaImages(id_, cj)

        
        for img in range(len(imgs)):
            Q.put(('m', (thumb.id, img)))

    else:
        imgs = pixiv.getLargeImage(id_, cj)
        ref = "http://www.pixiv.net/member_illust.php?mode=medium&illust_id="+str(id_)
        
        for i in imgs:
            Q.put(('i', (i, ref)))

def resolveMangaImages(Q, cj, v):
    id_, page = v
    
    print "resolvig real manga page: " + str(id_) + ", page: " + str(page)
    
    img = pixiv.getLargeMangaImage(id_, page, cj)

    if img is not None:
        Q.put(('i', img))

def fetchImage(Q, cj, path, v):
    url, ref = v
    print "fetching...: " + url

    filename = url.split('/')[-1]

    path = os.path.join(path, filename)

    with open(path, 'w') as f:
        res = pixiv.openI(url, referer=ref)

        for chunk in res.iter_content(1024*1024):
            f.write(chunk)
    
def run(cj, page = 1):
    Q = Queue.Queue()

    outpath = makeOutput('out')

    Q.put(('p', page))
    
    while not Q.empty():
        k, v = Q.get()

        try:
            if k == 'p':
                loadThumbs(Q, cj, v)
            elif k == 't':
                resolveImage(Q, cj, v)
            elif k == 'm':
                resolveMangaImages(Q, cj, v)
            elif k == 'i':
                fetchImage(Q, cj, outpath, v)
            else:
                print "??"
        except KeyboardInterrupt as e:
            raise e 
        except Exception as e:
           print(str(e))
           

        time.sleep(1)
    print "aa"
    
def main():
    cj = login()

    run(cj)
    

if __name__ == '__main__':
    main()
