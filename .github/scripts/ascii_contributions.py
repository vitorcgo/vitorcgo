"""Desenha o gráfico de contribuições do GitHub em ASCII, como um SVG animado.

Uso: python3 .github/scripts/ascii_contributions.py USUARIO SAIDA.svg
Só biblioteca padrão; lê a página pública de contribuições do perfil.
"""
import random
import re
import sys
import urllib.request
from datetime import date
from html import escape
from pathlib import Path

user, out = sys.argv[1], Path(sys.argv[2])
request = urllib.request.Request(f'https://github.com/users/{user}/contributions',
                                 headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(request, timeout=30).read().decode('utf-8')

days = {}
for match in re.finditer(r'<td[^>]*class="ContributionCalendar-day"[^>]*>', html):
    tag = match.group(0)
    day = re.search(r'data-date="([\d-]+)"', tag)
    level = re.search(r'data-level="(\d)"', tag)
    cell = re.search(r'id="contribution-day-component-(\d+)-(\d+)"', tag)
    if day and level and cell:
        days[int(cell.group(2)), int(cell.group(1))] = (date.fromisoformat(day.group(1)), int(level.group(1)))
if not days:
    sys.exit('Nenhuma contribuição encontrada; mantendo o SVG anterior.')

total = re.search(r'([\d,.]+)\s*contributions?\s*in the last year', html)
total = int(re.sub(r'\D', '', total.group(1))) if total else 0

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
CHARS = '·:+#@'
COLORS = ['#2e2e2e', '#6b6b6b', '#a3a3a3', '#d6d6d6', '#ffffff']
MONTHS = 'jan fev mar abr mai jun jul ago set out nov dez'.split()
W, H = 880, 250
weeks = max(week for week, _ in days) + 1
x0, y0, row_h = 72, 96, 17
col_w = (W - x0 - 32) / weeks
rnd = random.Random(7)

body = []
for week in range(weeks):
    cells = []
    for weekday in range(7):
        if (week, weekday) not in days:
            continue
        _, level = days[week, weekday]
        twinkle = ''
        if level >= 2 and rnd.random() < .08:
            twinkle = f' class="tw" style="animation-delay:{rnd.uniform(0, 6):.2f}s"'
        cells.append(f'<text x="{x0 + week * col_w + col_w / 2:.1f}" y="{y0 + weekday * row_h + 12}" '
                     f'fill="{COLORS[level]}"{twinkle}>{CHARS[level]}</text>')
    body.append(f'<g class="c" style="animation-delay:{week * .03:.2f}s">{"".join(cells)}</g>')

labels, last_month, last_col = [], None, -9
for week in range(weeks):
    first = min((days[week, d][0] for d in range(7) if (week, d) in days), default=None)
    if first and first.month != last_month:
        if week - last_col >= 3 and week < weeks - 2:
            labels.append(f'<text x="{x0 + week * col_w:.1f}" y="{y0 - 12}" font-size="11" fill="#8c8c8c">{MONTHS[first.month - 1]}</text>')
            last_col = week
        last_month = first.month
for weekday, name in ((1, 'seg'), (3, 'qua'), (5, 'sex')):
    labels.append(f'<text x="28" y="{y0 + weekday * row_h + 11}" font-size="11" fill="#5c5c5c">{name}</text>')

legend = ''.join(f'<tspan fill="{color}">{char} </tspan>' for char, color in zip(CHARS, COLORS))
grid_w = weeks * col_w
total_label = f'{total:,}'.replace(',', '.')
title = f'{total_label} contribuições no último ano, desenhadas em ASCII'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t" xml:space="preserve">
<title id="t">{escape(title)}</title>
<style>
text{{font-family:{MONO}}}
.g text{{font-size:13px;text-anchor:middle}}
.c{{opacity:0;animation:in .5s ease forwards}}
@keyframes in{{from{{opacity:0}}to{{opacity:1}}}}
.tw{{animation:tw 6s steps(1,end) infinite}}
@keyframes tw{{0%{{opacity:.15}}4%{{opacity:1}}8%{{opacity:.35}}10%,100%{{opacity:1}}}}
.sc{{animation:sc 7s linear 2s infinite;opacity:0}}
@keyframes sc{{0%{{transform:translateX(0);opacity:1}}100%{{transform:translateX({grid_w:.0f}px);opacity:1}}}}
</style>
<defs>
  <pattern id="sl" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="1" fill="#fff" fill-opacity=".025"/></pattern>
  <linearGradient id="band"><stop stop-color="#fff" stop-opacity="0"/><stop offset=".7" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#fff" stop-opacity=".14"/></linearGradient>
</defs>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="#0a0a0a" stroke="#242424"/>
<text x="20" y="25" font-size="11" fill="#8c8c8c">~/contribuições</text>
<text x="{W - 20}" y="25" font-size="11" fill="#8c8c8c" text-anchor="end">{total_label} no último ano</text>
<path d="M1 38H{W - 1}" stroke="#1a1a1a"/>
{''.join(labels)}
<g class="g">{''.join(body)}</g>
<rect class="sc" x="{x0 - 60}" y="{y0 - 4}" width="60" height="{7 * row_h + 4}" fill="url(#band)"/>
<text x="28" y="{H - 18}" font-size="11" fill="#4a4a4a">atualizado em {date.today():%d/%m/%Y}</text>
<text x="{W - 32}" y="{H - 18}" font-size="12" text-anchor="end"><tspan fill="#5c5c5c">menos </tspan>{legend}<tspan fill="#5c5c5c">mais</tspan></text>
<rect width="{W}" height="{H}" rx="6" fill="url(#sl)"/>
</svg>
'''
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(svg, encoding='utf-8')
print(f'{out}: {weeks} semanas, {total} contribuições')
