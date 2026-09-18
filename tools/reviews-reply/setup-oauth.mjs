#!/usr/bin/env node
/**
 * Taco Naan - connexion au compte Google, une seule fois.
 *
 * Ouvre le navigateur, te fait choisir le compte proprietaire de la fiche,
 * puis ecrit token.json a cote. Ce fichier contient un jeton de rafraichissement
 * qui permet a run.mjs de travailler ensuite sans jamais te redemander.
 *
 * Usage : node tools/reviews-reply/setup-oauth.mjs
 *
 * Aucune dependance : tout est dans Node.
 */

import { createServer } from 'node:http';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomBytes } from 'node:crypto';

const HERE = dirname(fileURLToPath(import.meta.url));
const SECRET_FILE = join(HERE, 'client_secret.json');
const TOKEN_FILE = join(HERE, 'token.json');

const PORT = 8731;
const REDIRECT = `http://localhost:${PORT}/callback`;
const SCOPE = 'https://www.googleapis.com/auth/business.manage';

function fail(message) {
  console.error('\n  ' + message + '\n');
  process.exit(1);
}

if (!existsSync(SECRET_FILE)) {
  fail(
    'client_secret.json est introuvable.\n' +
    '  Reprends l etape 1 du README : console Google Cloud -> Identifiants\n' +
    '  -> ID client OAuth -> Application de bureau, puis pose le fichier ici.'
  );
}

const raw = JSON.parse(readFileSync(SECRET_FILE, 'utf8'));
// Google livre le fichier sous la cle "installed" ou "web" selon le type choisi.
const creds = raw.installed || raw.web;
if (!creds?.client_id) fail('client_secret.json ne ressemble pas a un fichier Google valide.');

/* L etat protege contre une reponse qui ne viendrait pas de notre demande. */
const state = randomBytes(16).toString('hex');

const authUrl = 'https://accounts.google.com/o/oauth2/v2/auth?' + new URLSearchParams({
  client_id: creds.client_id,
  redirect_uri: REDIRECT,
  response_type: 'code',
  scope: SCOPE,
  access_type: 'offline',
  // force le renvoi d un refresh_token meme si le compte a deja autorise l app
  prompt: 'consent',
  state
});

function page(title, body) {
  return `<!doctype html><meta charset="utf-8">
<title>${title}</title>
<body style="margin:0;display:grid;place-content:center;min-height:100vh;
background:#0a0c0c;color:#f6f2e8;font:16px/1.6 system-ui,sans-serif;text-align:center">
<div><h1 style="color:#ffc61a;font-size:1.6rem;margin:0 0 .6rem">${title}</h1>
<p style="color:#9ba39f;margin:0">${body}</p></div>`;
}

const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  if (url.pathname !== '/callback') {
    res.writeHead(404).end();
    return;
  }

  const error = url.searchParams.get('error');
  if (error) {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
       .end(page('Autorisation refusee', error));
    console.error(`\n  Autorisation refusee : ${error}\n`);
    server.close();
    process.exit(1);
  }

  if (url.searchParams.get('state') !== state) {
    res.writeHead(400, { 'content-type': 'text/html; charset=utf-8' })
       .end(page('Reponse inattendue', 'La demande ne vient pas de ce script.'));
    server.close();
    process.exit(1);
  }

  const code = url.searchParams.get('code');

  const response = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      code,
      client_id: creds.client_id,
      client_secret: creds.client_secret,
      redirect_uri: REDIRECT,
      grant_type: 'authorization_code'
    })
  });

  const token = await response.json();

  if (!response.ok || !token.refresh_token) {
    res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
       .end(page('Echec', 'Regarde le terminal.'));
    console.error('\n  Google a repondu :', JSON.stringify(token, null, 2), '\n');
    server.close();
    process.exit(1);
  }

  writeFileSync(TOKEN_FILE, JSON.stringify({
    refresh_token: token.refresh_token,
    client_id: creds.client_id,
    client_secret: creds.client_secret,
    obtained: new Date().toISOString()
  }, null, 2));

  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' })
     .end(page('C est bon', 'Tu peux fermer cette page et revenir au terminal.'));

  console.log('\n  token.json ecrit. Tu n auras plus a refaire cette etape.');
  console.log('  Etape suivante :  node tools/reviews-reply/run.mjs --draft\n');

  server.close();
  process.exit(0);
});

server.listen(PORT, () => {
  console.log('\n  Ouverture du navigateur...');
  console.log('  Si rien ne s ouvre, colle cette adresse a la main :\n');
  console.log('  ' + authUrl + '\n');

  // start est une commande interne de cmd : d ou le shell.
  const open = process.platform === 'win32'
    ? spawn('cmd', ['/c', 'start', '', authUrl], { detached: true, stdio: 'ignore' })
    : spawn(process.platform === 'darwin' ? 'open' : 'xdg-open', [authUrl],
            { detached: true, stdio: 'ignore' });
  open.unref();
});
