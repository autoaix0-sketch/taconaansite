/* =========================================================================
   TACO NAAN — LA CARTE
   =========================================================================

   C'EST LE SEUL FICHIER À MODIFIER AU QUOTIDIEN.
   Tu changes un prix ici, il change partout sur le site.

   Prix repris de ta carte (menu/Taco Naan — Menu.md) et de tes panneaux
   en magasin. `pricesConfirmed` est donc à true : la mention « prix
   indicatifs » a disparu du site.

   Si tu augmentes un prix : tu modifies le chiffre ici, tu enregistres,
   c'est fait. Rien d'autre à toucher.

   FORMAT D'UN PLAT
     { name: 'Tacos Simple', tiers: [6.5, 7.5, 8.5] }
       -> trois colonnes : Seul / + Frite / + Menu
     { name: 'Café', price: 1.5 }
       -> un seul prix
     { name: 'Thé', free: true }
       -> affiche « offert »
   ========================================================================= */

window.TACONAAN_MENU = {
  pricesConfirmed: true,

  /* Les intitulés des trois colonnes de prix, dans les trois langues. */
  tierLabels: {
    fr: ['Seul', '+ Frite', '+ Menu'],
    es: ['Solo', '+ Patatas', '+ Menú'],
    en: ['Only', '+ Fries', '+ Meal']
  },

  /* Ce qui est vrai pour tout le monde est dit une fois ici, plutôt que
     répété sous chaque plat : la garniture de base, et ce que veut dire
     « + Menu ». Les descriptions des plats n'indiquent donc que ce qui les
     distingue. */
  tierNote: {
    fr: 'Tous les sandwichs sont garnis de tomate, salade, oignon, viande et sauces. Le menu comprend les frites et une boisson 33 cl.',
    es: 'Todos los bocadillos llevan tomate, lechuga, cebolla, carne y salsas. El menú incluye patatas y una bebida de 33 cl.',
    en: 'Every sandwich comes with tomato, lettuce, onion, meat and sauces. The meal deal includes fries and a 33 cl drink.'
  },

  categories: [
    {
      id: 'naan',
      num: '01',
      name: 'Cheese Naan',
      image: 'naan',
      board: 'board-naan',
      tagline: {
        fr: 'Le pain est pétri et cuit ici, tous les jours.',
        es: 'El pan se amasa y se hornea aquí, todos los días.',
        en: 'The bread is kneaded and baked here, every day.'
      },
      items: [
        {
          name: 'Cheese Naan', tiers: [6.5, 7.5, 8.5],
          note: {
            fr: 'viande au choix : kebab, poulet, cordon bleu, merguez…',
            es: 'carne a elegir: kebab, pollo, cordon bleu, merguez…',
            en: 'meat of your choice: kebab, chicken, cordon bleu, merguez…'
          }
        },
        {
          name: 'Cheese Naan Spécial', tiers: [8.0, 9.0, 10.0],
          note: {
            fr: '3 steaks, 3 cheddars, œuf',
            es: '3 filetes, 3 cheddars, huevo',
            en: '3 patties, 3 cheddar slices, egg'
          }
        },
        {
          name: 'Cheese Naan American', tiers: [7.0, 8.0, 9.0],
          note: {
            fr: '3 steaks, 3 cheddars',
            es: '3 filetes, 3 cheddars',
            en: '3 patties, 3 cheddar slices'
          }
        }
      ]
    },

    {
      id: 'tacos',
      num: '02',
      name: 'Tacos',
      image: 'tacos',
      board: 'board-tacos',
      tagline: {
        fr: 'Galette pressée au grill, sauce fromagère.',
        es: 'Tortilla prensada a la plancha, salsa de queso.',
        en: 'Griddle-pressed, cheese sauce.'
      },
      items: [
        { name: 'Tacos Simple', tiers: [6.5, 7.5, 8.5], note: { fr: '1 viande', es: '1 carne', en: '1 meat' } },
        { name: 'Tacos Double', tiers: [8.0, 9.0, 10.0], note: { fr: '2 viandes', es: '2 carnes', en: '2 meats' } },
        { name: 'Tacos Triple', tiers: [11.0, 12.0, 13.0], note: { fr: '3 viandes', es: '3 carnes', en: '3 meats' } }
      ]
    },

    {
      id: 'assiettes',
      num: '03',
      name: 'Assiettes',
      image: 'assiette_v2',
      tagline: {
        fr: 'Servie avec un cheese naan. On ne compte pas.',
        es: 'Servida con un cheese naan. Sin tacañería.',
        en: 'Served with a cheese naan. No skimping.'
      },
      items: [
        { name: 'Assiette Simple', price: 11.0 },
        { name: 'Assiette Double', price: 13.0 },
        { name: 'Assiette Triple', price: 14.0 },
        { name: 'Boisson en plus', price: 1.5 }
      ]
    },

    {
      id: 'barquette',
      num: '04',
      name: 'Barquettes',
      image: 'barquette_hd',
      board: 'board-barquette',
      tagline: {
        fr: 'La viande seule, ou juste les frites.',
        es: 'Solo la carne, o solo las patatas.',
        en: 'Just the meat, or just the fries.'
      },
      /* Ici les colonnes ne sont pas Seul / + Frite / + Menu mais deux
         tailles. Une categorie peut donc redefinir ses propres intitules. */
      tierLabels: {
        fr: ['Moyenne', 'Grande'],
        es: ['Mediana', 'Grande'],
        en: ['Medium', 'Large']
      },
      tiersOnly: [0, 1],
      items: [
        { name: 'Barquette Kebab', tiers: [8.0, 10.0] },
        { name: 'Barquette Frites', tiers: [3.0, 4.5] }
      ]
    },

    {
      id: 'burgers',
      num: '05',
      name: 'Burgers',
      image: 'burgers_double_cheese',
      board: 'board-burger',
      tiersOnly: [0, 2],
      tagline: {
        fr: 'Steak saisi à la commande, jamais avant.',
        es: 'Carne a la plancha al momento, nunca antes.',
        en: 'Patty seared to order, never before.'
      },
      items: [
        { name: 'Cheese Burger', tiers: [4.0, null, 6.0] },
        { name: 'Double Cheese', tiers: [5.0, null, 7.0] },
        { name: 'Chicken Burger', tiers: [5.5, null, 7.5] },
        { name: 'Big Burger', tiers: [7.0, null, 9.0] },
        { name: 'Supreme Burger', tiers: [7.5, null, 9.5] },
        { name: 'Double Chicken', tiers: [7.5, null, 9.5] }
      ]
    },

    {
      id: 'bowls',
      num: '06',
      name: 'Bowls',
      image: 'bowl',
      kind: 'photo',
      tagline: {
        fr: 'Sans pain. Tout le reste y est.',
        es: 'Sin pan. Todo lo demás está.',
        en: 'No bread. Everything else is in there.'
      },
      items: [
        { name: 'Kebab Bowl', tiers: [8.5, null, 9.5] },
        { name: 'Poulet Crousty Riz', price: 8.5 }
      ]
    },

    {
      id: 'texmex',
      num: '07',
      name: 'Tex-Mex',
      image: 'texmex',
      kind: 'photo',
      tiersOnly: [0, 2],
      tagline: {
        fr: 'À picorer, à partager, ou pas.',
        es: 'Para picar, para compartir, o no.',
        en: 'To pick at, to share, or not.'
      },
      items: [
        { name: 'Nuggets', tiers: [5.0, null, 7.0] },
        { name: 'Mozza Sticks', tiers: [5.0, null, 7.0] },
        { name: 'Bouchées Camembert', tiers: [5.0, null, 7.0] },
        { name: 'Jalapeños', tiers: [5.0, null, 7.0] },
        { name: 'Tenders', tiers: [5.0, null, 7.0] },
        { name: 'Falafel', tiers: [5.0, null, 7.0] },
        { name: 'Wings', tiers: [6.0, null, 8.0] }
      ]
    },

    {
      id: 'enfant',
      num: '08',
      name: 'Menu Kids',
      image: 'enfant',
      tagline: {
        fr: 'Le plat, les frites, la boisson — et la surprise.',
        es: 'El plato, las patatas, la bebida — y la sorpresa.',
        en: 'The dish, the fries, the drink — and the surprise.'
      },
      items: [
        {
          name: 'Menu Kids', price: 6.5,
          note: {
            fr: 'kebab ou nuggets · frites · boisson · sucette · ballon · surprise',
            es: 'kebab o nuggets · patatas · bebida · piruleta · globo · sorpresa',
            en: 'kebab or nuggets · fries · drink · lollipop · balloon · surprise'
          }
        }
      ]
    },

    {
      id: 'desserts',
      num: '09',
      name: 'Desserts',
      image: 'desserts_miel',
      flat: 3.0,
      tagline: {
        fr: 'Tous à 3 €.',
        es: 'Todos a 3 €.',
        en: 'All at €3.'
      },
      items: [
        { name: 'Naan Nutella', price: 3.0 },
        { name: 'Naan Miel', price: 3.0 },
        { name: 'Cheese Naan au fromage', price: 3.0 },
        { name: 'Tiramisu', price: 3.0 },
        { name: 'Tarte Daim', price: 3.0 }
      ]
    },

    {
      id: 'boissons',
      num: '10',
      name: 'Boissons',
      image: 'soda_coca',
      tagline: {
        fr: 'Et le thé est offert.',
        es: 'Y el té va por nuestra cuenta.',
        en: 'And the tea is on us.'
      },
      items: [
        { name: 'Canette 33 cl', price: 1.5 },
        { name: 'Bouteille 1,5 L', price: 3.0 },
        { name: 'Café', price: 1.5 },
        { name: 'Thé', free: true }
      ]
    }
  ],

  /* -----------------------------------------------------------------------
     Les choix, en bas de carte. Repris mot pour mot de tes panneaux.
     ----------------------------------------------------------------------- */

  extras: [
    {
      id: 'pains',
      title: { fr: 'Le pain', es: 'El pan', en: 'The bread' },
      values: ['Pain classique', 'Galette', 'Cheese naan']
    },
    {
      id: 'viandes',
      title: { fr: 'Les viandes', es: 'Las carnes', en: 'The meats' },
      surcharge: { amount: 2, label: { fr: 'viande en plus', es: 'carne extra', en: 'extra meat' } },
      values: ['Kebab', 'Steak', 'Viande hachée', 'Poulet', 'Cordon bleu',
               'Merguez', 'Nuggets', 'Tenders', 'Falafel']
    },
    {
      id: 'sauces',
      title: { fr: 'Les sauces', es: 'Las salsas', en: 'The sauces' },
      values: ['Mayonnaise', 'Blanche', 'Curry', 'Brésil', 'Marocaine',
               'Biggy Burger', 'Samouraï', 'Algérienne', 'Barbecue', 'Harissa',
               'Andalouse', 'Cheezy Easy', 'Moutarde', 'Ketchup', 'Chili Thaï']
    },
    {
      id: 'supplements',
      title: { fr: 'Les suppléments', es: 'Los extras', en: 'The toppings' },
      surcharge: { amount: 1, label: { fr: 'l’unité', es: 'la unidad', en: 'each' } },
      values: ['Cheddar', 'Chèvre', 'Emmental', 'Mozzarella', 'Qui Rit',
               'Raclette', 'Œuf', 'Miel', 'Légumes']
    }
  ]
};
