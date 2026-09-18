#!/usr/bin/env python3
"""
Taco Naan - les affiches.

Une affiche, c'est ce qui manquait : une vignette detouree, seule sur du noir,
ne dit rien. Composee avec un titre, un prix et le blason, la meme photo devient
une image de marque. Le principe vient de l'affiche papier de la boutique - un
grand titre, trois produits alignes, une mention en bas - refaite ici dans le
noir et le jaune du site plutot que dans son rouge d'origine, qui serait une
cinquieme palette sur la page.

Rien n'est invente : chaque affiche est montee a partir des detourages deja
presents dans assets/img/, et les textes sont ceux de data/menu.js, qui sont
deja ecrits et deja vrais.

Trois langues. Le site bascule en FR/ES/EN et renderAffiches() se rejoue a
chaque changement ; une affiche est une image, donc son texte y est cuit. Comme
elles sont generees, une variante de langue n'est qu'une ligne de table.

Volontairement separe des trois autres outils : ils ecrivent manifest.js,
extras.js et photos.js, celui-ci ecrit posters.js. Regenerer l'un n'efface
jamais les autres.

ATTENTION : ne relance pas tools/optimize_images.py. Sept de ses neuf sources
ont ete archivees, et un passage a vide reecrirait manifest.js sans elles.

Usage :  python tools/make_posters.py [--fonts DIR]
Dependances : Pillow et numpy.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_brand_assets import (CREAM, FAINT, FONT_URLS, MUTE, VOID, YELLOW,
                               grain, load_fonts)
from make_product_photos import key
from optimize_images import trim_to_content

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"

# Le brun chaud du bandeau central des panneaux. Il manquait cote Python : le
# site s'en sert (--amber), l'affiche s'en sert pour la lueur derriere le plat.
AMBER = (180, 98, 26)

# L'italique du titre. Le site l'utilise (Instrument+Serif:ital@0;1) mais le
# cache de polices ne contient que le romain. On tente le telechargement une
# fois ; s'il echoue, on retombe sur le romain et l'accent ne tient plus qu'a
# la couleur - exactement ce que fait deja make_og().
ITALIC = "InstrumentSerifItalic.ttf"
ITALIC_URL = ("https://github.com/google/fonts/raw/main/ofl/"
              "instrumentserif/InstrumentSerif-Italic.ttf")

W, H = 900, 1125              # 4:5, le format de l'affiche d'origine
WIDTHS = [450, 900]
MARGIN = 56                   # marge de texte
FRAME = 28                    # filet, comme le cadre de og.jpg

LINE = (44, 48, 46)           # --line rendu opaque sur --void


# ---------------------------------------------------------------------------
# Les affiches
# ---------------------------------------------------------------------------
#
# head : le mot entre *asterisques* passe en jaune. C'est la regle du site -
#        un seul accent, et il se pose sur un mot, pas sur une phrase.
# shots: (stem, largeur voulue dans l'affiche, decalage vertical en fraction)

POSTERS = [
    {
        "id": "trio",
        "shots": [("burgers-double-chicken", 290, 0.0),
                  ("burgers-supreme",        345, 0.0),
                  ("burgers-double-cheese",  290, 0.0)],
        "text": {
            "fr": {"eyebrow": "NOS BURGERS",
                   "head": "Le trio\n*incontournable*.",
                   "price": "À PARTIR DE 4,00 €",
                   "label": "Nos burgers",
                   "alt": "Affiche Taco Naan : le trio de burgers, à partir de 4 €"},
            "es": {"eyebrow": "NUESTRAS HAMBURGUESAS",
                   "head": "El trío\n*imprescindible*.",
                   "price": "DESDE 4,00 €",
                   "label": "Nuestras hamburguesas",
                   "alt": "Cartel Taco Naan: el trío de hamburguesas, desde 4 €"},
            "en": {"eyebrow": "OUR BURGERS",
                   "head": "The trio you\n*can't skip*.",
                   "price": "FROM 4,00 €",
                   "label": "Our burgers",
                   "alt": "Taco Naan poster: the burger trio, from €4"},
        },
    },
    {
        "id": "naan",
        "shots": [("naan-hero", 660, 0.0)],
        "text": {
            "fr": {"eyebrow": "LA MAISON",
                   "head": "Le pain est pétri\net *cuit ici*.",
                   "price": "SEUL 6,50 €  ·  MENU 8,50 €",
                   "label": "Cheese Naan",
                   "alt": "Affiche Taco Naan : le cheese naan, seul 6,50 € ou en menu 8,50 €"},
            "es": {"eyebrow": "LA CASA",
                   "head": "El pan se amasa\ny se *hornea aquí*.",
                   "price": "SOLO 6,50 €  ·  MENÚ 8,50 €",
                   "label": "Cheese Naan",
                   "alt": "Cartel Taco Naan: el cheese naan, solo 6,50 € o menú 8,50 €"},
            "en": {"eyebrow": "THE HOUSE",
                   "head": "The bread is kneaded\nand *baked here*.",
                   "price": "ONLY 6,50 €  ·  MEAL 8,50 €",
                   "label": "Cheese Naan",
                   "alt": "Taco Naan poster: the cheese naan, €6.50 alone or €8.50 as a meal"},
        },
    },
    {
        "id": "tacos",
        "shots": [("tacos", 620, 0.0)],
        "text": {
            "fr": {"eyebrow": "SIMPLE  ·  DOUBLE  ·  TRIPLE",
                   "head": "Galette pressée\n*au grill*.",
                   "price": "6,50 €  →  11,00 €",
                   "label": "Tacos",
                   "alt": "Affiche Taco Naan : le tacos, de 6,50 € à 11,00 €"},
            "es": {"eyebrow": "SIMPLE  ·  DOBLE  ·  TRIPLE",
                   "head": "Tortilla prensada\n*a la plancha*.",
                   "price": "6,50 €  →  11,00 €",
                   "label": "Tacos",
                   "alt": "Cartel Taco Naan: el tacos, de 6,50 € a 11,00 €"},
            "en": {"eyebrow": "SINGLE  ·  DOUBLE  ·  TRIPLE",
                   "head": "Griddle-pressed,\n*cheese sauce*.",
                   "price": "6,50 €  →  11,00 €",
                   "label": "Tacos",
                   "alt": "Taco Naan poster: the tacos, from €6.50 to €11"},
        },
    },
    {
        "id": "desserts",
        "shots": [("desserts-miel",     265, 0.0),
                  ("desserts-nutella",  265, 0.0),
                  ("desserts-tarte",    245, 0.0),
                  ("desserts-tiramisu", 175, 0.0)],
        "text": {
            "fr": {"eyebrow": "LES DESSERTS",
                   "head": "Tous à *3 €*.",
                   "price": "NAAN MIEL  ·  NUTELLA  ·  TARTE DAIM  ·  TIRAMISU",
                   "label": "Les desserts",
                   "alt": "Affiche Taco Naan : les desserts, tous à 3 €"},
            "es": {"eyebrow": "LOS POSTRES",
                   "head": "Todos a *3 €*.",
                   "price": "NAAN MIEL  ·  NUTELLA  ·  TARTA DAIM  ·  TIRAMISÚ",
                   "label": "Los postres",
                   "alt": "Cartel Taco Naan: los postres, todos a 3 €"},
            "en": {"eyebrow": "DESSERTS",
                   "head": "All at *3 €*.",
                   "price": "HONEY NAAN  ·  NUTELLA  ·  DAIM TART  ·  TIRAMISU",
                   "label": "Desserts",
                   "alt": "Taco Naan poster: desserts, all at €3"},
        },
    },
]

LANGS = ["fr", "es", "en"]


# ---------------------------------------------------------------------------
# Typographie
# ---------------------------------------------------------------------------

def fonts_for(folder: Path) -> dict[str, ImageFont.FreeTypeFont]:
    """Charge le romain et le mono du cache, et tente l'italique une fois."""
    paths = load_fonts(folder)

    italic = folder / ITALIC
    if not italic.exists():
        try:
            print(f"  . telechargement de {ITALIC}")
            urllib.request.urlretrieve(ITALIC_URL, italic)
        except (urllib.error.URLError, OSError) as exc:
            print(f"  ! italique indisponible ({exc}) - on garde le romain")

    serif = str(paths["InstrumentSerif.ttf"])
    mono = str(paths["PlexMono.ttf"])
    accent = str(italic) if italic.exists() else serif

    return {
        "head": ImageFont.truetype(serif, 82),
        "head_em": ImageFont.truetype(accent, 82),
        "eyebrow": ImageFont.truetype(mono, 19),
        "price": ImageFont.truetype(mono, 21),
        "sign": ImageFont.truetype(mono, 17),
    }


