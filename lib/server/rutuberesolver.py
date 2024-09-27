# -*- coding: UTF-8 -*-
# *      Copyright (C) 2011 Libor Zoubek
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
import re
import util
import json
__name__ = 'rutube'


def supports(url):
    return not _regex(url) is None


# returns the stream url
def url(url):
    m = _regex(url)
    if m:
        data = util.request('http://rutube.ru/' + m.group(1) + '/' +
                            m.group(2))
        n = re.search('canonical" href="(?P<url>https://rutube.ru/[^"]+)"',
                      data,
                      re.IGNORECASE | re.DOTALL)
        nurl = n.group('url')
        print('url: %s' % nurl)
        n = re.search(r'/(?P<id>[\da-z]{32})/?$', nurl,
                      re.IGNORECASE | re.DOTALL)
        id = n.group('id')
        print('id: %s' % id)
        data = util.request('https://rutube.ru/api/play/options/%s/?format=json' % id)
        jsondata = json.loads(data)
        nurl = jsondata['video_balancer']['m3u8']
        data = util.request(nurl)
        result = []
        for line in data.splitlines():
            if 'http' in line:
                result.append(line.strip())

        return result


def resolve(u):
    streams = url(u)
    result = []
    if streams:
        for stream in streams:
            result.append({'name': __name__,
                           'quality': '???',
                           'url': stream, 'surl': u, 'title': 'rutube stream'})
    return result


def _regex(url):
    return re.search('rutube\.ru/(play/embed|video/embed|embed)/(?P<id>[^$]+)',
                     url,
                     re.IGNORECASE | re.DOTALL)
