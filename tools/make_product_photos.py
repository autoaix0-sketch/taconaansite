#!/usr/bin/env python3
"""
Taco Naan - photos produit exportees depuis l outil de design.

Les fichiers de _work/sources/products/desserts, pains au choix, viandes au
choix, burgers et soda viennent d un export en JPEG : le damier de
transparence et le libelle du plat ("NAAN MIEL", "CORDON BLEU"...) sont donc
de vrais pixels, pas un canal alpha. Tels quels ils ne sont pas utilisables
sur le site.

Ce script fait trois choses :
  1. il retrouve les deux gris du damier sur le bord, et rend le fond transparent
     (le liseré blanc qui entoure chaque produit arrete le remplissage) ;
  2. il jette le libelle : une fois le fond parti, le texte forme des taches
     separees, sous le produit. On ne garde que les taches qui croisent la bande
     verticale du sujet principal ;
  3. il exporte en AVIF + WebP et ecrit assets/img/photos.js.

photos.js complete window.TACONAAN_IMAGES, exactement comme extras.js. Il est
volontairement separe de manifest.js (tools/optimize_images.py) et de extras.js
(tools/make_product_crops.py) : regenerer l un n efface jamais les autres.

tools/optimize_images.py lit ses RECIPES depuis _work/sources/ : il n y a
plus rien a corriger avant de le relancer.

Usage :  python tools/make_product_photos.py
Dependances : Pillow et numpy.
"""

from __future__ import annotations

import sys
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from optimize_images import add_grain, warm_grade  # meme traitement que les autres photos

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
SRC = ROOT / "_work" / "sources" / "products"

# Largeur de travail : au-dela, on ne gagne aucun detail utile et le detourage
# devient lent pour rien.
WORK_MAX = 1000

# Tolerance autour des gris du damier. Le liseré blanc du produit reste loin
# devant, donc on peut etre large sans mordre sur le sujet.
GREY_PAD = 22

# Elargissement du fond (voir grow_background). La bande GREY_PAD ne voit que
# le damier lui-meme ; elle laisse derriere elle la rampe d anti-aliasing et
# l ombre portee, qui restent opaques et se lisent en halo gris clair sur le
# noir du site. On repart donc du fond sur et on avance d un pixel a la fois.
BG_GROW_STEPS   = 44   # portee maximale, en pixels
BG_GROW_NEUTRAL = 24   # ecart max entre canaux : au-dela, c est de la couleur
BG_GROW_DELTA   = 18   # marche de luminosite max d un pixel au suivant
BG_GROW_FLOOR   = 140  # plancher par defaut, quand le damier n'est pas reconnu

# Le damier n'est pas toujours clair. Celui des burgers est un gris 91/143,
# entierement sous PEEL_LUM et sous BG_GROW_FLOOR : ni l'epluchage ni
# l'elargissement ne le voyaient, et il restait en dents sombres sous les pains.
# Les seuils sont donc cales sur les tons releves plutot que fixes d'avance.
# On ignore les tons tres sombres : un fond noir (les viandes, 0/4) est deja
# emporte par le remplissage, et l'eplucher rongerait la viande grillee.
TONE_FLOOR     = 60   # en dessous, on ne considere pas que c'est un damier
TONE_TOLERANCE = 16   # ecart admis autour d'un ton releve
TONE_MARGIN    = 35   # de combien on descend sous le ton le plus sombre

# Les dents qui subsistent contre le sujet ne sont ni l'un ni l'autre ton : ce
# sont des melanges d'anti-aliasing, et un test de couleur ne peut pas les
# voir. En revanche elles sont parfaitement plates - un carreau, c'est une
# seule valeur - alors qu'une creme, un pain ou une assiette ont toujours du
# modele. C'est la platitude qu'on mesure, pas la teinte.
FLAT_RADIUS = 2      # demi-cote de la fenetre de mesure
FLAT_LIMIT  = 3.2    # ecart-type local au-dela duquel c'est de la matiere
FLAT_REACH  = 70     # on ne descend pas plus bas que le ton sombre moins ca

# Ce qui reste apres tout ca tient en quelques pixels : de fines dents grises
# accrochees au bord, larges de quatre ou cinq pixels. Une ouverture
# morphologique les enleve sans toucher a la silhouette - c'est exactement
# l'outil pour retirer une excroissance fine. On ne l'applique qu'aux pixels
# neutres : le brin de romarin des merguez est vert, il ne bouge pas.
TEETH_SIZE = 9       # taille du noyau d'ouverture, impair

