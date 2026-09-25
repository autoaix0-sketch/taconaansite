# L'atelier — le guide

Ce fichier explique comment fabriquer, lancer et surveiller tout ce qui
entoure le site : les scripts, les recettes, les assistants, l'automatique, et
la sécurité. Il est écrit pour être relu dans six mois sans rien avoir retenu.

Il ne suppose aucune connaissance. Chaque mot compliqué est expliqué la
première fois qu'il apparaît.

**Rien de ce qui est décrit ici n'est encore construit**, sauf l'établi (§2),
qui existe déjà et qui marche.

---

## Comment lire ce guide

L'atelier est rangé comme la boutique. Six endroits, chacun avec son rôle.

| Endroit | C'est quoi | Section |
|---|---|---|
| **Le comptoir** | Là où tu parles à Claude | §1 |
| **L'établi** | Les scripts qui fabriquent les images | §2 |
| **Le carnet de recettes** | Les gestes que tu répètes | §3 |
| **Les commis** | Les assistants spécialisés | §4 |
| **L'horloge** | Ce qui tourne sans toi | §5 |
| **Le coffre** | La sécurité | §6 |

Lis §0 et §1 en entier la première fois. Le reste se picore.

Le plan de construction, dans l'ordre, est en §7. Si tu es perdu, §8.

---

## §0. Le vocabulaire, en dix lignes

- **Dépôt (repo)** : le dossier du projet, avec son historique. Le tien est
  sur GitHub, et il est **public**.
- **Script** : un fichier qui exécute toujours les mêmes gestes. Il ne décide
  rien.
- **Agent** : un assistant qui décide. Il coûte de l'argent à chaque fois.
- **Sous-agent (commis)** : un agent spécialisé, appelé pour une tâche, qui
  disparaît après.
- **Skill (recette)** : une fiche qui explique à Claude comment faire un geste
  que tu répètes.
- **Session** : une conversation avec Claude. Elle a une mémoire, qui s'arrête
  à la fin.
- **Jeton (token)** : un mot de passe pour une machine. À protéger comme les
  clés du local.
- **Terminal** : la fenêtre noire où on tape des commandes.
- **Committer / pousser** : enregistrer tes modifications, puis les envoyer
  sur GitHub.
- **Déployer** : rendre le site visible sur internet.

---

## §1. Le comptoir — l'interface Claude

### Ce qu'est une session

Une session est une conversation. Claude s'y souvient de tout ce qui a été dit
**depuis le début de cette conversation**, et de rien d'autre. Ferme-la, ouvre
une nouvelle : il repart à zéro.

Conséquence pratique : ce qui doit survivre ne va pas dans la conversation, il
va dans un fichier. C'est exactement la raison d'être de ce guide.

### Les trois façons de travailler

**1. Tu demandes, il fait.** Le mode normal. Tu décris, il exécute, tu
relis.

**2. Le mode plan.** Claude ne touche à rien : il enquête, puis il te présente
un plan que tu approuves ou non. À utiliser dès que la demande est floue ou
que ça touche beaucoup de fichiers. C'est le mode le plus rentable et le moins
utilisé.

**3. Les commandes `/`.** Tu tapes une barre oblique et un nom, et Claude
déroule une recette enregistrée. C'est le §3.

### Les permissions — la partie qui compte

Claude demande avant d'agir. Tu peux régler à quel point il demande.

| Réglage | Ce que ça fait | Quand |
|---|---|---|
| Demander à chaque fois | Il te demande avant chaque action | Par défaut. Garde-le. |
| Accepter les modifications | Il modifie les fichiers sans demander | Quand tu as confiance dans la tâche |
| Tout accepter | Il fait tout sans demander | **Jamais sur ce projet** |

Le dernier réglage existe pour des machines jetables. Ton dépôt est public et
contient l'accès à ta fiche Google. Voir §6.

