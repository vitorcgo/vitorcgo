"""Build the README's outlined SVGs: python tools/build-readme-assets.py FONT.ttf.

Requires fonttools. The font is Space Grotesk (OFL; license in src/readme).
Text is converted to paths so GitHub does not need to load a web font.
"""
from pathlib import Path
import sys
import base64
from html import escape
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import xml.etree.ElementTree as ET

font = TTFont(sys.argv[1])
glyphs = font.getGlyphSet()
cmap = font.getBestCmap()
units = font['head'].unitsPerEm
out = Path(__file__).resolve().parents[1] / 'src' / 'readme'
out.mkdir(parents=True, exist_ok=True)


def text(value, x, y, size, color):
    scale = size / units
    parts = []
    for char in value:
        name = cmap.get(ord(char), '.notdef')
        glyph = glyphs[name]
        pen = SVGPathPen(glyphs)
        glyph.draw(pen)
        parts.append(f'<path d="{pen.getCommands()}" transform="translate({x:.3f} {y}) scale({scale:.6f} {-scale:.6f})"/>')
        x += glyph.width * scale
    return f'<g fill="{color}">{"".join(parts)}</g>'


def svg(name, width, height, label, content):
    (out / name).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">\n'
        f'<title id="title">{escape(label)}</title>\n{content}\n</svg>\n', encoding='utf-8')


logo = base64.b64encode((out / 'aylo-logo.png').read_bytes()).decode('ascii')
svg('aylo-mark.svg', 80, 80, 'Logo do aylo.me',
    '<rect width="80" height="80" rx="18" fill="#10181c"/>'
    f'<image href="data:image/png;base64,{logo}" x="13" y="13" width="54" height="54"/>')

svg('aylo-card.svg', 480, 180,
    'aylo.me · Plataforma de link-in-bio · mais de 5.000 usuários · Em produção · Visitar plataforma', '''
<defs>
  <linearGradient id="surface" x2="1" y2="1"><stop stop-color="#172e29"/><stop offset=".55" stop-color="#101d20"/><stop offset="1" stop-color="#0f171c"/></linearGradient>
  <linearGradient id="edge"><stop stop-color="#6ee7b7" stop-opacity="0"/><stop offset=".5" stop-color="#6ee7b7" stop-opacity=".75"/><stop offset="1" stop-color="#6ee7b7" stop-opacity="0"/></linearGradient>
</defs>
<rect x=".5" y=".5" width="479" height="179" rx="18" fill="url(#surface)" stroke="#345148"/>
<path d="M24 1H456" stroke="url(#edge)"/>
<path d="M376 0 480 60M410 0 480 40M444 0 480 20" fill="none" stroke="#6ee7b7" stroke-opacity=".06"/>
<rect x="24" y="28" width="72" height="72" rx="20" fill="#19352d" stroke="#365a4b"/>
''' + f'<image href="data:image/png;base64,{logo}" x="35" y="39" width="50" height="50"/>'
    + text('aylo.me', 112, 59, 30, '#f2faf6')
    + text('Plataforma de link-in-bio', 113, 85, 13, '#a4bcb5')
    + '<path d="M332 35V93" stroke="#365148"/>'
    + text('5.000+', 351, 61, 26, '#93f1c8')
    + text('usuários', 358, 83, 13, '#a4bcb5')
    + '<path d="M24 116H456" stroke="#2a4139"/>'
    + '<circle cx="31" cy="148" r="7" fill="#6ee7b7" fill-opacity=".1"/><circle cx="31" cy="148" r="3" fill="#6ee7b7"/>'
    + text('Em produção', 47, 153, 13, '#bcd6cb')
    + '<rect x="280" y="132" width="176" height="32" rx="8" fill="#91edc5"/>'
    + text('Visitar plataforma', 296, 153, 13, '#102b22')
    + '<path d="M431 143H438V150M430 151 438 143" fill="none" stroke="#102b22" stroke-width="1.5"/>')


name_width = sum(glyphs[cmap[ord(c)]].width for c in 'Vitor Cavalcante Gomes') * 28 / units
group_x = (640 - 88 - name_width) / 2
svg('signature.svg', 640, 116, 'Vitor Cavalcante Gomes · Desenvolvedor Full Stack · São Paulo · BR', '''
<defs>
  <linearGradient id="top" x2="1" y2="1"><stop stop-color="#b4ffe2"/><stop offset="1" stop-color="#57cea4"/></linearGradient>
  <linearGradient id="side" x2="0" y2="1"><stop stop-color="#398b71"/><stop offset="1" stop-color="#163c33"/></linearGradient>
  <linearGradient id="surface" x2="1" y2="1"><stop stop-color="#142624"/><stop offset=".6" stop-color="#10181c"/><stop offset="1" stop-color="#0d1519"/></linearGradient>
  <linearGradient id="accent"><stop stop-color="#6ee7b7" stop-opacity="0"/><stop offset=".5" stop-color="#6ee7b7" stop-opacity=".8"/><stop offset="1" stop-color="#6ee7b7" stop-opacity="0"/></linearGradient>
</defs>
<rect x="0.5" y="0.5" width="639" height="115" rx="16" fill="url(#surface)" stroke="#304740"/>
<path d="M32 1H608M32 115H608" stroke="url(#accent)"/>
<g fill="none" stroke="#6ee7b7" stroke-opacity=".06"><path d="M500 0 640 80M540 0 640 58M580 0 640 36M0 80 64 116M0 102 24 116"/></g>
''' + f'<g transform="translate({group_x-23:.3f} 4)">' + '''
<path d="M25 78 55 61 85 78 55 95Z" fill="#6ee7b7" opacity=".07"/>
<path d="M27 48 55 32 83 48 55 64Z" fill="url(#top)"/>
<path d="M27 48 55 64 55 83 27 67Z" fill="#286c58"/>
<path d="M55 64 83 48 83 67 55 83Z" fill="url(#side)"/>
<path d="M27 48 55 64 83 48M55 64V83" fill="none" stroke="#c2ffe6" stroke-opacity=".5"/>
<path d="M27 30 55 14 83 30 55 46Z" fill="#6ee7b7" fill-opacity=".08" stroke="#6ee7b7" stroke-opacity=".7"/>
</g>
''' + text('Vitor Cavalcante Gomes', group_x+88, 47, 28, '#eef6f4')
    + text('Desenvolvedor Full Stack', group_x+89, 73, 15, '#91e4c3')
    + text('São Paulo · BR', group_x+89, 94, 12, '#a6b9b6'))