# Epluchage du lisere (voir peel_halo). Chaque produit de la planche source est
# entoure d un trait blanc de decoupe, et le damier vient buter dessus : c est
# ce trait qui arrete le remplissage, et c est lui qu on voit ensuite en halo
# clair sur le noir du site. On le retire depuis le bord du sujet vers
# l interieur, en s arretant des qu on rencontre de la vraie matiere.
PEEL_STEPS   = 3    # epaisseur retiree sur le seul critere de clarte
PEEL_TONE_STEPS = 12  # au-dela, on ne retire plus que la couleur exacte du damier
PEEL_LUM     = 172  # en dessous, c est du produit, pas du lisere
PEEL_NEUTRAL = 22   # ecart max entre canaux

# Damier vu au travers du sujet (voir checker_through). Le verre du tiramisu
# est transparent : le damier se lit dedans, loin du bord, donc ni le
# remplissage ni l epluchage ne peuvent l atteindre. On le reconnait a sa
# signature - ses deux gris se cotoient - et on le rend transparent lui aussi.
# Le noir de la page passe alors au travers du verre, ce qui est juste.
THROUGH_WINDOW = 9   # fenetre de voisinage, en pixels
THROUGH_TONE   = 7   # ecart max a l un des deux gris du damier

THUMB = [240, 480]
LARGE = [480, 960]

# stem, fichier source, kind, recadrage (gauche, haut, droite, bas) en fractions
# ou None, largeurs, et une 6e case optionnelle d options :
#   floor     gris le plus sombre encore pris pour du fond
#   labels    False si l image n a pas de libelle a jeter
#   full_res  detourer avant de reduire (le redimensionnement melange les
#             carreaux du damier avec le sujet et laisse un lisere)
# kind "cutout" = fond detoure ; kind "photo" = vraie photo, gardee telle
# quelle et passee au grain chaud du reste du site.
PHOTOS = [
    # --- desserts, tous a 3 EUR -------------------------------------------
    ("desserts-tiramisu",      "desserts/tiramisu.jpg",        "cutout", None, THUMB),
    ("desserts-tarte",         "desserts/tarte.jpg",           "cutout", None, THUMB),
    ("desserts-miel",          "desserts/miel.jpg",            "cutout", None, THUMB),
    ("desserts-nutella",       "desserts/nutella.jpg",         "cutout", None, THUMB),
    ("desserts-fromage",       "desserts/naan.jpg",            "cutout", None, THUMB),

    # --- le pain au choix --------------------------------------------------
    # Ici le libelle touche le pain : la detection ne peut pas l isoler, on
    # coupe donc juste au-dessus.
    ("pains-pain-classique",   "pains au choix/pain classique.jpg", "cutout", (0, 0, 1, 0.63), THUMB),
    ("pains-galette",          "pains au choix/galette.jpg",        "cutout", (0, 0, 1, 0.578), THUMB),
    ("pains-cheese-naan",      "pains au choix/pain naan.jpg",      "cutout", (0, 0, 1, 0.59), THUMB),

    # --- les viandes au choix -----------------------------------------------
    # steak.jpg (l export d origine) porte un filigrane Vecteezy en travers de
    # l image et reste inutilisable. steak.png est une autre photo, sans
    # filigrane, ajoutee le 20/09/2026 : meme traitement damier que les autres.
    ("viandes-kebab",          "viandes au choix/kebab.jpeg",        "cutout", None, THUMB),
    ("viandes-viande-hachee",  "viandes au choix/viande hachee.jpeg","cutout", None, THUMB),
    ("viandes-poulet",         "viandes au choix/poulet.jpeg",       "cutout", None, THUMB),
    ("viandes-cordon-bleu",    "viandes au choix/cordon bleu.jpeg",  "cutout", None, THUMB),
    ("viandes-merguez",        "viandes au choix/merguez.jpeg",      "cutout", None, THUMB),
    ("viandes-nuggets",        "viandes au choix/nuggets.jpeg",      "cutout", None, THUMB),
    ("viandes-tenders",        "viandes au choix/tenders.jpeg",      "cutout", None, THUMB),
    ("viandes-falafel",        "viandes au choix/falafel.jpeg",      "cutout", None, THUMB),
    ("viandes-steak",          "viandes au choix/steak.png",         "cutout", None, THUMB),

    # --- les boissons en canette ------------------------------------------
    ("soda-coca",              "soda/coca cola.jpg",           "cutout", None, THUMB),
    ("soda-coca-zero",         "soda/coca zero.jpg",           "cutout", None, THUMB),
    ("soda-lipton",            "soda/lipton.jpg",              "cutout", None, THUMB),
    ("soda-pepsi",             "soda/pepsi.jpg",               "cutout", None, THUMB),

    # --- les burgers -------------------------------------------------------
    ("burgers-cheese",         "burgers/cheese burger.jpg",    "cutout", None, THUMB),
    ("burgers-double-cheese",  "burgers/double cheese.jpg",    "cutout", None, THUMB),
    ("burgers-chicken",        "burgers/chicken burger.jpg",   "cutout", None, THUMB),
    ("burgers-big",            "burgers/big burger.jpg",       "cutout", None, THUMB),
    ("burgers-supreme",        "burgers/supreme.jpg",          "cutout", None, THUMB),
    ("burgers-double-chicken", "burgers/double chicken.jpg",   "cutout", None, THUMB),

    # --- les trois grandes ------------------------------------------------
    ("assiette-v2",            "assiette V2.jpeg",             "photo",  None, LARGE),
    ("barquette-hd",           "barquette.jpeg",               "cutout", None, LARGE),
    # Le hero est le seul visuel a montrer trois objets separes (canette,
    # frites, sandwich) et a porter une frise grise sous le sandwich.
    ("naan-hero",              "menu cheese naan.jpeg",        "cutout", None, LARGE,
     {"floor": 140, "labels": False, "full_res": True}),
]


