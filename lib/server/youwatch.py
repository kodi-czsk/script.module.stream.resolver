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
__name__ = 'youwatch'


def supports(url):
    return re.search(r'youwatch\.org/embed\-[^\.]+\.html', url) is not None


def resolve(url):
    data = re.search(
        r'<script\s*type=\"text/javascript\">.+?}\(\'(.+)\',\d+,\d+,\'([\w\|]+)\'.*</script>',
        util.request(url), re.I | re.S)
    if data:
        replacements = data.group(2).split('|')
        data = data.group(1)
        for i in reversed(range(len(replacements))):
            data = re.sub(r'\b%s\b' % util.int_to_base(i, 36), replacements[i], data)
        data = re.search(r'\.setup\(([^\)]+?)\);', data)
        if data:
            data = demjson.decode(data.group(1).decode('string_escape'))
            if 'file' in data:
                return [{'url': data['file']}]
    return None
