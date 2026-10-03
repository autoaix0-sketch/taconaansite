# Taco Naan — le site

Site vitrine d'un kebab-tacos-naan à Dax. Une seule page, statique, en trois
langues (FR/ES/EN), publiée sur Vercel :
https://taconaansite-eight.vercel.app/

## Ce qui change au quotidien : les fichiers `data/`

| Fichier | Contenu |
|---|---|
| [`data/menu.js`](data/menu.js) | La carte et les prix |
| [`data/offers.js`](data/offers.js) | Les offres du moment (section « En ce moment ») |
| [`data/hours.js`](data/hours.js) | Les horaires de la semaine et les fermetures exceptionnelles |
| [`assets/img/uploads.js`](assets/img/uploads.js) | Les photos ajoutées (fichiers dans `assets/img/uploads/`) |
| [`data/reviews.js`](data/reviews.js) | La note Google, à relever 2 fois par an |

Les quatre premiers sont **écrits par le tableau de bord** (projet séparé
`taconaan-admin`, en construction) : il fait un commit sur `main`, Vercel
republie. **Fais donc un `git pull` avant de travailler à la main**, sinon ton
`git push` sera refusé.

Ces fichiers sont du **JSON pur** (guillemets doubles, pas de virgule finale,
pas de commentaire dans les données) précédé d'un commentaire d'en-tête. Si tu
les modifies à la main, garde-les ainsi : le tableau de bord les relit tels
quels et refuse d'écrire sur un fichier qu'il ne comprend pas.

`data/reviews.js` reste écrit à la main : `rating` et `count`. Le score, le
titre de la section avis et le bouton « Voir les … avis » le lisent tous les
trois depuis ce seul fichier, dans les trois langues.

### La carte (`data/menu.js`)

Le tableau de bord sait ajouter, renommer, supprimer et déplacer les plats et
les catégories ; à la main, voici ce qu'il écrit.

Chaque catégorie a un `id`, un `num` (deux chiffres, la place dans la carte),
un `name`, une `image` (clé du manifeste d'images) **ou** une `photo` envoyée
(c'est le cas d'une catégorie créée depuis le tableau de bord), un `tagline`
`{fr, es, en}` et des `items`. Un plat prend l'une de ces formes :

- `{ "name": "Tacos Simple", "tiers": [6.5, 7.5, 8.5] }` — trois colonnes
  *Seul / + Frite / + Menu* (`null` = pas de prix dans cette colonne)
- `{ "name": "Café", "price": 1.5 }` — un seul prix
- `{ "name": "Thé", "free": true }` — affiche « offert »

Champs facultatifs : `note` `{fr, es, en}` sous le nom du plat ; `hidden: true`
sur un plat pour le retirer de la carte sans l'effacer (une catégorie dont
tous les plats sont masqués disparaît aussi) ; `photo` sur une catégorie pour
remplacer son image par une photo ajoutée (clé de `uploads.js`, toujours de la
forme `up-…`) ; `tiersOnly` et `tierLabels` pour les catégories qui n'ont pas
les trois colonnes habituelles.

### Les offres (`data/offers.js`)

`{ id, title {fr,es,en}, text {fr,es,en} | null, price | null, photo | null,
start, end }`, dates au format `AAAA-MM-JJ`, **heure de Paris**. Une offre
s'affiche du jour `start` au jour `end` inclus, puis disparaît toute seule. La
section entière est cachée quand aucune offre n'est en cours.

### Les horaires (`data/hours.js`)

`week` donne, pour chaque jour (`mon`…`sun`), de 0 à 2 services
`["11:30", "15:00"]` (`[]` = fermé ce jour-là). `closures` liste les
fermetures exceptionnelles `{ from, to, note {fr,es,en} }` : un bandeau
prévient les visiteurs dès 7 jours avant, et le badge « ouvert / fermé » passe
à « Fermé exceptionnellement ». « Ouvert 7j/7 » disparaît tout seul si un jour
est fermé.

## `?v=` : seulement pour le code

Dans `index.html`, `site.js`, `site.css` et les manifestes d'images sont
appelés avec `?v=18` à la fin. Ce numéro force le navigateur d'un client déjà
venu à retélécharger le fichier.

**Si tu modifies `assets/js/site.js` ou `assets/css/site.css`**, remplace
partout `?v=18` par `?v=19` (puis 20…) — dans `index.html` **et** dans
`404.html` :

```bash
sed -i 's/?v=18"/?v=19"/g' index.html 404.html
```

Les fichiers `data/menu.js`, `data/offers.js`, `data/hours.js` et
`assets/img/uploads.js` n'ont **pas** de `?v=` : `vercel.json` leur donne
`Cache-Control: no-cache`, le navigateur revérifie donc à chaque visite. Un
changement de prix ou d'offre est visible dès que Vercel a republié.

Les images n'ont pas besoin de ça non plus : elles changent de nom quand elles
changent.

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

Le dépôt est relié à Vercel (projet `taconaansite`). Un `git push` sur `main`
met le site à jour en quelques secondes : https://taconaansite-eight.vercel.app/