# ---------------------------------------------------------------------------
# Detourage
# ---------------------------------------------------------------------------

def components(mask: np.ndarray) -> np.ndarray:
    """Etiquette les zones connexes de mask. Zero = hors zone.

    Passage par lignes : on repere les segments vrais de chaque ligne et on
    les relie a ceux de la ligne precedente. Beaucoup plus rapide qu un
    parcours pixel par pixel, et sans dependance en plus.
    """
    h, w = mask.shape
    labels = np.zeros((h, w), np.int32)
    parent = {0: 0}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    nxt = 1
    previous: list[tuple[int, int, int]] = []

    for y in range(h):
        row = mask[y]
        if not row.any():
            previous = []
            continue

        edges = np.diff(row.astype(np.int8))
        starts = (np.flatnonzero(edges == 1) + 1).tolist()
        ends = (np.flatnonzero(edges == -1) + 1).tolist()
        if row[0]:
            starts.insert(0, 0)
        if row[-1]:
            ends.append(w)

        current = []
        for start, end in zip(starts, ends):
            found = 0
            for p_start, p_end, p_label in previous:
                if p_start < end and start < p_end:
                    if found == 0:
                        found = p_label
                    else:
                        union(found, p_label)
            if found == 0:
                found = nxt
                parent[found] = found
                nxt += 1
            labels[y, start:end] = found
            current.append((start, end, found))
        previous = current

    if nxt == 1:
        return labels

    table = np.arange(nxt, dtype=np.int32)
    for label in range(1, nxt):
        table[label] = find(label)
    return table[labels]


def grey_tones(rgb: Image.Image) -> list[int]:
    """Les deux gris du damier, releves sur le bord de l image."""
    a = np.asarray(rgb).astype(int)
    border = np.concatenate([a[0, :], a[-1, :], a[:, 0], a[:, -1]])
    greys = border[(border.max(1) - border.min(1)) <= 12][:, 0]
    if not len(greys):
        return []

    clusters: list[list[int]] = []
    for value, count in Counter(greys.tolist()).most_common():
        for cluster in clusters:
            if abs(cluster[0] - value) <= 14:
                cluster[1] += count
                break
        else:
            clusters.append([value, count])
    clusters.sort(key=lambda c: -c[1])
    return [c[0] for c in clusters[:2]]


def checker_tones(tones: list[int]) -> list[int]:
    """Les tons du damier assez clairs pour etre traites comme du fond."""
    return [t for t in tones if t >= TONE_FLOOR]


def box_mean(values: np.ndarray, radius: int) -> np.ndarray:
    """Moyenne sur une fenetre carree, par image integrale."""
    pad = np.pad(values, radius, mode="edge")
    total = pad.cumsum(0).cumsum(1)
    total = np.pad(total, ((1, 0), (1, 0)))
    h, w = values.shape
    side = 2 * radius + 1
    box = (total[side:side + h, side:side + w] - total[0:h, side:side + w]
           - total[side:side + h, 0:w] + total[0:h, 0:w])
    return box / (side * side)


