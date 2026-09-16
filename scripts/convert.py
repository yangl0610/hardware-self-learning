"""Convert the textbook with Pandoc; run explicitly to overwrite generated chapters."""
from pathlib import Path
import json
import re
import pypandoc
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / '教材'

def convert(text, chapter, language):
    text = text.replace(r'\thechapter', str(chapter))
    text = re.sub(r'\\begin\{adjustbox\}\{[^\n]*\}', '', text)
    text = text.replace(r'\end{adjustbox}', '')
    text = text.replace(r'\begin{examplebox}', '\nEXAMPLESTART\n\n').replace(r'\end{examplebox}', '\n\nEXAMPLEEND\n')
    ast = json.loads(pypandoc.convert_text(text, 'json', format='latex'))
    def walk(node):
        if isinstance(node, dict):
            if node.get('t') == 'Math':
                node['c'][1] = node['c'][1].replace(r'\begin{equation}', '').replace(r'\end{equation}', '').replace('{align}', '{aligned}').strip()
                node['c'][1] = re.sub(r'(?<!\\)\|', lambda m: r'\vert ', node['c'][1])
            if node.get('t') == 'CodeBlock':
                node['c'][0][1] = [language]
            if node.get('t') in ('RawBlock', 'RawInline') and node['c'][0] == 'latex':
                raise ValueError(f'Unconverted LaTeX: {node}')
            for value in node.values(): walk(value)
        elif isinstance(node, list):
            for item in node: walk(item)
    walk(ast)
    md = pypandoc.convert_text(json.dumps(ast), 'gfm-tex_math_gfm+tex_math_dollars', format='json', extra_args=['--wrap=none'])
    md = re.sub(r'\$\$(.*?)\$\$', lambda m: '\n\n$$\n'+m[1].strip()+'\n$$\n\n', md, flags=re.S)
    md = re.sub(r'EXAMPLESTART\s*\n(.*?)\n\s*EXAMPLEEND', lambda m: '!!! example "例题"\n\n' + '\n'.join('    '+line if line else '' for line in m[1].strip().splitlines()), md, flags=re.S)
    # Pandoc writes display equations on one line; Arithmatex needs block delimiters.
    md = re.sub(r'(?m)^(\s*)\$\$(.*?)\$\$$', lambda m: m[1]+'$$\n'+m[1]+m[2]+'\n'+m[1]+'$$', md)
    return '\n'.join(line.rstrip() for line in md.splitlines()).strip()+'\n'

def main():
    main_tex = (SOURCE/'main.tex').read_text()
    parts = []
    count = 0
    report = []
    for token in re.finditer(r'\\part\{([^}]+)\}|\\input\{chapters/([^}]+)\}', main_tex):
        if token[1]:
            parts.append((token[1], []))
            continue
        count += 1
        stem = token[2]
        source = (SOURCE/'chapters'/f'{stem}.tex').read_text()
        title = re.search(r'\\chapter\{([^}]+)\}', source)[1]
        md = convert(source, count, {'ch18':'c','ch19':'cpp','ch20':'asm'}.get(stem, 'text'))
        (ROOT/'docs/chapters'/f'{stem}.md').write_text(md)
        parts[-1][1].append({title: f'chapters/{stem}.md'})
        report.append({'file':stem,'title':title,'math':len(re.findall(r'(?<!\\)\$', source))//2+source.count(r'\[')+source.count(r'\begin{equation}')+source.count(r'\begin{align}'), 'sections':source.count(r'\section{'), 'tables':source.count(r'\begin{table}'), 'examples':source.count(r'\begin{examplebox}'), 'code_blocks':source.count(r'\begin{lstlisting}')})
    config = yaml.safe_load((ROOT/'mkdocs.yml').read_text())
    config['nav'] = [{'开始阅读':'index.md'},{'学习路线':'roadmap.md'}]+[{name:items} for name,items in parts]+[{'编写说明':'about.md'}]
    (ROOT/'mkdocs.yml').write_text(yaml.safe_dump(config,allow_unicode=True,sort_keys=False))
    (ROOT/'conversion-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f'Converted {count} chapters.')

if __name__ == '__main__': main()
