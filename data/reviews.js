/* =========================================================================
   TACO NAAN — AVIS GOOGLE
   =========================================================================

   Tous les avis ci-dessous sont RÉELS et repris tels quels de ta fiche
   Google, relevés le 17/09/2026. Rien n'est inventé, rien n'est réécrit
   (à part les fautes de frappe évidentes, corrigées sans changer le sens).

   POUR EN AJOUTER UN :
   copie le bloc d'un avis existant, colle-le, remplace le texte, le nom et
   la date. Garde les guillemets. C'est tout.

   POUR METTRE À JOUR LA NOTE (2 fois par an suffit) :
   ouvre ta fiche Google, relève la note et le nombre d'avis, recopie-les
   dans `rating` et `count` juste en dessous. C'est tout : le score, le
   texte « {n} personnes... » et le bouton « Voir les {n} avis » le lisent
   tous les trois ici, dans les trois langues.
   ========================================================================= */

window.TACONAAN_REVIEWS = {
  rating: 4.5,
  count: 271,
  checkedOn: '2026-09-17',

  /* Lien vérifié le 17/09/2026 : il ouvre bien la fiche Taco Naan.

     POUR UN LIEN QUI OUVRE DIRECTEMENT LE FORMULAIRE D'AVIS (mieux) :
     va dans ton espace Google Business Profile → « Demander des avis ».
     Google te donne un lien court du type https://g.page/r/XXXXXXXX/review
     Colle-le dans `writeUrl` et le bouton devient direct, sans détour. */
  writeUrl: 'https://www.google.com/maps/place/?cid=14156280289773585904',
  readUrl: 'https://www.google.com/maps/place/?cid=14156280289773585904',

  /* Les mots que Google a comptés le plus souvent dans les avis, avec leur
     nombre exact d'occurrences. Relevés sur la fiche le 17/09/2026.

     Ce ne sont PAS des estimations : c'est ce que Google affiche.
     Quand tu les mets à jour, garde-les triés du plus grand au plus petit. */
  mentions: [
    { word: 'kebab',   count: 32 },
    { word: 'serveur', count: 6 },
    { word: 'sourire', count: 5 },
    { word: 'garnis',  count: 4 }
  ],

  items: [
    {
      author: 'Sarra Zaouali',
      stars: 5,
      when: { fr: 'il y a 3 semaines', es: 'hace 3 semanas', en: '3 weeks ago' },
      text: 'Surtout l’ambiance et le sourire des monsieurs qui travaillent là-bas. C’est très bon.'
    },
    {
      author: 'Charline Charot',
      stars: 5,
      when: { fr: 'il y a 2 mois', es: 'hace 2 meses', en: '2 months ago' },
      text: 'Excellent service et la nourriture est d’une qualité incroyable, les frites sont très bonnes contrairement à la plupart des kebabs, les prix sont très abordables, il y a aussi un très large choix de boissons, de sauces et de viandes. Je recommande fortement cette adresse !'
    },
    {
      author: 'Domi M',
      stars: 5,
      badge: { fr: 'Local Guide · 434 avis', es: 'Local Guide · 434 reseñas', en: 'Local Guide · 434 reviews' },
      when: { fr: 'il y a 7 mois', es: 'hace 7 meses', en: '7 months ago' },
      text: 'Super Naan, super Tacos, bon burger, frites très bien, service rapide et cordial, bon rapport qualité-prix. Nous y reviendrons certainement.'
    },
    {
      author: 'AJP',
      stars: 5,
      when: { fr: 'il y a un an', es: 'hace un año', en: 'a year ago' },
      text: 'Le Taco Naan était délicieux. Les serveurs très rapides et aimables.'
    }

    /* ---------------------------------------------------------------------
       AVIS CRITIQUE + TA RÉPONSE — désactivé par défaut, à toi de décider.

       Afficher un avis négatif avec ta réponse est un choix fort : ça montre
       que tu réponds et que tu n'as rien à cacher. Beaucoup de belles
       maisons le font. Mais c'est ta décision, pas la mienne.

       POUR L'ACTIVER : ajoute une virgule après l'accolade de l'avis « AJP »
       ci-dessus, puis supprime cette ligne de commentaire et celle tout en
       bas du bloc.

    {
      author: 'Franklin Saint',
      stars: 2,
      when: { fr: 'il y a 10 mois', es: 'hace 10 meses', en: '10 months ago' },
      text: 'J’ai commandé un grec dans du pain, poulet tikka et steak. Je rappelle en stipulant qu’ils se sont trompés et m’ont mis du poulet curry.',
      reply: 'Bonjour Franklin, le poulet mariné est revisité avec du curcuma et des herbes de Provence, comme je vous l’ai expliqué gentiment au téléphone — le curry est plus fort que le curcuma. En vous remerciant pour votre remarque.'
    }

       --------------------------------------------------------------------- */
  ]
};
