from flask import Flask
from flask import render_template
from pygments import highlight
import pygments.lexers as pyg_lexers
from pygments.formatters import HtmlFormatter
import requests, re
from flask import request
from urlparse import urlparse
from flask import redirect, url_for
import pygments.styles as pyg_styles
app = Flask(__name__)

@app.route("/")
def index():
    url = request.args.get('url', None)
    fontsize = request.args.get('fontsize', 100)
    pystyle = request.args.get('pystyle', 'default')
    if url:
        return redirect(url_for('found', fontsize = fontsize, pystyle = pystyle, url = url))
    rawurl = request.args.get('rawurl', None)
    if rawurl:
        return redirect(url_for('show', fontsize = fontsize, pystyle = pystyle, url = rawurl))
    fontsizes = [100, 120, 150, 180, 200]
    pystyles = pyg_styles.get_all_styles()
    return render_template('index.jinja', pystyles = pystyles, fontsizes = fontsizes)


@app.route("/found/<int:fontsize>/<pystyle>/<path:url>")
def found(fontsize = 100, pystyle = 'default', url = None):
    output = 'url: %s\n' % url
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri).strip('/')
    output += 'domain: %s\n' % domain
    r = requests.get(url)
    # for m in re.finditer('href="(.*?)".*?>(.*?)<', r.text, re.MULTILINE):
    #     output += 'MATCH: %s\n' % str(m.groups())
    urls = re.findall('href="(.*?)"', r.text)
    links = []
    for urlfound in urls:
        if 'raw' in urlfound:
            if urlfound.startswith('/'):
                urlfound = domain + urlfound
            output += 'url: %s\n' % urlfound
            links.append({'name': urlfound, 'url': url_for('show', 
                                                        fontsize = fontsize, 
                                                        pystyle = pystyle,
                                                        url = urlfound)})
    return render_template('find_links.jinja', url = url, links = links) # , output = output

@app.route("/show/<int:fontsize>/<pystyle>/<path:url>")
def show(fontsize = 100, pystyle = 'default', url = None):
    print 'pystyle', pystyle
    r = requests.get(url)
    fname = url.split('/')[-1]
    contype = r.headers.get('content-type', None)
    if contype and ';' in contype:
        contype = contype.split(';')[0]
    try:
        lexer = pyg_lexers.get_lexer_for_filename(fname)
    except:
        try:
            lexer = pyg_lexers.get_lexer_for_mimetype(contype)
        except:
            lexer = pyg_lexers.get_lexer_for_filename('.txt')
    # pystyle = pyg_styles.get_style_by_name(pystyle)
    formatter = HtmlFormatter(linenos=True, cssclass='code', style = pystyle)
    css = formatter.get_style_defs('.code').encode('utf8')
    code = highlight(r.text, lexer, formatter)
    return render_template('showcode.jinja', title = fname, code = code, css = css, fontsize = fontsize)

if __name__ == "__main__":
    app.run(debug=True)#