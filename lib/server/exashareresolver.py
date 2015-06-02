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
from demjson import demjson

__author__ = 'Lubomir Kucera'
__name__ = 'exashare'


def supports(url):
    return re.search(r'exashare\.com/embed\-[^\.]+\.html', url) is not None


def resolve(url):
    data = re.search(r'<script[^\.]+?\.setup\((.+?)\);', util.request(url), re.I | re.S)
    if data:
        data = data.group(1).decode('string_escape')
        data = re.sub(r'\w+\(([^\)]+?)\)', r'\1', data)  # Strip JS functions
        data = demjson.decode(data)
        if 'playlist' in data:
            result = []
            for stream in data['playlist']:
                if 'tracks' in stream:
                    for track in stream['tracks']:
                        result.append({'url': stream['file'], 'subs': track['file'],
                                       'lang': ' %s subtitles' % track['label']})
                else:
                    result.append({'url': stream['file']})
            return result
    return None
