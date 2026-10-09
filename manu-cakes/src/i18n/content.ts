export type Lang = 'it' | 'de'

export const content = {
  it: {
    header: {
      nav: [
        { href: '#gallery', label: 'Creazioni' },
        { href: '#about', label: 'Chi Sono' },
        { href: '#services', label: 'Servizi' },
        { href: '#contact', label: 'Contatti' },
      ],
      cta: 'Scrivimi',
    },
    hero: {
      eyebrow: 'Torte Artigianali · Sargans',
      titleStart: 'Dolci che',
      titleEmphasis: 'raccontano',
      titleEnd: 'emozioni',
      body: 'Creazioni artigianali realizzate con passione — torte nuziali, compleanni e momenti speciali, fatte a mano da Manuela, a Sargans.',
      ctaPrimary: 'Scrivimi su Instagram',
      ctaSecondary: 'Guarda le Creazioni',
      heroImageAlt: 'Torta nuziale Manu Cakes, con cuore di fiori',
    },
    gallery: {
      eyebrow: 'Creazioni',
      titleStart: 'Ogni torta,',
      titleEmphasis: 'una storia',
      body: 'Una selezione delle creazioni di Manuela — ogni pezzo fatto a mano, su misura per il momento che festeggi.',
      pieces: [
        'Torta Nuziale, Rose Rosse',
        'Torta al Cioccolato e Frutti di Bosco',
        'Torta Unicorno',
        'Naked Cake, Mirtilli e Fiori',
        '“Auguri Amore”',
        'Torta a Tema Fattoria',
      ],
    },
    about: {
      eyebrow: 'Chi Sono',
      titleStart: 'Manuela —',
      titleEmphasis: 'pasticcera',
      titleEnd: ', per passione',
      body: 'Pasticcera diplomata, creo torte su misura per matrimoni, compleanni e ogni occasione che merita di essere festeggiata con qualcosa di speciale. Ogni dolce nasce nel mio laboratorio a Sargans, fatto a mano, con cura e con amore — dalle torte nuziali eleganti ai dolci più giocosi per i più piccoli.',
      quote: 'Dolci fatti con amore, per momenti speciali.',
    },
    services: {
      eyebrow: 'Servizi',
      titleStart: 'Per ogni',
      titleEmphasis: 'occasione',
      items: [
        {
          title: 'Torte Nuziali',
          description: 'Creazioni eleganti su misura per il giorno più importante, dal bozzetto al taglio della torta.',
        },
        {
          title: 'Torte di Compleanno',
          description: 'Dai classici più raffinati ai temi più creativi per i più piccoli — ogni età, ogni stile.',
        },
        {
          title: 'Torte Personalizzate',
          description: 'Hai un’idea in mente? La realizziamo insieme, su misura per la tua occasione.',
        },
        {
          title: 'Buffet di Dolci',
          description: 'Tavoli di dolci e composizioni per eventi, feste e ricorrenze.',
        },
        {
          title: 'Opzioni Senza Glutine',
          description: 'Creazioni gluten-free, senza rinunciare al gusto e alla bellezza.',
        },
        {
          title: 'Cene a Domicilio',
          description: 'Con La Monsù Napoletana, porto la cucina di casa direttamente a casa tua.',
          link: '/la-monsu',
        },
      ],
    },
    contact: {
      eyebrow: 'Contatti',
      titleStart: 'Parliamo della tua',
      titleEmphasis: 'torta',
      body: 'Sargans, Svizzera — scrivimi su Instagram per raccontarmi la tua occasione speciale.',
    },
    footer: {
      location: 'Sargans, Svizzera',
    },
    laMonsu: {
      eyebrow: 'Servizio Personal Chef',
      title: 'Non hai tempo di cucinare? Ci penso io!',
      body: 'Cucino oggi, tu mangi bene tutta la settimana. Arrivo direttamente a casa tua e, in poche ore, preparo i tuoi pasti — fatti in casa, con ingredienti genuini e il gusto autentico della cucina napoletana.',
      cta: 'Scrivimi su Instagram',
      backLink: 'Torna a Manu Cakes',
      stepsTitle: 'Come Funziona',
      steps: [
        { title: 'Mi scrivi', body: 'Raccontami le tue preferenze e quante persone sarete.' },
        { title: 'Vengo da te', body: 'Arrivo a casa tua con tutto il necessario per cucinare.' },
        { title: 'Mangi tutta la settimana', body: 'Pasti pronti, freschi, fatti con amore.' },
      ],
    },
  },
  de: {
    header: {
      nav: [
        { href: '#gallery', label: 'Kreationen' },
        { href: '#about', label: 'Über Mich' },
        { href: '#services', label: 'Leistungen' },
        { href: '#contact', label: 'Kontakt' },
      ],
      cta: 'Schreib mir',
    },
    hero: {
      eyebrow: 'Handgefertigte Torten · Sargans',
      titleStart: 'Süsses, das',
      titleEmphasis: 'Geschichten',
      titleEnd: 'erzählt',
      body: 'Handgefertigte Kreationen mit Leidenschaft — Hochzeitstorten, Geburtstage und besondere Momente, von Manuela liebevoll von Hand gemacht, in Sargans.',
      ctaPrimary: 'Schreib mir auf Instagram',
      ctaSecondary: 'Kreationen ansehen',
      heroImageAlt: 'Hochzeitstorte von Manu Cakes, mit Blumenherz',
    },
    gallery: {
      eyebrow: 'Kreationen',
      titleStart: 'Jede Torte,',
      titleEmphasis: 'eine Geschichte',
      body: 'Eine Auswahl von Manuelas Kreationen — jedes Stück von Hand gefertigt, massgeschneidert für den Anlass, den Sie feiern.',
      pieces: [
        'Hochzeitstorte mit roten Rosen',
        'Schokoladentorte mit Beeren',
        'Einhorn-Torte',
        'Naked Cake mit Heidelbeeren und Blüten',
        '„Auguri Amore“',
        'Bauernhof-Torte',
      ],
    },
    about: {
      eyebrow: 'Über Mich',
      titleStart: 'Manuela —',
      titleEmphasis: 'Konditorin',
      titleEnd: ', aus Leidenschaft',
      body: 'Als diplomierte Konditorin gestalte ich maasgeschneiderte Torten für Hochzeiten, Geburtstage und jeden Anlass, der mit etwas Besonderem gefeiert werden soll. Jede Süssigkeit entsteht in meinem Atelier in Sargans, von Hand, mit Sorgfalt und Liebe — von eleganten Hochzeitstorten bis zu verspielten Torten für die Kleinsten.',
      quote: 'Süsses mit Liebe gemacht, für besondere Momente.',
    },
    services: {
      eyebrow: 'Leistungen',
      titleStart: 'Für jeden',
      titleEmphasis: 'Anlass',
      items: [
        {
          title: 'Hochzeitstorten',
          description: 'Elegante, massgeschneiderte Kreationen für den wichtigsten Tag — vom Entwurf bis zum Anschnitt.',
        },
        {
          title: 'Geburtstagstorten',
          description: 'Von raffinierten Klassikern bis zu kreativen Themen für die Kleinsten — jedes Alter, jeder Stil.',
        },
        {
          title: 'Individuelle Torten',
          description: 'Haben Sie eine Idee im Kopf? Wir setzen sie gemeinsam um, massgeschneidert für Ihren Anlass.',
        },
        {
          title: 'Dessert-Buffets',
          description: 'Süsse Tische und Kompositionen für Events, Feste und besondere Anlässe.',
        },
        {
          title: 'Glutenfreie Optionen',
          description: 'Glutenfreie Kreationen, ohne auf Geschmack und Schönheit zu verzichten.',
        },
        {
          title: 'Kochen bei Ihnen zu Hause',
          description: 'Mit La Monsù Napoletana bringe ich die italienische Hausmannskost direkt zu Ihnen.',
          link: '/la-monsu',
        },
      ],
    },
    contact: {
      eyebrow: 'Kontakt',
      titleStart: 'Lassen Sie uns über Ihre',
      titleEmphasis: 'Torte',
      body: 'Sargans, Schweiz — schreiben Sie mir auf Instagram und erzählen Sie mir von Ihrem besonderen Anlass.',
    },
    footer: {
      location: 'Sargans, Schweiz',
    },
    laMonsu: {
      eyebrow: 'Personal-Chef-Service',
      title: 'Keine Zeit zum Kochen? Ich kümmere mich darum!',
      body: 'Ich koche heute, Sie essen die ganze Woche gut. Ich komme direkt zu Ihnen nach Hause und bereite in wenigen Stunden Ihre Mahlzeiten zu — hausgemacht, mit echten Zutaten und dem authentischen Geschmack der neapolitanischen Küche.',
      cta: 'Schreib mir auf Instagram',
      backLink: 'Zurück zu Manu Cakes',
      stepsTitle: 'So Funktioniert’s',
      steps: [
        { title: 'Sie schreiben mir', body: 'Erzählen Sie mir Ihre Vorlieben und wie viele Personen Sie sind.' },
        { title: 'Ich komme zu Ihnen', body: 'Ich komme mit allem Nötigen zu Ihnen nach Hause.' },
        { title: 'Sie essen die ganze Woche', body: 'Frisch zubereitete Mahlzeiten, mit Liebe gemacht.' },
      ],
    },
  },
}
