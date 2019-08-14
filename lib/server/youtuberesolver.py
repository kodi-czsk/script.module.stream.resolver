# -*- coding: UTF-8 -*-
import operator


#source from https://github.com/rg3/youtube-dl/blob/master/youtube_dl/utils.py
class ExtractorError(Exception):
    """Error during info extraction."""

    def __init__(self, msg, tb=None, expected=False, cause=None, video_id=None):
        """ tb, if given, is the original traceback (so that it can be printed out).
        If expected is set, this is a normal error message and most likely not a bug in youtube-dl.
        """

        if sys.exc_info()[0] in (compat_urllib_error.URLError, socket.timeout, UnavailableVideoError):
            expected = True
        if video_id is not None:
            msg = video_id + ': ' + msg
        if cause:
            msg += ' (caused by %r)' % cause
        if not expected:
            msg += bug_reports_message()
        super(ExtractorError, self).__init__(msg)

        self.traceback = tb
        self.exc_info = sys.exc_info()  # preserve original exception
        self.cause = cause
        self.video_id = video_id

    def format_traceback(self):
        if self.traceback is None:
            return None
        return ''.join(traceback.format_tb(self.traceback))

_OPERATORS = [
    ('|', operator.or_),
    ('^', operator.xor),
    ('&', operator.and_),
    ('>>', operator.rshift),
    ('<<', operator.lshift),
    ('-', operator.sub),
    ('+', operator.add),
    ('%', operator.mod),
    ('/', operator.truediv),
    ('*', operator.mul),
]
_ASSIGN_OPERATORS = [(op + '=', opfunc) for op, opfunc in _OPERATORS]
_ASSIGN_OPERATORS.append(('=', lambda cur, right: right))

_NAME_RE = r'[a-zA-Z_$][a-zA-Z_$0-9]*'


