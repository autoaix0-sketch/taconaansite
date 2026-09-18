#!/usr/bin/env node
/**
 * Taco Naan - reponses aux avis Google.
 *
 *   node run.mjs --draft   prepare les reponses dans brouillons.md, ne publie rien
 *   node run.mjs           publie les reponses aux avis 4 et 5 etoiles
 *
 * REGLE NON NEGOCIABLE : un avis a 3 etoiles ou moins n est JAMAIS publie
 * automatiquement. Il part dans brouillons.md pour que tu tranches. Une
 * reponse maladroite a un client mecontent est publique et definitive.
 *
 * Aucune dependance : tout est dans Node.
 */

import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const TOKEN_FILE = join(HERE, 'token.json');
const DONE_FILE = join(HERE, 'repondus.json');
const DRAFT_FILE = join(HERE, 'brouillons.md');

const DRAFT_ONLY = process.argv.includes('--draft');

/* En dessous de ce nombre d etoiles, on ne publie jamais sans relecture. */
const SEUIL_PUBLICATION_AUTO = 4;

// --------------------------------------------------------------------------
// Jeton
// --------------------------------------------------------------------------

function loadToken() {
  if (!existsSync(TOKEN_FILE)) {
    console.error(
      '\n  token.json est introuvable.\n' +
      '  Lance d abord :  node tools/reviews-reply/setup-oauth.mjs\n'
    );
    process.exit(1);
  }
  return JSON.parse(readFileSync(TOKEN_FILE, 'utf8'));
}

async function accessToken(saved) {
  const response = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      refresh_token: saved.refresh_token,
      client_id: saved.client_id,
      client_secret: saved.client_secret,
      grant_type: 'refresh_token'
    })
  });
  const data = await response.json();
  if (!data.access_token) {
    console.error('\n  Impossible de rafraichir la session :',
                  JSON.stringify(data, null, 2));
    console.error('  Relance setup-oauth.mjs.\n');
    process.exit(1);
  }
  return data.access_token;
}

async function api(url, token, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      authorization: `Bearer ${token}`,
      'content-type': 'application/json',
      ...(options.headers || {})
    }
  });

  const text = await response.text();
  const body = text ? JSON.parse(text) : {};

  if (!response.ok) {
    /* C est l erreur que tout le monde rencontre avant l autorisation de
       Google. Elle merite une explication, pas une trace technique. */
    if (response.status === 403) {
      console.error(
        '\n  Google refuse l acces (403).\n' +
        '  C est normal tant que ta demande d acces a l API Business Profile\n' +
        '  n a pas ete acceptee. Voir l etape 2 du README.\n\n' +
        '  En attendant, ceci fonctionne :\n' +
        '      node tools/reviews-reply/run.mjs --draft\n'
      );
      process.exit(1);
    }
    console.error(`\n  ${response.status} sur ${url}`);
    console.error('  ' + JSON.stringify(body) + '\n');
    process.exit(1);
  }
  return body;
}

// --------------------------------------------------------------------------
// Redaction
// --------------------------------------------------------------------------

/* Le script n invente pas de prose : il assemble des tournures courtes,
   calquees sur la facon dont tu reponds deja (voir style-reference.md).
   Court, le prenom en ouverture, un merci a la fin, aucune formule toute
   faite d entreprise. */

const OUVERTURES = [
  (prenom) => `Bonjour ${prenom}`,
  (prenom) => `Merci ${prenom}`
];

const CORPS_5 = [
  'Content que ça vous ait plu.',
  'Ravi que ce soit passé comme il faut.',
  'Ça fait plaisir à lire.'
];

const CORPS_4 = [
  'Merci pour le retour, on note.',
  'Content que ça vous ait plu, et merci pour la remarque.'
];

const FERMETURES = [
  'À bientôt chez Taco Naan.',
  'Au plaisir de vous revoir.',
  'Merci d’être passé.'
];

/* Un choix stable : le meme avis donne toujours la meme reponse, ce qui evite
   de publier deux textes differents si le script est relance. */
function pick(list, seed) {
  let h = 0;
  for (const ch of String(seed)) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return list[h % list.length];
}

function firstName(review) {
  const full = review.reviewer?.displayName?.trim() || '';
  return full.split(/\s+/)[0] || 'et merci';
}

function mentions(text) {
  const t = (text || '').toLowerCase();
  const found = [];
  if (/naan|pain/.test(t)) found.push('Le pain est pétri et cuit ici tous les jours.');
  if (/frite/.test(t)) found.push('Les frites, on y tient.');
  if (/rapide|service|serveur|accueil|sourire/.test(t)) found.push('L’équipe va apprécier.');
  if (/prix|qualité|abordable/.test(t)) found.push('On préfère remplir l’assiette.');
  return found.slice(0, 1);
}

