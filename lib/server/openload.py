# -*- coding: UTF-8 -*-
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
import xbmc
import xbmcgui
from json import loads

__author__ = 'Jose Riha/Lubomir Kucera'
__name__ = 'openload'


def supports(url):
    return re.search(r'openload\.\w+/embed/.+', url) is not None


def resolve(url):
    video_code = url.split('/')[-2]
    api_url = 'https://api.openload.co/1/streaming/get?file=%s' % video_code
    print('api_url: %s' % api_url)

    page = util.request(api_url)

    response = loads(page)
    print(response['result'])
    if response['msg'] not in 'OK':
        d = xbmcgui.Dialog()
        d.notification('OpenLoad resolver - pairing needed', 'visit openload.co/pair',
                       xbmcgui.NOTIFICATION_INFO, 7000)
        del d
    else:
        url = response['result']['url']

    return [{'url': url}]