Certaines commandes de réglage (`/permissions`, `/config`, `/hooks`) ouvrent
un panneau qui n'existe que dans le terminal, pas dans l'application. Si tu ne
les trouves pas dans l'app, c'est normal.

### Où vivent les choses

```
taconaansite/
├── CLAUDE.md              ← à créer : les règles lues à chaque session
├── ATELIER.md             ← ce guide
├── GOOGLE-BUSINESS.md     ← la fiche Google
├── .claude/
│   ├── launch.json        ← existe : le serveur local
│   ├── settings.json      ← à créer : permissions
│   ├── skills/            ← à créer : les recettes (§3)
│   └── agents/            ← à créer : les commis (§4)
├── tools/                 ← existe : l'établi (§2)
├── assets/                ← le site
└── data/                  ← les prix, les avis
```

### `CLAUDE.md` — la mémoire du projet

C'est le seul fichier que Claude lit **automatiquement** à chaque session. Ce
que tu y écris, tu n'as plus à le répéter.

Ce qu'il faut y mettre pour ce projet :

- La palette et les polices, pour qu'aucun visuel ne dérive.
- « Ne jamais relancer `tools/optimize_images.py` » — sept de ses sources ont
  été archivées, il détruirait le manifeste.
- « Le dépôt est public. Aucun secret ne doit y entrer. »
- « Rien qui parle à un client n'est publié sans relecture. »

Court et impératif. Une page maximum, sinon il se dilue.

---

## §2. L'établi — les scripts

### Ce que tu as déjà

Sept scripts Python dans `tools/`. Ils tournent sur ta machine, sans internet
et sans intelligence artificielle. Ils font toujours la même chose.

| Script | Ce qu'il fabrique |
|---|---|
| `optimize_images.py` | La bibliothèque commune : étalonnage chaud, grain, export AVIF+WebP |
| `make_product_photos.py` | Les 29 photos produit détourées |
| `make_board_images.py` | Les 4 panneaux du comptoir, nettoyés |
| `make_product_crops.py` | Les vignettes découpées dans les panneaux |
| `make_category_cutouts.py` | Les 4 vignettes de carte détourées : assiette, bowl, Tex-Mex, menu kids |
| `make_posters.py` | Les 4 affiches, en 3 langues |
| `make_brand_assets.py` | Favicon, icône, image de partage |

Et trois vérificateurs dans `_work/review/` : la planche contact sur fond noir, la
mesure des halos, le balai des fichiers périmés.

### Comment on lance un script

Ouvre un terminal dans le dossier du projet, et tape :

```bash
python tools/make_posters.py
```

C'est tout. Il écrit ce qu'il fait, et s'arrête.

Après avoir lancé un script d'images, lance toujours le vérificateur :

```bash
node tools/check-images.mjs
```

S'il affiche `0 erreur`, tout va bien.

### La règle d'or

**Un script ne décide rien.** Si tu te surprends à vouloir qu'un script
« choisisse » quelque chose, c'est qu'il te faut une recette (§3) ou un commis
(§4).

### Ce qu'on pourrait ajouter à l'établi

- Les formats réseaux sociaux dans `make_posters.py` : carré 1080, portrait
  4:5, story 9:16. Le générateur existe, il lui manque des tailles.
- Un script qui fabrique une affiche « fermé le 25 décembre », à partir d'une
  date.
- Un script qui reconstruit tout d'un coup, pour ne pas en oublier un.

---

## §3. Le carnet de recettes — les skills

### Ce que c'est

Une recette est une fiche que tu écris une fois, et que tu appelles ensuite
par son nom. Tu tapes `/nouvelle-promo`, et Claude déroule les étapes que tu
as écrites dedans.

L'intérêt n'est pas de gagner du temps de frappe. C'est que le geste soit
**identique** à chaque fois, même dans six mois, même si quelqu'un d'autre le
fait.

### À quoi ça ressemble

Un dossier, un fichier :

```
.claude/skills/nouvelle-promo/SKILL.md
```

Dedans, un en-tête et des instructions en français :

