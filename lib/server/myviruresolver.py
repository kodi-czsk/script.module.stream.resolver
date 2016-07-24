#!/usr/bin/python
# -*- coding: utf-8 -*-

# /*
# *      Copyright (C) 2015 Lubomir Kucera
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

import re
import util
import urllib
import pickle
from demjson import demjson

__author__ = 'Jose Riha'
__name__ = 'myviru'

UA = urllib.quote(util.UA)


def supports(url):
    return re.search(r'http://myvi.ru/player/flash', url) is not None


def resolve(url):
    cookies = {}
    result = []
    util.init_urllib(cookies)
    id = re.search(r'.*player/flash/(?P<url>.+)', url).group('url')
    r = util.request('http://myvi.ru/player/api/Video/Get/%s?sig' % id)
    jsondata = demjson.decode(r)
    playlist = jsondata['sprutoData']['playlist'][0]
    uuid = pickle.loads(util._cookie_jar.dump())[
        '.myvi.ru']['/']['UniversalUserID']
    for f in playlist['video']:
        streamurl = f['url']
        streamurl += '|Cookie=UniversalUserID%3D' + urllib.quote(uuid.value)
        streamurl += '&User-Agent=' + UA
        result.append({'url': streamurl})
    if result:
        return result
    else:
        return None
