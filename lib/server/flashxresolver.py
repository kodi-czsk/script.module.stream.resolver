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

import os
import re
import sys

parent_dir=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(parent_dir,'venom'))
import venom_flashxresolver

__name__ = 'flashx'


def supports(url):
    return re.search(r'flashx\.tv/embed\-[^\.]+\.html', url) is not None


def resolve(url):
    hoster=venom_flashxresolver.cHoster()
    hoster.setUrl(url)
    status, surl = hoster.getMediaLink()
    if status:
        return [{'url': surl}]
    else:
        return None