```markdown
---
name: nouvelle-promo
description: Fabrique une affiche promo à partir d'un plat et d'un prix.
---

1. Demander le plat et le prix si on ne me les a pas donnés.
2. Vérifier le prix dans data/menu.js. S'il diffère, le signaler.
3. Écrire le titre : un mot en jaune, le reste en crème.
   Reprendre le ton de data/menu.js. Phrases courtes.
4. Ajouter l'entrée dans la table POSTERS de tools/make_posters.py,
   en français, espagnol et anglais.
5. Lancer python tools/make_posters.py
6. Lancer node tools/check-images.mjs
7. Montrer l'affiche. Ne rien publier.
```

Tu remarques la dernière ligne. Elle est importante.

### Trois recettes qui valent la peine ici

| Recette | Ce qu'elle fait |
|---|---|
| `/nouvelle-promo` | Un plat + un prix → une affiche finie, dans les 3 langues |
| `/prix-change` | Modifie `data/menu.js`, regénère les affiches touchées, incrémente `?v=`, vérifie |
| `/repondre-avis` | Rédige une réponse dans ton ton, à partir de `style-reference.md`. Ne publie jamais. |

La deuxième évite une erreur classique : changer un prix et oublier de
reconstruire l'affiche qui l'affiche.

---

## §4. Les commis — les sous-agents

### Ce que c'est, et ce que ce n'est pas

Un commis est un assistant qu'on appelle pour une tâche précise. Il arrive
avec une tête neuve, fait son travail, rend son rapport, et disparaît.

**Ce n'est pas** un robot qui vit quelque part et surveille ton site. Il
n'existe que pendant la durée de sa tâche, à l'intérieur d'une conversation.

Pourquoi c'est utile : il a sa propre mémoire. Il peut fouiller trente
fichiers sans encombrer la conversation principale. Tu ne reçois que la
conclusion.

### À quoi ça ressemble

Un fichier par commis :

```
.claude/agents/auditeur-carte.md
```

```markdown
---
name: auditeur-carte
description: Compare la carte papier au site et signale les écarts.
tools: Read, Grep, Glob
---

Tu compares `menu/Taco Naan — Menu.md` à `data/menu.js`.

Tu signales :
- tout plat présent d'un côté et absent de l'autre
- tout prix qui diffère
- toute liste fusionnée qui ne devrait pas l'être

Tu ne modifies rien. Tu rends une liste, la plus courte possible.
```

La ligne `tools:` limite ce qu'il a le droit de faire. Ici, lecture seule. Un
commis qui n'a pas besoin d'écrire ne doit pas pouvoir écrire. C'est de la
sécurité (§6).

### Deux commis qui gagnent leur place

**L'auditeur de carte.** Celui du dessus. Il aurait déjà trouvé deux choses :
« Barquette Frites » est sur le site mais pas sur la carte papier, et les deux
listes de viandes ont été fusionnées alors que le steak n'existe qu'en
sandwich.

**Le gardien de marque.** Il regarde tout nouveau visuel et vérifie : fond
`#0a0c0c`, un seul accent jaune `#ffc61a`, Instrument Serif pour les titres,
aucun angle arrondi, pas de logo étranger. Il dit oui ou non, et pourquoi.

### Quand ne PAS en utiliser

- Pour une tâche que tu peux décrire exactement → c'est un script.
- Pour un fichier que tu connais déjà → demande directement.
- Pour aller vite → un commis est plus lent qu'une question simple.

Un commis coûte de l'argent à chaque appel. Trois commis lancés pour une
question à laquelle un `grep` répond, c'est du gaspillage.

---

## §5. L'horloge — ce qui tourne sans toi

### Les deux horloges

| Où | Tourne quand | Coût | Bon pour |
|---|---|---|---|
| **Ton PC** (Planificateur de tâches Windows) | Seulement si la machine est allumée | Gratuit | Reconstruire des images, vérifier des fichiers locaux |
| **Le cloud** (agent programmé) | Toujours | Payant à chaque exécution | Vérifier que le site en ligne répond |