function compose(review, stars) {
  const prenom = firstName(review);
  const seed = review.reviewId || review.name || prenom;

  const lignes = [pick(OUVERTURES, seed)(prenom)];
  lignes.push(stars >= 5 ? pick(CORPS_5, seed) : pick(CORPS_4, seed));
  lignes.push(...mentions(review.comment));
  lignes.push(pick(FERMETURES, seed));

  return lignes.join('\n');
}

const STAR_WORDS = { ONE: 1, TWO: 2, THREE: 3, FOUR: 4, FIVE: 5 };

// --------------------------------------------------------------------------
// Programme
// --------------------------------------------------------------------------

async function main() {
  const saved = loadToken();
  const token = await accessToken(saved);

  const done = existsSync(DONE_FILE)
    ? new Set(JSON.parse(readFileSync(DONE_FILE, 'utf8')))
    : new Set();

  // 1. le compte
  const accounts = await api(
    'https://mybusinessaccountmanagement.googleapis.com/v1/accounts', token);
  const account = accounts.accounts?.[0];
  if (!account) {
    console.error('\n  Aucun compte Business Profile sur cette session.\n');
    process.exit(1);
  }

  // 2. l etablissement
  const locations = await api(
    `https://mybusinessbusinessinformation.googleapis.com/v1/${account.name}` +
    '/locations?readMask=name,title&pageSize=100', token);
  const location = locations.locations?.[0];
  if (!location) {
    console.error('\n  Aucun etablissement sur ce compte.\n');
    process.exit(1);
  }

  const locId = location.name.split('/').pop();
  const base = `https://mybusiness.googleapis.com/v4/${account.name}/locations/${locId}`;

  console.log(`\n  ${location.title}`);

  // 3. les avis
  const reviews = await api(`${base}/reviews?pageSize=50&orderBy=updateTime desc`, token);
  const all = reviews.reviews || [];

  const publiables = [];
  const aRelire = [];

  for (const review of all) {
    if (review.reviewReply) continue;            // deja repondu, sur Google
    if (done.has(review.reviewId)) continue;     // deja traite, par nous

    const stars = STAR_WORDS[review.starRating] || 0;
    const entry = { review, stars, texte: compose(review, stars) };

    if (stars >= SEUIL_PUBLICATION_AUTO) publiables.push(entry);
    else aRelire.push(entry);
  }

  console.log(`  ${all.length} avis lus · ${publiables.length} à publier · ` +
              `${aRelire.length} à relire`);

  // 4. brouillons : tout ce qui n est pas encore parti
  const draftBody = [...publiables, ...aRelire].map(({ review, stars, texte }) => {
    const auto = stars >= SEUIL_PUBLICATION_AUTO;
    return `## ${review.reviewer?.displayName || 'Anonyme'} — ${stars}★` +
      `${auto ? '' : '  ⚠ À RELIRE, non publié automatiquement'}\n\n` +
      `> ${(review.comment || '(pas de texte)').replace(/\n/g, '\n> ')}\n\n` +
      `**Réponse proposée :**\n\n\`\`\`\n${texte}\n\`\`\`\n`;
  }).join('\n---\n\n');

  writeFileSync(DRAFT_FILE,
    `# Réponses à donner\n\nGénéré le ${new Date().toLocaleString('fr-FR')}.\n\n` +
    (draftBody || '_Rien de nouveau : tous les avis ont déjà une réponse._\n'),
    'utf8');

  if (DRAFT_ONLY) {
    console.log(`\n  Brouillons écrits dans tools/reviews-reply/brouillons.md`);
    console.log('  Rien n a été publié.\n');
    return;
  }

  // 5. publication, uniquement les 4 et 5 etoiles
  for (const { review, texte } of publiables) {
    await api(`${base}/reviews/${review.reviewId}/reply`, token, {
      method: 'PUT',
      body: JSON.stringify({ comment: texte })
    });
    done.add(review.reviewId);
    console.log(`  publie -> ${review.reviewer?.displayName || 'Anonyme'}`);
  }

  writeFileSync(DONE_FILE, JSON.stringify([...done], null, 2), 'utf8');

  if (aRelire.length) {
    console.log(`\n  ${aRelire.length} avis attendent ta relecture ` +
                '(3 étoiles ou moins) : voir brouillons.md\n');
  } else {
    console.log('');
  }
}

main().catch((error) => {
  console.error('\n  ' + error.message + '\n');
  process.exit(1);
});
