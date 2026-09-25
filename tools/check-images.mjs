/* Controle : toutes les images citees par le site existent-elles vraiment ?
   Se lance depuis la racine :  node tools/check-images.mjs               */
import { readFileSync, existsSync } from 'node:fs';

globalThis.window = {};
for (const f of ['assets/img/manifest.js', 'assets/img/extras.js', 'assets/img/photos.js',
               'assets/img/cutouts.js', 'data/menu.js']) {
  new Function(readFileSync(f, 'utf8')).call(globalThis);
}
const IMAGES = window.TACONAAN_IMAGES;
const MENU = window.TACONAAN_MENU;

let errors = 0, checked = 0;
const seen = new Set();

function slug(value) {
  return String(value).normalize('NFD').replace(/[̀-ͯ]/g, '')
    .toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
}

function entryOf(key) {
  return IMAGES[key] || IMAGES[String(key).replace(/-/g, '_')];
}

function files(where, key, required = true) {
  const entry = entryOf(key);
  if (!entry) {
    if (required) { console.log(`  ERREUR  ${where}: cle « ${key} » absente du manifeste`); errors++; }
    return false;
  }
  for (const [w] of entry.sizes) {
    for (const ext of ['webp', 'avif']) {
      const path = `assets/img/${entry.stem}-${w}.${ext}`;
      checked++;
      if (!existsSync(path)) { console.log(`  ERREUR  ${where}: ${path} manquant`); errors++; }
    }
  }
  seen.add(entry.stem);
  return true;
}

console.log('\n1. les vignettes de la carte');
for (const cat of MENU.categories) {
  const ok = files(`categorie ${cat.id}`, cat.image);
  if (ok) console.log(`  ok      ${cat.id.padEnd(11)} -> ${entryOf(cat.image).stem}`);
}

console.log('\n2. les choix (pain, viandes, sauces, supplements)');
for (const group of MENU.extras) {
  const withPic = group.values.filter(v => entryOf(group.id + '_' + slug(v)));
  withPic.forEach(v => files(`choix ${group.id}`, group.id + '_' + slug(v)));
  const missing = group.values.filter(v => !entryOf(group.id + '_' + slug(v)));
  console.log(`  ${group.id.padEnd(12)} ${withPic.length}/${group.values.length} avec photo` +
    (withPic.length && missing.length ? `  (sans : ${missing.join(', ')})` : ''));
}

// Les affiches : un stem par langue, et les memes tailles pour les trois.
// On verifie que chaque variante existe vraiment - c'est la seule section du
// site ou l'image porte le texte, donc une langue manquante se voit.
console.log('\n3. les affiches');
const postersSrc = readFileSync('assets/img/posters.js', 'utf8');
const posters = [...postersSrc.matchAll(
  /id: '([^']+)', stem: \{([^}]*)\}[\s\S]*?sizes: \[(.*?)\]\s*\}/g)];

for (const [, id, stems, dims] of posters) {
  const widths = [...dims.matchAll(/\[(\d+),\s*(\d+)\]/g)].map(m => m[1]);
  for (const [, lang, stem] of stems.matchAll(/(\w+):\s*'([^']+)'/g)) {
    for (const w of widths) {
      for (const ext of ['avif', 'webp']) {
        const file = `assets/img/${stem}-${w}.${ext}`;
        seen.add(file);
        if (!existsSync(file)) {
          console.log(`  ERREUR  affiche ${id}/${lang}: ${file} absent`);
          errors++;
        }
      }
    }
  }
}
console.log(`  ${posters.length} affiches x 3 langues`);

console.log('\n4. les images ecrites en dur dans index.html');
const html = readFileSync('index.html', 'utf8');
const refs = new Set();
for (const m of html.matchAll(/(?:src|href|srcset|poster|content)="([^"]+)"/g)) {
  for (const part of m[1].split(',')) {
    const url = part.trim().split(' ')[0];
    if (/^assets\/.+\.(webp|avif|jpg|png|mp4|webm)$/.test(url)) refs.add(url);
  }
}
for (const url of [...refs].sort()) {
  checked++;
  if (!existsSync(url)) { console.log(`  ERREUR  index.html: ${url} manquant`); errors++; }
  else console.log(`  ok      ${url}`);
}

console.log(`\n${checked} fichiers verifies, ${errors} erreur(s).`);
process.exit(errors ? 1 : 0);
