#!/usr/bin/env python3
"""
Taco Naan - preparation des images du site.

Lit les photos d'origine dans _work/sources/, les retravaille pour qu'elles
appartiennent toutes au meme univers visuel (papier kraft & encre), puis les
exporte en AVIF + WebP sur plusieurs largeurs dans assets/img/.

Usage :  python tools/optimize_images.py
Aucune dependance a installer : Pillow suffit.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img"
# Les photos d'origine (naaan.png, tacoss.png, ...) ont ete rangees hors du
# depot public. Elles restent lisibles par ce script a cet endroit ; si une
# recette ne s'y trouve pas, on retombe sur ROOT au cas ou elle a ete remise
# a la racine a la main.
SRC = ROOT / "_work" / "sources"

# Couleur temoin utilisee par le remplissage par diffusion pour marquer le fond.
FLOOD_MARK = (255, 0, 255)


# --------------------------------------------------------------------------
# Traitement colorimetrique
# --------------------------------------------------------------------------

def warm_grade(rgb: Image.Image) -> Image.Image:
    """Ramene une photo vers un rendu chaud et encre, coherent avec le papier.

    Les photos d'origine viennent de sources differentes (banques d'images,
    catalogues fournisseur). Sans ce passage elles ne ressemblent pas a une
    meme serie. On desature legerement, on monte le contraste, puis on pousse
    les rouges et on retient les bleus.
    """
    rgb = ImageEnhance.Color(rgb).enhance(0.88)
    rgb = ImageEnhance.Contrast(rgb).enhance(1.14)

    r, g, b = rgb.split()
    r = r.point(lambda v: min(255, int(v * 1.05 + 5)))
    g = g.point(lambda v: min(255, int(v * 1.00 + 2)))
    b = b.point(lambda v: min(255, int(v * 0.90 + 4)))
    return Image.merge("RGB", (r, g, b))


def add_grain(rgb: Image.Image, amount: float = 0.055) -> Image.Image:
    """Depose un grain argentique fin. C'est ce qui casse l'aspect rendu 3D."""
    w, h = rgb.size
    noise = Image.new("L", (w, h))
    rnd = random.Random(40100)  # graine fixe : rendu reproductible d'un run a l'autre
    noise.putdata([int(max(0, min(255, rnd.gauss(128, 34)))) for _ in range(w * h)])
    noise = noise.filter(ImageFilter.GaussianBlur(0.4))
    return Image.blend(rgb, Image.merge("RGB", (noise, noise, noise)), amount)


# --------------------------------------------------------------------------
# Detourage
# --------------------------------------------------------------------------

def cutout_white(im: Image.Image, tolerance: int = 38) -> Image.Image:
    """Rend transparent le fond blanc, sans manger les blancs interieurs.

    On ne peut pas se contenter de "tout ce qui est blanc devient transparent" :
    l'assiette de assiette.png est blanche elle aussi. On procede donc par
    diffusion depuis le bord, ce qui ne touche que la zone de fond
    effectivement reliee a l'exterieur.
    """
    rgb = im.convert("RGB")
    w, h = rgb.size

    # Une bordure d'un pixel garantit que les quatre coins communiquent entre eux,
    # meme si le sujet touche un bord.
    padded = Image.new("RGB", (w + 2, h + 2), (255, 255, 255))
    padded.paste(rgb, (1, 1))

    ImageDraw.floodfill(padded, (0, 0), FLOOD_MARK, thresh=tolerance)

    marked = padded.crop((1, 1, w + 1, h + 1))
    # Masque : 0 la ou le fond a ete marque, 255 pour le sujet.
    diff = ImageChops.difference(marked, Image.new("RGB", (w, h), FLOOD_MARK))
    alpha = diff.convert("L").point(lambda v: 255 if v > 12 else 0)

    # Un pixel d'erosion supprime le lisere blanc laisse par l'antialiasing
    # de l'image d'origine, puis un flou tres court adoucit la decoupe.
    alpha = alpha.filter(ImageFilter.MinFilter(3))
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.6))

    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def trim_to_content(im: Image.Image, padding: int = 8) -> Image.Image:
    """Recadre sur le sujet visible, avec une marge de respiration."""
    if im.mode != "RGBA":
        return im
    bbox = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    w, h = im.size
    box = (max(0, x0 - padding), max(0, y0 - padding),
           min(w, x1 + padding), min(h, y1 + padding))
    return im.crop(box)


# --------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------

def export(im: Image.Image, stem: str, widths: list[int]) -> tuple[list[str], list[tuple[int, int]]]:
    OUT.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    made: list[tuple[int, int]] = []
    src_w = im.size[0]
    done: set[int] = set()

    for width in widths:
        # On n'agrandit jamais une image : ca ne cree pas de detail,
        # ca ne fait qu'alourdir le fichier.
        width = min(width, src_w)
        if width in done:
            continue
        done.add(width)

        height = max(1, round(im.size[1] * width / im.size[0]))
        resized = im.resize((width, height), Image.LANCZOS)
        made.append((width, height))

        webp = OUT / f"{stem}-{width}.webp"
        resized.save(webp, "WEBP", quality=82, method=6)
        written.append(webp.name)

        avif = OUT / f"{stem}-{width}.avif"
        try:
            resized.save(avif, "AVIF", quality=58, speed=4)
            written.append(avif.name)
        except Exception as exc:  # depend de la build Pillow installee
            print(f"    ! AVIF ignore pour {stem}-{width} ({exc})")

    return written, made


# --------------------------------------------------------------------------
# Recettes
# --------------------------------------------------------------------------
# kind = "cutout"  -> pose directement sur le papier, fond transparent
# kind = "photo"   -> encadree, traitee grain + chaleur
# crop             -> fraction (gauche, haut, droite, bas) a retirer
#
# Les sources sont lues depuis SRC (_work/sources/), avec repli sur la
# racine du projet si une source a ete remise la a la main. Voir aussi
# l'avertissement en tete de make_product_photos.py pour l'autre pipeline.
#
# A verifier aussi sur toute nouvelle source : _work/sources/products/viandes
# au choix/steak.jpg (l'export d'origine, distinct de steak.png) porte un
# filigrane "Vecteezy" en travers de l'image et reste inutilisable.

RECIPES = [
    # nom de sortie      source                kind      widths            crop
    ("naan",             "naaan.png",          "cutout", [480, 960],       None),
    ("tacos",            "tacoss.png",         "cutout", [480, 960],       None),
    ("assiette",         "assiette.png",       "cutout", [480, 960],       None),
    ("burger",           "berger.jpg",         "cutout", [480, 960],       None),
    # RETIRES. bowl.png, rizzz.png et mini.jpg ont ete supprimes : les deux
    # premiers montraient le papier d'emballage d'une autre enseigne, et un
    # autocollant "Taco Naan" qui n'est pas celui de la boutique - le recadrage
    # qui suivait ne gardait donc pas "la partie authentique", contrairement a
    # ce qui etait note ici. mini.jpg etait une boite a gouter sans rapport.
    # Les bols, le menu enfant et le Tex-Mex sont desormais decoupes dans le
    # panneau du comptoir par tools/make_product_crops.py.
    ("texmex",           "texmex.jpg",         "photo",  [480, 960],       None),
    ("wraps",            "Naan.jpg",           "photo",  [480, 960],       None),
    ("grillades",        "tacos.jpg",          "photo",  [480, 960],       None),
    ("logo-ink",         "taco-naan-ink.png",  "cutout", [320, 640, 960],  None),
    ("logo-white",       "taco-naan-white.png", "cutout", [320, 640],      None),
]


def apply_crop(im: Image.Image, crop) -> Image.Image:
    if not crop:
        return im
    left, top, right, bottom = crop
    w, h = im.size
    return im.crop((round(w * left), round(h * top),
                    round(w * (1 - right)), round(h * (1 - bottom))))


def write_manifest(manifest: dict) -> None:
    """Ecrit les dimensions reelles de chaque image pour le site.

    Le HTML a besoin du ratio exact de chaque visuel pour reserver la place
    avant meme que l'image n'arrive. Sans ca, la page saute au chargement.
    """
    lines = [
        "/* Genere par tools/optimize_images.py - ne pas modifier a la main. */",
        "/* Dimensions reelles de chaque image, pour reserver la place avant",
        "   le chargement et eviter que la page ne saute. */",
        "window.TACONAAN_IMAGES = {",
    ]
    for stem in sorted(manifest):
        entry = manifest[stem]
        sizes = ", ".join(f"[{w}, {h}]" for w, h in entry["sizes"])
        lines.append(f"  {stem.replace('-', '_')}: "
                     f"{{ stem: '{stem}', kind: '{entry['kind']}', sizes: [{sizes}] }},")
    lines.append("};")
    (OUT / "manifest.js").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  = manifest.js ({len(manifest)} images)")


def main() -> int:
    if not (ROOT / "index.html").exists():
        print(f"! Lance depuis la racine du projet. ROOT vu : {ROOT}")
        return 1

    total = 0
    manifest: dict[str, dict] = {}
    for stem, src_name, kind, widths, crop in RECIPES:
        src = SRC / src_name
        if not src.exists():
            src = ROOT / src_name
        if not src.exists():
            print(f"  - {src_name} introuvable, ignore")
            continue

        im = Image.open(src)
        im = apply_crop(im, crop)

        if kind == "flat":
            im = im.convert("RGB")
        elif kind == "cutout":
            already_cut = im.mode == "RGBA" and im.getchannel("A").getextrema()[0] < 250
            im = im.convert("RGBA") if already_cut else cutout_white(im)
            im = trim_to_content(im)
        else:
            im = add_grain(warm_grade(im.convert("RGB")))

        files, made = export(im, stem, widths)
        total += len(files)
        manifest[stem] = {"kind": kind, "sizes": [list(s) for s in made]}
        print(f"  + {stem:12s} <- {src_name:24s} {im.size[0]}x{im.size[1]}  ({len(files)} fichiers)")

    write_manifest(manifest)

    weight = sum(f.stat().st_size for f in OUT.glob("*")) // 1024
    print(f"\n{total} fichiers ecrits dans assets/img/ - {weight} Ko au total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