# source from https://github.com/rg3/youtube-dl/blob/master/youtube_dl/jsinterp.py
class JSInterpreter(object):
    def __init__(self, code, objects=None):
        if objects is None:
            objects = {}
        self.code = code
        self._functions = {}
        self._objects = objects

    def remove_quotes(self, s):
        if s is None or len(s) < 2:
            return s
        for quote in ('"', "'", ):
            if s[0] == quote and s[-1] == quote:
                return s[1:-1]
        return s

    def interpret_statement(self, stmt, local_vars, allow_recursion=100):
        if allow_recursion < 0:
            raise ExtractorError('Recursion limit reached')

        should_abort = False
        stmt = stmt.lstrip()
        stmt_m = re.match(r'var\s', stmt)
        if stmt_m:
            expr = stmt[len(stmt_m.group(0)):]
        else:
            return_m = re.match(r'return(?:\s+|$)', stmt)
            if return_m:
                expr = stmt[len(return_m.group(0)):]
                should_abort = True
            else:
                # Try interpreting it as an expression
                expr = stmt

        v = self.interpret_expression(expr, local_vars, allow_recursion)
        return v, should_abort

    def interpret_expression(self, expr, local_vars, allow_recursion):
        expr = expr.strip()
        if expr == '':  # Empty expression
            return None

        if expr.startswith('('):
            parens_count = 0
            for m in re.finditer(r'[()]', expr):
                if m.group(0) == '(':
                    parens_count += 1
                else:
                    parens_count -= 1
                    if parens_count == 0:
                        sub_expr = expr[1:m.start()]
                        sub_result = self.interpret_expression(
                            sub_expr, local_vars, allow_recursion)
                        remaining_expr = expr[m.end():].strip()
                        if not remaining_expr:
                            return sub_result
                        else:
                            expr = json.dumps(sub_result) + remaining_expr
                        break
            else:
                raise ExtractorError('Premature end of parens in %r' % expr)

        for op, opfunc in _ASSIGN_OPERATORS:
            m = re.match(r'''(?x)
                (?P<out>%s)(?:\[(?P<index>[^\]]+?)\])?
                \s*%s
                (?P<expr>.*)$''' % (_NAME_RE, re.escape(op)), expr)
            if not m:
                continue
            right_val = self.interpret_expression(
                m.group('expr'), local_vars, allow_recursion - 1)

            if m.groupdict().get('index'):
                lvar = local_vars[m.group('out')]
                idx = self.interpret_expression(
                    m.group('index'), local_vars, allow_recursion)
                assert isinstance(idx, int)
                cur = lvar[idx]
                val = opfunc(cur, right_val)
                lvar[idx] = val
                return val
            else:
                cur = local_vars.get(m.group('out'))
                val = opfunc(cur, right_val)
                local_vars[m.group('out')] = val
                return val

        if expr.isdigit():
            return int(expr)

        var_m = re.match(
            r'(?!if|return|true|false)(?P<name>%s)$' % _NAME_RE,
            expr)
        if var_m:
            return local_vars[var_m.group('name')]

        try:
            return json.loads(expr)
        except ValueError:
            pass

        m = re.match(
            r'(?P<in>%s)\[(?P<idx>.+)\]$' % _NAME_RE, expr)
        if m:
            val = local_vars[m.group('in')]
            idx = self.interpret_expression(
                m.group('idx'), local_vars, allow_recursion - 1)
            return val[idx]

        m = re.match(
            r'(?P<var>%s)(?:\.(?P<member>[^(]+)|\[(?P<member2>[^]]+)\])\s*(?:\(+(?P<args>[^()]*)\))?$' % _NAME_RE,
            expr)
        if m:
            variable = m.group('var')
            member = self.remove_quotes(m.group('member') or m.group('member2'))
            arg_str = m.group('args')

            if variable in local_vars:
                obj = local_vars[variable]
            else:
                if variable not in self._objects:
                    self._objects[variable] = self.extract_object(variable)
                obj = self._objects[variable]

            if arg_str is None:
                # Member access
                if member == 'length':
                    return len(obj)
                return obj[member]

            assert expr.endswith(')')
            # Function call
            if arg_str == '':
                argvals = tuple()
            else:
                argvals = tuple([
                    self.interpret_expression(v, local_vars, allow_recursion)
                    for v in arg_str.split(',')])

            if member == 'split':
                assert argvals == ('',)
                return list(obj)
            if member == 'join':
                assert len(argvals) == 1
                return argvals[0].join(obj)
            if member == 'reverse':
                assert len(argvals) == 0
                obj.reverse()
                return obj
            if member == 'slice':
                assert len(argvals) == 1
                return obj[argvals[0]:]
            if member == 'splice':
                assert isinstance(obj, list)
                index, howMany = argvals
                res = []
                for i in range(index, min(index + howMany, len(obj))):
                    res.append(obj.pop(index))
                return res

            return obj[member](argvals)

        for op, opfunc in _OPERATORS:
            m = re.match(r'(?P<x>.+?)%s(?P<y>.+)' % re.escape(op), expr)
            if not m:
                continue
            x, abort = self.interpret_statement(
                m.group('x'), local_vars, allow_recursion - 1)
            if abort:
                raise ExtractorError(
                    'Premature left-side return of %s in %r' % (op, expr))
            y, abort = self.interpret_statement(
                m.group('y'), local_vars, allow_recursion - 1)
            if abort:
                raise ExtractorError(
                    'Premature right-side return of %s in %r' % (op, expr))
            return opfunc(x, y)

        m = re.match(
            r'^(?P<func>%s)\((?P<args>[a-zA-Z0-9_$,]*)\)$' % _NAME_RE, expr)
        if m:
            fname = m.group('func')
            argvals = tuple([
                int(v) if v.isdigit() else local_vars[v]
                for v in m.group('args').split(',')]) if len(m.group('args')) > 0 else tuple()
            if fname not in self._functions:
                self._functions[fname] = self.extract_function(fname)
            return self._functions[fname](argvals)

        raise ExtractorError('Unsupported JS expression %r' % expr)

    def extract_object(self, objname):
        _FUNC_NAME_RE = r'''(?:[a-zA-Z$0-9]+|"[a-zA-Z$0-9]+"|'[a-zA-Z$0-9]+')'''
        obj = {}
        obj_m = re.search(
            r'''(?x)
                (?<!this\.)%s\s*=\s*{\s*
                    (?P<fields>(%s\s*:\s*function\s*\(.*?\)\s*{.*?}(?:,\s*)?)*)
                }\s*;
            ''' % (re.escape(objname), _FUNC_NAME_RE),
            self.code)
        fields = obj_m.group('fields')
        # Currently, it only supports function definitions
        fields_m = re.finditer(
            r'''(?x)
                (?P<key>%s)\s*:\s*function\s*\((?P<args>[a-z,]+)\){(?P<code>[^}]+)}
            ''' % _FUNC_NAME_RE,
            fields)
        for f in fields_m:
            argnames = f.group('args').split(',')
            obj[self.remove_quotes(f.group('key'))] = self.build_function(argnames, f.group('code'))

        return obj

    def extract_function(self, funcname):
        func_m = re.search(
            r'''(?x)
                (?:function\s+%s|[{;,]\s*%s\s*=\s*function|var\s+%s\s*=\s*function)\s*
                \((?P<args>[^)]*)\)\s*
                \{(?P<code>[^}]+)\}''' % (
                re.escape(funcname), re.escape(funcname), re.escape(funcname)),
            self.code)
        if func_m is None:
            raise ExtractorError('Could not find JS function %r' % funcname)
        argnames = func_m.group('args').split(',')

        return self.build_function(argnames, func_m.group('code'))

    def call_function(self, funcname, *args):
        f = self.extract_function(funcname)
        return f(args)

    def build_function(self, argnames, code):
        def resf(args):
            local_vars = dict(zip(argnames, args))
            for stmt in code.split(';'):
                res, abort = self.interpret_statement(stmt, local_vars)
                if abort:
                    break
            return res
        return resf


