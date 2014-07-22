from flask import Flask
from flask import render_template
from pygments import highlight
import pygments.lexers as pyg_lexers
from pygments.formatters import HtmlFormatter
import requests, re
from flask import request
from urlparse import urlparse
from flask import redirect, url_for
app = Flask(__name__)

@app.route("/")
def index():
    url = request.args.get('url', None)
    print 'url:', url
    if url:
        return redirect(url_for('found', url = url))
    rawurl = request.args.get('rawurl', None)
    print 'rawurl:', rawurl
    if rawurl:
        return redirect(url_for('show', url = rawurl))
    return render_template('index.jinja')


@app.route("/found/<path:url>")
def found(url = None):
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
            links.append({'name': urlfound, 'url': '/show/%s' % urlfound})
    return render_template('find_links.jinja', url = url, links = links) # , output = output

@app.route("/show/<path:url>")
def show(url = None):
    r = requests.get(url)
    fname = url.split('/')[-1]
    try:
        lexer = pyg_lexers.get_lexer_for_filename(fname)
    except:
        lexer = pyg_lexers.get_lexer_for_filename('.txt')
    pyg_css = HtmlFormatter().get_style_defs('.code')
    css = pyg_css.encode('utf8')
    formatter = HtmlFormatter(linenos=True, cssclass='code')#
    code = highlight(r.text, lexer, formatter)
    return render_template('showcode.jinja', title = fname, code = code, css = css)

if __name__ == "__main__":
    app.run(debug=True)#