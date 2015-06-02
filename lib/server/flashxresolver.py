# -*- coding: UTF-8 -*-
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
from xml.etree import ElementTree
import util
from demjson import demjson
from copy import deepcopy

__name__ = 'flashx'


def base36encode(number):
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    base36 = ''
    sign = ''
    if number < 0:
        sign = '-'
        number = -number
    if 0 <= number < len(alphabet):
        return sign + alphabet[number]
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
    return sign + base36


def supports(url):
    return re.search(r'flashx\.tv/embed\-[^\.]+\.html', url) is not None


def resolve(url):
    data = re.search(r'<script.+?}\(\'(.+)\',\d+,\d+,\'([\w\|]+)\'.*</script>',
                     util.request(url), re.I | re.S)
    if data:
        replacements = data.group(2).split('|')
        data = data.group(1)
        for i in reversed(range(len(replacements))):
            if len(replacements[i]) > 0:
                data = re.sub(r'\b%s\b' % base36encode(i), replacements[i], data)
        data = re.search(r'\.setup\(([^\)]+?)\);', data)
        if data:
            result = []
            data = demjson.decode(data.group(1).decode('string_escape'))
            for source in data['sources']:
                items = []
                if source['file'].endswith('.smil'):
                    tree = ElementTree.fromstring(util.request(source['file']))
                    base_path = tree.find('./head/meta').get('base')
                    for video in tree.findall('./body/switch/video'):
                        items.append({
                            'url': '%s playpath=%s pageUrl=%s swfUrl=%s swfVfy=true' %
                                   (base_path, video.get('src'), url,
                                    'http://static.flashx.tv/player6/jwplayer.flash.swf'),
                            'quality': video.get('height') + 'p'
                        })
                else:
                    items.append({'url': source['file']})
                if len(data['tracks']) > 0:
                    for item in items:
                        for track in data['tracks']:
                            new_item = deepcopy(item)
                            new_item['subs'] = track['file']
                            new_item['lang'] = ' %s subtitles' % track['label']
                            result.append(new_item)
                else:
                    result += items
            return result
    return None