def flat_local(lum: np.ndarray, radius: int = FLAT_RADIUS) -> np.ndarray:
    """Vrai la ou l'image ne bouge pas : un aplat, donc un carreau de damier."""
    mean = box_mean(lum, radius)
    var = np.maximum(box_mean(lum * lum, radius) - mean * mean, 0.0)
    return np.sqrt(var) <= FLAT_LIMIT


def strip_teeth(a: np.ndarray, subject: np.ndarray,
                size: int = TEETH_SIZE) -> np.ndarray:
    """Retire les dents de damier restees accrochees au bord du sujet.

    Une ouverture - erosion puis dilatation - efface ce qui est plus mince que
    le noyau et remet le reste a sa taille. Seuls les pixels neutres perdus au
    passage sont reellement retires, pour ne pas manger une feuille de salade
    ou une brindille, qui sont colorees.
    """
    mask = Image.fromarray((subject * 255).astype("uint8"), "L")
    opened = mask.filter(ImageFilter.MinFilter(size)).filter(ImageFilter.MaxFilter(size))
    lost = subject & ~(np.asarray(opened) > 127)
    neutral = (a.max(2) - a.min(2)) <= PEEL_NEUTRAL
    return subject & ~(lost & neutral)


def near_tone(lum: np.ndarray, tones: list[int]) -> np.ndarray:
    """Vrai la ou la luminosite colle a l'un des tons du damier."""
    hit = np.zeros(lum.shape, bool)
    for tone in tones:
        hit |= np.abs(lum - tone) <= TONE_TOLERANCE
    return hit


def grow_background(a: np.ndarray, bg: np.ndarray, tones: list[int],
                    steps: int = BG_GROW_STEPS) -> np.ndarray:
    """Etend le fond deja reconnu sur la rampe d anti-aliasing et l ombre.

    La bande de gris de cutout() est volontairement etroite : elargie d un
    bloc, elle mordrait sur les sujets clairs (le pain naan, la sauce blanche,
    le bun). On part donc du fond sur - celui qui touche le bord - et on
    avance d un pixel a la fois, en n avalant qu un voisin neutre, clair, et
    proche en luminosite du fond qu il touche. Une arete franche, c est-a-dire
    le bord reel du produit, arrete la progression d elle-meme.
    """
    lum = a.mean(2)
    neutral = (a.max(2) - a.min(2)) <= BG_GROW_NEUTRAL
    # Le damier qui passe dans l'ombre portee du plat descend tres bas : sous
    # le naan au miel il tombe a 91, alors que ses deux tons sont a 205 et 253.
    # Se caler sur les tons laissait donc toute l'ombre dans le sujet, en dents
    # grises. On descend jusqu'au plancher general ; ce qui protege le plat,
    # ce n'est pas le seuil mais la marche maximale d'un pixel au suivant -
    # une ombre monte en pente douce, un bord d'aliment est une falaise.
    floor = TONE_FLOOR if checker_tones(tones) else BG_GROW_FLOOR
    free = neutral & (lum >= floor) & ~bg

    for _ in range(steps):
        if not free.any():
            break
        gained = np.zeros_like(bg)
        for axis, shift in ((0, 1), (0, -1), (1, 1), (1, -1)):
            near_bg = np.roll(bg, shift, axis)
            near_lum = np.roll(lum, shift, axis)
            # np.roll est circulaire : on coupe la ligne revenue de l autre bord.
            cut = [slice(None), slice(None)]
            cut[axis] = 0 if shift > 0 else -1
            near_bg = near_bg.copy()
            near_bg[tuple(cut)] = False
            gained |= near_bg & free & (np.abs(lum - near_lum) <= BG_GROW_DELTA)
        if not gained.any():
            break
        bg = bg | gained
        free &= ~gained
    return bg


def checker_through(a: np.ndarray, tones: list[int]) -> np.ndarray:
    """Les pixels de damier restes a l interieur du sujet.

    La signature du damier, c est que ses deux gris se touchent : un pixel du
    carreau clair a toujours un carreau sombre dans son voisinage immediat, et
    l inverse. Une creme ou un pain clair n a qu un ton autour de lui, et
    passe donc au travers de ce test sans etre touche.
    """
    if len(tones) < 2:
        return np.zeros(a.shape[:2], bool)

    flat = (a.max(2) - a.min(2)) <= 12
    lum = a.mean(2)
    near = [flat & (np.abs(lum - t) <= THROUGH_TONE) for t in tones[:2]]

    def spread(mask):
        img = Image.fromarray((mask * 255).astype("uint8"), "L")
        return np.asarray(img.filter(ImageFilter.MaxFilter(THROUGH_WINDOW))) > 0

    both = spread(near[0]) & spread(near[1])
    return (near[0] | near[1]) & both