Ton PC est éteint la nuit et fermé les jours fériés. Donc : ce qui doit
tourner de façon fiable va dans le cloud, ce qui touche tes fichiers locaux
reste sur le PC.

### Ce qui mérite une horloge

- **Une fois par semaine** : le site répond-il ? les images se chargent-elles
  toutes ? Un rapport de trois lignes.
- **Une fois par mois** : rappel de relever la note Google et le nombre
  d'avis, et de les recopier dans `data/reviews.js`.
- **Une fois par trimestre** : l'auditeur de carte (§4).

### Ce qui n'en mérite pas

Une vérification toutes les heures d'un site qui change deux fois par an. Tu
paierais 700 fois pour la même réponse.

**Règle** : règle l'horloge sur la vitesse à laquelle la chose change
vraiment, pas sur ton inquiétude.

### Ce qu'une horloge ne doit jamais faire

Publier. Ni un post, ni une réponse à un avis, ni une modification du site.
Une horloge **regarde et signale**. La décision reste à toi.

---

## §6. Le coffre — la sécurité

### La chose à retenir avant tout

**Ton dépôt GitHub est public.** Tout ce qui y entre est lisible par
n'importe qui, immédiatement, et reste dans l'historique même après
suppression.

### Les secrets, et ce qu'ils ouvrent

Trois types de secrets peuvent apparaître dans ce projet :

| Secret | Ce qu'il ouvre si quelqu'un le vole |
|---|---|
| `client_secret.json`, `token.json` (Google) | Ta fiche Google : publier des réponses en ton nom, changer tes horaires, ton adresse |
| Un jeton Meta / Instagram | Publier sur ton compte |
| Une clé d'API (Claude, autre) | Dépenser ton argent |

Un jeton volé n'est pas un désagrément. C'est quelqu'un qui parle à tes
clients avec ta voix.

### Ce qui est déjà protégé

Ton `.gitignore` couvre déjà l'essentiel, et il le dit :

```
# SECRETS - reponse automatique aux avis Google.
# Le depot est PUBLIC. Ces fichiers donnent acces a la fiche Google de
# l etablissement : ils ne doivent jamais y arriver.
tools/reviews-reply/client_secret.json
tools/reviews-reply/token.json
tools/reviews-reply/*secret*
tools/reviews-reply/*token*
tools/reviews-reply/*credential*
```

Les filets `*secret*`, `*token*`, `*credential*` attrapent aussi les fichiers
renommés. C'est bien vu. Garde-les.

### Les six règles

1. **Un secret ne se tape jamais dans une conversation.** Ni à Claude, ni
   ailleurs. Si ça arrive, considère-le comme grillé et régénère-le.
2. **Avant chaque envoi sur GitHub, regarde ce qui part.** Tape
   `git status` puis `git diff --staged`. Si un nom contient `token`, `secret`
   ou `key`, arrête-toi.
3. **Un secret parti sur GitHub est mort.** Le supprimer ne suffit pas : il
   reste dans l'historique. Il faut le **révoquer** chez Google ou Meta, et en
   créer un nouveau.
4. **Donne le minimum à chaque commis.** Un commis qui lit n'a pas besoin
   d'écrire. La ligne `tools:` sert à ça.
5. **Ne mets jamais Claude en « tout accepter » sur ce projet.** Une commande
   mal comprise sur un dépôt public ne se rattrape pas toujours.
6. **Rien ne parle à un client sans que tu l'aies lu.** C'est la règle qui
   couvre tout le reste.

### Sur le script de réponse aux avis

Il a déjà le bon réflexe : `SEUIL_PUBLICATION_AUTO = 4`. Un avis à trois
étoiles ou moins n'est **jamais** publié automatiquement.

Ne touche pas à cette valeur. C'est la ligne qui te protège du jour où un
client mécontent reçoit une réponse automatique maladroite.

### Les données des clients

