#!/usr/bin/env python3
"""Prepare static gallery assets for O Natal que Pintamos Juntos.

The process is intentionally deterministic and non-creative:

* select the 19 approved color scene PNGs from the source book directory;
* copy each original PNG byte-for-byte to public/assets/downloads/;
* make aspect-preserving WebP display images (longest side <= 1600, quality 88);
* make aspect-preserving 560px-wide WebP thumbnails (quality 84);
* parse scene titles from the editorial ``#### N. Title — páginas ...`` headings;
* write public/data/scenes.json with relative paths for GitHub Pages subdirectories;
* copy the local Nunito/Fredoka TTFs and their OFL license files;
* make the requested cover JPEG, footer star copy, and 96px PNG favicon.

Run from any directory:

    python3 scripts/prepare_assets.py
    python3 scripts/prepare_assets.py --source-root /path/to/livro-0db6350d

The output root is always the project root (the parent of this scripts/
directory), so the script cannot accidentally write outside the project asset,
data, and script areas.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Iterable

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = Path("/home/ubuntu/projects/livro-0db6350d")
EDITORIAL_NAME = "Roteiro_editorial_O_Natal_que_Pintamos_Juntos_v1.md"

# Approved scene source selection.  Keep these paths relative to source-root.
SCENE_SOURCES: dict[int, str] = {
    1: "Cena_01_referencia_colorida_v3.png",
    2: "Cena_02_referencia_colorida_v1.png",
    3: "Cena_03_referencia_colorida_v1.png",
    4: "Cena_04_referencia_colorida_v1.png",
    5: "Cena_05_referencia_colorida_v1.png",
    6: "Ilustracao_piloto_cena_06_referencia_colorida_v1.png",
    7: "Cena_07_referencia_colorida_v1.png",
    8: "Cena_08_referencia_colorida_v1.png",
    9: "Cena_09_referencia_colorida_v1.png",
    10: "Cena_10_referencia_colorida_v1.png",
    11: "Cena_11_referencia_colorida_v1.png",
    12: "Cena_12_referencia_colorida_v4.png",
    13: "Cena_13_referencia_colorida_v1.png",
    14: "Cena_14_referencia_colorida_v1.png",
    15: "Cena_15_referencia_colorida_v1.png",
    16: "Cena_16_referencia_colorida_v5.png",
    17: "Cena_17_referencia_colorida_v1.png",
    18: "Cena_18_referencia_colorida_v1.png",
    19: "Cena_19_referencia_colorida_v1.png",
}

HEADING_RE = re.compile(
    r"^####\s+(?P<number>\d+)\.\s+(?P<title>.+?)\s+—\s+páginas\b",
    re.MULTILINE,
)


class PreparationError(RuntimeError):
    """Raised when a required source or verification check is missing."""


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file without loading it all at once."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(path: Path) -> Path:
    if not path.is_file():
        raise PreparationError(f"Required source file is missing: {path}")
    return path


def copy_checked(source: Path, destination: Path) -> int:
    """Copy source byte-for-byte and verify size plus SHA-256 afterwards."""
    require_file(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    source_hash = sha256_file(source)
    destination_hash = sha256_file(destination)
    source_size = source.stat().st_size
    destination_size = destination.stat().st_size
    if source_size != destination_size or source_hash != destination_hash:
        raise PreparationError(
            f"Byte-identical copy check failed: {source} -> {destination} "
            f"(source {source_size}/{source_hash}, destination "
            f"{destination_size}/{destination_hash})"
        )
    return destination_size


def checked_dimensions(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def resized_to_longest(image: Image.Image, longest: int) -> Image.Image:
    """Return a copy with its longest dimension at most ``longest``."""
    result = image.copy()
    result.thumbnail((longest, longest), Image.Resampling.LANCZOS)
    return result


def resized_to_width(image: Image.Image, width: int) -> Image.Image:
    """Return a copy with exact target width and a rounded proportional height."""
    if image.width <= 0 or image.height <= 0:
        raise PreparationError("Cannot resize an image with an empty dimension")
    height = max(1, round(image.height * width / image.width))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def save_scene_webp(source: Path, destination: Path, *, longest: int, quality: int) -> tuple[int, int, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as original:
        image = resized_to_longest(original, longest)
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
        image.save(destination, format="WEBP", quality=quality, method=6)
    return destination.stat().st_size, *checked_dimensions(destination)


def save_thumb_webp(source: Path, destination: Path, *, width: int, quality: int) -> tuple[int, int, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as original:
        image = resized_to_width(original, width)
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
        image.save(destination, format="WEBP", quality=quality, method=6)
    return destination.stat().st_size, *checked_dimensions(destination)


def save_cover_jpeg(source: Path, destination: Path, *, width: int, quality: int) -> tuple[int, int, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as original:
        image = resized_to_width(original.convert("RGB"), width)
        image.save(destination, format="JPEG", quality=quality, optimize=True)
    return destination.stat().st_size, *checked_dimensions(destination)


def save_favicon_png(source: Path, destination: Path, *, size: int) -> tuple[int, int, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as original:
        image = original.copy()
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        image.save(destination, format="PNG", optimize=True)
    return destination.stat().st_size, *checked_dimensions(destination)


def parse_titles(editorial: Path) -> dict[int, str]:
    text = require_file(editorial).read_text(encoding="utf-8")
    titles: dict[int, str] = {}
    for match in HEADING_RE.finditer(text):
        number = int(match.group("number"))
        title = match.group("title").strip()
        if number in titles:
            raise PreparationError(f"Duplicate scene heading in {editorial}: {number}")
        titles[number] = title
    expected = set(SCENE_SOURCES)
    if set(titles) != expected:
        missing = sorted(expected - set(titles))
        extra = sorted(set(titles) - expected)
        raise PreparationError(
            f"Editorial headings do not match scenes; missing={missing}, extra={extra}"
        )
    return titles


def iter_font_files(source_root: Path) -> Iterable[Path]:
    font_dir = source_root / "atividade_final" / "fonts"
    if not font_dir.is_dir():
        raise PreparationError(f"Required font directory is missing: {font_dir}")
    files = sorted(
        path
        for path in font_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() in {".ttf", ".txt"}
        and path.name in {
            "Nunito-Variable.ttf",
            "Fredoka-Variable.ttf",
            "Nunito-OFL.txt",
            "Fredoka-OFL.txt",
        }
    )
    expected = {
        "Nunito-Variable.ttf",
        "Fredoka-Variable.ttf",
        "Nunito-OFL.txt",
        "Fredoka-OFL.txt",
    }
    found = {path.name for path in files}
    if found != expected:
        raise PreparationError(
            f"Expected Nunito/Fredoka TTF and OFL files in {font_dir}; "
            f"missing={sorted(expected - found)}"
        )
    return files


def prepare(source_root: Path) -> dict[str, int]:
    source_root = source_root.expanduser().resolve()
    public = PROJECT_ROOT / "public"
    downloads = public / "assets" / "downloads"
    scenes_dir = public / "assets" / "scenes"
    thumbs_dir = public / "assets" / "thumbs"
    fonts_dir = public / "assets" / "fonts"
    data_dir = public / "data"

    titles = parse_titles(source_root / EDITORIAL_NAME)
    counts = {
        "scene_downloads": 0,
        "scene_display_webp": 0,
        "scene_thumbnails": 0,
        "font_and_license_copies": 0,
        "other_copies": 0,
    }
    bytes_written = 0
    metadata: list[dict[str, object]] = []

    for number in sorted(SCENE_SOURCES):
        scene = f"{number:02d}"
        source = require_file(source_root / SCENE_SOURCES[number])
        download = downloads / f"cena-{scene}.png"
        bytes_written += copy_checked(source, download)
        counts["scene_downloads"] += 1

        display = scenes_dir / f"cena-{scene}.webp"
        display_bytes, display_width, display_height = save_scene_webp(
            source, display, longest=1600, quality=88
        )
        bytes_written += display_bytes
        counts["scene_display_webp"] += 1

        thumbnail = thumbs_dir / f"cena-{scene}.webp"
        thumbnail_bytes, _, _ = save_thumb_webp(
            source, thumbnail, width=560, quality=84
        )
        bytes_written += thumbnail_bytes
        counts["scene_thumbnails"] += 1

        metadata.append(
            {
                "number": number,
                "title": titles[number],
                "page": 2 * number + 3,
                "thumbnail": f"assets/thumbs/cena-{scene}.webp",
                "image": f"assets/scenes/cena-{scene}.webp",
                "download": f"assets/downloads/cena-{scene}.png",
                "filename": f"O-Natal-que-Pintamos-Juntos-cena-{scene}.png",
                "width": display_width,
                "height": display_height,
            }
        )

    data_dir.mkdir(parents=True, exist_ok=True)
    scenes_json = data_dir / "scenes.json"
    scenes_json.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    bytes_written += scenes_json.stat().st_size

    for source in iter_font_files(source_root):
        destination = fonts_dir / source.name
        bytes_written += copy_checked(source, destination)
        counts["font_and_license_copies"] += 1

    star_source = source_root / "motivos_rodape" / "05_estrela.png"
    bytes_written += copy_checked(star_source, public / "assets" / "estrela.png")
    counts["other_copies"] += 1

    cover_source = source_root / "capa" / "conceitos" / "Conceito_B_Capa_Frontal_prova.png"
    cover_bytes, cover_width, cover_height = save_cover_jpeg(
        cover_source, public / "assets" / "capa.jpg", width=800, quality=88
    )
    bytes_written += cover_bytes
    counts["other_copies"] += 1

    favicon_bytes, favicon_width, favicon_height = save_favicon_png(
        star_source, public / "favicon.png", size=96
    )
    bytes_written += favicon_bytes
    counts["other_copies"] += 1

    print(f"source_root={source_root}")
    print(f"project_root={PROJECT_ROOT}")
    print(f"scenes={len(metadata)} display_dimensions={metadata[0]['width']}x{metadata[0]['height']}")
    print(f"thumbnail_dimensions={checked_dimensions(thumbs_dir / 'cena-01.webp')[0]}px-wide")
    print(f"cover={cover_width}x{cover_height} bytes={cover_bytes}")
    print(f"favicon={favicon_width}x{favicon_height} bytes={favicon_bytes}")
    print(f"counts={json.dumps(counts, sort_keys=True)}")
    print(f"bytes_written={bytes_written}")
    print("All byte-identical copies verified with SHA-256.")
    return {**counts, "bytes_written": bytes_written}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        type=Path,
        default=DEFAULT_SOURCE_ROOT,
        help=f"Original book source root (default: {DEFAULT_SOURCE_ROOT})",
    )
    args = parser.parse_args()
    prepare(args.source_root)


if __name__ == "__main__":
    main()