def peel_halo(a: np.ndarray, subject: np.ndarray, tones: list[int],
              steps: int = PEEL_STEPS) -> np.ndarray:
    """Retire le lisere clair reste sur le contour du sujet.

    On avance depuis le bord du sujet vers l interieur, un pixel a la fois, et
    on ne retire qu un pixel de contour clair et neutre. Le premier pixel
    colore ou sombre - de la vraie matiere - arrete l epluchage sur place, si
    bien qu un pain pale ou une creme ne sont pas ronges : leur texture les
    sort tout de suite de la fourchette.
    """
    lum = a.mean(2)
    neutral = (a.max(2) - a.min(2)) <= PEEL_NEUTRAL
    usable = checker_tones(tones)
    floor = max(TONE_FLOOR, min(usable) - FLAT_REACH) if usable else 256
    # Pile sur un ton, ou bien un aplat clair colle au sujet : dans les deux
    # cas c'est du damier, jamais de l'aliment.
    exact = neutral & (near_tone(lum, usable) | (flat_local(lum) & (lum >= floor)))
    # Deux passes. La premiere retire ce qui est simplement clair et neutre :
    # c'est le trait de decoupe, et trois pixels suffisent. La seconde continue
    # bien plus loin mais ne mord plus que sur la couleur exacte du damier -
    # les dents qui restent sous un pain ou un verre font parfois dix pixels,
    # et aucun aliment n'est a la fois plat, neutre et pile sur ce ton.
    phases = [(steps, exact | (neutral & (lum >= PEEL_LUM))),
              (PEEL_TONE_STEPS, exact)]

    for limit, removable in phases:
      for _ in range(limit):
        border = np.zeros_like(subject)
        for axis, shift in ((0, 1), (0, -1), (1, 1), (1, -1)):
            outside = np.roll(~subject, shift, axis)
            cut = [slice(None), slice(None)]
            cut[axis] = 0 if shift > 0 else -1
            outside = outside.copy()
            outside[tuple(cut)] = True       # hors cadre compte comme dehors
            border |= outside
        strip = subject & border & removable
        if not strip.any():
            break
        subject = subject & ~strip
    return subject


def cutout(rgb: Image.Image, floor: int | None = None,
           drop_labels: bool = True) -> Image.Image | None:
    """Fond damier (ou blanc) -> transparence, libelle jete au passage.

    floor : gris le plus sombre encore considere comme du fond. Par defaut
      on se cale sur le damier ; le visuel du hero porte en plus une frise
      grise en dents de scie, plus foncee, qu il faut descendre chercher.
    drop_labels : a False, on garde tout ce qui est consequent. A utiliser
      quand l image n a pas de libelle mais plusieurs objets separes (la
      canette du hero est loin au-dessus du sandwich).
    """
    tones = grey_tones(rgb)
    if not tones:
        return None

    a = np.asarray(rgb).astype(int)
    low = floor if floor is not None else min(tones) - GREY_PAD
    high = max(tones) + GREY_PAD
    mean = a.mean(2)
    candidate = ((a.max(2) - a.min(2)) <= 18) & (mean >= low) & (mean <= high)

    # Est fond ce qui est gris ET relie au bord : un gris pris au milieu du
    # produit (une ombre, un reflet) ne part pas.
    marks = components(candidate)
    touching = set(marks[0, :]) | set(marks[-1, :]) | set(marks[:, 0]) | set(marks[:, -1])
    touching.discard(0)
    if not touching:
        return None
    background = grow_background(a, np.isin(marks, list(touching)), tones)
    subject = ~background
    if not subject.any():
        return None

    # Le libelle est sous le produit et n a rien a faire sur une vignette :
    # on garde le plus gros bloc et ce qui partage sa hauteur (la sauce, le
    # brin de persil, la deuxieme galette).
    blobs = components(subject)
    ids, counts = np.unique(blobs[blobs > 0], return_counts=True)

    if not drop_labels:
        keep = ids[counts >= counts.max() * 0.01].tolist()
    else:
        biggest = ids[counts.argmax()]
        rows = np.flatnonzero((blobs == biggest).any(1))
        top, bottom = rows[0], rows[-1]

        keep = []
        for label, count in zip(ids.tolist(), counts.tolist()):
            if count < counts.max() * 0.05:
                continue
            ys = np.flatnonzero((blobs == label).any(1))
            if ys[0] <= bottom and ys[-1] >= top:
                keep.append(label)

    kept = peel_halo(a, np.isin(blobs, keep) & ~checker_through(a, tones), tones)
    kept = strip_teeth(a, kept)
    alpha = np.where(kept, 255, 0).astype("uint8")
    mask = Image.fromarray(alpha, "L")
    # Un pixel d erosion enleve le lisere du damier reste sur le bord, puis un
    # flou tres court adoucit la decoupe. Meme traitement que optimize_images.
    # Sur une grande image, un pixel d erosion ne suffit pas a manger le lisere.
    bite, soften = (5, 1.2) if rgb.size[0] > 1200 else (3, 0.6)
    mask = mask.filter(ImageFilter.MinFilter(bite)).filter(ImageFilter.GaussianBlur(soften))

    out = rgb.convert("RGBA")
    out.putalpha(mask)
    box = mask.point(lambda v: 255 if v > 8 else 0).getbbox()
    return out.crop(box) if box else out


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export(im: Image.Image, stem: str, widths: list[int]) -> list[tuple[int, int]]:
    made: list[tuple[int, int]] = []
    done: set[int] = set()
    for width in widths:
        width = min(width, im.size[0])   # on n agrandit jamais
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


