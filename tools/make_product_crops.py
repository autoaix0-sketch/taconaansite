#!/usr/bin/env python3
"""
Taco Naan - vignettes de plats decoupees dans les panneaux.

Certaines categories de la carte n'ont pas de photo produit a part. Mais les
panneaux du dossier menu/ en contiennent : on y decoupe la vignette.

C'est aussi d'ici que viennent les bols, le menu enfant et le Tex-Mex. Les
images qui tenaient ces places avant venaient d'ailleurs : deux montraient un
autocollant "Taco Naan" qui n'est pas le notre, pose sur le papier d'emballage
d'une autre enseigne. Leurs fichiers d'origine ont ete supprimes et ne peuvent
pas etre refaits. Le panneau du comptoir, lui, montre les bons plats : on y
decoupe donc directement, et tout ce qui est affiche sur le site vient de la
boutique.

Ces vignettes sont petites - le panneau fait 1156 px de large, pas davantage.
Elles sont donc exportees a leur taille reelle, sans agrandissement, avec un
leger renforcement de nettete. Elles tiennent bien sur les fiches de la carte ;
on ne les met pas dans la galerie, ou elles seraient affichees plus grand.

Elles passent en revanche par le meme etalonnage chaud et le meme grain que
toutes les autres photos du site (warm_grade et add_grain, dans
optimize_images.py). Sans lui, la boite du menu enfant arrivait en bleu ciel au
milieu d'une page noir et jaune, et on ne voyait plus qu'elle. Les panneaux
entiers, eux, n'y passent pas : ce sont des prix, ils doivent rester lisibles.

Le resultat est ecrit dans assets/img/extras.js, qui vient completer le
manifeste principal. Volontairement separe de tools/optimize_images.py pour
que regenerer l'un n'efface jamais l'autre.

Usage :  python tools/make_product_crops.py
Aucune dependance a installer : Pillow suffit.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageEnhance

sys.path.insert(0, str(Path(__file__).resolve().parent))
from optimize_images import add_grain, warm_grade  # meme traitement que les autres photos

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "menu"
OUT = ROOT / "assets" / "img"

# nom de sortie, panneau source, zone a decouper en fractions
# (gauche, haut, droite, bas) -- 0 = bord gauche/haut, 1 = bord droit/bas.
CROPS = [
    ("barquette", "barquette.png", (0.7930, 0.1220, 0.9900, 0.2980)),

    # --- decoupes dans le panneau Burgers ---------------------------------
    # Les deux bols, photographies dans leur cercle sur le panneau.
    ("bowl",      "burger.png",    (0.5848, 0.5212, 0.7249, 0.7303)),
    ("crousty",   "burger.png",    (0.5952, 0.7242, 0.7266, 0.9455)),
    # Le menu enfant : la meme boite que sur le panneau, prise sur le panneau.
    ("enfant",    "burger.png",    (0.7647, 0.5879, 0.8633, 0.7818)),
    # Tex-Mex : les wings, le plat le plus lisible de la rangee.
    ("texmex",    "burger.png",    (0.4775, 0.3182, 0.5692, 0.4318)),
]

WIDTHS = [300, 600]


def main() -> int:
    if not SRC.is_dir():
        print(f"! Dossier introuvable : {SRC}")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    entries = []

    for stem, filename, box in CROPS:
        path = SRC / filename
        if not path.exists():
            print(f"  - {filename} introuvable, ignore")
            continue

        original = Image.open(path)
        if original.mode == "RGBA":
            flat = Image.new("RGB", original.size, (8, 10, 10))
            flat.paste(original, (0, 0), original)
            original = flat
        else:
            original = original.convert("RGB")

        w, h = original.size
        left, top, right, bottom = box
        crop = original.crop((round(w * left), round(h * top),
                              round(w * right), round(h * bottom)))

        sizes = []
        for width in WIDTHS:
            width = min(width, crop.size[0])
            if any(width == existing for existing, _ in sizes):
                continue
            height = max(1, round(crop.size[1] * width / crop.size[0]))
            resized = crop.resize((width, height), Image.LANCZOS)
            # Une vignette tiree d'un panneau a deja subi une reduction : un
            # coup de nettete leger lui rend le mordant perdu en route.
            resized = ImageEnhance.Sharpness(resized).enhance(1.6)
            resized = add_grain(warm_grade(resized))
            sizes.append((width, height))

            resized.save(OUT / f"{stem}-{width}.webp", "WEBP", quality=86, method=6)
            try:
                resized.save(OUT / f"{stem}-{width}.avif", "AVIF", quality=62, speed=4)
            except Exception as exc:
                print(f"    ! AVIF ignore pour {stem}-{width} ({exc})")

        entries.append((stem, sizes))
        print(f"  + {stem:12s} <- menu/{filename:16s} {crop.size[0]}x{crop.size[1]}")

    lines = [
        "/* Genere par tools/make_product_crops.py - ne pas modifier a la main. */",
        "/* Vignettes decoupees dans les panneaux, ajoutees au manifeste. */",
        "window.TACONAAN_IMAGES = Object.assign(window.TACONAAN_IMAGES || {}, {",
    ]
    for stem, sizes in entries:
        dims = ", ".join(f"[{w}, {h}]" for w, h in sizes)
        lines.append(f"  {stem.replace('-', '_')}: "
                     f"{{ stem: '{stem}', kind: 'photo', sizes: [{dims}] }},")
    lines.append("});")
    (OUT / "extras.js").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n  = extras.js ({len(entries)} vignette(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
