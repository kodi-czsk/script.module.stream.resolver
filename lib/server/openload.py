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
# uses code fragments from https://github.com/LordVenom/venom-xbmc-addons
import re
import util
import urllib
import urllib2
from aadecode import AADecoder

class cRequestHandler:
    REQUEST_TYPE_GET = 0
    REQUEST_TYPE_POST = 1

    def __init__(self, sUrl):
        self.__sUrl = sUrl
        self.__sRealUrl = ''
        self.__cType = 0
        self.__aParamaters = {}
        self.__aHeaderEntries = []
        self.removeBreakLines(True)
        self.removeNewLines(True)
        self.__setDefaultHeader()

    def removeNewLines(self, bRemoveNewLines):
        self.__bRemoveNewLines = bRemoveNewLines

    def removeBreakLines(self, bRemoveBreakLines):
        self.__bRemoveBreakLines = bRemoveBreakLines

    def setRequestType(self, cType):
        self.__cType = cType

    def addHeaderEntry(self, sHeaderKey, sHeaderValue):
        aHeader = {sHeaderKey : sHeaderValue}
        self.__aHeaderEntries.append(aHeader)

    def addParameters(self, sParameterKey, mParameterValue):
        self.__aParamaters[sParameterKey] = mParameterValue

    def getResponseHeader(self):
        return self.__sResponseHeader

    # url after redirects
    def getRealUrl(self):
        return self.__sRealUrl;

    def request(self):
        self.__sUrl = self.__sUrl.replace(' ', '+')
        return self.__callRequest()

    def getRequestUri(self):
        return self.__sUrl + '?' + urllib.urlencode(self.__aParamaters)

    def __setDefaultHeader(self):
        UA = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de-DE; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
        self.addHeaderEntry('User-Agent', UA)
        self.addHeaderEntry('Accept-Language', 'de-DE,de;q=0.8,en-US;q=0.6,en;q=0.4')
        self.addHeaderEntry('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7')

    def __callRequest(self):
        sParameters = urllib.urlencode(self.__aParamaters)

        if (self.__cType == cRequestHandler.REQUEST_TYPE_GET):
            if (len(sParameters) > 0):
                if (self.__sUrl.find('?') == -1):
                    self.__sUrl = self.__sUrl + '?' + str(sParameters)
                    sParameters = ''
                else:
                    self.__sUrl = self.__sUrl + '&' + str(sParameters)
                    sParameters = ''

        if (len(sParameters) > 0):
            oRequest = urllib2.Request(self.__sUrl, sParameters)
        else:
            oRequest = urllib2.Request(self.__sUrl)

        for aHeader in self.__aHeaderEntries:
                for sHeaderKey, sHeaderValue in aHeader.items():
                    oRequest.add_header(sHeaderKey, sHeaderValue)

        sContent = ''

        try:
            oResponse = urllib2.urlopen(oRequest, timeout=30)
            sContent = oResponse.read()

            self.__sResponseHeader = oResponse.info()
            self.__sRealUrl = oResponse.geturl()

            oResponse.close()

        except urllib2.HTTPError, e:
            if e.code == 503:
                if cloudflare.CheckIfActive(e.headers):
                    cookies = e.headers['Set-Cookie']
                    cookies = cookies.split(';')[0]
                    from resources.lib.cloudflare import CloudflareBypass
                    sContent = CloudflareBypass().GetHtml(self.__sUrl,e.read(),cookies)

                    self.__sResponseHeader = ''
                    self.__sRealUrl = ''

            if not  sContent:
                cConfig().error("%s,%s" % (cConfig().getlanguage(30205), self.__sUrl))
                return ''

        if (self.__bRemoveNewLines == True):
            sContent = sContent.replace("\n","")
            sContent = sContent.replace("\r\t","")

        if (self.__bRemoveBreakLines == True):
            sContent = sContent.replace("&nbsp;","")

        return sContent

    def getHeaderLocationUrl(self):
        opened = urllib.urlopen(self.__sUrl)
        return opened.geturl()