# inspired by https://github.com/rg3/youtube-dl/blob/master/youtube_dl/extractor/youtube.py
import urllib2
class SignatureExtractor:

    def __init__(self):
        self.algoCache = {}

    def decryptSignature(self, s, playerUrl):
        util.debug("decrypt_signature sign_len[%d] playerUrl[%s]" % (len(s), playerUrl))

        if playerUrl is None:
            raise ExtractorError('Cannot decrypt signature without playerUrl')

        if playerUrl.startswith('//'):
            playerUrl = 'https:' + playerUrl
        elif playerUrl.startswith('/'):
            playerUrl = 'https://youtube.com' + playerUrl

        # use algoCache
        if playerUrl not in self.algoCache:
            # get player HTML 5 sript
            request = urllib2.Request(playerUrl)
            try:
                self.playerData = urllib2.urlopen(request).read()
                self.playerData = self.playerData.decode('utf-8', 'ignore')
            except:
                util.debug('Unable to download playerUrl webpage')
                return ''

            patterns = [
                r'\b[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*encodeURIComponent\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'\b[a-zA-Z0-9]+\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*encodeURIComponent\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'(?P<sig>[a-zA-Z0-9$]+)\s*=\s*function\(\s*a\s*\)\s*{\s*a\s*=\s*a\.split\(\s*""\s*\)',
                # Obsolete patterns
                r'(["\'])signature\1\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'\.sig\|\|(?P<sig>[a-zA-Z0-9$]+)\(',
                r'yt\.akamaized\.net/\)\s*\|\|\s*.*?\s*[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*(?:encodeURIComponent\s*\()?\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'\b[cs]\s*&&\s*[adf]\.set\([^,]+\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'\b[a-zA-Z0-9]+\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'\bc\s*&&\s*a\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'\bc\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\(',
                r'\bc\s*&&\s*[a-zA-Z0-9]+\.set\([^,]+\s*,\s*\([^)]*\)\s*\(\s*(?P<sig>[a-zA-Z0-9$]+)\('
            ]

            match = None
            for pattern in patterns:
                match = re.search(pattern, self.playerData)
                if match is not None:
                    break
                    
            if match:
                mainFunName = match.group('sig')
                util.debug('Main signature function name = "%s"' % mainFunName)
            else:
                util.debug('Can not get main signature function name')
                return ''

            jsi = JSInterpreter(self.playerData)
            initial_function = jsi.extract_function(mainFunName)
            algoCodeObj = lambda s: initial_function([s])
        else:
            # get algoCodeObj from algoCache
            util.debug('Algo taken from cache')
            algoCodeObj = self.algoCache[playerUrl]

        signature = algoCodeObj(s)

        util.debug('Decrypted signature = [%s]' % signature)
        # if algo seems ok and not in cache, add it to cache
        if playerUrl not in self.algoCache and '' != signature:
            util.debug('Algo from player [%s] added to cache' % playerUrl)
            self.algoCache[playerUrl] = algoCodeObj

        return signature

decryptor = SignatureExtractor()

'''
   YouTube plugin for XBMC
    Copyright (C) 2010-2012 Tobias Ussing And Henrik Mosgaard Jensen

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import cgi
import json

class YoutubePlayer(object):
    fmt_value = {
            5: "240p",
            18: "360p",
            22: "720p",
            26: "???",
            33: "???",
            34: "360p",
            35: "480p",
            37: "1080p",
            38: "720p",
            43: "360p",
            44: "480p",
            45: "720p",
            46: "520p",
            59: "480",
            78: "400",
            82: "360p",
            83: "240p",
            84: "720p",
            85: "520p",
            100: "360p",
            101: "480p",
            102: "720p",
            120: "hd720",
            121: "hd1080"
            }

    # YouTube Playback Feeds
    urls = {}
    urls['video_stream'] = "http://www.youtube.com/watch?v=%s&safeSearch=none"
    urls['embed_stream'] = "http://www.youtube.com/embed/%s"
    urls['video_info'] = "http://www.youtube.com/get_video_info?video_id=%s" \
                         "&eurl=https://youtube.googleapis.com/v/%s&sts=%s"

    def __init__(self):
        pass

    def removeAdditionalEndingDelimiter(self, data):
        pos = data.find("};")
        if pos != -1:
            data = data[:pos + 1]
        return data

    def extractFlashVars(self, data, assets):
        flashvars = {}
        found = False

        for line in data.split("\n"):
            if line.strip().find(";ytplayer.config = ") > 0:
                found = True
                p1 = line.find(";ytplayer.config = ") + len(";ytplayer.config = ") - 1
                p2 = line.rfind(";")
                if p1 <= 0 or p2 <= 0:
                    continue
                data = line[p1 + 1:p2]
                break
        data = self.removeAdditionalEndingDelimiter(data)

        if found:
            data = json.loads(data)
            if assets:
                flashvars = data["assets"]
            else:
                flashvars = data["args"]
        return flashvars

    def scrapeWebPageForVideoLinks(self, result, video, video_id):
        links = {}
        if re.search(r'player-age-gate-content">', result) is not None:
            # We simulate the access to the video from www.youtube.com/v/{video_id}
            # this can be viewed without login into Youtube
            embed_webpage = util.request(self.urls[u"embed_stream"] % video_id)

            sts = re.search('"sts"\s*:\s*(\d+)', embed_webpage).group().replace('"sts":', '')
            result = util.request(self.urls[u"video_info"] % (video_id, video_id, sts))

            flashvars = cgi.parse_qs(result)
            flashvars[u"url_encoded_fmt_stream_map"] = flashvars[u"url_encoded_fmt_stream_map"][0]
            flashvars[u"title"] = flashvars[u"title"][0]
        else:
            flashvars = self.extractFlashVars(result, 0)

        if not flashvars.has_key(u"url_encoded_fmt_stream_map"):
            return links

        if flashvars.has_key(u"ttsurl"):
            video[u"ttsurl"] = flashvars[u"ttsurl"]
        if flashvars.has_key("title"):
            video["title"] = flashvars["title"]

        for url_desc in flashvars[u"url_encoded_fmt_stream_map"].split(u","):
            url_desc_map = cgi.parse_qs(url_desc)
            if not (url_desc_map.has_key(u"url") or url_desc_map.has_key(u"stream")):
                continue

            key = int(url_desc_map[u"itag"][0])
            url = u""
            if url_desc_map.has_key(u"url"):
                url = urllib.unquote(url_desc_map[u"url"][0])
            elif url_desc_map.has_key(u"conn") and url_desc_map.has_key(u"stream"):
                url = urllib.unquote(url_desc_map[u"conn"][0])
                if url.rfind("/") < len(url) - 1:
                    url = url + "/"
                url = url + urllib.unquote(url_desc_map[u"stream"][0])
            elif url_desc_map.has_key(u"stream") and not url_desc_map.has_key(u"conn"):
                url = urllib.unquote(url_desc_map[u"stream"][0])

            if url_desc_map.has_key(u"sig"):
                url = url + u"&sig=" + url_desc_map[u"sig"][0]
            elif url_desc_map.has_key(u"s"):
                sig = url_desc_map[u"s"][0]
                flashvars = self.extractFlashVars(result, 1)
                js = flashvars[u"js"]
                url = url + u"&sig=" + self.decrypt_signature(sig, js)

            links[key] = url

        return links

    def decrypt_signature(self, s, js):
        return decryptor.decryptSignature(s, js)


    def extractVideoLinksFromYoutube(self, url, videoid, video):
        result = util.request(self.urls[u"video_stream"] % videoid)
        links = self.scrapeWebPageForVideoLinks(result, video, videoid)
        if len(links) == 0:
            util.error(u"Couldn't find video url- or stream-map.")
        return links
# /*
# *      Copyright (C) 2011 Libor Zoubek
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
import re, util, urllib
__name__ = 'youtube'


def supports(url):
    return not _regex(url) == None

def resolve(url):
    m = _regex(url)
    if not m == None:
        player = YoutubePlayer()
        video = {'title':'žádný název'}
        index = url.find('&')  # strip out everytihing after &
        if index > 0:
            url = url[:index]
        links = player.extractVideoLinksFromYoutube(url, m.group('id'), video)
        resolved = []
        for q in links:
            if q in player.fmt_value.keys():
                quality = player.fmt_value[q]
                item = {}
                item['name'] = __name__
                item['url'] = links[q]
                item['quality'] = quality
                item['surl'] = url
                item['subs'] = ''
                item['title'] = video['title']
                item['fmt'] = q
                resolved.append(item)
        return resolved

def _regex(url):
    return re.search('(www\.youtube\.com/(watch\?v=|v/|embed/)|youtu\.be/)(?P<id>.+?)(\?|$|&)', url, re.IGNORECASE | re.DOTALL)
