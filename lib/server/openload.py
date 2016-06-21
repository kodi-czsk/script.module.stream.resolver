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
import urllib2
from aadecode import AADecoder

__author__ = 'Jose Riha/Lubomir Kucera'
__name__ = 'openload'


def supports(url):
    return re.search(r'openload\.\w+/embed/.+', url) is not None


# uses code fragments from https://github.com/LordVenom/venom-xbmc-addons
def resolve(url):

    input = util.request(url)

    c = re.search('>welikekodi_ya_rly = ([0-9- ]+);<', input).group(1)
    cc = str(eval(c))                                                        
    vid = '[' + cc + ']'
    
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
    
    sPattern = '<script type="text\/javascript">(.........+?)<\/script>'
    aResult = re.findall(sPattern, input, flags=re.M )
    string2=[]
    
    for aEntry in aResult:
    	s = AADecoder(aEntry).decode()                                       
    	string2.append(s)   
    
    for string3 in string2:                                                                     
    	if isinstance (string3,bool):
    		continue
                                                                                                        
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
    string=string.replace('src="','').replace('"','')
    return [{'url': string}]
