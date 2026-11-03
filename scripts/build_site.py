#!/usr/bin/env python3
"""Generate the complete static gallery. Python standard library only.

Assets are already committed; image generation/preparation is NOT part of deploy.
Optionally set SITE_URL to the confirmed public URL to add canonical/social tags.
"""
from pathlib import Path
import html
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'

def escape(value):
    return html.escape(str(value), quote=True)

def build():
    scenes = json.loads((PUBLIC / 'data/scenes.json').read_text(encoding='utf-8'))
    if [scene['number'] for scene in scenes] != list(range(1, 20)):
        raise ValueError('Exactly 19 scenes in sequence are required.')
    cards = []
    options = []
    for scene in scenes:
        number = scene['number']
        for key in ('thumbnail', 'image', 'download'):
            path = PUBLIC / scene[key]
            if not path.is_file() or path.stat().st_size == 0:
                raise ValueError(f'Missing asset: {path}')
        number_text = f'{number:02d}'
        scene_id = f'cena-{number_text}'
        title = escape(scene['title'])
        alt = escape(f'Cena {number}: {scene["title"]} — referência colorida')
        options.append(f'<option value="{scene_id}">{number_text} — {title}</option>')
        cards.append(f'''<article class="scene-card" id="{scene_id}" data-page="{scene['page']}" data-width="{scene['width']}" data-height="{scene['height']}" aria-labelledby="titulo-{scene_id}">
  <a class="scene-image-link" href="{escape(scene['image'])}" aria-label="Ampliar ilustração da cena {number}: {title}">
    <img src="{escape(scene['thumbnail'])}" alt="{alt}" width="{scene['width']}" height="{scene['height']}" loading="lazy" decoding="async">
    <span class="enlarge-label" aria-hidden="true">⤢ Ampliar</span>
  </a>
  <div class="scene-body">
    <div class="scene-meta"><span>Cena {number_text}</span><span class="page-reference">Página {scene['page']} do livro</span></div>
    <h3 id="titulo-{scene_id}">{title}</h3>
    <div class="card-footer"><a class="download-link" href="{escape(scene['download'])}" download="{escape(scene['filename'])}" aria-label="Baixar referência colorida da cena {number}: {title}"><span aria-hidden="true">↓</span> Baixar referência</a><span class="file-type">PNG ORIGINAL</span></div>
  </div>
</article>''')
    site_file = ROOT / 'site-settings.json'
    settings = json.loads(site_file.read_text()) if site_file.exists() else {}
    site_url = (os.environ.get('SITE_URL') or settings.get('siteUrl', '')).strip()
    metadata = ''
    if site_url:
        from urllib.parse import urlparse, urljoin
        parsed = urlparse(site_url)
        if parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('SITE_URL must be a real public HTTPS base URL without credentials, query or fragment.')
        if parsed.hostname in ('localhost', '127.0.0.1'):
            raise ValueError('An internal URL cannot be used as public metadata.')
        site_url = site_url.rstrip('/') + '/'
        image_url = urljoin(site_url, 'assets/capa.jpg')
        metadata = f'''<link rel="canonical" href="{escape(site_url)}">
  <meta property="og:url" content="{escape(site_url)}">
  <meta property="og:image" content="{escape(image_url)}">
  <meta property="og:image:alt" content="Capa de O Natal que Pintamos Juntos, de Eliane Tomás">
  <meta name="twitter:title" content="Um Natal com as suas cores">
  <meta name="twitter:description" content="As 19 referências coloridas do livro de Eliane Tomás.">
  <meta name="twitter:image" content="{escape(image_url)}">'''
        (PUBLIC / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{escape(site_url)}</loc></url></urlset>\n')
    source = (ROOT / 'templates/index.html').read_text(encoding='utf-8')
    output = source.replace('{{SCENE_CARDS}}', '\n'.join(cards)).replace('{{SCENE_OPTIONS}}', '\n'.join(options)).replace('{{PUBLIC_METADATA}}', metadata)
    if '{{' in output:
        raise ValueError('Unresolved template marker')
    (PUBLIC / 'index.html').write_text(output, encoding='utf-8')
    (PUBLIC / '.nojekyll').touch()
    (PUBLIC / 'manus-routes.json').write_text(json.dumps({'routes': [{'path': '/', 'title': 'Referências coloridas — O Natal que Pintamos Juntos'}]}, ensure_ascii=False) + '\n')
    print(f'Generated public/index.html: {len(scenes)} scenes; public URL: {site_url or "not configured"}')

if __name__ == '__main__':
    try:
        build()
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
