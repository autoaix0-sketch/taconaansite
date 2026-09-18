# Répondre automatiquement aux avis Google

Tu as choisi le 100 % automatique. Voici ce que c'est, ce que ça coûte, et
pourquoi ça ne marchera pas dès ce soir.

## Ce qu'il faut savoir avant de commencer

L'API qui permet de répondre aux avis s'appelle **Google Business Profile
API**. Elle est **gratuite**. Mais :

1. **Google doit t'autoriser à l'utiliser.** Il faut remplir un formulaire et
   attendre leur réponse — de quelques jours à quelques semaines. Ils
   acceptent la plupart des commerces qui gèrent leur propre fiche, mais
   personne ne peut te garantir le délai.
2. **Ça ne peut pas tourner depuis le site.** Le site est un simple fichier
   déposé chez GitHub : il n'y a pas de serveur derrière. Le script tourne
   donc sur ton PC, une fois par jour.

En attendant l'autorisation, le mode **brouillon** (`--draft`) fonctionne
dès maintenant : il te prépare les réponses, tu copies-colles. Sans API,
sans attente.

---

## Ce que le script fait, et ne fait pas

| | |
|---|---|
| Récupère les nouveaux avis | oui |
| Rédige une réponse dans ton ton | oui, à partir de `style-reference.md` |
| Publie tout seul les avis **4 et 5 étoiles** | oui |
| Publie tout seul les avis **3 étoiles ou moins** | **non, jamais** |
| Répond deux fois au même avis | non |

### Pourquoi les avis négatifs ne partent jamais tout seuls

Une réponse maladroite à un client mécontent fait plus de dégâts qu'une
absence de réponse : elle est publique, définitive, et lue par tous les
suivants. Ta réponse à Franklin est bonne **parce qu'elle est de toi** — tu
expliques le curcuma et les herbes de Provence, ce qu'aucun script ne saurait
inventer. Les avis à 3 étoiles ou moins sont donc mis de côté dans un fichier,
avec une proposition de réponse, et c'est toi qui décides.

---

## Mise en place

### Étape 1 — Créer le projet Google (10 min, à faire une fois)

1. <https://console.cloud.google.com/> → **Nouveau projet**, appelle-le
   `taco-naan-avis`.
2. Menu **API et services** → **Bibliothèque** → active ces trois API :
   - `Google My Business API`
   - `My Business Account Management API`
   - `My Business Business Information API`
3. Menu **Identifiants** → **Créer des identifiants** → **ID client OAuth** →
   type **Application de bureau**.
4. Télécharge le fichier JSON, renomme-le **`client_secret.json`** et pose-le
   dans ce dossier (`tools/reviews-reply/`).

> Ce fichier est un mot de passe. Il est déjà exclu de Git par le
> `.gitignore` : ne le mets jamais en ligne, ne l'envoie à personne.

### Étape 2 — Demander l'accès à Google (5 min, puis attendre)

Formulaire : <https://support.google.com/business/contact/api_default>

Ce qu'ils demandent, et quoi répondre :

- **Nom du projet Google Cloud** : `taco-naan-avis`
- **Numéro du projet** : visible sur la page d'accueil de la console
- **Usage prévu** : *Gérer les réponses aux avis de notre propre établissement
  (Taco Naan, 38 Av. Saint-Vincent de Paul, 40100 Dax). Usage interne, un seul
  établissement, pas de revente ni de service tiers.*
- **Tu es** : propriétaire de l'établissement

Google répond par mail. Tant que ce mail n'est pas arrivé, l'étape 4 renverra
une erreur `PERMISSION_DENIED` — c'est normal, ce n'est pas une panne.

### Étape 3 — Connecter ton compte (1 min, à faire une fois)

```bash
node tools/reviews-reply/setup-oauth.mjs
```

Ton navigateur s'ouvre, tu choisis le compte Google **propriétaire de la
fiche**, tu acceptes. Le script écrit `token.json` à côté. Terminé.

### Étape 4 — Lancer

```bash
# Prépare les réponses dans un fichier, ne publie rien.
# FONCTIONNE SANS L'AUTORISATION GOOGLE.
node tools/reviews-reply/run.mjs --draft

# Publie pour de vrai les avis 4 et 5 étoiles.
# Nécessite l'autorisation de l'étape 2.
node tools/reviews-reply/run.mjs
```

Les brouillons arrivent dans `brouillons.md`, dans ce dossier.

### Étape 5 — Automatiser (optionnel)

Pour que ça tourne tous les jours à 10 h sans y penser, dans PowerShell :

```powershell
schtasks /create /tn "Taco Naan - avis" /tr "node C:\Users\sakka\Desktop\taconaansite\taconaansite\tools\reviews-reply\run.mjs" /sc daily /st 10:00
```

---

## Fichiers

| Fichier | Rôle |
|---|---|
| `setup-oauth.mjs` | connexion à ton compte Google, une seule fois |
| `run.mjs` | récupère les avis, rédige, publie ou prépare |
| `style-reference.md` | **tes** vraies réponses, qui servent de modèle de ton |
| `client_secret.json` | tes identifiants Google — *jamais sur Git* |
| `token.json` | ta session — *jamais sur Git* |
| `repondus.json` | mémoire des avis déjà traités |
| `brouillons.md` | ce que le mode `--draft` écrit pour toi |

---

## Si tu veux arrêter

Supprime `token.json`. Le script n'a plus accès à rien.