Les avis affichés contiennent des prénoms. Ils sont déjà publics sur Google,
donc les reprendre est défendable. Mais deux précautions :

- N'ajoute jamais de nom de famille, d'email ou de téléphone d'un client.
- Si quelqu'un demande le retrait de son avis du site, retire-le. C'est son
  droit.

### Les sauvegardes

Avant toute opération qui réécrit beaucoup de fichiers, copie d'abord. C'est
ce que fait déjà `_work/backups/`.

Et retiens : `_work/review/stale/` et `_work/review/unused/` ne sont pas des poubelles.
Ce sont des fichiers mis de côté, récupérables en les remettant à leur place.
Rien n'a été supprimé.

---

## §7. Le plan de construction

Dans l'ordre. Chaque étape sert à quelque chose toute seule, donc tu peux
t'arrêter n'importe où.

### Étape 1 — Publier le site

Rien d'autre ne compte tant que le site n'est pas en ligne.

⚠️ **Attention** : le dépôt contient encore la version de décembre 2025. Si tu
actives GitHub Pages maintenant, c'est cette vieille page cassée qui
s'affiche. Il faut d'abord enregistrer le travail actuel.

Tu sauras que c'est fini quand : l'adresse répond, et l'adresse est collée
dans ta fiche Google.

### Étape 2 — Les formats réseaux sociaux

Ajouter le carré et le portrait à `make_posters.py`. Tu as douze affiches et
aucun moyen de les poster.

Tu sauras que c'est fini quand : un dossier contient douze images au bon
format, prêtes à envoyer depuis ton téléphone.

### Étape 3 — La recette `/nouvelle-promo`

Celle qui change ta semaine. Un plat, un prix, et l'affiche est prête.

Tu sauras que c'est fini quand : tu tapes `/nouvelle-promo`, tu réponds à deux
questions, et tu as une image.

### Étape 4 — `CLAUDE.md`

Une page de règles, lue à chaque session. À faire après les étapes 2 et 3,
parce que tu sauras alors quelles règles compter.

### Étape 5 — L'auditeur de carte

Un commis en lecture seule. Il trouvera les écarts déjà connus, et ceux à
venir.

### Étape 6 — La vérification hebdomadaire

Une horloge qui regarde et signale. La dernière, parce que c'est la seule qui
coûte de l'argent en continu.

### Ce que je ne construirais pas

- Un agent qui publie tout seul sur Instagram.
- Un agent qui répond tout seul aux avis.
- Une horloge qui tourne plus vite que la réalité.

Ton commerce tient sur 271 personnes qui ont aimé la façon dont on les a
traitées. Ça ne se délègue pas à une machine pour gagner trois minutes.

---

## §8. Si tu es perdu

### Tu ne sais plus où tu en es

Ouvre une session et dis : « Lis `ATELIER.md` et dis-moi ce qui est fait et ce
qui reste. » Claude lira ce fichier et répondra.

### Tu veux annuler quelque chose

Tant que ce n'est pas envoyé sur GitHub, tout est récupérable :

```bash
git status          # ce qui a changé
git diff            # le détail
git checkout -- .   # tout annuler (attention : définitif)
```

Dans le doute, demande avant de taper la troisième.

### Une image a l'air cassée

```bash
node tools/check-images.mjs
python _work/review/contact-sheet.py
```

Le premier dit si un fichier manque. Le second fabrique une planche de toutes
les découpes sur fond noir — c'est le seul test qui compte pour un détourage.

### Claude fait n'importe quoi

Passe-le en mode plan et redemande. Neuf fois sur dix, c'est que la demande
était ambiguë et qu'il a deviné.

### Tu veux repartir de zéro sur une tâche

Ouvre une nouvelle session. La mémoire de la précédente ne suit pas — c'est
une fonctionnalité, pas un bug.

---

*Guide écrit le 18 septembre 2026. Si tu ajoutes une recette ou un commis,
ajoute-le ici : c'est ce fichier qui doit rester vrai.*
