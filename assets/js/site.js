/* =========================================================================
   TACO NAAN — le moteur du site
   =========================================================================

   Tout est écrit à la main. Aucune librairie, rien à mettre à jour, rien qui
   casse dans deux ans.

   Ce fichier ne contient AUCUN prix et AUCUN avis : ils vivent dans
   data/menu.js et data/reviews.js. Pour changer la carte, c'est là-bas.

   Ce qu'il fait, dans l'ordre :
     1. les textes en trois langues
     2. la carte, construite à partir de data/menu.js
     3. les avis, construits à partir de data/reviews.js
     4. le badge « ouvert / fermé », calculé à l'heure de Paris
     5. les filtres de la carte
     6. la barre d'appel, la visionneuse, la carte Google, les apparitions
   ========================================================================= */

(function () {
  'use strict';

  var PHONE_HUMAN = '09 79 13 85 43';
  var PHONE_LINK = '+33979138543';

  /* Les horaires. Même chose tous les jours, 7j/7.
     En minutes depuis minuit : 11:30 = 690, 23:30 = 1410.
     Si un jour de fermeture apparaît, voir la note dans openState(). */
  var SERVICES = [
    [11 * 60 + 30, 15 * 60],       // 11:30 – 15:00
    [18 * 60, 23 * 60 + 30]        // 18:00 – 23:30
  ];

  /* ---------------------------------------------------------------- textes */

  var STRINGS = {
    fr: {
      'nav.carte': 'La carte',
      'nav.maison': 'La maison',
      'nav.avis': 'Les avis',
      'nav.venir': 'Nous trouver',
      'nav.call': 'Appeler',
      'skip': 'Aller au contenu',

      'hero.kicker': 'Dax · Avenue Saint-Vincent de Paul',
      'hero.t1': 'Kebab, naan, tacos.',
      'hero.t2': 'Faits ici, à Dax.',
      'hero.lede': 'Le pain naan est pétri et cuit sur place. La viande est grillée à la commande. <strong>On ne livre pas</strong> : vous appelez, vous passez, c’est prêt.',
      'hero.cta': 'Commander · ' + PHONE_HUMAN,
      'fact.1': 'Sur place & à emporter',
      'fact.2': 'Commande par téléphone',
      'fact.3': 'Pas de livraison',
      'fact.4': 'Ouvert 7j/7',
      'hero.alt': 'Naan kebab garni, prêt à emporter',
      'score.meta': 'avis Google',

      'carte.eyebrow': 'La carte',
      'carte.h2': 'Ce qu’il y a à manger',
      'carte.intro': 'Tout est préparé à la commande. Les prix sont les mêmes sur place et à emporter.',
      'carte.all': 'Tout',
      'carte.from': 'À partir de',
      'carte.here': 'Sur place ou à emporter',
      'carte.warn': 'Prix indicatifs, donnés de bonne foi. Confirmez au téléphone avant de passer commande.',

      'maison.eyebrow': 'La maison',
      'maison.h2': 'Un comptoir, pas une chaîne',
      'maison.p1': 'On a ouvert avenue Saint-Vincent de Paul pour faire une chose correctement : du pain naan pétri sur place, de la viande grillée au moment où vous la commandez, et des portions qui tiennent au corps.',
      'maison.p2': 'Pas de livraison, pas d’application, pas quarante minutes d’attente. Vous appelez, on prépare, vous passez prendre. C’est plus simple pour tout le monde, et c’est meilleur.',
      'proof.1.t': 'Le pain, tous les jours',
      'proof.1.d': 'Le naan est pétri et cuit ici. C’est ce qui prend le plus de temps, et c’est ce qui change tout.',
      'proof.2.t': 'Servi vite, servi chaud',
      'proof.2.d': '« Service rapide et cordial » revient dans les avis. On y tient plus qu’à tout le reste.',
      'proof.3.t': 'Le compte est bon',
      'proof.3.d': '« Les prix sont très abordables », « bon rapport qualité-prix ». On préfère remplir l’assiette.',
      'maison.caption': 'Avenue Saint-Vincent de Paul, Dax',
      'maison.alt': 'Deux naans garnis sortis du four',

      'avis.eyebrow': 'Les avis',
      'avis.h2': '271 personnes ont pris le temps d’écrire.',
      'avis.mentions': 'Ce que les clients citent le plus',
      'avis.write': 'Laisser un avis',
      'avis.read': 'Voir les 271 avis',
      'avis.source': 'Avis repris tels quels de notre fiche Google, relevés le 17 septembre 2026. La note et le nombre d’avis évoluent : Google fait foi.',
      'avis.reply': 'Notre réponse',

      'venir.eyebrow': 'Nous trouver',
      'venir.h2': '38 avenue Saint-Vincent de Paul',
      'venir.address': 'Adresse',
      'venir.phone': 'Téléphone',
      'venir.hours': 'Horaires',
      'venir.hours.v': 'Tous les jours<span>11:30 – 15:00</span><span>18:00 – 23:30</span>',
      'venir.service': 'Service',
      'venir.service.v': 'Sur place et à emporter. Commande par téléphone. Nous ne livrons pas.',
      'venir.route': 'Itinéraire',
      'map.title': 'Ouvrir la carte',
      'map.sub': 'Cliquer pour charger',
      'map.note': 'La carte Google ne se charge qu’à votre demande : la page reste rapide et aucun traceur ne démarre avant.',
      'gallery.h': 'Nos affiches',

      'foot.orders': 'Commandes',
      'foot.legal': '© 2026 Taco Naan · Dax',
      'foot.made': 'Sur place et à emporter, sans livraison',

      'open': 'Ouvert',
      'closed': 'Fermé',
      'closes.at': 'ferme à',
      'closes.in': 'ferme dans',
      'opens.at': 'ouvre à',
      'opens.tomorrow': 'ouvre demain à',
      'min': 'min',
      'close': 'Fermer',

      'free': 'offert',
      'carte.tiernote': 'Le menu comprend les frites et une boisson 33 cl.',
      'boards.eyebrow': 'La carte au comptoir',
      'boards.h2': 'Les mêmes prix qu’en vitrine.',
      'boards.intro': 'Voici nos panneaux, photographiés tels quels. Rien de retouché : ce que vous lisez ici, c’est ce que vous lisez sur place.',
      'boards.zoom': 'Agrandir',
      'boards.alt': 'Panneau de la carte —',
      'hero.scroll': 'Voir la carte',
      'video.alt': 'Préparation d’un tacos chez Taco Naan'
    },

    es: {
      'nav.carte': 'La carta',
      'nav.maison': 'La casa',
      'nav.avis': 'Opiniones',
      'nav.venir': 'Cómo llegar',
      'nav.call': 'Llamar',
      'skip': 'Ir al contenido',

      'hero.kicker': 'Dax · Avenue Saint-Vincent de Paul',
      'hero.t1': 'Kebab, naan, tacos.',
      'hero.t2': 'Hechos aquí, en Dax.',
      'hero.lede': 'El pan naan se amasa y se hornea aquí. La carne se hace a la plancha al pedirla. <strong>No repartimos a domicilio</strong>: usted llama, pasa, y está listo.',
      'hero.cta': 'Pedir · ' + PHONE_HUMAN,
      'fact.1': 'En local y para llevar',
      'fact.2': 'Pedidos por teléfono',
      'fact.3': 'Sin reparto a domicilio',
      'fact.4': 'Abierto todos los días',
      'hero.alt': 'Naan kebab relleno, listo para llevar',
      'score.meta': 'opiniones en Google',

      'carte.eyebrow': 'La carta',
      'carte.h2': 'Lo que hay para comer',
      'carte.intro': 'Todo se prepara al momento. Los precios son los mismos en local y para llevar.',
      'carte.all': 'Todo',
      'carte.from': 'Desde',
      'carte.here': 'En local o para llevar',
      'carte.warn': 'Precios orientativos, dados de buena fe. Confírmelos por teléfono antes de pedir.',

      'maison.eyebrow': 'La casa',
      'maison.h2': 'Un mostrador, no una cadena',
      'maison.p1': 'Abrimos en la avenue Saint-Vincent de Paul para hacer una cosa bien: pan naan amasado en el local, carne a la plancha en el momento del pedido, y raciones que llenan de verdad.',
      'maison.p2': 'Sin reparto, sin aplicación, sin cuarenta minutos de espera. Usted llama, nosotros preparamos, usted pasa a recoger. Es más sencillo para todos, y sale mejor.',
      'proof.1.t': 'El pan, cada día',
      'proof.1.d': 'El naan se amasa y se hornea aquí. Es lo que más tiempo lleva, y lo que marca la diferencia.',
      'proof.2.t': 'Rápido y caliente',
      'proof.2.d': '«Servicio rápido y cordial» se repite en las opiniones. Es a lo que más cuidamos.',
      'proof.3.t': 'Las cuentas claras',
      'proof.3.d': '«Los precios son muy asequibles», «buena relación calidad-precio». Preferimos llenar el plato.',
      'maison.caption': 'Avenue Saint-Vincent de Paul, Dax',
      'maison.alt': 'Dos naans rellenos recién salidos del horno',

      'avis.eyebrow': 'Opiniones',
      'avis.h2': '271 personas se tomaron el tiempo de escribir.',
      'avis.mentions': 'Lo que más mencionan los clientes',
      'avis.write': 'Dejar una opinión',
      'avis.read': 'Ver las 271 opiniones',
      'avis.source': 'Opiniones reproducidas tal cual desde nuestra ficha de Google, consultadas el 17 de septiembre de 2026. La nota y el número de opiniones cambian: Google manda.',
      'avis.reply': 'Nuestra respuesta',

      'venir.eyebrow': 'Cómo llegar',
      'venir.h2': '38 avenue Saint-Vincent de Paul',
      'venir.address': 'Dirección',
      'venir.phone': 'Teléfono',
      'venir.hours': 'Horario',
      'venir.hours.v': 'Todos los días<span>11:30 – 15:00</span><span>18:00 – 23:30</span>',
      'venir.service': 'Servicio',
      'venir.service.v': 'En local y para llevar. Pedidos por teléfono. No repartimos a domicilio.',
      'venir.route': 'Cómo llegar',
      'map.title': 'Abrir el mapa',
      'map.sub': 'Pulse para cargar',
      'map.note': 'El mapa de Google solo se carga si usted lo pide: la página va rápida y ningún rastreador se activa antes.',
      'gallery.h': 'Nuestros carteles',

      'foot.orders': 'Pedidos',
      'foot.legal': '© 2026 Taco Naan · Dax',
      'foot.made': 'En local y para llevar, sin reparto',

      'open': 'Abierto',
      'closed': 'Cerrado',
      'closes.at': 'cierra a las',
      'closes.in': 'cierra en',
      'opens.at': 'abre a las',
      'opens.tomorrow': 'abre mañana a las',
      'min': 'min',
      'close': 'Cerrar',

      'free': 'gratis',
      'carte.tiernote': 'El menú incluye patatas y una bebida de 33 cl.',
      'boards.eyebrow': 'La carta del mostrador',
      'boards.h2': 'Los mismos precios que en la tienda.',
      'boards.intro': 'Estos son nuestros paneles, fotografiados tal cual. Nada retocado: lo que lee aquí es lo que lee allí.',
      'boards.zoom': 'Ampliar',
      'boards.alt': 'Panel de la carta —',
      'hero.scroll': 'Ver la carta',
      'video.alt': 'Preparación de un tacos en Taco Naan'
    },

    en: {
      'nav.carte': 'The menu',
      'nav.maison': 'The place',
      'nav.avis': 'Reviews',
      'nav.venir': 'Find us',
      'nav.call': 'Call',
      'skip': 'Skip to content',

      'hero.kicker': 'Dax · Avenue Saint-Vincent de Paul',
      'hero.t1': 'Kebab, naan, tacos.',
      'hero.t2': 'Made here, in Dax.',
      'hero.lede': 'The naan is kneaded and baked on site. The meat is grilled when you order it. <strong>We don’t deliver</strong>: you call, you come by, it’s ready.',
      'hero.cta': 'Order · ' + PHONE_HUMAN,
      'fact.1': 'Eat in & takeaway',
      'fact.2': 'Order by phone',
      'fact.3': 'No delivery',
      'fact.4': 'Open 7 days',
      'hero.alt': 'Loaded naan kebab, ready to take away',
      'score.meta': 'Google reviews',

      'carte.eyebrow': 'The menu',
      'carte.h2': 'What there is to eat',
      'carte.intro': 'Everything is made to order. Prices are the same whether you eat in or take away.',
      'carte.all': 'Everything',
      'carte.from': 'From',
      'carte.here': 'Eat in or take away',
      'carte.warn': 'Indicative prices, given in good faith. Please confirm by phone before ordering.',

      'maison.eyebrow': 'The place',
      'maison.h2': 'A counter, not a chain',
      'maison.p1': 'We opened on avenue Saint-Vincent de Paul to do one thing properly: naan kneaded on site, meat grilled the moment you order it, and portions that actually fill you up.',
      'maison.p2': 'No delivery, no app, no forty-minute wait. You call, we cook, you pick it up. It’s simpler for everyone, and the food is better for it.',
      'proof.1.t': 'The bread, every day',
      'proof.1.d': 'The naan is kneaded and baked here. It takes the longest, and it makes all the difference.',
      'proof.2.t': 'Served fast, served hot',
      'proof.2.d': '“Quick and friendly service” keeps coming up in the reviews. We care about that most.',
      'proof.3.t': 'The maths works out',
      'proof.3.d': '“Very affordable prices”, “good value for money”. We would rather fill the plate.',
      'maison.caption': 'Avenue Saint-Vincent de Paul, Dax',
      'maison.alt': 'Two loaded naans fresh from the oven',

      'avis.eyebrow': 'Reviews',
      'avis.h2': '271 people took the time to write.',
      'avis.mentions': 'What customers mention most',
      'avis.write': 'Leave a review',
      'avis.read': 'Read all 271 reviews',
      'avis.source': 'Reviews reproduced as written on our Google listing, checked on 17 September 2026. The rating and count change over time: Google is the source of truth.',
      'avis.reply': 'Our reply',

      'venir.eyebrow': 'Find us',
      'venir.h2': '38 avenue Saint-Vincent de Paul',
      'venir.address': 'Address',
      'venir.phone': 'Phone',
      'venir.hours': 'Opening hours',
      'venir.hours.v': 'Every day<span>11:30 – 15:00</span><span>18:00 – 23:30</span>',
      'venir.service': 'Service',
      'venir.service.v': 'Eat in and takeaway. Order by phone. We do not deliver.',
      'venir.route': 'Directions',
      'map.title': 'Open the map',
      'map.sub': 'Click to load',
      'map.note': 'The Google map only loads when you ask for it: the page stays fast and no tracker starts before that.',
      'gallery.h': 'Our posters',

      'foot.orders': 'Orders',
      'foot.legal': '© 2026 Taco Naan · Dax',
      'foot.made': 'Eat in and takeaway, no delivery',

      'open': 'Open',
      'closed': 'Closed',
      'closes.at': 'closes at',
      'closes.in': 'closes in',
      'opens.at': 'opens at',
      'opens.tomorrow': 'opens tomorrow at',
      'min': 'min',
      'close': 'Close',

      'free': 'free',
      'carte.tiernote': 'The meal deal includes fries and a 33 cl drink.',
      'boards.eyebrow': 'The board in the shop',
      'boards.h2': 'The same prices as on the wall.',
      'boards.intro': 'These are our boards, photographed as they are. Nothing retouched: what you read here is what you read in the shop.',
      'boards.zoom': 'Enlarge',
      'boards.alt': 'Menu board —',
      'hero.scroll': 'See the menu',
      'video.alt': 'Making a tacos at Taco Naan'
    }
  };

  var LOCALES = { fr: 'fr-FR', es: 'es-ES', en: 'en-GB' };

  var lang = 'fr';
  var MENU = window.TACONAAN_MENU || { categories: [], extras: [] };
  var REVIEWS = window.TACONAAN_REVIEWS || { items: [] };
  var IMAGES = window.TACONAAN_IMAGES || {};

  /* ------------------------------------------------------------- outillage */

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) {
    return Array.prototype.slice.call((ctx || document).querySelectorAll(sel));
  }

  function t(key) {
    var table = STRINGS[lang] || STRINGS.fr;
    return table[key] != null ? table[key] : (STRINGS.fr[key] != null ? STRINGS.fr[key] : key);
  }

  /* Choisit la bonne langue dans un objet {fr, es, en}, ou renvoie la chaîne
     telle quelle si le champ n'est pas traduit. */
  function pick(value) {
    if (value == null) return '';
    if (typeof value === 'string') return value;
    return value[lang] || value.fr || '';
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* « Viande hachée » -> « viande_hachee ». Sert à retrouver la photo d'un
     choix dans le manifeste : identifiant du groupe + slug de la valeur,
     soit viandes_viande_hachee. Un choix sans photo reste en texte. */
  function slug(value) {
    var text = String(value);
    if (text.normalize) text = text.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    return text.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
  }

  function money(value) {
    if (value == null) return '';
    try {
      return new Intl.NumberFormat(LOCALES[lang], {
        style: 'currency', currency: 'EUR', minimumFractionDigits: 2
      }).format(value);
    } catch (e) {
      return value.toFixed(2) + ' €';
    }
  }

  /* Construit un <picture> complet à partir du manifeste : AVIF pour les
     navigateurs récents, WebP pour tous les autres, et surtout width/height
     pour que la page ne saute pas pendant le chargement. */
  function picture(key, alt, sizes, eager) {
    var entry = IMAGES[key] || IMAGES[String(key).replace(/-/g, '_')];
    if (!entry) return '';

    var stem = entry.stem;
    var last = entry.sizes[entry.sizes.length - 1];

    function srcset(ext) {
      return entry.sizes.map(function (s) {
        return 'assets/img/' + stem + '-' + s[0] + '.' + ext + ' ' + s[0] + 'w';
      }).join(', ');
    }

    return '<picture>' +
      '<source type="image/avif" srcset="' + srcset('avif') + '" sizes="' + sizes + '">' +
      '<img src="assets/img/' + stem + '-' + last[0] + '.webp"' +
      ' srcset="' + srcset('webp') + '" sizes="' + sizes + '"' +
      ' width="' + last[0] + '" height="' + last[1] + '"' +
      ' alt="' + escapeHtml(alt) + '"' +
      (eager ? ' fetchpriority="high"' : ' loading="lazy"') +
      ' decoding="async">' +
      '</picture>';
  }

  /* --------------------------------------------------------- ouvert/fermé */

  /* L'heure de Paris, quel que soit le fuseau du visiteur. Un client à
     Londres doit voir « fermé » quand c'est fermé à Dax, pas chez lui. */
  function parisMinutes() {
    var parts = new Intl.DateTimeFormat('en-GB', {
      timeZone: 'Europe/Paris', hour: '2-digit', minute: '2-digit', hour12: false
    }).formatToParts(new Date());
    var h = 0, m = 0;
    parts.forEach(function (p) {
      if (p.type === 'hour') h = parseInt(p.value, 10);
      if (p.type === 'minute') m = parseInt(p.value, 10);
    });
    return h * 60 + m;
  }

  function hhmm(minutes) {
    var h = Math.floor(minutes / 60) % 24;
    var m = minutes % 60;
    return (h < 10 ? '0' : '') + h + ':' + (m < 10 ? '0' : '') + m;
  }

  /* Renvoie { open: bool, label: '...' }.
     Si un jour de fermeture arrive un jour, c'est ici qu'il faut l'ajouter :
     il suffit de tester le jour de la semaine avant la boucle. */
  function openState() {
    var now = parisMinutes();

    for (var i = 0; i < SERVICES.length; i++) {
      var start = SERVICES[i][0], end = SERVICES[i][1];
      if (now >= start && now < end) {
        var left = end - now;
        var label = left <= 60
          ? t('closes.in') + ' ' + left + ' ' + t('min')
          : t('closes.at') + ' ' + hhmm(end);
        return { open: true, label: label };
      }
    }

    for (var j = 0; j < SERVICES.length; j++) {
      if (now < SERVICES[j][0]) {
        return { open: false, label: t('opens.at') + ' ' + hhmm(SERVICES[j][0]) };
      }
    }
    return { open: false, label: t('opens.tomorrow') + ' ' + hhmm(SERVICES[0][0]) };
  }

  function paintStatus() {
    var state = openState();
    $$('[data-status]').forEach(function (node) {
      node.className = 'status ' + (state.open ? 'status--open' : 'status--closed');
      node.innerHTML = '<span class="status__dot"></span><span><b>' +
        escapeHtml(state.open ? t('open') : t('closed')) + '</b> · ' +
        escapeHtml(state.label) + '</span>';
    });
  }

  /* ------------------------------------------------------------- la carte */

  /* Une ligne de carte. Trois cas :
       tiers  -> Seul / + Frite / + Menu, en colonnes alignees
       free   -> affiche « offert »
       price  -> un prix unique */
  function menuLine(item, columns) {
    /* Le nom et sa composition forment un seul bloc, la composition sur une
       deuxieme ligne. Cote a cote, une description un peu longue ecraserait
       la colonne des prix. */
    var note = item.note
      ? '<span class="ticket__note">' + escapeHtml(pick(item.note)) + '</span>'
      : '';
    var head = '<span class="ticket__label">' +
      '<span class="ticket__name">' + escapeHtml(item.name) + '</span>' +
      note +
    '</span>';

    if (item.tiers) {
      var cells = columns.map(function (i) {
        var value = item.tiers[i];
        return '<span class="ticket__cell">' +
          (value == null ? '<i>—</i>' : escapeHtml(money(value))) + '</span>';
      }).join('');
      return '<li class="ticket__row">' + head +
        '<span class="ticket__cells">' + cells + '</span></li>';
    }

    var solo = item.free
      ? '<span class="ticket__price ticket__price--free">' + escapeHtml(t('free')) + '</span>'
      : (item.price != null
          ? '<span class="ticket__price">' + escapeHtml(money(item.price)) + '</span>'
          : '');
    return '<li class="ticket__row ticket__row--solo">' + head +
      '<span class="ticket__lead"></span>' + solo + '</li>';
  }

  function renderMenu() {
    var grid = $('.carte__grid');
    var chips = $('.chips');
    if (!grid) return;

    var labels = (MENU.tierLabels && MENU.tierLabels[lang]) ||
                 (MENU.tierLabels && MENU.tierLabels.fr) || [];

    grid.innerHTML = MENU.categories.map(function (cat) {
      var entry = IMAGES[cat.image] || {};
      var kind = cat.kind || entry.kind || 'cutout';

      /* Les burgers et le Tex-Mex n ont pas de formule « + Frite » :
         la categorie declare alors les colonnes qui la concernent. */
      var usesTiers = cat.items.some(function (it) { return !!it.tiers; });
      var columns = cat.tiersOnly || [0, 1, 2];

      /* Les barquettes se vendent en Moyenne / Grande, pas en
         Seul / + Frite / + Menu : une categorie peut redefinir ses intitules
         de colonnes, sinon on prend ceux de la carte. */
      var catLabels = (cat.tierLabels &&
                       (cat.tierLabels[lang] || cat.tierLabels.fr)) || labels;

      var header = usesTiers
        ? '<li class="ticket__head"><span></span><span class="ticket__cells">' +
            columns.map(function (i) {
              return '<span class="ticket__cell">' + escapeHtml(catLabels[i] || '') + '</span>';
            }).join('') +
          '</span></li>'
        : '';

      var lines = cat.items.map(function (it) { return menuLine(it, columns); }).join('');

      var prices = [];
      cat.items.forEach(function (it) {
        if (it.tiers) {
          it.tiers.forEach(function (v) { if (typeof v === 'number') prices.push(v); });
        } else if (typeof it.price === 'number') {
          prices.push(it.price);
        }
      });
      var lowest = prices.length ? Math.min.apply(null, prices) : null;

      var foot = (lowest != null
          ? '<span>' + escapeHtml(t('carte.from')) + ' <b>' + escapeHtml(money(lowest)) + '</b></span>'
          : '') +
        '<span>' + escapeHtml(t('carte.here')) + '</span>';

      return '<article class="ticket" data-cat="' + escapeHtml(cat.id) + '" data-reveal>' +
        '<div class="ticket__top">' +
          '<span class="ticket__num">' + escapeHtml(cat.num) + '</span>' +
          '<div class="ticket__title">' +
            '<h3>' + escapeHtml(cat.name) + '</h3>' +
            '<p>' + escapeHtml(pick(cat.tagline)) + '</p>' +
          '</div>' +
          '<div class="ticket__thumb" data-kind="' + kind + '">' +
            picture(cat.image, cat.name, '(min-width: 52rem) 8rem, 6rem') +
          '</div>' +
        '</div>' +
        '<ul class="ticket__list">' + header + lines + '</ul>' +
        '<div class="ticket__foot">' + foot + '</div>' +
      '</article>';
    }).join('');

    if (chips) {
      chips.innerHTML = '<button type="button" data-filter="*" aria-pressed="true">' +
        escapeHtml(t('carte.all')) + '</button>' +
        MENU.categories.map(function (cat) {
          return '<button type="button" data-filter="' + escapeHtml(cat.id) +
            '" aria-pressed="false">' + escapeHtml(cat.name) + '</button>';
        }).join('');
    }

    var tierNote = $('.tier-note');
    if (tierNote) tierNote.textContent = pick(MENU.tierNote);

    var extras = $('.extras');
    if (extras) {
      extras.innerHTML = (MENU.extras || []).map(function (group) {
        /* Le supplement viande et le supplement fromage n ont pas le meme
           tarif : chaque groupe porte le sien. */
        var tag = group.surcharge
          ? '<span class="extras__tag">+' + escapeHtml(money(group.surcharge.amount)) +
            ' <i>' + escapeHtml(pick(group.surcharge.label)) + '</i></span>'
          : '';
        /* Le pain et les viandes ont une photo par choix : on les montre.
           Les sauces et les suppléments n'en ont pas, ils restent en liste. */
        var keyOf = function (value) { return group.id + '_' + slug(value); };
        var withPics = group.values.some(function (v) { return !!IMAGES[keyOf(v)]; });

        var values = group.values.map(function (v) {
          if (!withPics) return '<li>' + escapeHtml(v) + '</li>';
          /* Le steak n a pas de photo : on garde quand meme la case, sinon
             son nom remonte tout seul au-dessus de la ligne des autres. */
          var pic = picture(keyOf(v), v, '(min-width: 52rem) 5rem, 4rem');
          return '<li class="extras__item">' +
            '<span class="extras__pic">' + pic + '</span>' +
            '<span class="extras__name">' + escapeHtml(v) + '</span></li>';
        }).join('');

        return '<div class="extras__group" data-reveal>' +
          '<h3>' + escapeHtml(pick(group.title)) + tag + '</h3>' +
          '<ul' + (withPics ? ' data-pics' : '') + '>' + values + '</ul></div>';
      }).join('');
    }

    /* La mention de prix indicatifs disparait d elle-meme le jour ou
       pricesConfirmed passe a true dans data/menu.js. */
    var warn = $('.price-note');
    if (warn) {
      warn.hidden = !!MENU.pricesConfirmed;
      if (!MENU.pricesConfirmed) warn.textContent = t('carte.warn');
    }
  }

  /* --------------------------------------------------------- les panneaux */

  /* La carte telle qu elle est affichee au comptoir. C est la preuve que les
     prix du site sont les vrais : le visiteur voit le meme panneau. */
  function renderBoards() {
    var host = $('.boards');
    if (!host || !window.TACONAAN_BOARDS) return;

    host.innerHTML = window.TACONAAN_BOARDS.map(function (board) {
      var big = board.sizes[board.sizes.length - 1];
      var srcset = function (ext) {
        return board.sizes.map(function (sz) {
          return 'assets/img/' + board.stem + '-' + sz[0] + '.' + ext + ' ' + sz[0] + 'w';
        }).join(', ');
      };
      return '<button type="button" class="board" data-full="assets/img/' +
          board.stem + '-' + big[0] + '.webp">' +
        '<picture>' +
          '<source type="image/avif" srcset="' + srcset('avif') + '" sizes="(min-width: 60rem) 34rem, 92vw">' +
          '<img src="assets/img/' + board.stem + '-' + big[0] + '.webp"' +
            ' srcset="' + srcset('webp') + '" sizes="(min-width: 60rem) 34rem, 92vw"' +
            ' width="' + big[0] + '" height="' + big[1] + '"' +
            ' alt="' + escapeHtml(t('boards.alt') + ' ' + board.label) + '"' +
            ' loading="lazy" decoding="async">' +
        '</picture>' +
        '<span class="board__label">' + escapeHtml(board.label) +
          '<i>' + escapeHtml(t('boards.zoom')) + '</i></span>' +
      '</button>';
    }).join('');
  }


  function wireFilters() {
    var chips = $('.chips');
    if (!chips) return;

    chips.addEventListener('click', function (event) {
      var button = event.target.closest('button[data-filter]');
      if (!button) return;

      var wanted = button.getAttribute('data-filter');
      $$('button', chips).forEach(function (b) {
        b.setAttribute('aria-pressed', String(b === button));
      });
      $$('.ticket').forEach(function (card) {
        card.hidden = wanted !== '*' && card.getAttribute('data-cat') !== wanted;
      });
    });
  }

  /* --------------------------------------------------------------- avis */

  function stars(count) {
    var full = Math.round(count || 5);
    return new Array(full + 1).join('★') + new Array(6 - full).join('☆');
  }

  function renderReviews() {
    var grid = $('.avis__grid');
    if (grid) {
      grid.innerHTML = (REVIEWS.items || []).map(function (review) {
        var badge = review.badge ? escapeHtml(pick(review.badge)) + ' · ' : '';
        var reply = review.reply
          ? '<div class="note__reply"><b>' + escapeHtml(t('avis.reply')) + '</b>' +
            escapeHtml(review.reply) + '</div>'
          : '';
        return '<figure class="note" data-reveal>' +
          '<div class="note__stars" aria-label="' + review.stars + '/5">' +
            stars(review.stars) + '</div>' +
          '<blockquote class="note__text">' + escapeHtml(review.text) + '</blockquote>' +
          '<figcaption class="note__by"><b>' + escapeHtml(review.author) + '</b>' +
            badge + escapeHtml(pick(review.when)) + '</figcaption>' +
          reply +
        '</figure>';
      }).join('');
    }

    /* Les mots que les clients emploient, avec le nombre de fois où Google
       les a comptés. Ce sont des chiffres relevés sur la fiche, pas une
       estimation. */
    var gauge = $('.gauge');
    if (gauge && REVIEWS.mentions && REVIEWS.mentions.length) {
      var top = Math.max.apply(null, REVIEWS.mentions.map(function (m) { return m.count; }));
      gauge.innerHTML = REVIEWS.mentions.map(function (m, i) {
        return '<div class="gauge__row"' + (i === 0 ? ' data-top' : '') + '>' +
          '<span>' + escapeHtml(m.word) + '</span>' +
          '<span class="gauge__bar"><span class="gauge__fill" data-w="' +
            Math.round(m.count / top * 100) + '"></span></span>' +
          '<span>' + m.count + '×</span>' +
        '</div>';
      }).join('');
    }

    var num = $('.score__num');
    if (num && REVIEWS.rating) {
      num.textContent = new Intl.NumberFormat(LOCALES[lang], {
        minimumFractionDigits: 1
      }).format(REVIEWS.rating);
    }
    $$('[data-review-count]').forEach(function (n) { n.textContent = REVIEWS.count; });
    $$('[data-review-write]').forEach(function (n) { n.href = REVIEWS.writeUrl; });
    $$('[data-review-read]').forEach(function (n) { n.href = REVIEWS.readUrl; });
  }

  /* ------------------------------------------------------------- galerie */

  /* ------------------------------------------------------------ affiches */

  /* Les affiches. Une vignette détourée, seule sur du noir, ne dit rien ; la
     même photo avec un titre, un prix et le blason devient une image de
     marque. C'est le principe de l'affiche papier du comptoir, refaite dans le
     noir et le jaune du site.

     Le texte est cuit dans l'image, donc il y a une affiche par langue :
     tools/make_posters.py en génère trois, et renderAffiches() se rejoue à
     chaque bascule — pick() choisit la bonne. */
  function renderAffiches() {
    var host = $('.affiches');
    if (!host || !window.TACONAAN_POSTERS) return;

    host.innerHTML = window.TACONAAN_POSTERS.map(function (poster) {
      var stem = pick(poster.stem);
      var alt = pick(poster.alt);
      var big = poster.sizes[poster.sizes.length - 1];

      function srcset(ext) {
        return poster.sizes.map(function (sz) {
          return 'assets/img/' + stem + '-' + sz[0] + '.' + ext + ' ' + sz[0] + 'w';
        }).join(', ');
      }

      var sizes = '(min-width: 60rem) 19rem, 45vw';

      return '<button type="button" class="affiche"' +
          ' data-full="assets/img/' + stem + '-' + big[0] + '.webp"' +
          ' data-label="' + escapeHtml(alt) + '">' +
        '<picture>' +
          '<source type="image/avif" srcset="' + srcset('avif') + '" sizes="' + sizes + '">' +
          '<img src="assets/img/' + stem + '-' + big[0] + '.webp"' +
            ' srcset="' + srcset('webp') + '" sizes="' + sizes + '"' +
            ' width="' + big[0] + '" height="' + big[1] + '"' +
            ' alt="' + escapeHtml(alt) + '"' +
            ' loading="lazy" decoding="async">' +
        '</picture>' +
        /* Pas de bandeau de titre ici : l'affiche porte deja le sien, en bas,
           et deux pieds de page l'un sur l'autre se marchent dessus - c'etait
           illisible sur telephone. Il ne reste que la pastille d'agrandissement,
           et le nom du plat vit dans l'alt. */
        '<i class="affiche__zoom">' + escapeHtml(t('boards.zoom')) + '</i>' +
      '</button>';
    }).join('');
  }

  function wireLightbox() {
    var box = $('.lightbox');
    if (!box) return;
    var img = $('img', box);

    document.addEventListener('click', function (event) {
      var button = event.target.closest('[data-full]');
      if (!button) return;
      img.src = button.getAttribute('data-full');
      /* L'agrandissement garde le nom du plat : c'est la même image, elle ne
         devient pas décorative en grandissant. */
      img.alt = button.getAttribute('data-label') || '';
      if (typeof box.showModal === 'function') box.showModal();
    });

    $('.lightbox__close', box).addEventListener('click', function () { box.close(); });
    /* Un clic sur le fond noir ferme aussi : c'est le geste attendu. */
    box.addEventListener('click', function (event) {
      if (event.target === box) box.close();
    });
    box.addEventListener('close', function () { img.removeAttribute('src'); });
  }

  /* ------------------------------------------------------- carte Google */

  function wireMap() {
    var facade = $('.mapbox__facade');
    if (!facade) return;

    facade.addEventListener('click', function () {
      var frame = document.createElement('iframe');
      frame.src = 'https://maps.google.com/maps?q=' +
        encodeURIComponent('38 Av. Saint-Vincent de Paul, 40100 Dax, France') +
        '&output=embed';
      frame.title = 'Taco Naan — 38 avenue Saint-Vincent de Paul, Dax';
      frame.loading = 'lazy';
      frame.referrerPolicy = 'no-referrer-when-downgrade';
      facade.replaceWith(frame);
    });
  }

  /* ------------------------------------------- apparitions, barre, langue */

  function wireReveal() {
    if (!('IntersectionObserver' in window) ||
        matchMedia('(prefers-reduced-motion: reduce)').matches) {
      $$('[data-reveal]').forEach(function (n) { n.classList.add('is-in'); });
      $$('.gauge__fill').forEach(function (n) { n.style.width = n.dataset.w + '%'; });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        /* isIntersecting seul ne suffit pas. Lors d'un saut - clic sur un lien
           d'ancre, molette rapide, restauration de la position de lecture au
           retour sur la page - l'element traverse l'ecran entre deux images et
           l'observateur ne le voit jamais « dedans ». Il resterait alors
           invisible pour toujours, et la section apparaitrait vide.
           On revele donc aussi tout ce qui est deja remonte au-dessus de la
           ligne de flottaison. */
        var passed = entry.boundingClientRect.top < window.innerHeight;
        if (!entry.isIntersecting && !passed) return;

        entry.target.classList.add('is-in');
        $$('.gauge__fill', entry.target).forEach(function (fill) {
          fill.style.width = fill.dataset.w + '%';
        });
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });

    $$('[data-reveal]').forEach(function (n) { observer.observe(n); });
  }

  /* ------------------------------------------------------- video du hero */

  /* Une video de fond qui tourne en permanence, c'est du processeur et de la
     batterie consommes pour une image que plus personne ne regarde des qu'on
     a defile. On la met en pause des qu'elle quitte l'ecran, et on ne la
     lance pas du tout si le visiteur a demande moins d'animations : il voit
     alors l'affiche fixe, qui suffit.

     Sur un ecran etroit, on ne la lance pas non plus. Le degrade du hero la
     couvre a 96 % du cote du texte, et sur un telephone il ne reste rien a
     regarder : la video coutait 337 Ko pour un liseré. L'affiche, elle, fait
     37 Ko et dit la meme chose. Avec preload="none" dans le HTML, ne pas
     appeler play() suffit a ce que rien ne parte sur le reseau. */
  var VIDEO_MIN_WIDTH = '(min-width: 48rem)';

  function wireHeroVideo() {
    var video = $('.hero__video');
    if (!video) return;

    var still = matchMedia('(prefers-reduced-motion: reduce)').matches
             || !matchMedia(VIDEO_MIN_WIDTH).matches;

    /* Le HTML ne porte plus autoplay : sans appel a play(), rien ne part sur
       le reseau et l'affiche reste. Il n'y a donc rien a defaire ici. */
    if (still) return;

    /* play() renvoie une promesse rejetee si le navigateur refuse de lancer la
       lecture - onglet en arriere-plan, economie d'energie, reglage du
       systeme. Ce n'est pas une erreur : l'affiche reste, on ne signale rien. */
    function start() {
      var attempt = video.play();
      if (attempt && attempt.catch) attempt.catch(function () {});
    }

    /* Sans IntersectionObserver, plus personne ne mettrait la video en pause
       en bas de page - mais ne pas la lancer du tout serait pire : le HTML ne
       porte plus autoplay, donc il ne resterait que l'affiche. On la lance. */
    if (!('IntersectionObserver' in window)) {
      start();
      return;
    }

    new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          start();
        } else {
          video.pause();
        }
      });
    }, { threshold: 0.05 }).observe(video);
  }

  function wireChrome() {
    var topbar = $('.topbar');
    var callbar = $('.callbar');
    var hero = $('.hero');

    function onScroll() {
      if (topbar) topbar.setAttribute('data-stuck', String(window.scrollY > 24));
      if (callbar && hero) {
        callbar.setAttribute('data-show', String(window.scrollY > hero.offsetHeight * 0.6));
      }
    }
    addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  function applyLanguage(next) {
    lang = STRINGS[next] ? next : 'fr';
    document.documentElement.setAttribute('lang', lang);

    $$('[data-i18n]').forEach(function (node) {
      node.textContent = t(node.getAttribute('data-i18n'));
    });
    /* Quelques textes contiennent du gras ou des <span> : ceux-là sont
       injectés en HTML, et uniquement depuis le dictionnaire ci-dessus. */
    $$('[data-i18n-html]').forEach(function (node) {
      node.innerHTML = t(node.getAttribute('data-i18n-html'));
    });
    $$('[data-i18n-aria]').forEach(function (node) {
      node.setAttribute('aria-label', t(node.getAttribute('data-i18n-aria')));
    });

    $$('.lang button').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === lang));
    });

    try { localStorage.setItem('taconaan.lang', lang); } catch (e) { /* navigation privée */ }

    renderMenu();
    renderBoards();
    renderReviews();
    renderAffiches();
    paintStatus();
    wireReveal();
  }

  function wireLanguage() {
    var box = $('.lang');
    if (!box) return;
    box.addEventListener('click', function (event) {
      var button = event.target.closest('button[data-lang]');
      if (button) applyLanguage(button.getAttribute('data-lang'));
    });
  }

  function initialLanguage() {
    var saved = null;
    try { saved = localStorage.getItem('taconaan.lang'); } catch (e) { /* ignore */ }
    if (saved && STRINGS[saved]) return saved;
    var browser = (navigator.language || 'fr').slice(0, 2).toLowerCase();
    return STRINGS[browser] ? browser : 'fr';
  }

  /* ------------------------------------------------------------- démarrage */

  function start() {
    wireHeroVideo();
    wireLanguage();
    wireFilters();
    wireLightbox();
    wireMap();
    wireChrome();
    applyLanguage(initialLanguage());

    /* Le badge se rafraîchit tout seul : un visiteur qui laisse l'onglet
       ouvert pendant le service voit « ouvert » devenir « fermé ». */
    setInterval(paintStatus, 60000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
