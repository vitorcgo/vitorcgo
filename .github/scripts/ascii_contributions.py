"""Desenha o gráfico de contribuições do GitHub em ASCII, como um SVG animado.

Uso: python3 .github/scripts/ascii_contributions.py USUARIO SAIDA.svg
Só biblioteca padrão; lê a página pública de contribuições do perfil.
"""
import json
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

try:
    request = urllib.request.Request(f'https://api.github.com/users/{user}', headers={'User-Agent': 'Mozilla/5.0'})
    profile = json.load(urllib.request.urlopen(request, timeout=30))
except Exception:
    profile = {}

# sequências em dias seguidos com contribuição; hoje sem nada ainda não quebra a atual
levels = [level for _, level in sorted(days.values())]
longest = run = 0
for level in levels:
    run = run + 1 if level else 0
    longest = max(longest, run)
current = 0
for level in reversed(levels[:-1] if levels and not levels[-1] else levels):
    if not level:
        break
    current += 1

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
CHARS = '·:+#@'
COLORS = ['#3a3a3a', '#6b6b6b', '#a3a3a3', '#d6d6d6', '#ffffff']
MONTHS = 'jan fev mar abr mai jun jul ago set out nov dez'.split()
W, H = 880, 304
weeks = max(week for week, _ in days) + 1
x0, y0, row_h = 84, 134, 20
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
        cells.append(f'<text x="{x0 + week * col_w + col_w / 2:.1f}" y="{y0 + weekday * row_h + 15}" '
                     f'fill="{COLORS[level]}"{twinkle}>{CHARS[level]}</text>')
    body.append(f'<g class="c" style="animation-delay:{week * .03:.2f}s">{"".join(cells)}</g>')

labels, last_month, last_col = [], None, -9
for week in range(weeks):
    first = min((days[week, d][0] for d in range(7) if (week, d) in days), default=None)
    if first and first.month != last_month:
        if week - last_col >= 3 and week < weeks - 2:
            labels.append(f'<text x="{x0 + week * col_w:.1f}" y="{y0 - 14}" font-size="14" fill="#a6a6a6">{MONTHS[first.month - 1]}</text>')
            last_col = week
        last_month = first.month
for weekday, name in ((1, 'seg'), (3, 'qua'), (5, 'sex')):
    labels.append(f'<text x="28" y="{y0 + weekday * row_h + 15}" font-size="14" fill="#7a7a7a">{name}</text>')

legend = ''.join(f'<tspan fill="{color}">{char} </tspan>' for char, color in zip(CHARS, COLORS))
grid_w = weeks * col_w
total_label = f'{total:,}'.replace(',', '.')
stats = [f'{total_label} contribuições no último ano']
if 'followers' in profile:
    stats += [f'{profile["followers"]} seguidores', f'{profile["public_repos"]} repositórios']
stats += [f'sequência atual {current} {"dia" if current == 1 else "dias"}', f'maior {longest} dias']
title = ' · '.join(stats) + ', desenhado em ASCII'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t" xml:space="preserve">
<title id="t">{escape(title)}</title>
<style>
text{{font-family:{MONO}}}
.g text{{font-size:18px;text-anchor:middle}}
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
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="8" fill="#0a0a0a" stroke="#2a2a2a"/>
<text x="24" y="29" font-size="14" fill="#a6a6a6">[04] ~/contribuições</text>
<text x="{W - 24}" y="29" font-size="14" fill="#a6a6a6" text-anchor="end">{escape(' · '.join(stats[1:3]))}</text>
<text x="28" y="86" font-size="17"><tspan fill="#f2f2f2">{total_label}</tspan><tspan fill="#a6a6a6"> no último ano  ·  sequência atual </tspan><tspan fill="#f2f2f2">{current}</tspan><tspan fill="#a6a6a6">  ·  maior </tspan><tspan fill="#f2f2f2">{longest}</tspan><tspan fill="#a6a6a6"> dias</tspan></text>
<path d="M1 46H{W - 1}" stroke="#1c1c1c"/>
{''.join(labels)}
<g class="g">{''.join(body)}</g>
<rect class="sc" x="{x0 - 60}" y="{y0 - 4}" width="60" height="{7 * row_h + 4}" fill="url(#band)"/>
<text x="28" y="{H - 22}" font-size="14" fill="#7a7a7a">atualizado em {date.today():%d/%m/%Y}</text>
<text x="{W - 32}" y="{H - 22}" font-size="15" text-anchor="end"><tspan fill="#7a7a7a">menos </tspan>{legend}<tspan fill="#7a7a7a">mais</tspan></text>
<rect width="{W}" height="{H}" rx="6" fill="url(#sl)"/>
</svg>
'''
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(svg, encoding='utf-8')
print(f'{out}: {weeks} semanas, {total} contribuições')
