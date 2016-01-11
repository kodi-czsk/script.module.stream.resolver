# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2016 mx3L & lzoubek
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */
import re, util,urllib2
__name__ = 'videomail'
def supports(url):
    return not _regex(url) == None

# returns the steam url
def resolve(url):
    m = _regex(url)
    if m:
        items = []
        vurl = m.group('url')
        vurl = re.sub('\&[^$]*','',vurl)
        vurl = re.sub('/embed','',vurl)
        vurl = 'http://videoapi.my.mail.ru/' + vurl + '.json'

        util.init_urllib()
        req = urllib2.Request(vurl)
        req.add_header('User-Agent', util.UA)
        resp = urllib2.urlopen(req)
        data = resp.read()
        vkey = []
        for cookie in re.finditer('(video_key=[^\;]+)',resp.headers.get('Set-Cookie'),re.IGNORECASE | re.DOTALL):
            vkey.append(cookie.group(1))
        headers = {'Cookie':vkey[-1]}
        item = util.json.loads(data)
        for v in item[u'videos']:
            quality = v['key']
            link = v['url']
            items.append({'quality':quality, 'url':link, 'headers':headers})
        return items

def _regex(url):
    m1 = re.search('http://.+?mail\.ru.+?<param.+?value=\"movieSrc=(?P<url>[^\"]+)', url, re.IGNORECASE | re.DOTALL)
    m2 = re.search('://video.+?\.mail\.ru\/(?P<url>.+?)\.html', url, re.IGNORECASE | re.DOTALL)
    return m1 or m2
