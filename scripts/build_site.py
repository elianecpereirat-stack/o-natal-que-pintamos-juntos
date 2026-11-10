#!/usr/bin/env python3
"""Generate the static Portuguese and American English coloring-guide pages."""
from pathlib import Path
import html
import json
import os
import re
import sys
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'


def escape(value):
    return html.escape(str(value), quote=True)


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate_site_url(site_url):
    parsed = urlparse(site_url)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('SITE_URL must be a real public HTTPS base URL without credentials, query or fragment.')
    if parsed.hostname in ('localhost', '127.0.0.1'):
        raise ValueError('An internal URL cannot be used as public metadata.')
    return site_url.rstrip('/') + '/'


def public_metadata(language, page_url, site_url):
    image_url = urljoin(site_url, 'assets/capa.jpg')
    if language == 'en':
        title = 'The Christmas We Painted Together | Eliane Tomás'
        description = 'A Christmas story to read together, with illustrations to color and a final page for children to draw their own holiday memory.'
        image_alt = 'Cover art from the original Portuguese edition of The Christmas We Painted Together.'
    else:
        title = 'O Natal que Pintamos Juntos | Eliane Tomás'
        description = 'Uma história de Natal para ler em família, com ilustrações para colorir e espaço para a criança desenhar sua própria memória.'
        image_alt = 'Capa de O Natal que Pintamos Juntos, de Eliane Tomás.'
    portuguese_url = site_url
    english_url = urljoin(site_url, 'en/')
    return f'''<link rel="canonical" href="{escape(page_url)}">
  <link rel="alternate" hreflang="pt-BR" href="{escape(portuguese_url)}">
  <link rel="alternate" hreflang="en-US" href="{escape(english_url)}">
  <link rel="alternate" hreflang="x-default" href="{escape(portuguese_url)}">
  <meta property="og:url" content="{escape(page_url)}">
  <meta property="og:image" content="{escape(image_url)}">
  <meta property="og:image:alt" content="{escape(image_alt)}">
  <meta name="twitter:title" content="{escape(title)}">
  <meta name="twitter:description" content="{escape(description)}">
  <meta name="twitter:image" content="{escape(image_url)}">'''


def language_script(language):
    if language == 'en':
        return '''<script>
  (() => {
    try {
      const requested = new URLSearchParams(window.location.search).get('lang');
      if (requested === 'pt' || requested === 'en') localStorage.setItem('natal-page-language', requested);
    } catch (_) {}
  })();
</script>'''
    return '''<script>
  (() => {
    const key = 'natal-page-language';
    const readSaved = () => { try { return localStorage.getItem(key); } catch (_) { return null; } };
    const save = value => { try { localStorage.setItem(key, value); } catch (_) {} };
    const requested = new URLSearchParams(window.location.search).get('lang');
    if (requested === 'pt' || requested === 'en') save(requested);
    const saved = readSaved();
    const languages = Array.from(navigator.languages || []);
    if (!languages.length && navigator.language) languages.push(navigator.language);
    const firstSupported = languages.find(value => /^(en|pt)(-|$)/i.test(value)) || '';
    const browserLanguage = /^en(-|$)/i.test(firstSupported) ? 'en' : 'pt';
    const selected = requested === 'pt' || requested === 'en' ? requested :
      (saved === 'pt' || saved === 'en' ? saved : browserLanguage);
    if (selected === 'en') window.location.replace(new URL('en/', window.location.href).href);
  })();
</script>'''


def language_switch(language):
    if language == 'en':
        return '''<nav class="language-switch" aria-label="Choose language">
        <a href="../?lang=pt" lang="pt-BR">PT</a><span aria-hidden="true">/</span><a class="is-active" href="./?lang=en" lang="en-US" aria-current="page">EN</a>
      </nav>'''
    return '''<nav class="language-switch" aria-label="Selecionar idioma">
        <a class="is-active" href="./?lang=pt" lang="pt-BR" aria-current="page">PT</a><span aria-hidden="true">/</span><a href="en/?lang=en" lang="en-US">EN</a>
      </nav>'''


def english_purchase_cta(url):
    if not url:
        return ''
    parsed = urlparse(url)
    if parsed.scheme != 'https' or not parsed.hostname or 'amazon.' not in parsed.hostname or parsed.username or parsed.password:
        raise ValueError('amazonEnglishUrl must be an Amazon HTTPS URL.')
    return f'<a class="book-link" href="{escape(url)}" target="_blank" rel="noopener noreferrer">Discover the book on Amazon <span aria-hidden="true">↗</span></a>'