def key(stem: str) -> str:
    text = unicodedata.normalize("NFD", stem).encode("ascii", "ignore").decode()
    return text.replace("-", "_")


def main() -> int:
    if not (ROOT / "index.html").exists():
        print(f"! Lance depuis la racine du projet. ROOT vu : {ROOT}")
        return 1

    entries: list[tuple[str, str, list[tuple[int, int]]]] = []

    for entry in PHOTOS:
        stem, source, kind, crop, widths = entry[:5]
        opts = entry[5] if len(entry) > 5 else {}
        path = SRC / source
        if not path.exists():
            path = ROOT / source
        if not path.exists():
            print(f"  - {source} introuvable, ignore")
            continue

        im = Image.open(path).convert("RGB")
        if crop:
            w, h = im.size
            left, top, right, bottom = crop
            im = im.crop((round(w * left), round(h * top),
                          round(w * right), round(h * bottom)))
        # Le sujet n occupe qu une partie du cadre : on travaille au double de
        # la plus grande largeur demandee pour qu il reste net apres recadrage.
        work = max(WORK_MAX, max(widths) * 2)
        if im.size[0] > work and not opts.get("full_res"):
            im = im.resize((work, round(im.size[1] * work / im.size[0])), Image.LANCZOS)

        if kind == "cutout":
            cut = cutout(im, floor=opts.get("floor"),
                         drop_labels=opts.get("labels", True))
            if cut is None:
                print(f"  ! {stem:22s} fond non reconnu, garde en photo")
                kind = "photo"
            else:
                im = cut
            if im.size[0] > work:
                im = im.resize((work, round(im.size[1] * work / im.size[0])), Image.LANCZOS)

        if kind == "photo":
            im = add_grain(warm_grade(im.convert("RGB")))

        sizes = export(im, stem, widths)
        entries.append((stem, kind, sizes))
        print(f"  + {stem:22s} <- {source:32s} {im.size[0]}x{im.size[1]}")

    lines = [
        "/* Genere par tools/make_product_photos.py - ne pas modifier a la main. */",
        "/* Les photos produit detourees : desserts, pains, viandes, boissons,",
        "   burgers. Complete le manifeste, ne le remplace pas. */",
        "window.TACONAAN_IMAGES = Object.assign(window.TACONAAN_IMAGES || {}, {",
    ]
    for stem, kind, sizes in entries:
        dims = ", ".join(f"[{w}, {h}]" for w, h in sizes)
        lines.append(f"  {key(stem)}: {{ stem: '{stem}', kind: '{kind}', sizes: [{dims}] }},")
    lines.append("});")
    # CRLF comme manifest.js et extras.js, pour ne pas polluer le diff.
    with open(IMG / "photos.js", "w", encoding="utf-8", newline="\r\n") as handle:
        handle.write("\n".join(lines) + "\n")

    print(f"\n  = photos.js ({len(entries)} images)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