def tracked(draw: ImageDraw.ImageDraw, xy, text: str,
            font: ImageFont.FreeTypeFont, fill, tracking: float) -> float:
    """Ecrit en lettres espacees. Rend la largeur occupee.

    Pillow ne connait pas l'interlettrage, et le mono du site en porte beaucoup
    (.24em sur les eyebrows). Sans lui, les petites capitales n'ont pas du tout
    le meme air.
    """
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += draw.textlength(char, font=font) + tracking
    return x - xy[0]


def split_accent(line: str) -> list[tuple[str, bool]]:
    """Decoupe une ligne en morceaux (texte, est_accentue) sur les *etoiles*."""
    parts, accent = [], False
    for chunk in line.split("*"):
        if chunk:
            parts.append((chunk, accent))
        accent = not accent
    return parts


def draw_head(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
              fonts: dict, leading: int = 88) -> int:
    """Ecrit le titre. Rend le y d'apres la derniere ligne."""
    for line in text.split("\n"):
        cursor = x
        for chunk, accent in split_accent(line):
            font = fonts["head_em"] if accent else fonts["head"]
            draw.text((cursor, y), chunk, font=font,
                      fill=YELLOW if accent else CREAM)
            cursor += draw.textlength(chunk, font=font)
        y += leading
    return y


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------

