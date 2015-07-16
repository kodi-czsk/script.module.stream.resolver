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
from copy import deepcopy

__name__ = 'flashx'


def supports(url):
    return re.search(r'flashx\.tv/embed\-[^\.]+\.html', url) is not None


def resolve(url):
    data = util.extract_jwplayer_setup(util.request(url))
    if data and 'sources' in data:
        result = []
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
