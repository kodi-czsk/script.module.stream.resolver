# -*- coding: UTF-8 -*-
# /*
# *      Copyright (C) 2016 Jose Riha
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
import time
import pickle

__author__ = 'Jose Riha'
__name__ = 'mojevideo.sk'


def supports(url):
    return re.search(r'mojevideo\.sk/video/\w+/.+\.html', url) is not None


def resolve(url):
    cookies = {}
    util.init_urllib(cookies)
    data = util.request(url)
    view = pickle.loads(util._cookie_jar.dump())[
        '.mojevideo.sk']['/'].keys()[0]
    st = re.search(r'vHash=\[\'([^\']+)', data)
    if not st:
        return None
    st = st.group(1)
    tim = int(time.time())
    base = 'http://fs5.mojevideo.sk:8080/securevd/'
    return [{'url': base + view.replace('view', '') + '.mp4?st=%s&e=%s|Cookie=%s=1' % (st, tim, view)}]