def glow(size: tuple[int, int], center: tuple[int, int],
         radius: int, colour: tuple[int, int, int], strength: float) -> Image.Image:
    """Une lueur chaude derriere le plat, comme le halo des fiches de la carte.

    Sans elle, un detourage pose sur du noir plat a l'air decoupe aux ciseaux.
    Avec, il a un fond d'ou sortir.
    """
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.hypot(xx - center[0], yy - center[1]) / radius
    falloff = np.clip(1.0 - dist, 0.0, 1.0) ** 2.2 * strength

    layer = np.zeros((h, w, 3), np.float64)
    for i, value in enumerate(colour):
        layer[..., i] = value * falloff
    return Image.fromarray(layer.round().astype("uint8"), "RGB")


def shadow(cut: Image.Image, blur: int = 22, spread: float = 0.62) -> Image.Image:
    """L'ombre portee du detourage, tiree de son propre alpha."""
    alpha = cut.getchannel("A").point(lambda v: int(v * spread))
    pad = blur * 3
    canvas = Image.new("L", (cut.width + pad * 2, cut.height + pad * 2), 0)
    canvas.paste(alpha, (pad, pad))
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))

    out = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    out.putalpha(canvas)
    return out


def load_shot(stem: str, width: int) -> Image.Image | None:
    """Ouvre le detourage le plus large disponible et le met a la largeur voulue."""
    candidates = sorted(IMG.glob(f"{stem}-*.webp"),
                        key=lambda p: int(p.stem.rsplit("-", 1)[1]))
    if not candidates:
        print(f"    ! {stem} introuvable")
        return None

    cut = trim_to_content(Image.open(candidates[-1]).convert("RGBA"), padding=2)
    source_width = cut.width
    height = max(1, round(cut.height * width / cut.width))
    cut = cut.resize((width, height), Image.LANCZOS)

    if width > source_width:
        # Les vignettes burgers et desserts plafonnent vers 200-400 px : montees
        # a la taille de l'affiche elles s'emoussent. Meme correctif que dans
        # make_product_crops.py. On ne l'applique qu'en agrandissement - sur une
        # reduction il ne ferait que durcir des bords deja nets.
        cut = ImageEnhance.Sharpness(cut).enhance(1.6)
    return cut


