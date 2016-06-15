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

__author__ = 'Jose Riha'
__name__ = 'videram'


def supports(url):
    return re.search(r'play\.videram\.com', url) is not None


def resolve(url):
    try:
        data=[x for x in util.request('http:'+url).splitlines() if 'file:' in x and '.mp4' in x][0]
    except:
        return None 
    streamurl = re.search(r'.*file: *"([^"]+?)".*', data).group(1)
    return [{'url': streamurl}]
