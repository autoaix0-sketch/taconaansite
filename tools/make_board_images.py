#!/usr/bin/env python3
"""
Taco Naan - preparation des panneaux de la boutique.

Les fichiers de menu/ sont les photos des panneaux affiches au comptoir.
Ce sont des visuels graphiques, pas des photos de plats : ils ne recoivent
ni grain ni correction chaude, qui rendraient les prix moins lisibles. On se
contente de redimensionner proprement et d'exporter en AVIF + WebP.

Deux traces de capture d ecran trainaient sur les quatre panneaux et se
voyaient sur le site : un bandeau noir dans le coin haut-gauche, et une barre
de defilement claire en bas. Ni l un ni l autre n est sur le mur de la
boutique. On coupe le bandeau et on efface la barre : le panneau retrouve ce
qu il est reellement, et rien de ce qui est ecrit dessus n est touche.

Volontairement separe de tools/optimize_images.py, qui traite les plats.

Usage :  python tools/make_board_images.py
Aucune dependance a installer : Pillow suffit.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "menu"
OUT = ROOT / "assets" / "img"

# nom de sortie, fichier source, intitule affiche sous le panneau
BOARDS = [
    ("board-naan",      "naan.png",      "Cheese Naan"),
    ("board-tacos",     "tacoos.png",    "Tacos"),
    ("board-burger",    "burger.png",    "Burgers"),
    ("board-barquette", "barquette.png", "Barquettes"),
]

# Deux largeurs suffisent : une vignette, et une version nette pour le zoom.
WIDTHS = [720, 1160]

# Le bandeau de capture est un aplat VRAIMENT noir, colle au coin haut-gauche.
# Le seuil est severe a dessein : les panneaux ont eux-memes des fonds tres
# sombres, et un seuil laxiste emporterait le panneau avec le bandeau.
BAR_BLACK, BAR_MIN_RUN, BAR_ZONE = 10, 60, 0.12

# La barre de defilement est un trait clair, plein, d un seul tenant, large
# d au moins un quart du panneau. C est cette continuite qui la distingue
# d une rangee de frites ou d un bandeau jaune, clairs mais decoupes.
SCROLL_ZONE, SCROLL_LUM, SCROLL_MIN_RUN, SCROLL_MAX_ROWS = 0.08, 120, 0.25, 16
# Ses bords sont adoucis : le coeur de la barre passe le seuil, pas sa frange.
# Reboucher a partir d une ligne qui en contient encore etale le probleme au
# lieu de le retirer, alors on sort d abord de la frange.
SCROLL_EDGE_RUN, SCROLL_EDGE_MAX = 0.05, 10


def longest_run(flags) -> int:
    """Longueur du plus long segment vrai d une ligne."""
    best = run = 0
    for v in flags:
        run = run + 1 if v else 0
        if run > best:
            best = run
    return best


def mask_top_bar(a) -> tuple[int, int]:
    """Efface le bandeau noir du coin haut-gauche. Rend sa taille.

    On ne recadre pas : sur un panneau comme naan.png le bandeau descend
    jusqu a 46 px, et couper cette bande emporterait le haut de la colonne
    voisine. On repeint donc le rectangle avec la couleur qui l entoure -
    partout ici un noir de fond - et le panneau reste entier.
    """
    h, w = a.shape[:2]
    black = a[:, :, :3].max(2) <= BAR_BLACK

    runs = {}
    for y in range(min(int(h * BAR_ZONE), h)):
        run = 0
        while run < w and black[y, run]:
            run += 1
        # Un liseré pleine largeur est une bordure du panneau, pas le bandeau.
        if BAR_MIN_RUN <= run < w * 0.9:
            runs[y] = run

    if not runs:
        return 0, 0
    # Le bandeau garde la meme largeur sur toute sa hauteur : c est donc la
    # largeur la plus frequente. Les lignes qui s en ecartent appartiennent
    # deja au panneau. On n exige pas qu il commence a la ligne 0 - un horodatage
    # clair peut le surmonter - mais on repeint depuis le haut pour l emporter.
    widths = list(runs.values())
    bar_w = max(set(widths), key=widths.count)
    band = [y for y, r in runs.items() if abs(r - bar_w) <= bar_w * 0.1]
    bar_h = max(band) + 1

    fill = np.median(a[bar_h:bar_h + 8, :bar_w].reshape(-1, a.shape[2]), axis=0)
    a[:bar_h, :bar_w] = fill.round().astype(a.dtype)
    return bar_w, bar_h


def heal_scrollbar(a) -> int:
    """Efface la barre de defilement en rebouchant par le haut et le bas.

    Elle flotte au-dessus du panneau : la couper emporterait du contenu. On
    remplace donc ses lignes par un degrade entre la ligne saine juste
    au-dessus et celle juste en dessous. Sur un aplat graphique, la reprise
    ne se voit pas.
    """
    h, w = a.shape[:2]
    light = a[:, :, :3].min(2) > SCROLL_LUM
    need = int(w * SCROLL_MIN_RUN)

    rows = [y for y in range(int(h * (1 - SCROLL_ZONE)), h)
            if longest_run(light[y]) >= need]
    if not rows or len(rows) > SCROLL_MAX_ROWS:
        return 0

    top, bottom = min(rows), max(rows)

    # On recule jusqu a une ligne vraiment propre de part et d autre.
    fringe = int(w * SCROLL_EDGE_RUN)
    above, below = top - 1, bottom + 1
    steps = 0
    while above > 0 and longest_run(light[above]) >= fringe and steps < SCROLL_EDGE_MAX:
        above -= 1
        steps += 1
    steps = 0
    while below < h - 1 and longest_run(light[below]) >= fringe and steps < SCROLL_EDGE_MAX:
        below += 1
        steps += 1
    if above < 0 or below >= h:
        return 0
    top, bottom = above + 1, below - 1

    span = below - above
    for y in range(top, bottom + 1):
        t = (y - above) / span
        a[y] = (a[above] * (1 - t) + a[below] * t).round().astype(a.dtype)
    return bottom - top + 1


def main() -> int:
    if not SRC.is_dir():
        print(f"! Dossier introuvable : {SRC}")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    entries = []

    for stem, filename, label in BOARDS:
        path = SRC / filename
        if not path.exists():
            print(f"  - {filename} introuvable, ignore")
            continue

        # Les panneaux sont en RGBA avec un fond noir opaque : on aplatit sur
        # du noir pour eviter un liseré clair sur le site sombre.
        original = Image.open(path)
        if original.mode == "RGBA":
            flat = Image.new("RGB", original.size, (8, 10, 10))
            flat.paste(original, (0, 0), original)
            original = flat
        else:
            original = original.convert("RGB")

        # On retire les traces de capture avant tout redimensionnement :
        # a pleine resolution, les bornes sont nettes.
        pixels = np.array(original)
        bar_w, bar_h = mask_top_bar(pixels)
        healed = heal_scrollbar(pixels)
        original = Image.fromarray(pixels)
        notes = []
        if bar_h:
            notes.append(f"bandeau {bar_w}x{bar_h}")
        if healed:
            notes.append(f"barre {healed}px")

        sizes = []
        for width in WIDTHS:
            width = min(width, original.size[0])
            if any(width == w for w, _ in sizes):
                continue
            height = max(1, round(original.size[1] * width / original.size[0]))
            resized = original.resize((width, height), Image.LANCZOS)
            sizes.append((width, height))

            resized.save(OUT / f"{stem}-{width}.webp", "WEBP", quality=86, method=6)
            try:
                resized.save(OUT / f"{stem}-{width}.avif", "AVIF", quality=62, speed=4)
            except Exception as exc:
                print(f"    ! AVIF ignore pour {stem}-{width} ({exc})")

        entries.append((stem, label, sizes))
        detail = ("  [" + ", ".join(notes) + "]") if notes else ""
        print(f"  + {stem:17s} <- menu/{filename:16s} "
              f"{original.size[0]}x{original.size[1]}{detail}")

    lines = [
        "/* Genere par tools/make_board_images.py - ne pas modifier a la main. */",
        "/* Les panneaux affiches au comptoir, photographies tels quels. */",
        "window.TACONAAN_BOARDS = [",
    ]
    for stem, label, sizes in entries:
        dims = ", ".join(f"[{w}, {h}]" for w, h in sizes)
        lines.append(f"  {{ stem: '{stem}', label: '{label}', sizes: [{dims}] }},")
    lines.append("];")
    (OUT / "boards.js").write_text("\n".join(lines) + "\n", encoding="utf-8")

    weight = sum((OUT / f"{s}-{w}.webp").stat().st_size
                 for s, _, sz in entries for w, _ in sz) // 1024
    print(f"\n  = boards.js ({len(entries)} panneaux, {weight} Ko en WebP)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
