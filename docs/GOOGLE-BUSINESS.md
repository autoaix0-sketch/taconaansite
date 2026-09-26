# Mettre le site en ligne et le relier à Google

Le site est fini. Ce fichier est la liste de ce qui reste à faire **toi**,
dans l'ordre. Compte 20 minutes en tout.

Le point le plus important est le numéro 2. Aujourd'hui, ta fiche Google
affiche encore « Ajouter un site Web » : des gens te cherchent, tombent sur ta
fiche, et n'ont aucun lien vers ta carte. C'est la plus grosse perte de
clients de toute cette affaire, et ça se règle en deux minutes.

---

## 1. Publier le site

✅ Fait. Le site est en ligne sur Vercel, relié au dépôt GitHub : chaque
`git push` sur `main` republie automatiquement.

Ton adresse est :

```
https://taconaansite-eight.vercel.app/
```

Vérifie qu'elle s'ouvre bien avant de passer à la suite.

> **Plus tard, si tu veux `taconaan.fr`** (~12 €/an) : achète le nom chez un
> registrar, puis dis-le moi — je le connecte au projet Vercel. Le site ne
> bouge pas, seule l'adresse change.

---

## 2. Ajouter le site à ta fiche Google ← le plus rentable

1. Ouvre <https://business.google.com> avec le compte propriétaire de la fiche
2. Sélectionne **Taco Naan**
3. **Modifier le profil** → onglet **Coordonnées** → champ **Site Web**
4. Colle l'adresse du point 1 → **Enregistrer**

Google met de quelques heures à deux jours à l'afficher.

---

## 3. Pendant que tu y es, dans la même fiche

Cinq choses qui rapportent, une fois pour toutes :

- **Horaires** : vérifie 11:30–15:00 et 18:00–23:30, 7j/7.
- **Attributs** : coche *Repas sur place*, *Vente à emporter*, **décoche
  *Livraison***. Coche *Halal*, *Cartes de paiement acceptées*, *Entrée
  accessible en fauteuil roulant*. Ce sont des filtres de recherche : un
  client qui cherche « kebab halal Dax » ne te trouve pas si ce n'est pas coché.
- **Photos** : tu en as 61. Ajoute les quatre panneaux de la carte
  (`_work/sources/boards/*.png`) — les gens cherchent les prix avant d'appeler.
- **Menu** : Google laisse coller un lien de carte. Mets
  `https://taconaansite-eight.vercel.app/#carte`
- **Lien d'avis en un clic** : dans ton espace, cherche **Demander des avis**.
  Google te donne un lien court du type `https://g.page/r/XXXXXXXX/review`.
  Copie-le dans `data/reviews.js`, ligne `writeUrl`. Le bouton « Laisser un
  avis » du site ouvrira alors directement le formulaire, au lieu de passer
  par la fiche. Tu auras plus d'avis, mécaniquement.

---

## 4. Quand tu changes un prix

Un seul fichier : **`data/menu.js`**.

1. Tu ouvres le fichier, tu changes le chiffre, tu enregistres.
2. Tu ouvres **`index.html`** et tu remplaces tous les `?v=6` par `?v=7`
   (puis `?v=8` la fois d'après, etc.).

Cette deuxième étape est importante : sans elle, les gens déjà venus sur le
site garderaient l'ancienne carte en mémoire et verraient de vieux prix.

---

## 5. Si tu changes tes horaires

Trois endroits, et il faut les trois :

| Où | Quoi |
|---|---|
| `assets/js/site.js` | la constante `SERVICES`, tout en haut — c'est elle qui pilote le badge « Ouvert / Fermé » |
| `assets/js/site.js` | les textes `venir.hours.v` dans les trois langues |
| `index.html` | le bloc `openingHoursSpecification` (celui que Google lit) |

Dis-le moi plutôt que de le faire à la main, c'est le seul endroit du projet
où une erreur se voit tout de suite.

---

## 6. Régénérer les images

Seulement si tu ajoutes ou remplaces des photos.

```bash
python tools/optimize_images.py      # les plats
python tools/make_board_images.py    # les panneaux du dossier menu/
python tools/make_brand_assets.py    # favicon, icône, image de partage
```

---

## Ce qui a été volontairement écarté

**Le balisage d'avis (`aggregateRating`) dans le code de la page.**
Techniquement, on pourrait déclarer « 4,5 étoiles » à Google directement dans
le site pour tenter d'obtenir des étoiles dans les résultats de recherche.
C'est contraire aux consignes de Google — un commerce n'a pas le droit de se
noter lui-même sur son propre site — et ça peut coûter l'affichage enrichi
sur *toutes* les pages. La note est donc affichée visuellement, sourcée, avec
un lien vers ta fiche. Même effet de confiance, aucun risque.
