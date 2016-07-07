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
	return re.search(r'nahnoji\.cz/.+', url) is not None

def resolve(url):
        # returns the stream url
        stream = []
	if url.endswith('.flv'):
            stream = [url]
        else:
	    page = util.parse_html(url)
            stream = ['http://nahnoji.cz'+x['src'] for x in page.select('source[type=video/mp4]')]
	if stream:
		result=[]
		for streamurl in stream:
			result.append({'name':__name__,'quality':'360p','url':streamurl,'surl':url})
		return result

