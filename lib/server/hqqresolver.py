# -*- coding: UTF-8 -*-
# *  GNU General Public License for more details.
# *
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# *
# *  original based on https://gitorious.org/iptv-pl-dla-openpli/ urlresolver
# *  update based on https://github.com/LordVenom/
# */
from StringIO import StringIO
import json
import util
import re
import base64
import urllib

__name__ = 'hqq'

def supports(url):
    return _regex(url) is not None


def _decode(data):
    def O1l(string):
        ret = ""
        i = len(string) - 1
        while i >= 0:
            ret += string[i]
            i -= 1
        return ret

    def l0I(string):
        enc = ""
        dec = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        i = 0
        while True:
            h1 = dec.find(string[i])
            i += 1
            h2 = dec.find(string[i])
            i += 1
            h3 = dec.find(string[i])
            i += 1
            h4 = dec.find(string[i])
            i += 1
            bits = h1 << 18 | h2 << 12 | h3 << 6 | h4
            o1 = bits >> 16 & 0xff
            o2 = bits >> 8 & 0xff
            o3 = bits & 0xff
            if h3 == 64:
                enc += unichr(o1)
            else:
                if h4 == 64:
                    enc += unichr(o1) + unichr(o2)
                else:
                    enc += unichr(o1) + unichr(o2) + unichr(o3)
            if i >= len(string):
                break
        return enc

    escape = re.search("var _escape=\'([^\']+)", l0I(O1l(data))).group(1)
    return escape.replace('%', '\\').decode('unicode-escape')


def _decode2(file_url):
    def K12K(a, typ='b'):
        codec_a = ["G", "L", "M", "N", "Z", "o", "I", "t", "V", "y", "x", "p", "R", "m", "z", "u",
                   "D", "7", "W", "v", "Q", "n", "e", "0", "b", "="]
        codec_b = ["2", "6", "i", "k", "8", "X", "J", "B", "a", "s", "d", "H", "w", "f", "T", "3",
                   "l", "c", "5", "Y", "g", "1", "4", "9", "U", "A"]
        if 'd' == typ:
            tmp = codec_a
            codec_a = codec_b
            codec_b = tmp
        idx = 0
        while idx < len(codec_a):
            a = a.replace(codec_a[idx], "___")
            a = a.replace(codec_b[idx], codec_a[idx])
            a = a.replace("___", codec_b[idx])
            idx += 1
        return a

    def _xc13(_arg1):
        _lg27 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        _local2 = ""
        _local3 = [0, 0, 0, 0]
        _local4 = [0, 0, 0]
        _local5 = 0
        while _local5 < len(_arg1):
            _local6 = 0
            while _local6 < 4 and (_local5 + _local6) < len(_arg1):
                _local3[_local6] = _lg27.find(_arg1[_local5 + _local6])
                _local6 += 1
            _local4[0] = ((_local3[0] << 2) + ((_local3[1] & 48) >> 4))
            _local4[1] = (((_local3[1] & 15) << 4) + ((_local3[2] & 60) >> 2))
            _local4[2] = (((_local3[2] & 3) << 6) + _local3[3])

            _local7 = 0
            while _local7 < len(_local4):
                if _local3[_local7 + 1] == 64:
                    break
                _local2 += chr(_local4[_local7])
                _local7 += 1
            _local5 += 4
        return _local2

    return _xc13(K12K(file_url, 'e'))


def _decode3(w, i, s, e):
    var1 = 0
    var2 = 0
    var3 = 0
    var4 = []
    var5 = []
    while (True):
        if (var1 < 5):
            var5.append(w[var1])
        elif (var1 < len(w)):
            var4.append(w[var1])
        var1 += 1
        if (var2 < 5):
            var5.append(i[var2])
        elif (var2 < len(i)):
            var4.append(i[var2])
        var2 += 1
        if (var3 < 5):
            var5.append(s[var3])
        elif (var3 < len(s)):
            var4.append(s[var3])
        var3 += 1
        if (len(w) + len(i) + len(s) + len(e) == len(var4) + len(var5) + len(e)):
            break
    var6 = ''.join(var4)
    var7 = ''.join(var5)
    var2 = 0
    result = []
    for var1 in range(0, len(var4), 2):
        ll11 = -1
        if (ord(var7[var2]) % 2):
            ll11 = 1
        result.append(chr(int(var6[var1:var1 + 2], 36) - ll11))
        var2 += 1
        if (var2 >= len(var5)):
            var2 = 0
    return ''.join(result)

