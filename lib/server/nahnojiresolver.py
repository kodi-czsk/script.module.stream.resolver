# *	 GNU General Public License for more details.
# *
# *	 You should have received a copy of the GNU General Public License
# *	 along with this program; see the file COPYING.	 If not, write to
# *	 the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *	 http://www.gnu.org/copyleft/gpl.html
# *
# */
import re,util
__name__='nahnoji'
__priiority__=-1

def supports(url):
	return not _regex(url) == None

# returns the steam url
def url(url):
	m = _regex(url)
	if m:
		ur = m.group('url')
		if m.group('flv'): return [ur]
		page = util.parse_html(ur)
		data = page.select('source[type=video/mp4]')[0]['src']
		return ['http://nahnoji.cz'+data]

def resolve(u):
	stream = url(u)
	if stream:
		return [{'name':__name__,'quality':'360p','url':stream[0],'surl':u}]

def _regex(url):
	return re.search(r'(?P<url>http://nahnoji.cz/((?P<flv>.+\.flv)|(.+)))$',url,re.IGNORECASE | re.DOTALL)

