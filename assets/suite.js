// ===== Driver360 — l'enveloppe parle la langue de la page =====
//
// LE PROBLEME QU'IL RESOUT (constate le 30/08/2026, signale par l'utilisateur).
// Chaque page de la suite superposait TROIS couches de langue independantes :
//
//   1. le CORPS de la page — traduit par son propre mecanisme (dictionnaire
//      inline pour l'accueil et jobs, assets/i18n.js pour les pages derivees
//      d'atmart.ltd) ;
//   2. la NAVIGATION, ecrite en dur en anglais par tools/regen.py ;
//   3. le PIED et le BANDEAU employeur, ecrits en dur en francais.
//
// Resultat : la page anglaise affichait un pied francais, la page francaise une
// navigation anglaise, et ainsi de suite sur les six pages. Aucune page n'etait
// entierement dans une seule langue.
//
// LA SOLUTION : une seule source pour l'enveloppe, branchee sur `<html lang>`.
// On ne se branche PAS sur un mecanisme de traduction particulier — il y en a
// deux dans la suite, et ils ne se connaissent pas. On observe l'attribut
// `lang` de <html>, que les deux posent. C'est le seul signal commun, et c'est
// deja celui qu'utilise l'applier de rejistre.html.
//
// AJOUTER UNE PHRASE A L'ENVELOPPE : la mettre ici DANS LES QUATRE LANGUES, et
// poser `data-d3="cle"` sur l'element. Une cle absente d'une langue laisse le
// texte du HTML — c'est-a-dire l'anglais — et donc un melange. Les quatre
// langues, ou rien.
(function () {
  "use strict";

  var D = {
    en: {
      n_home: "Home", n_jobs: "Jobs",
      x_hiring: "I&rsquo;m hiring &rarr;", x_drive: "&larr; I drive",
      f_service: 'Driver360 — a service by <a href="https://atmart.ltd" style="color:var(--accent)">Atmart LLC</a>. Massachusetts.',
      f_question: "A question",
      f_rights: "All rights reserved.",
      b_titre: "The pool is still being built",
      b_texte: "We have no drivers to show you yet, and we are not going to pretend otherwise: the pools below are empty today. Tell us instead <strong>what you are looking for</strong> — we will let you know as soon as a profile matches, and it tells us where to concentrate our recruiting.",
      b_bouton: "Tell us what we should look for",
      b_note: "No commitment, and we never pass on a driver's name without their agreement."
    },
    fr: {
      n_home: "Accueil", n_jobs: "Emplois",
      x_hiring: "Je recrute &rarr;", x_drive: "&larr; Je conduis",
      f_service: 'Driver360 — un service <a href="https://atmart.ltd" style="color:var(--accent)">Atmart LLC</a>. Massachusetts.',
      f_question: "Une question",
      f_rights: "Tous droits réservés.",
      b_titre: "Le vivier est en train de se constituer",
      b_texte: "Nous n'avons pas encore de chauffeurs à vous montrer, et nous n'allons pas faire semblant : les viviers ci-dessous sont vides aujourd'hui. Dites-nous plutôt <strong>ce que vous cherchez</strong> — nous vous préviendrons dès qu'un profil correspond, et cela nous dit où concentrer le recrutement.",
      b_bouton: "Dire ce que je recherche",
      b_note: "Aucun engagement, et nous ne diffusons le nom d'aucun chauffeur sans son accord."
    },
    ht: {
      n_home: "Akèy", n_jobs: "Travay",
      x_hiring: "M ap anboche &rarr;", x_drive: "&larr; M ap kondi",
      f_service: 'Driver360 — yon sèvis <a href="https://atmart.ltd" style="color:var(--accent)">Atmart LLC</a>. Massachusetts.',
      f_question: "Yon kesyon",
      f_rights: "Tout dwa rezève.",
      b_titre: "Vivye a ap konstwi kounye a",
      b_texte: "Nou poko gen chofè pou nou montre w, epi nou pa pral fè sanblan : vivye anba yo vid jodi a. Pito di nou <strong>sa w ap chèche</strong> — n ap avèti w kou yon moun kadre, epi sa di nou ki kote pou nou konsantre rekritman an.",
      b_bouton: "Di nou sa m ap chèche",
      b_note: "Pa gen okenn angajman, epi nou pa bay non okenn chofè san li pa dakò."
    },
    es: {
      n_home: "Inicio", n_jobs: "Empleos",
      x_hiring: "Estoy contratando &rarr;", x_drive: "&larr; Conduzco",
      f_service: 'Driver360 — un servicio de <a href="https://atmart.ltd" style="color:var(--accent)">Atmart LLC</a>. Massachusetts.',
      f_question: "Una pregunta",
      f_rights: "Todos los derechos reservados.",
      b_titre: "El registro se está formando",
      b_texte: "Todavía no tenemos conductores que mostrarte, y no vamos a fingir lo contrario: los registros de abajo están vacíos hoy. Dinos mejor <strong>qué estás buscando</strong> — te avisaremos en cuanto un perfil encaje, y nos dice dónde concentrar la búsqueda.",
      b_bouton: "Decir lo que busco",
      b_note: "Sin compromiso, y nunca damos el nombre de un conductor sin su acuerdo."
    }
  };

  // Les NOMS DE PRODUIT ne se traduisent pas — Driver Pool, Driver Coach,
  // 7D Coach, Driver Employer. Ce sont des noms propres : les traduire ferait
  // croire a quatre produits differents selon la langue. Ils n'ont donc pas de
  // `data-d3` et restent tels quels dans le HTML.

  function poser() {
    var l = document.documentElement.lang;
    var d = D[l] || D.en;
    var noeuds = document.querySelectorAll("[data-d3]");
    for (var i = 0; i < noeuds.length; i++) {
      var t = d[noeuds[i].getAttribute("data-d3")];
      if (t != null) noeuds[i].innerHTML = t;
    }
  }

  poser();
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", poser);
  }
  // Les deux mecanismes de traduction de la suite posent `lang` sur <html> :
  // c'est le seul signal qu'ils ont en commun.
  new MutationObserver(poser).observe(document.documentElement, {
    attributes: true, attributeFilter: ["lang"]
  });
})();
