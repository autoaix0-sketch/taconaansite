#!/usr/bin/env python3
"""
Taco Naan - detourage des quatre vignettes de la carte restees en photo.

Sur la carte, chaque fiche porte une vignette. Neuf d'entre elles sont
detourees : le plat flotte sur le noir de la page, avec une ombre portee.
Quatre ne l'etaient pas - Assiettes, Bowls, Tex-Mex et Menu Kids - et
arrivaient donc en rectangle encadre au milieu des autres (data-kind="photo"
dans assets/css/site.css). C'est ce que ce script corrige : il refait les
quatre en PNG detoure, avec un canal alpha, pour qu'elles se tiennent comme
les neuf autres.

Chaque image demande sa propre methode, parce que chaque fond est different :

  assiette  - photo du plat sur une table en bois floue. Le bois est chaud et
              tres proche de la viande : un seuil de couleur seul deborde a
              tous les coups. On repere donc le blanc de l'assiette, on ajuste
              une ellipse sur son bord (l'assiette vue de biais est une
              ellipse), et on y ajoute ce qui depasse en haut - salade, frites,
              tomates - en restant colle a l'ellipse sur les cotes.

  bowl      - decoupe dans le panneau du comptoir. Le bol est un cercle vu du
              dessus : on cherche le meilleur cercle sur la tache chaude et on
              s'arrete la. Rien a deviner de plus.

  texmex    - decoupe dans le meme panneau. Les wings y sont posees en
              autocollant, avec un liseré blanc ferme tout autour. On remplit
              l'interieur de ce liseré : ni le prix en jaune ni le filet
              vertical a cote ne peuvent entrer.

  enfant    - la boite Kiddy Box, deja detouree autrefois puis mise de cote.
              Reprise telle quelle depuis _work/sources : la meme boite que
              celle du panneau, mais a 348 px au lieu de 114.

Les quatre passent par warm_grade et add_grain (optimize_images.py), comme les
vignettes qu'elles remplacent : sans ca la boite du menu enfant revient en bleu
ciel au milieu d'une page noir et jaune. Le grain s'applique sous l'alpha, il
ne touche donc pas au bord.

Le resultat est ecrit dans assets/img/cutouts.js, qui complete le manifeste
comme extras.js et photos.js. Il est charge en dernier dans index.html : ses
quatre cles ont donc le dernier mot.

Usage :  python tools/make_category_cutouts.py
Dependances : Pillow, numpy et scipy.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
from optimize_images import add_grain, warm_grade  # meme traitement que les autres photos

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "img"
SRC = ROOT / "_work" / "sources"

# Les vignettes sont affichees entre 4.5rem et 7rem de large (site.css). Deux
# tailles suffisent : la seconde couvre les ecrans a forte densite. On
# n'agrandit jamais au-dela de la source - les decoupes du panneau font a peine
# 130 px, les gonfler ne rendrait que du flou.
WIDTHS = [160, 320]


# --------------------------------------------------------------------------
# Outils communs
# --------------------------------------------------------------------------

def load_board(name: str) -> Image.Image:
    """Ouvre un panneau du comptoir, aplati sur le noir du site."""
    im = Image.open(SRC / "boards" / name)
    if im.mode == "RGBA":
        flat = Image.new("RGB", im.size, (8, 10, 10))
        flat.paste(im, (0, 0), im)
        return flat
    return im.convert("RGB")


def channels(rgb: Image.Image):
    """Renvoie (tableau, luminance, saturation) - les trois mesures utilisees
    partout ci-dessous pour separer un sujet de son fond."""
    a = np.asarray(rgb).astype(float)
    hi = a.max(axis=2)
    lo = a.min(axis=2)
    return a, a.mean(axis=2), np.where(hi > 0, (hi - lo) / np.maximum(hi, 1), 0.0)


def soften(mask: np.ndarray, blur: float = 1.1) -> np.ndarray:
    """Adoucit le bord d'un masque binaire sur un pixel.

    Un alpha franc laisse un escalier bien visible sur le noir de la page,
    surtout sur les decoupes du panneau qui font 130 px de large.
    """
    return np.clip((ndimage.gaussian_filter(mask.astype(float), blur) - 0.45) * 4.0, 0, 1)


def to_rgba(rgb: Image.Image, alpha: np.ndarray) -> Image.Image:
    """Assemble l'image detouree, grade comme les autres photos du site, et la
    rogne sur son contenu."""
    graded = add_grain(warm_grade(rgb))
    band = Image.fromarray((alpha * 255).astype(np.uint8))
    out = Image.merge("RGBA", (*graded.split(), band))
    box = band.point(lambda v: 255 if v > 6 else 0).getbbox()
    return out.crop(box) if box else out


def fit_ellipse(points: np.ndarray):
    """Ajuste une ellipse sur un nuage de points (Fitzgibbon).

    Renvoie une fonction inside(fx, fy) qui dit, pour chaque pixel, s'il est
    dans l'ellipse dilatee de fx en largeur et fy en hauteur.
    """
    x, y = points[:, 0], points[:, 1]
    ox, oy = x.mean(), y.mean()
    scale = max(x.std(), y.std())
    xn, yn = (x - ox) / scale, (y - oy) / scale

    design = np.column_stack([xn * xn, xn * yn, yn * yn, xn, yn, np.ones_like(xn)])
    constraint = np.zeros((6, 6))
    constraint[0, 2] = constraint[2, 0] = 2
    constraint[1, 1] = -1
    values, vectors = np.linalg.eig(np.linalg.solve(design.T @ design, constraint))
    a, b, c, d, e, f = np.real(vectors[:, np.argmax(np.real(values))])
    cx, cy = np.linalg.solve(np.array([[2 * a, b], [b, 2 * c]]), [-d, -e])

    def inside(shape, fx: float, fy: float | None = None) -> np.ndarray:
        fy = fx if fy is None else fy
        yy, xx = np.mgrid[:shape[0], :shape[1]]
        u = cx + ((xx - ox) / scale - cx) / fx
        v = cy + ((yy - oy) / scale - cy) / fy
        return (a * u * u + b * u * v + c * v * v + d * u + e * v + f) * np.sign(a) <= 0

    return inside, cy * scale + oy


# --------------------------------------------------------------------------
# Assiettes - l'assiette blanche sur la table en bois
# --------------------------------------------------------------------------

def cut_assiette() -> Image.Image:
    im = Image.open(SRC / "products" / "assiette V2.jpeg").convert("RGB")
    a, lum, sat = channels(im)
    red, green, blue = a[..., 0], a[..., 1], a[..., 2]
    h, w = lum.shape

    # 1. le blanc de l'assiette : clair et quasi neutre. Le bois clair du bas
    #    monte a la meme luminosite mais reste nettement plus sature.
    white = ndimage.binary_opening((lum > 188) & (sat < 0.20), np.ones((5, 5)))
    label, count = ndimage.label(white)
    sizes = ndimage.sum(white, label, range(1, count + 1))
    rim = ndimage.binary_closing(label == (np.argmax(sizes) + 1), np.ones((9, 9)))

    # 2. l'ellipse passe par le bord exterieur de ce blanc : le point le plus
    #    bas de chaque colonne, le plus a gauche et le plus a droite de chaque
    #    ligne. Le haut de l'assiette est cache par la viande, l'arc du bas
    #    suffit a fixer l'ellipse.
    ys, xs = np.nonzero(rim)
    edge = [(x, ys[xs == x].max()) for x in np.unique(xs)]
    for y in np.unique(ys):
        row = xs[ys == y]
        edge += [(row.min(), y), (row.max(), y)]
    inside, center_y = fit_ellipse(np.array(edge, float))

    plate = inside((h, w), 1.09)

    # 3. ce qui deborde par-dessus le bord : salade, tomates, frites. On les
    #    cherche haut seulement, et sans marge sur les cotes - a droite et a
    #    gauche il n'y a que du bois, chaud comme des frites.
    yy = np.mgrid[:h, :w][0]
    above = (
        ((green > red + 6) & (sat > 0.16))                                        # salade, concombre
        | ((red > green * 1.45) & (red > 100) & (sat > 0.42))                     # tomate
        | ((red > 155) & (green > 125) & (blue < green * 0.72)
           & (sat > 0.38) & (lum > 130))                                          # frites
    ) & inside((h, w), 1.01, 1.30) & (yy < center_y)
    above = ndimage.binary_closing(above, np.ones((7, 7)))

    label, count = ndimage.label(above)
    keep = np.zeros_like(plate)
    for i in range(1, count + 1):
        blob = label == i
        # une tache n'est retenue que si elle est grande et qu'elle mord
        # vraiment sur l'assiette : le bois isole ne passe pas.
        if blob.sum() > 800 and (blob & plate).sum() > 60:
            keep |= blob

    mask = ndimage.binary_fill_holes(ndimage.binary_closing(plate | keep, np.ones((9, 9))))
    label, count = ndimage.label(mask)
    sizes = ndimage.sum(mask, label, range(1, count + 1))
    mask = label == (np.argmax(sizes) + 1)

    return to_rgba(im, soften(mask, 1.2))


# --------------------------------------------------------------------------
# Bowls - le bol vu du dessus, decoupe dans le panneau Burgers
# --------------------------------------------------------------------------

BOWL_BOX = (0.5848, 0.5212, 0.7249, 0.7303)   # meme cadrage que make_product_crops.py


def cut_bowl() -> Image.Image:
    board = load_board("burger.png")
    bw, bh = board.size
    left, top, right, bottom = BOWL_BOX
    pad = 8
    im = board.crop((round(bw * left) - pad, round(bh * top) - pad,
                     round(bw * right) + pad, round(bh * bottom) + pad))
    a, lum, sat = channels(im)
    h, w = lum.shape

    # Le bol et ce qu'il contient sont chauds et satures ; le fond du panneau,
    # derriere, est un flou verdatre.
    warm = (sat > 0.40) & ((a[..., 0] - a[..., 2]) > 45) & (a.max(axis=2) > 70)
    warm = ndimage.binary_fill_holes(ndimage.binary_closing(warm, np.ones((5, 5))))

    label, count = ndimage.label(warm)
    seed = label[h // 2, w // 2]
    if seed == 0:
        sizes = ndimage.sum(warm, label, range(1, count + 1))
        seed = int(np.argmax(sizes)) + 1
    blob = label == seed

    # Meilleur cercle sur cette tache : on balaie centre et rayon, et on penalise
    # deux fois ce qui deborde. Sans cette penalite le cercle avale une couronne
    # de fond tout autour du bol.
    ys, xs = np.nonzero(blob)
    cy0, cx0 = ys.mean(), xs.mean()
    r0 = np.sqrt(blob.sum() / np.pi)
    yy, xx = np.ogrid[:h, :w]
    best = None
    for dy in np.arange(-10, 10.5, 1.0):
        for dx in np.arange(-10, 10.5, 1.0):
            dist2 = (yy - (cy0 + dy)) ** 2 + (xx - (cx0 + dx)) ** 2
            for factor in np.arange(0.80, 1.06, 0.02):
                radius = r0 * factor
                disc = dist2 <= radius * radius
                score = (disc & blob).sum() - 2.0 * (disc & ~blob).sum()
                if best is None or score > best[0]:
                    best = (score, cx0 + dx, cy0 + dy, radius)

    _, cx, cy, radius = best
    dist = np.sqrt((np.mgrid[:h, :w][0] - cy) ** 2 + (np.mgrid[:h, :w][1] - cx) ** 2)
    return to_rgba(im, np.clip((radius + 0.5 - dist) * 1.6, 0, 1))


# --------------------------------------------------------------------------
# Tex-Mex - les wings en autocollant, decoupees dans le meme panneau
# --------------------------------------------------------------------------

TEXMEX_BOX = (0.4775, 0.3182, 0.5692, 0.4318)


def cut_texmex() -> Image.Image:
    board = load_board("burger.png")
    bw, bh = board.size
    left, top, right, bottom = TEXMEX_BOX
    margin = 0.055   # large : il faut voir tout le liseré, pas seulement le plat
    im = board.crop((round(bw * (left - margin)), round(bh * (top - margin)),
                     round(bw * (right + margin)), round(bh * (bottom + margin))))
    a, _, _ = channels(im)
    hi, lo = a.max(axis=2), a.min(axis=2)

    # Le liseré blanc de l'autocollant. Il se coupe par endroits, la ou une aile
    # sombre passe dessous : on le dilate d'abord pour le refermer, puis on
    # remplit, puis on revient a la taille d'origine.
    stroke = (lo > 150) & ((hi - lo) < 45)
    grow = np.ones((5, 5), bool)
    filled = ndimage.binary_fill_holes(ndimage.binary_dilation(stroke, grow))

    label, count = ndimage.label(filled)
    sizes = ndimage.sum(filled, label, range(1, count + 1))
    sticker = label == (np.argmax(sizes) + 1)

    # Le prix "+ MENU 7,00 EUR" est jaune, pas blanc : il n'a jamais rejoint le
    # liseré, il tombe donc de lui-meme.
    mask = ndimage.binary_fill_holes(ndimage.binary_erosion(sticker, grow) | (stroke & sticker))

    # On rentre ensuite sous le liseré : garde, il ferait un contour blanc
    # d'autocollant autour des wings, seul de son espece parmi neuf vignettes
    # detourees a ras.
    mask = ndimage.binary_erosion(mask, np.ones((7, 7)))
    return to_rgba(im, soften(mask, 0.8))


# --------------------------------------------------------------------------
# Menu Kids - la boite Kiddy Box, deja detouree
# --------------------------------------------------------------------------

def cut_enfant() -> Image.Image:
    im = Image.open(SRC / "enfant-kiddy-box.png").convert("RGBA")
    alpha = np.asarray(im.getchannel("A")).astype(float) / 255.0
    return to_rgba(im.convert("RGB"), alpha)


# --------------------------------------------------------------------------

CUTOUTS = [
    ("assiette-cut", cut_assiette),
    ("bowl-cut",     cut_bowl),
    ("texmex-cut",   cut_texmex),
    ("enfant-cut",   cut_enfant),
]


def export(im: Image.Image, stem: str) -> list[tuple[int, int]]:
    sizes: list[tuple[int, int]] = []
    for width in WIDTHS:
        width = min(width, im.size[0])
        if any(width == done for done, _ in sizes):
            continue
        height = max(1, round(im.size[1] * width / im.size[0]))
        resized = im.resize((width, height), Image.LANCZOS)
        sizes.append((width, height))

        resized.save(OUT / f"{stem}-{width}.webp", "WEBP", quality=86, method=6)
        try:
            resized.save(OUT / f"{stem}-{width}.avif", "AVIF", quality=62, speed=4)
        except Exception as exc:
            print(f"    ! AVIF ignore pour {stem}-{width} ({exc})")
    return sizes


def main() -> int:
    if not (ROOT / "index.html").exists():
        print(f"! Lance depuis la racine du projet. ROOT vu : {ROOT}")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    entries = []

    for stem, make in CUTOUTS:
        try:
            im = make()
        except FileNotFoundError as exc:
            print(f"  - {stem} : source introuvable ({exc}), ignore")
            continue
        sizes = export(im, stem)
        entries.append((stem, sizes))
        print(f"  + {stem:14s} {im.size[0]}x{im.size[1]} -> " +
              ", ".join(f"{w}x{h}" for w, h in sizes))

    lines = [
        "/* Genere par tools/make_category_cutouts.py - ne pas modifier a la main. */",
        "/* Les quatre vignettes de la carte qui restaient en photo rectangulaire,",
        "   refaites en detoure. Charge apres extras.js et photos.js : ces cles-la",
        "   ont le dernier mot. */",
        "window.TACONAAN_IMAGES = Object.assign(window.TACONAAN_IMAGES || {}, {",
    ]
    for stem, sizes in entries:
        dims = ", ".join(f"[{w}, {h}]" for w, h in sizes)
        lines.append(f"  {stem.replace('-', '_')}: "
                     f"{{ stem: '{stem}', kind: 'cutout', sizes: [{dims}] }},")
    lines.append("});")
    (OUT / "cutouts.js").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  = cutouts.js ({len(entries)} vignettes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