buttons = [
    ('portfolio', 'Portfólio', 'globe2', '#8cf0c7'),
    ('linkedin', 'LinkedIn', 'linkedin', '#79b8ff'),
    ('email', 'Email', 'envelope', '#eac699'),
    ('whatsapp', 'WhatsApp', 'whatsapp', '#73e5a1'),
    ('instagram', 'Instagram', 'instagram', '#e9a5d5'),
    ('github', 'GitHub', 'github', '#dbe8ed'),
]
for slug, label, icon_name, color in buttons:
    icon = ET.parse(out / 'icons' / f'{icon_name}.svg').getroot()
    icon_body = ''.join(ET.tostring(child, encoding='unicode') for child in icon)
    label_width = sum(glyphs[cmap[ord(c)]].width for c in label) * 12 / units
    svg(f'link-{slug}.svg', 112, 70, label,
        '<rect x="1" y="1" width="110" height="64" rx="8" fill="#101b1e" stroke="#30413f"/>'
        f'<path d="M35 1H77" stroke="{color}" stroke-opacity=".7"/>'
        f'<svg x="46" y="12" width="20" height="20" viewBox="0 0 16 16" fill="{color}">{icon_body}</svg>'
        '<path d="M94 12H99V17M94 17 99 12" fill="none" stroke="#6c8380" stroke-width="1"/>'
        + text(label, (112-label_width)/2, 52, 12, '#e5efed'))

stacks = [
    ('react', 'React', '#61dafb'), ('nextjs', 'Next.js', '#edf2f5'),
    ('typescript', 'TypeScript', '#62a7f8'), ('tailwind', 'Tailwind', '#38bdf8'),
    ('vue', 'Vue.js', '#4fc08d'), ('node', 'Node.js', '#77bb68'),
    ('laravel', 'Laravel', '#ff706b'), ('php', 'PHP', '#aaa3ed'),
    ('java', 'Java', '#f3ad6a'), ('spring', 'Spring', '#94cf67'),
    ('postgresql', 'PostgreSQL', '#83b8e5'), ('supabase', 'Supabase', '#3fcf8e'),
    ('mysql', 'MySQL', '#67b6d5'), ('python', 'Python', '#ffd43b'),
    ('cloudflare', 'Cloudflare', '#f7a652'), ('git', 'Git', '#f7816f'),
    ('figma', 'Figma', '#c4a2ff'),
    ('websockets', 'WebSockets', '#c1d5e2'),
]
for slug, label, color in stacks:
    width = max(80, round(sum(glyphs[cmap[ord(c)]].width for c in label) * 13 / units) + 40)
    svg(f'{slug}.svg', width, 32, label,
        f'<rect x=".5" y=".5" width="{width-1}" height="31" rx="8" fill="#10181c" stroke="#2b393d"/>'
        f'<circle cx="15" cy="16" r="3" fill="{color}"/>' + text(label, 27, 21, 13, '#e5efed'))

svg('private-repository.svg', 168, 26, 'Repositório privado',
    '<rect x=".5" y=".5" width="167" height="25" rx="6" fill="#10181c" stroke="#2b393d"/>'
    '<g fill="none" stroke="#9eb4ae" stroke-width="1.2"><rect x="12" y="11" width="9" height="8" rx="1.5"/>'
    '<path d="M14 11V8a2.5 2.5 0 0 1 5 0v3"/><path d="M16.5 14V16"/></g>'
    + text('Repositório privado', 30, 17, 12, '#acbcb7'))

svg('spotify.svg', 164, 32, 'Ouvir no Spotify',
    '<rect x=".5" y=".5" width="163" height="31" rx="16" fill="#10181c" stroke="#2b393d"/>'
    '<circle cx="18" cy="16" r="10" fill="#1ed760"/>'
    '<g fill="none" stroke="#10181c" stroke-linecap="round"><path d="M12 13Q18 10 24 14" stroke-width="1.8"/>'
    '<path d="M13 16Q18 14 23 17" stroke-width="1.5"/><path d="M14 19Q18 17.5 22 20" stroke-width="1.3"/></g>'
    + text('Ouvir no Spotify', 35, 20, 12, '#e5efed'))
