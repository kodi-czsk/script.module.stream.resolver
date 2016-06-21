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

__author__ = 'Jose Riha/Lubomir Kucera'
__name__ = 'exashare'


def supports(url):
    return re.search(r'exashare\.com/embed\-[^\.]+\.html', url) is not None


def resolve(url):
    realurl = re.search(r'<iframe src="([^"]+)".*', util.request(url), re.I | re.S).group(1)
    data = re.search(r'<script[^\.]+?\.setup\((.+?)\);', util.request(realurl), re.I | re.S)
    if data:
        data = data.group(1).decode('string_escape')
        data = re.sub(r'\w+\(([^\)]+?)\)', r'\1', data) # Strip JS functions
        data = re.sub(r': *([^"][a-zA-Z]+)',r':"\1"', data) # Fix incorrect JSON
        data = demjson.decode(data)
        if 'sources' in data:
            result = []
            for source in data['sources']:           
                if 'tracks' in data:                                                        
                    for track in data['tracks']:                                            
                        result.append({
                                       'url': source['file'],
                                      'subs': track['file'],
                                      'lang': ' %s subtitles' % track['label']
                                       })
            return result
    return None