def compose(poster: dict, lang: str, fonts: dict) -> Image.Image:
    text = poster["text"][lang]

    shots = [(load_shot(stem, width), offset)
             for stem, width, offset in poster["shots"]]
    shots = [(cut, offset) for cut, offset in shots if cut is not None]
    if not shots:
        raise RuntimeError(f"aucun visuel pour {poster['id']}")

    # Les plats reposent tous sur une meme ligne, comme sur un comptoir. Les
    # centrer verticalement, c'etait les faire flotter chacun a sa hauteur.
    base_y = int(H * 0.78)          # la ligne de pose
    band_y = int(H * 0.62)          # centre de la lueur
    card = Image.new("RGB", (W, H), VOID)

    # La lueur d'abord : tout se pose dessus.
    card = Image.blend(card, glow((W, H), (W // 2, band_y), int(W * 0.78),
                                  AMBER, 0.30), 1.0)

    # Les produits, centres sur la bande, poses de gauche a droite. Ils se
    # chevauchent legerement quand ils sont plusieurs - c'est ce qui fait une
    # composition plutot qu'un alignement.
    #
    # L'encombrement n'est pas la somme des largeurs : chaque visuel sauf le
    # dernier n'avance que d'une fraction de la sienne. Calculer autrement
    # decentre la rangee et la fait deborder du filet.
    overlap = 0.86 if len(shots) > 2 else 1.0

    def extent(items) -> float:
        widths = [cut.width for cut, _ in items]
        return sum(w * overlap for w in widths[:-1]) + widths[-1]

    usable = W - 2 * MARGIN
    if extent(shots) > usable:
        scale = usable / extent(shots)
        shots = [(cut.resize((max(1, round(cut.width * scale)),
                              max(1, round(cut.height * scale))), Image.LANCZOS), off)
                 for cut, off in shots]

    x = round((W - extent(shots)) / 2)

    for cut, offset in shots:
        y = base_y - cut.height + int(H * offset)
        cast = shadow(cut)
        card.paste(cast, (x - (cast.width - cut.width) // 2,
                          y - (cast.height - cut.height) // 2 + 14), cast)
        card.paste(cut, (x, y), cut)
        x += int(cut.width * overlap)

    draw = ImageDraw.Draw(card)

    # Le filet, comme le cadre de og.jpg et la bordure des panneaux.
    draw.rectangle([FRAME, FRAME, W - FRAME - 1, H - FRAME - 1], outline=LINE, width=1)

    # Le blason, en haut a droite, incline comme sur og.jpg.
    stamp_path = IMG / "logo-white-320.webp"
    if stamp_path.exists():
        stamp = Image.open(stamp_path).convert("RGBA")
        stamp.thumbnail((132, 132), Image.LANCZOS)
        stamp = stamp.rotate(-3, expand=True, resample=Image.BICUBIC)
        card.paste(stamp, (W - stamp.width - MARGIN, MARGIN + 6), stamp)

    # Le texte : eyebrow, puis titre.
    tracked(draw, (MARGIN, MARGIN + 18), text["eyebrow"],
            fonts["eyebrow"], YELLOW, 4.4)
    draw_head(draw, MARGIN, MARGIN + 62, text["head"], fonts)

    # Le pied : filet, prix en jaune, signature en gris.
    foot = H - MARGIN - 78
    draw.line([(MARGIN, foot), (MARGIN + 190, foot)], fill=LINE, width=1)
    if text["price"]:
        tracked(draw, (MARGIN, foot + 22), text["price"],
                fonts["price"], YELLOW, 1.6)
    tracked(draw, (MARGIN, foot + 56), "TACO NAAN  ·  DAX",
            fonts["sign"], FAINT, 3.2)

    return grain(card)


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export(im: Image.Image, stem: str, widths: list[int]) -> list[tuple[int, int]]:
    made: list[tuple[int, int]] = []
    done: set[int] = set()
    for width in widths:
        width = min(width, im.size[0])          # on n'agrandit jamais
        if width in done:
            continue
        done.add(width)
        height = max(1, round(im.size[1] * width / im.size[0]))
        resized = im.resize((width, height), Image.LANCZOS)
        made.append((width, height))
        resized.save(IMG / f"{stem}-{width}.webp", "WEBP", quality=86, method=6)
        try:
            resized.save(IMG / f"{stem}-{width}.avif", "AVIF", quality=62, speed=4)
        except Exception as exc:
            print(f"    ! AVIF ignore pour {stem}-{width} ({exc})")
    return made


def js_dict(field: str, poster: dict) -> str:
    def esc(value: str) -> str:
        return value.replace("\\", "\\\\").replace("'", "\\'")
    parts = ", ".join(f"{lang}: '{esc(poster['text'][lang][field])}'" for lang in LANGS)
    return "{ " + parts + " }"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fonts", type=Path, default=ROOT / ".fonts-cache")
    args = parser.parse_args()

    if not (ROOT / "index.html").exists():
        print(f"! Lance depuis la racine du projet. ROOT vu : {ROOT}")
        return 1

    fonts = fonts_for(args.fonts)
    IMG.mkdir(parents=True, exist_ok=True)
    entries = []

    for poster in POSTERS:
        stems, sizes = {}, None
        for lang in LANGS:
            stem = f"affiche-{poster['id']}-{lang}"
            sizes = export(compose(poster, lang, fonts), stem, WIDTHS)
            stems[lang] = stem
        dims = ", ".join(f"[{w}, {h}]" for w, h in sizes)
        entries.append((poster["id"], stems, poster, dims))
        print(f"  + affiche-{poster['id']:10s} {len(LANGS)} langues  {W}x{H}")

    lines = [
        "/* Genere par tools/make_posters.py - ne pas modifier a la main. */",
        "/* Les affiches : un titre, un plat, un prix. Une par langue, parce",
        "   que le texte est cuit dans l'image. */",
        "window.TACONAAN_POSTERS = [",
    ]
    for pid, stems, poster, dims in entries:
        stem_js = ", ".join(f"{lang}: '{stems[lang]}'" for lang in LANGS)
        lines.append(f"  {{ id: '{key(pid)}', stem: {{ {stem_js} }},")
        lines.append(f"    label: {js_dict('label', poster)},")
        lines.append(f"    alt: {js_dict('alt', poster)},")
        lines.append(f"    sizes: [{dims}] }},")
    lines.append("];")

    # CRLF comme les autres manifestes, pour ne pas polluer le diff.
    with open(IMG / "posters.js", "w", encoding="utf-8", newline="\r\n") as handle:
        handle.write("\n".join(lines) + "\n")

    print(f"\n  = posters.js ({len(entries)} affiches x {len(LANGS)} langues)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