def render_cards(scenes, language, prefix):
    cards = []
    options = []
    for scene in scenes:
        number = scene['number']
        number_text = f'{number:02d}'
        scene_id = f'cena-{number_text}'
        title = escape(scene['title'])
        if language == 'en':
            alt = escape(f'Scene {number}: {scene["title"]} — color reference')
            image_label = escape(f'Enlarge scene {number}: {scene["title"]}')
            scene_label = f'Scene {number_text}'
            page_label = f"Page {scene['page']} in the book"
            download_label = escape(f'Download color reference for scene {number}: {scene["title"]}')
            download_text = 'Download reference'
            file_type = 'ORIGINAL PNG'
            filename = f'The-Christmas-We-Painted-Together-scene-{number_text}.png'
            option_text = f'{number_text} — {title}'
        else:
            alt = escape(f'Cena {number}: {scene["title"]} — referência colorida')
            image_label = escape(f'Ampliar ilustração da cena {number}: {scene["title"]}')
            scene_label = f'Cena {number_text}'
            page_label = f"Página {scene['page']} do livro"
            download_label = escape(f'Baixar referência colorida da cena {number}: {scene["title"]}')
            download_text = 'Baixar referência'
            file_type = 'PNG ORIGINAL'
            filename = scene['filename']
            option_text = f'{number_text} — {title}'
        options.append(f'<option value="{scene_id}">{option_text}</option>')
        image_path = escape(prefix + scene['image'])
        thumbnail_path = escape(prefix + scene['thumbnail'])
        download_path = escape(prefix + scene['download'])
        cards.append(f'''<article class="scene-card" id="{scene_id}" data-page="{scene['page']}" data-width="{scene['width']}" data-height="{scene['height']}" aria-labelledby="titulo-{scene_id}">
  <a class="scene-image-link" href="{image_path}" aria-label="{image_label}">
    <img src="{thumbnail_path}" alt="{alt}" width="{scene['width']}" height="{scene['height']}" loading="lazy" decoding="async">
    <span class="enlarge-label" aria-hidden="true">⤢ {'Enlarge' if language == 'en' else 'Ampliar'}</span>
  </a>
  <div class="scene-body">
    <div class="scene-meta"><span>{scene_label}</span><span class="page-reference">{page_label}</span></div>
    <h3 id="titulo-{scene_id}">{title}</h3>
    <div class="card-footer"><a class="download-link" href="{download_path}" download="{escape(filename)}" aria-label="{download_label}"><span aria-hidden="true">↓</span> {download_text}</a><span class="file-type">{file_type}</span></div>
  </div>
</article>''')
    return '\n'.join(cards), '\n'.join(options)


def render_page(template_path, language, scenes, settings, site_url):
    prefix = '../' if language == 'en' else ''
    page_url = urljoin(site_url, 'en/') if language == 'en' else site_url
    cards, options = render_cards(scenes, language, prefix)
    metadata = public_metadata(language, page_url, site_url) if site_url else ''
    replacements = {
        '{{PUBLIC_METADATA}}': metadata,
        '{{LANGUAGE_SCRIPT}}': language_script(language),
        '{{LANGUAGE_SWITCH}}': language_switch(language),
        '{{ASSET_PREFIX}}': prefix,
        '{{SCENE_CARDS}}': cards,
        '{{SCENE_OPTIONS}}': options,
    }
    if language == 'en':
        english_url = settings.get('amazonEnglishUrl', '').strip()
        purchase = english_purchase_cta(english_url)
        replacements['{{ENGLISH_BUY_LINK_TOP}}'] = purchase or '<p class="book-link-pending">The English edition is in preparation.</p>'
        replacements['{{ENGLISH_BUY_LINK_BOTTOM}}'] = purchase
    output = template_path.read_text(encoding='utf-8')
    for marker, value in replacements.items():
        output = output.replace(marker, value)
    if re.search(r'\{\{[A-Z_]+\}\}', output):
        raise ValueError(f'Unresolved template marker in {template_path}')
    return output


def build():
    pt_scenes = load_json(PUBLIC / 'data/scenes.json')
    en_titles = load_json(PUBLIC / 'data/scenes.en.json')
    if [scene['number'] for scene in pt_scenes] != list(range(1, 20)):
        raise ValueError('Exactly 19 Portuguese scenes in sequence are required.')
    if [scene['number'] for scene in en_titles] != list(range(1, 20)):
        raise ValueError('Exactly 19 English scene titles in sequence are required.')
    en_title_by_number = {scene['number']: scene['title'] for scene in en_titles}
    en_scenes = []
    for scene in pt_scenes:
        for key in ('thumbnail', 'image', 'download'):
            path = PUBLIC / scene[key]
            if not path.is_file() or path.stat().st_size == 0:
                raise ValueError(f'Missing asset: {path}')
        en_scene = dict(scene)
        en_scene['title'] = en_title_by_number[scene['number']]
        en_scenes.append(en_scene)

    settings_path = ROOT / 'site-settings.json'
    settings = load_json(settings_path) if settings_path.exists() else {}
    site_url = (os.environ.get('SITE_URL') or settings.get('siteUrl', '')).strip()
    if site_url:
        site_url = validate_site_url(site_url)

    pt_output = render_page(ROOT / 'templates/index.html', 'pt', pt_scenes, settings, site_url)
    en_output = render_page(ROOT / 'templates/index.en.html', 'en', en_scenes, settings, site_url)
    (PUBLIC / 'index.html').write_text(pt_output, encoding='utf-8')
    english_dir = PUBLIC / 'en'
    english_dir.mkdir(parents=True, exist_ok=True)
    (english_dir / 'index.html').write_text(en_output, encoding='utf-8')
    (PUBLIC / '.nojekyll').touch()

    if site_url:
        sitemap_urls = [site_url, urljoin(site_url, 'en/')]
        entries = ''.join(f'<url><loc>{escape(url)}</loc></url>' for url in sitemap_urls)
        (PUBLIC / 'sitemap.xml').write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f'{entries}</urlset>\n', encoding='utf-8'
        )

    routes = {'routes': [
        {'path': '/', 'title': 'O Natal que Pintamos Juntos — Eliane Tomás'},
        {'path': '/en/', 'title': 'The Christmas We Painted Together — Eliane Tomás'},
    ]}
    (PUBLIC / 'manus-routes.json').write_text(json.dumps(routes, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Generated Portuguese and English pages: 19 scenes each; base URL: {site_url or "not configured"}')


if __name__ == '__main__':
    try:
        build()
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
