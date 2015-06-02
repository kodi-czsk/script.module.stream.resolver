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

__author__ = 'Lubomir Kucera'
__name__ = 'youwatch'


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
    return re.search(r'youwatch\.org/embed\-[^\.]+\.html', url) is not None


def resolve(url):
    data = re.search(
        r'<script\s*type=\"text/javascript\">.+?}\(\'(.+)\',\d+,\d+,\'([\w\|]+)\'.*</script>',
        util.request(url), re.I | re.S)
    if data:
        replacements = data.group(2).split('|')
        data = data.group(1)
        for i in reversed(range(len(replacements))):
            data = re.sub(r'\b' + base36encode(i) + r'\b', replacements[i], data)
        data = re.search(r'file:\s*\"([^\"]+)\"', data)
        if data:
            return [{'url': data.group(1)}]
    return None
