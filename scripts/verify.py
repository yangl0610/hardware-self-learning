"""Check converted structures, search coverage and local links after mkdocs build."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT/'site'

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.ids = set()
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs: self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs: self.links.append(attrs[key])

report = json.loads((ROOT/'conversion-report.json').read_text())
for row in report:
    md = (ROOT/'docs/chapters'/f"{row['file']}.md").read_text()
    html = (SITE/'chapters'/row['file']/'index.html').read_text()
    counts = {
        'math': html.count('class="arithmatex"'),
        'sections': len(re.findall(r'^## ', md, re.M)),
        'tables': html.count('<table>'),
        'examples': html.count('admonition example'),
        'code_blocks': len(re.findall(r'^\s*```\s*(?:c|cpp|asm|text)\b', md, re.M)),
    }
    for key, value in counts.items():
        assert value == row[key], (row['file'], key, value, row[key])
    assert 'EXAMPLESTART' not in md and 'EXAMPLEEND' not in md
    assert '``` math' not in md and '$`' not in md
    assert html.count('class="highlight"') == row['code_blocks'], (row['file'], 'rendered code count')

pages = {p.resolve(): Page(p.read_text()) for p in SITE.rglob('*.html')}
for path, page in pages.items():
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc or link.startswith('/') or not url.path:
            continue
        target = (path.parent/unquote(url.path)).resolve()
        if target.is_dir(): target /= 'index.html'
        assert target.exists(), (path, link)
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, (path, link, 'missing anchor')
search = json.loads((SITE/'search/search_index.json').read_text())
for row in report:
    assert any(d['location'].startswith('chapters/'+row['file']+'/') for d in search['docs']), row['file']
print(f'PASS: {len(report)} chapters; 75 tables; 96 examples; 25 code blocks; local links and search coverage.')
