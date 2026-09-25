# Taco Naan — le site

Site vitrine d'un kebab-tacos-naan à Dax. Une seule page, statique, en trois
langues (FR/ES/EN), publiée sur GitHub Pages :
https://autoaix0-sketch.github.io/taconaansite/

## Le seul fichier à modifier au quotidien

**[`data/menu.js`](data/menu.js)** — la carte et les prix. Tout changement de
prix se fait ici, rien d'autre à toucher.

Pour mettre à jour la note Google (2 fois par an) :
**[`data/reviews.js`](data/reviews.js)** — `rating` et `count`. Le score,
le titre de la section avis et le bouton « Voir les … avis » le lisent tous
les trois depuis ce seul fichier, dans les trois langues.

## ⚠️ Après avoir changé un prix : monter le `?v=`

Dans `index.html`, tous les fichiers sont appelés avec `?v=16` à la fin :

```html
<script src="data/menu.js?v=16"></script>
```

Ce numéro est ce qui force le navigateur d'un client déjà venu à retélécharger
le fichier. **Si tu changes un prix sans monter ce numéro, les clients qui sont
déjà venus continuent de voir l'ancien prix**, parfois pendant des jours.

À chaque changement dans `data/menu.js`, `data/reviews.js`, `assets/js/site.js`
ou `assets/css/site.css`, remplace donc partout `?v=16` par `?v=17` (puis 18,
19…) — dans `index.html` **et** dans `404.html` :

```bash
sed -i 's/?v=16"/?v=17"/g' index.html 404.html
```

Les images n'ont pas besoin de ça : elles changent de nom quand elles changent.

## Avant de publier — la liste

```bash
node tools/check-images.mjs     # chaque image déclarée existe bien
python -m http.server 4174      # puis ouvrir http://localhost:4174/
```

Sur la page ouverte, vérifier une fois : les trois langues (FR/ES/EN), les prix
de deux ou trois catégories, le badge « ouvert/fermé », et le bouton Appeler
sur téléphone. Puis `git push` (voir « Déployer » en bas).

## Prévisualiser en local

```bash
python -m http.server 4174
```

puis http://localhost:4174/. (Un `.claude/launch.json` fait la même chose
automatiquement si tu ouvres ce dossier dans Claude Code — il y en a un à la
racine du dépôt et un identique un niveau au-dessus, selon d'où tu ouvres.)

## Comment le site est construit

- `index.html`, `assets/css/site.css`, `assets/js/site.js` — la page, le
  style, le comportement (langues, filtres de carte, horaires, lightbox…).
- `data/menu.js`, `data/reviews.js` — le contenu qui change dans le temps.
- `assets/img/manifest.js`, `extras.js`, `photos.js`, `cutouts.js`,
  `boards.js`, `posters.js` — les dimensions et variantes de chaque image, **générées**
  par les scripts de `tools/`, à ne pas modifier à la main.
- `tools/*.py` — les scripts qui fabriquent les images (recadrage, détourage,
  export AVIF/WebP) depuis les photos d'origine, rangées dans `_work/sources/`
  (hors dépôt, voir plus bas). Voir [`docs/ATELIER.md`](docs/ATELIER.md) pour
  le détail de chacun.
- `tools/check-images.mjs` — le vérificateur ci-dessous.

Après tout changement dans `assets/img/`, `data/menu.js` ou `data/reviews.js` :

```bash
node tools/check-images.mjs
```

vérifie que chaque image déclarée existe bien sur le disque.

## `_work/`

Tout ce qui sert à fabriquer le site mais que le site ne charge jamais : les
photos d'origine (`sources/`), les fichiers maîtres (`masters/`), les lots de
photos à valider (`review/`) et les sauvegardes (`backups/`). Ce dossier n'est
pas versionné (`.gitignore`) — il reste sur ce disque, à côté du dépôt.

## Documentation

- [`docs/ATELIER.md`](docs/ATELIER.md) — comment fabriquer, lancer et
  surveiller les scripts, les assistants et l'automatisation autour du site.
- [`docs/GOOGLE-BUSINESS.md`](docs/GOOGLE-BUSINESS.md) — ce qu'il reste à
  faire côté fiche Google (lien vers le site, avis).
- [`docs/Taco Naan — Menu.md`](docs/Taco%20Naan%20—%20Menu.md) — la carte
  telle que reprise dans `data/menu.js`.

## Déployer

Le dépôt est public sur GitHub. Un `git push` sur `main` met le site à jour
sur GitHub Pages en quelques minutes.
