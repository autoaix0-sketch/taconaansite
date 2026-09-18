#!/usr/bin/env python3
"""
Taco Naan - fabrication des visuels de marque.

Produit trois fichiers que le navigateur et les reseaux sociaux reclament, et
qu'aucun site serieux ne peut laisser manquants :

    assets/img/favicon.png          l'icone de l'onglet
    assets/img/apple-touch-icon.png l'icone quand on ajoute le site a l'ecran
    assets/img/og.jpg               l'apercu quand on partage le lien

Usage :  python tools/make_brand_assets.py
         python tools/make_brand_assets.py --fonts C:/chemin/vers/polices

Les polices de la marque (Instrument Serif, IBM Plex Mono) sont telechargees
automatiquement depuis Google Fonts si elles ne sont pas deja la. Elles ne sont
PAS stockees dans le projet : elles ne servent qu'a fabriquer ces trois images.
"""

from __future__ import annotations

import argparse
import random
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img"

# Palette relevee sur les panneaux affiches au comptoir (menu/*.png) : noir
# mat et jaune. Le site, la vitrine et l'image de partage disent la meme chose.
VOID = (10, 12, 12)
COAL = (17, 22, 21)
YELLOW = (255, 198, 26)
CREAM = (246, 242, 232)
MUTE = (155, 163, 159)
FAINT = (109, 117, 112)

FONT_URLS = {
    "InstrumentSerif.ttf":
        "https://github.com/google/fonts/raw/main/ofl/instrumentserif/InstrumentSerif-Regular.ttf",
    "PlexMono.ttf":
        "https://github.com/google/fonts/raw/main/ofl/ibmplexmono/IBMPlexMono-Medium.ttf",
}


def load_fonts(folder: Path) -> dict[str, Path]:
    folder.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, url in FONT_URLS.items():
        target = folder / name
        if not target.exists():
            print(f"  . telechargement de {name}")
            urllib.request.urlretrieve(url, target)
        paths[name] = target
    return paths


def grain(image: Image.Image, amount: float = 0.05) -> Image.Image:
    """Le meme grain que le site, pour que l'apercu ait la meme peau."""
    w, h = image.size
    noise = Image.new("L", (w, h))
    rnd = random.Random(40100)
    noise.putdata([rnd.gauss(128, 30) for _ in range(w * h)])
    noise = noise.filter(ImageFilter.GaussianBlur(0.4))
    return Image.blend(image, Image.merge("RGB", (noise, noise, noise)), amount)


# --------------------------------------------------------------------------
# Icones
# --------------------------------------------------------------------------

def make_icons(fonts: dict[str, Path]) -> None:
    """Le badge complet est illisible a 32 px : a cette taille on ne garde que
    le monogramme. C'est la seule facon d'avoir une icone reconnaissable dans
    un onglet."""
    size = 512
    icon = Image.new("RGB", (size, size), VOID)
    draw = ImageDraw.Draw(icon)

    # Le filet interieur, comme le cadre imprime du site.
    inset = int(size * 0.075)
    draw.rectangle([inset, inset, size - inset, size - inset],
                   outline=YELLOW, width=int(size * 0.018))

    serif = ImageFont.truetype(str(fonts["InstrumentSerif.ttf"]), int(size * 0.56))
    text = "TN"
    box = draw.textbbox((0, 0), text, font=serif)
    draw.text(((size - (box[2] - box[0])) / 2 - box[0],
               (size - (box[3] - box[1])) / 2 - box[1] - size * 0.02),
              text, font=serif, fill=YELLOW)

    icon.resize((180, 180), Image.LANCZOS).save(OUT / "apple-touch-icon.png")
    # Un PNG multi-tailles : le navigateur prend celle qui lui va.
    icon.resize((48, 48), Image.LANCZOS).save(
        OUT / "favicon.png", sizes=[(16, 16), (32, 32), (48, 48)])
    print("  + favicon.png, apple-touch-icon.png")


# --------------------------------------------------------------------------
# Image de partage
# --------------------------------------------------------------------------

def make_og(fonts: dict[str, Path]) -> None:
    W, H = 1200, 630
    card = Image.new("RGB", (W, H), VOID)
    draw = ImageDraw.Draw(card)

    serif = ImageFont.truetype(str(fonts["InstrumentSerif.ttf"]), 92)
    serif_em = ImageFont.truetype(str(fonts["InstrumentSerif.ttf"]), 92)
    mono_s = ImageFont.truetype(str(fonts["PlexMono.ttf"]), 21)
    mono_m = ImageFont.truetype(str(fonts["PlexMono.ttf"]), 26)

    margin = 64
    draw.rectangle([margin // 2, margin // 2, W - margin // 2, H - margin // 2],
                   outline=COAL, width=1)

    x = margin + 18
    y = 86

    draw.text((x, y), "DAX  ·  AVENUE SAINT-VINCENT DE PAUL",
              font=mono_s, fill=YELLOW)
    y += 56

    draw.text((x, y), "Kebab, naan, tacos.", font=serif, fill=CREAM)
    y += 96
    draw.text((x + 40, y), "Faits ici, à Dax.", font=serif_em, fill=YELLOW)
    y += 128

    draw.line([(x, y), (x + 300, y)], fill=COAL, width=1)
    y += 34

    draw.text((x, y), "SUR PLACE & À EMPORTER  ·  PAS DE LIVRAISON",
              font=mono_s, fill=MUTE)
    y += 40
    draw.text((x, y), "09 79 13 85 43", font=mono_m, fill=YELLOW)

    # Le tampon, pose a droite, legerement de travers.
    stamp_path = OUT / "logo-white-640.webp"
    if stamp_path.exists():
        stamp = Image.open(stamp_path).convert("RGBA")
        stamp.thumbnail((430, 430), Image.LANCZOS)
        stamp = stamp.rotate(-3, expand=True, resample=Image.BICUBIC)
        card.paste(stamp, (W - stamp.size[0] - margin - 10, 150), stamp)

    card = grain(card)
    card.save(OUT / "og.jpg", "JPEG", quality=88, optimize=True, progressive=True)
    print(f"  + og.jpg ({(OUT / 'og.jpg').stat().st_size // 1024} Ko)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fonts", default=None,
                        help="dossier ou garder les polices telechargees")
    args = parser.parse_args()

    folder = Path(args.fonts) if args.fonts else ROOT / ".fonts-cache"
    OUT.mkdir(parents=True, exist_ok=True)

    fonts = load_fonts(folder)
    make_icons(fonts)
    make_og(fonts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