class cParser:

    def parseSingleResult(self, sHtmlContent, sPattern):
        aMatches = re.compile(sPattern).findall(sHtmlContent)
        if (len(aMatches) == 1):
                aMatches[0] = self.__replaceSpecialCharacters(aMatches[0])
                return True, aMatches[0]
        return False, aMatches

    def __replaceSpecialCharacters(self, sString):
        res=sString.replace('\\/','/').replace('&amp;','&').replace('\xc9','E').replace('&#8211;', '-')
        res=res.replace('&#038;', '&').replace('&rsquo;','\'').replace('\r','').replace('\n','')
        res=res.replace('\t','').replace('&#039;',"'")
        return res

    def parse(self, sHtmlContent, sPattern, iMinFoundValue = 1):
        sHtmlContent = self.__replaceSpecialCharacters(str(sHtmlContent))
        aMatches = re.compile(sPattern, re.IGNORECASE).findall(sHtmlContent)
        if (len(aMatches) >= iMinFoundValue):
            return True, aMatches
        return False, aMatches

    def replace(self, sPattern, sReplaceString, sValue):
         return re.sub(sPattern, sReplaceString, sValue)

    def escape(self, sValue):
        return re.escape(sValue)

    def getNumberFromString(self, sValue):
        sPattern = "\d+"
        aMatches = re.findall(sPattern, sValue)
        if (len(aMatches) > 0):
            return aMatches[0]
        return 0


__author__ = 'Jose Riha/Lubomir Kucera'
__name__ = 'openload'


def supports(url):
    return re.search(r'openload\.\w+/embed/.+', url) is not None

def base10toN(num, n):
    """Change a  to a base-n number.
    Up to base-36 is supported without special notation."""

    new_num_string = ''
    current = num

    while current != 0:
        remainder = current % n
        if 36 > remainder > 9:
            remainder_string = chr(remainder + 87)
        elif remainder >= 36:
            remainder_string = '(' + str(remainder) + ')'
        else:
            remainder_string = str(remainder)
        new_num_string = remainder_string + new_num_string
        current = current / n
    return new_num_string

def resolve(url):

    oRequest = cRequestHandler(url)
    sHtmlContent = oRequest.request()

    oParser = cParser()
    string = ''

    sPattern = '<script type="text\/javascript">(ﾟωﾟ.+?)<\/script>'
    aResult = oParser.parse(sHtmlContent, sPattern)

    vid = 'XXXXXX'
    string2=[]

    for aEntry in aResult[1]:
        s = AADecoder(aEntry).decode()
        string2.append(s)

        if 'welikekodi_ya_rly' in s:
            c0 = re.search('welikekodi_ya_rly = ([^<>;"]+);', s)
            if c0:
                c = c0.group(1)
                c = c.replace('Math.round','int')
                cc = str(eval(c))
                vid = '[' + cc + ']'

    for string3 in string2:
        if ('toString' in string3) and (vid in string3):
            base = int(re.findall('toString\(a\+([0-9]+)\)',string3)[0])
            table = re.findall('(\([0-9][^)]+\))',string3)

            for str1 in table:
                val = re.findall('([0-9]+),([0-9]+)',str1)
                base2 = base + int(val[0][0])
                str2 = base10toN(int(val[0][1]), base2)
                string3 = string3.replace(str1, str2)

            #clean up
            string3 = string3.replace('+', '')
            string3 = string3.replace('"', '')
            string3 = string3.replace('', '')

            #a hack for not having to recode everything
            url = re.findall('(http[^<>}]+)',string3)[0]
            string = 'src="' + url + '?mime=true"'

    if (string):
        sContent = string.replace('\\','')

        api_call = ''

        sPattern = 'src=\s*?"(.*?)\?'
        aResult = oParser.parse(sContent, sPattern)

        if (aResult[0] == True):
            api_call = aResult[1][0]

        if not api_call:
            sPattern = 'window\.vr *=["\'](.+?)["\']'
            aResult = oParser.parse(sContent, sPattern)
            if (aResult[0] == True):
                api_call = aResult[1][0]

    if (api_call):

        if 'openload.co/stream' in api_call:
            UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'
            headers = {'User-Agent': UA }

            req = urllib2.Request(api_call,None,headers)
            res = urllib2.urlopen(req)
            finalurl = res.geturl()
            api_call = finalurl

    return [{'url': api_call}]

