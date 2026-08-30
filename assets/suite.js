// ===== Driver360 — l'enveloppe et le choix de la langue =====
//
// CE FICHIER EST LA SEULE MECANIQUE DE LANGUE DE LA SUITE.
//
// Historique, pour qu'on ne refasse pas le chemin a l'envers :
//
//  · 30/08/2026 — l'utilisateur signale que les pages melangent les langues.
//    La cause n'etait pas la traduction : TROIS couches se superposaient sans
//    se connaitre (le corps de la page, la navigation ecrite en dur en
//    anglais, le pied ecrit en dur en francais). Chaque couche etait juste ;
//    leur somme ne l'etait pas. Ce fichier a d'abord regle l'enveloppe.
//
//  · Le meme jour — en verifiant, on constate qu'il ne reste AUCUN attribut
//    `data-i18n` dans les pages de la suite : `tools/regen.py` remplace la
//    navigation et le pied d'atmart.ltd, qui les portaient tous. `i18n.js` ne
//    servait donc plus qu'a poser un SECOND selecteur de langue, different de
//    celui de l'accueil. Il n'est plus charge ici, et ce fichier prend aussi
//    en charge le menu de langue — un seul menu, partout le meme.
//
// LE POINT D'ACCROCHE EST `document.documentElement.lang`. Chaque page a son
// propre dictionnaire (l'accueil et jobs en ligne, les pages derivees dans
// leur `applyLang`), et TOUTES observent cet attribut. Changer la langue se
// resume donc a le poser : le reste suit.
//
// AJOUTER UNE PHRASE A L'ENVELOPPE : la mettre ici DANS LES QUATRE LANGUES et
// poser `data-d3="cle"` sur l'element. Une cle absente d'une langue laisse
// l'anglais du HTML — donc un melange. `tools/verif_langue.py` le refuse.
(function () {
  "use strict";

  // L'ORDRE DE CETTE LISTE EST CELUI DU MENU (demande le 30/08/2026).
  // Anglais, espagnol, kreyol, francais — l'ordre des langues du
  // Massachusetts, pas l'ordre alphabetique ni celui de nos habitudes.
  var LANGUES = { en: "English", es: "Español", ht: "Kreyòl", fr: "Français" };

  var D = {
    en: {
      t_auto: "Auto",
      t_clair: "Light",
      t_sombre: "Dark",
      t_titre: "Background: %s. Click to change.",
      n_jobs: "Job Postings",
      f_service: 'Driver360 — a service by <a href="https://atmart.ltd" style="color:var(--accent)">Atmart LLC</a>.',
      f_question: "A question",
      f_rights: "All rights reserved.",
      f_terms: "Terms and conditions",
      f_privacy: "Privacy",
      b_titre: "The pool is still being built",
      b_texte: "We have no drivers to show you yet, and we are not going to pretend otherwise: the pools below are empty today. Tell us instead <strong>what you are looking for</strong> — we will let you know as soon as a profile matches, and it tells us where to concentrate our recruiting.",
      b_bouton: "Tell us what we should look for",
      b_note: "No commitment, and we never pass on a driver's name without their agreement."
    },
    fr: {
      t_auto: "Auto",
      t_clair: "Clair",
      t_sombre: "Sombre",
      t_titre: "Fond : %s. Cliquez pour changer.",
      n_jobs: "Offres d'emploi",
      f_service: 'Driver360 — un service <a href="https://atmart.ltd" style="color:var(--accent)">Atmart LLC</a>.',
      f_question: "Une question",
      f_rights: "Tous droits réservés.",
      f_terms: "Conditions d'utilisation",
      f_privacy: "Confidentialité",
      b_titre: "Le vivier est en train de se constituer",
      b_texte: "Nous n'avons pas encore de chauffeurs à vous montrer, et nous n'allons pas faire semblant : les viviers ci-dessous sont vides aujourd'hui. Dites-nous plutôt <strong>ce que vous cherchez</strong> — nous vous préviendrons dès qu'un profil correspond, et cela nous dit où concentrer le recrutement.",
      b_bouton: "Dire ce que je recherche",
      b_note: "Aucun engagement, et nous ne diffusons le nom d'aucun chauffeur sans son accord."
    },
    ht: {
      t_auto: "Otomatik",
      t_clair: "Klè",
      t_sombre: "Fonse",
      t_titre: "Fon : %s. Klike pou chanje.",
      n_jobs: "Òf travay",
      f_service: 'Driver360 — yon sèvis <a href="https://atmart.ltd" style="color:var(--accent)">Atmart LLC</a>.',
      f_question: "Yon kesyon",
      f_rights: "Tout dwa rezève.",
      f_terms: "Kondisyon itilizasyon",
      f_privacy: "Konfidansyalite",
      b_titre: "Vivye a ap konstwi kounye a",
      b_texte: "Nou poko gen chofè pou nou montre w, epi nou pa pral fè sanblan : vivye anba yo vid jodi a. Pito di nou <strong>sa w ap chèche</strong> — n ap avèti w kou yon moun kadre, epi sa di nou ki kote pou nou konsantre rekritman an.",
      b_bouton: "Di nou sa m ap chèche",
      b_note: "Pa gen okenn angajman, epi nou pa bay non okenn chofè san li pa dakò."
    },
    es: {
      t_auto: "Auto",
      t_clair: "Claro",
      t_sombre: "Oscuro",
      t_titre: "Fondo: %s. Haz clic para cambiar.",
      n_jobs: "Ofertas de empleo",
      f_service: 'Driver360 — un servicio de <a href="https://atmart.ltd" style="color:var(--accent)">Atmart LLC</a>.',
      f_question: "Una pregunta",
      f_rights: "Todos los derechos reservados.",
      f_terms: "Términos y condiciones",
      f_privacy: "Privacidad",
      b_titre: "El registro se está formando",
      b_texte: "Todavía no tenemos conductores que mostrarte, y no vamos a fingir lo contrario: los registros de abajo están vacíos hoy. Dinos mejor <strong>qué estás buscando</strong> — te avisaremos en cuanto un perfil encaje, y nos dice dónde concentrar la búsqueda.",
      b_bouton: "Decir lo que busco",
      b_note: "Sin compromiso, y nunca damos el nombre de un conductor sin su acuerdo."
    }
  };

  // Les NOMS DE PRODUIT ne se traduisent pas — Driver Pool, Driver Employer,
  // Driver Coach. Ce sont des noms propres : les traduire ferait croire a des
  // produits differents selon la langue. Ils n'ont donc pas de `data-d3`.

  function courante() {
    var l = document.documentElement.lang;
    return D[l] ? l : "en";
  }

  function poser() {
    var d = D[courante()];
    var n = document.querySelectorAll("[data-d3]");
    for (var i = 0; i < n.length; i++) {
      var t = d[n[i].getAttribute("data-d3")];
      if (t != null) n[i].innerHTML = t;
    }
    var cur = document.querySelector(".lang-current");
    if (cur) cur.textContent = "🌐 " + courante().toUpperCase();
    if (document.querySelector(".theme-btn")) appliquerTheme(themeChoisi());
    var opts = document.querySelectorAll(".lang-opt");
    for (var j = 0; j < opts.length; j++) {
      opts[j].classList.toggle("active", opts[j].getAttribute("data-lang") === courante());
    }
  }

  // --- le menu de langue -------------------------------------------------
  // UNE LISTE DEROULANTE, pas une rangee de boutons : a quatre langues la
  // rangee mangeait la barre de navigation, et sur telephone elle passait a la
  // ligne. Les classes sont celles que style.css connait deja.
  //
  // LA LANGUE RESTE AUTOMATIQUE : le petit script en tete de chaque page lit
  // `navigator.languages` et pose `lang` AVANT le premier affichage. Ce menu
  // ne sert qu'a contredire la detection, et ce choix-la est memorise.
  function menu() {
    var nav = document.querySelector(".nav-links");
    if (!nav || document.querySelector(".lang-select")) return;

    var li = document.createElement("li");
    li.className = "lang-select";
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "lang-current";
    btn.setAttribute("aria-label", "Language");
    btn.textContent = "🌐 " + courante().toUpperCase();
    var boite = document.createElement("div");
    boite.className = "lang-menu";

    Object.keys(LANGUES).forEach(function (code) {
      var o = document.createElement("button");
      o.type = "button";
      o.className = "lang-opt";
      o.setAttribute("data-lang", code);
      o.textContent = LANGUES[code];
      o.addEventListener("click", function (e) {
        e.stopPropagation();
        try { localStorage.setItem("atmart_lang", code); } catch (err) {}
        // Poser l'attribut SUFFIT : l'enveloppe et le corps de la page
        // l'observent tous les deux.
        document.documentElement.lang = code;
        boite.classList.remove("open");
      });
      boite.appendChild(o);
    });

    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      boite.classList.toggle("open");
    });
    document.addEventListener("click", function () { boite.classList.remove("open"); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") boite.classList.remove("open");
    });

    li.appendChild(btn);
    li.appendChild(boite);
    nav.appendChild(li);
    poser();
  }

  // --- le fond clair ou sombre -------------------------------------------
  // TROIS ÉTATS, et « auto » est le premier : quelqu'un qui a mis son
  // téléphone en clair a déjà dit ce qu'il voulait. On le suit, et on lui
  // laisse la possibilité de nous contredire.
  //
  // La CLASSE est posée par le petit script du <head>, avant le premier
  // affichage — sinon la page apparaîtrait sombre puis basculerait sous les
  // yeux du visiteur. Ici on ne fait que la changer quand il décide.
  var ETATS = ["auto", "clair", "sombre"];

  function themeChoisi() {
    try {
      var v = localStorage.getItem("atmart_theme");
      return ETATS.indexOf(v) >= 0 ? v : "auto";
    } catch (e) { return "auto"; }
  }

  function themeEffectif(choix) {
    if (choix === "clair" || choix === "sombre") return choix;
    try {
      return (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches)
        ? "clair" : "sombre";
    } catch (e) { return "sombre"; }
  }

  function appliquerTheme(choix) {
    var clair = themeEffectif(choix) === "clair";
    document.documentElement.classList.toggle("clair", clair);
    // La barre du navigateur, sur telephone, prend cette couleur : sans cette
    // ligne elle resterait bleu nuit au-dessus d'une page blanche.
    var m = document.querySelector('meta[name="theme-color"]');
    if (m) m.setAttribute("content", clair ? "#f4f8fb" : "#0e2240");
    var b = document.querySelector(".theme-btn");
    if (b) {
      var d = D[courante()];
      var nom = choix === "clair" ? d.t_clair : choix === "sombre" ? d.t_sombre : d.t_auto;
      b.textContent = (clair ? "\u2600\uFE0F " : "\uD83C\uDF19 ") + nom;
      b.setAttribute("aria-label", d.t_titre.replace("%s", nom));
      b.setAttribute("title", d.t_titre.replace("%s", nom));
    }
  }

  function boutonTheme() {
    var nav = document.querySelector(".nav-links");
    if (!nav || document.querySelector(".theme-btn")) return;
    var li = document.createElement("li");
    var b = document.createElement("button");
    b.type = "button";
    b.className = "theme-btn";
    b.addEventListener("click", function () {
      var suivant = ETATS[(ETATS.indexOf(themeChoisi()) + 1) % ETATS.length];
      try { localStorage.setItem("atmart_theme", suivant); } catch (e) {}
      appliquerTheme(suivant);
    });
    li.appendChild(b);
    nav.appendChild(li);
    appliquerTheme(themeChoisi());
  }

  // Le systeme peut changer d'avis pendant la visite (coucher du soleil,
  // bascule programmee). En mode « auto », on suit.
  try {
    var mq = window.matchMedia("(prefers-color-scheme: light)");
    var suivre = function () { if (themeChoisi() === "auto") appliquerTheme("auto"); };
    if (mq.addEventListener) mq.addEventListener("change", suivre);
    else if (mq.addListener) mq.addListener(suivre);
  } catch (e) {}

  // --- le menu repliable du telephone ------------------------------------
  // `aria-expanded` n'est pas un ornement : sans lui, un lecteur d'ecran
  // annonce « bouton » sans dire si le menu est ouvert ou ferme.
  function menuMobile() {
    var b = document.getElementById("d3-menu");
    var nav = document.getElementById("d3-nav");
    if (!b || !nav) return;
    b.addEventListener("click", function () {
      var ouvert = nav.classList.toggle("open");
      b.setAttribute("aria-expanded", ouvert ? "true" : "false");
    });
    // Choisir une destination referme le menu : le laisser ouvert par-dessus
    // la nouvelle page donne l'impression que le clic n'a rien fait.
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        nav.classList.remove("open");
        b.setAttribute("aria-expanded", "false");
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("open")) {
        nav.classList.remove("open");
        b.setAttribute("aria-expanded", "false");
        b.focus();
      }
    });
  }

  function demarrer() { menu(); boutonTheme(); menuMobile(); poser(); }

  poser();
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", demarrer);
  } else {
    demarrer();
  }
  new MutationObserver(poser).observe(document.documentElement, {
    attributes: true, attributeFilter: ["lang"]
  });
})();