def _decode_data(data):
    valuesPattern = r";}\('(\w+)','(\w*)','(\w*)','(\w*)'\)\)"
    values = re.search(valuesPattern, data, re.DOTALL)
    return _decode3(values.group(1), values.group(2), values.group(3), values.group(4))

def resolve(url):
    m = _regex(url)
    if m:
        vid = m.group('vid')
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Content-Type': 'text/html; charset=utf-8'}

        player_url = "http://hqq.tv/player/embed_player.php?vid=%s&autoplay=no" % vid
        data = util.request(player_url, headers)

        data = _decode_data(data)
        data = _decode_data(data)
        blocs = data.split(';; ')
        data = _decode_data(blocs[1])

        jsonInfo = util.request("http://hqq.tv/player/ip.php?type=json", headers)
        jsonIp = json.loads(jsonInfo)['ip']
        at = re.search(r'at = "(\w+)";', data, re.DOTALL)
        if jsonIp and at:
            get_data = {'iss': jsonIp, 'vid': vid, 'at': at.group(1), 'autoplayed': 'yes', 'referer': 'on',
                        'http_referer': '', 'pass': '', 'embed_from' : '', 'need_captcha' : '0' }

            data = urllib.unquote(util.request("http://hqq.tv/sec/player/embed_player.php?" +
                                               urllib.urlencode(get_data), headers))

            l = re.search(r'link_1: ([a-zA-Z]+), server_1: ([a-zA-Z]+)', data)
            vid_server = re.search(r'var ' + l.group(2) + ' = "([^"]+)"', data).group(1)
            vid_link = re.search(r'var ' + l.group(1) + ' = "([^"]+)"', data).group(1)

            if vid_server and vid_link:
                get_data = {'server_1': vid_server, 'link_1': vid_link, 'at': at.group(1), 'adb': '0/',
                            'b': '1', 'vid': vid }
                headers['x-requested-with'] = 'XMLHttpRequest'
                data = util.request("http://hqq.tv/player/get_md5.php?" + urllib.urlencode(get_data), headers)
                jsonData = json.loads(data)
                encodedm3u = jsonData['file']
                decodedm3u = _decode2(encodedm3u.replace('\\', ''))

                agent = 'User-Agent=Mozilla/5.0 (iPhone; CPU iPhone OS 5_0_1 like Mac OS X)'
                return [{'url': decodedm3u + '|' + agent, 'quality': '360p'}]
    return None


def _regex(url):
    match = re.search("(hqq|netu)\.tv/watch_video\.php\?v=(?P<vid>[0-9A-Za-z]+)", url)
    if match:
        return match
    match = re.search(r'(hqq|netu)\.tv/player/embed_player\.php\?vid=(?P<vid>[0-9A-Za-z]+)', url)
    if match:
        return match
    match = re.search(r'(hqq|netu)\.tv/player/hash\.php\?hash=\d+', url)
    if match:
        match = re.search(r'var\s+vid\s*=\s*\'(?P<vid>[^\']+)\'', urllib.unquote(util.request(url)))
        if match:
            return match
    b64enc = re.search(r'data:text/javascript\;charset\=utf\-8\;base64([^\"]+)', url)
    b64dec = b64enc and base64.decodestring(b64enc.group(1))
    enc = b64dec and re.search(r"\'([^']+)\'", b64dec).group(1)
    if enc:
        decoded = _decode(enc)
        match = re.search(r'<input name="vid"[^>]+? value="(?P<vid>[^"]+?)">', decoded)
        if re.search(r'<form(.+?)action="[^"]*(hqq|netu)\.tv/player/embed_player\.php"[^>]*>',
                     decoded) and match:
            return match
    return None
