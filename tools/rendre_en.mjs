// Enregistreur de langue : rejoue applyLang() de la page, en anglais, hors
// navigateur, et dit quel element recoit quel texte.
//
// POURQUOI CE DETOUR. Les quatre pages produit naissent en francais : le
// balisage porte le francais, un voile cache la page, puis applyLang() la
// traduit et le voile se leve. Un visiteur avec JavaScript ne voit jamais le
// francais — mais un moteur d'indexation, un lecteur d'ecran et quiconque
// perd le script voient une page francaise annoncee <html lang="fr">.
//
// On ne peut pas deviner la traduction par expression reguliere : chaque page
// branche ses cles a sa facon (textContent, innerHTML, setTxt, setH, et des
// gardes conditionnelles). On execute donc le script DE LA PAGE avec un DOM
// d'enregistrement : ce n'est pas moi qui decide quel texte va ou, c'est la
// page elle-meme. Ce qu'elle ecrit, on le note ; on l'appliquera au balisage.
//
// Usage : node tools/rendre_en.mjs <fichier.html> <langue>
import fs from "node:fs";
import vm from "node:vm";

const [, , fichier, langue = "en"] = process.argv;
const html = fs.readFileSync(fichier, "utf8");

const ecrits = Object.create(null); // id -> {mode, v}
const options = Object.create(null); // id de <select> -> {rang: texte}
const soucis = [];

// ⚠️ LES <option> D'UNE LISTE DEROULANTE SE TRADUISENT PAR RANG, PAS PAR
// IDENTIFIANT : la page ecrit `select.options[0].text = t.a0`. Sans ce relais,
// `options` etait un tableau vide, `options[0]` valait undefined, et le script
// de vivye.html mourait AVANT de poser le titre de l'onglet — d'ou une page
// dont seule une moitie se traduisait.
function listeOptions(idSelect) {
  const rangs = new Map();
  return new Proxy({ length: 8 }, {
    get(o, p) {
      if (p === "length") return o.length;
      if (typeof p === "symbol" || !/^\d+$/.test(String(p))) return undefined;
      const r = Number(p);
      if (!rangs.has(r)) {
        rangs.set(r, new Proxy({ value: "", selected: false, text: "" }, {
          get(t2, p2) { return p2 in t2 ? t2[p2] : undefined; },
          set(t2, p2, v) {
            if (idSelect && (p2 === "text" || p2 === "textContent" || p2 === "label")) {
              (options[idSelect] ||= {})[r] = String(v);
            }
            t2[p2] = v;
            return true;
          },
        }));
      }
      return rangs.get(r);
    },
  });
}

const RIEN = () => undefined;
const methodes = {
  addEventListener: RIEN, removeEventListener: RIEN, dispatchEvent: RIEN,
  appendChild: RIEN, removeChild: RIEN, insertBefore: RIEN, remove: RIEN,
  append: RIEN, prepend: RIEN, replaceChildren: RIEN, cloneNode: RIEN,
  focus: RIEN, blur: RIEN, click: RIEN, submit: RIEN, reset: RIEN,
  setAttribute: RIEN, removeAttribute: RIEN, scrollIntoView: RIEN,
  insertAdjacentHTML: RIEN, insertAdjacentElement: RIEN, animate: RIEN,
  play: RIEN, pause: RIEN, load: RIEN, select: RIEN, setSelectionRange: RIEN,
  getAttribute: () => null, hasAttribute: () => false, closest: () => null,
  matches: () => false, contains: () => false,
  getBoundingClientRect: () => ({ top: 0, left: 0, width: 0, height: 0, bottom: 0, right: 0 }),
};

function element(id) {
  const t = {
    id: id || "", tagName: "DIV", nodeType: 1,
    dataset: {}, style: {}, classList: {
      add: RIEN, remove: RIEN, toggle: RIEN, contains: () => false, replace: RIEN,
    },
    children: [], childNodes: [], parentNode: null, firstChild: null,
    nextElementSibling: null, previousElementSibling: null,
    value: "", checked: false, disabled: false, selectedIndex: 0,
    options: listeOptions(id),
    textContent: "", innerHTML: "", innerText: "", outerHTML: "",
    className: "", href: "", src: "", hidden: false, files: [],
    offsetWidth: 0, offsetHeight: 0, scrollTop: 0, scrollHeight: 0,
    ...methodes,
    querySelector: () => element(""),
    querySelectorAll: () => [],
    getElementsByTagName: () => [],
    getElementsByClassName: () => [],
  };
  return new Proxy(t, {
    get(o, p) {
      if (p in o) return o[p];
      if (typeof p === "symbol") return undefined;
      return undefined;
    },
    set(o, p, v) {
      // ⚠️ C'EST ICI QUE TOUT SE JOUE. On ne note que les elements qui ont un
      // identifiant : ce sont les seuls qu'on saura retrouver dans le balisage.
      if (id && (p === "textContent" || p === "innerHTML")) {
        ecrits[id] = { mode: p, v: String(v) };
      }
      o[p] = v;
      return true;
    },
  });
}

const cache = new Map();
function parId(id) {
  if (!cache.has(id)) cache.set(id, element(id));
  return cache.get(id);
}

const racine = element("");
racine.lang = langue;
racine.className = "";

let titre = "";
let description = "";

const metaDescr = element("");
metaDescr.setAttribute = (n, v) => { if (n === "content") description = String(v); };

const document = new Proxy({
  documentElement: racine,
  body: element(""),
  head: element(""),
  readyState: "loading",
  cookie: "",
  getElementById: (id) => parId(String(id)),
  querySelector: (s) => (/meta\[name="description"\]/.test(String(s)) ? metaDescr : element("")),
  querySelectorAll: () => [],
  getElementsByTagName: () => [],
  getElementsByClassName: () => [],
  createElement: () => element(""),
  createTextNode: () => element(""),
  createDocumentFragment: () => element(""),
  addEventListener: RIEN, removeEventListener: RIEN,
  execCommand: RIEN, write: RIEN, close: RIEN,
  activeElement: null,
}, {
  get(o, p) {
    if (p === "title") return titre;
    if (p in o) return o[p];
    return undefined;
  },
  set(o, p, v) {
    if (p === "title") { titre = String(v); return true; }
    o[p] = v;
    return true;
  },
});

const stockage = {
  getItem: (k) => (k === "atmart_lang" ? langue : null),
  setItem: RIEN, removeItem: RIEN, clear: RIEN, key: () => null, length: 0,
};

const fenetre = {
  document,
  localStorage: stockage, sessionStorage: stockage,
  location: { href: "https://driver360.atmart.ltd/", search: "", hash: "", pathname: "/", origin: "https://driver360.atmart.ltd", protocol: "https:", host: "driver360.atmart.ltd", reload: RIEN, replace: RIEN, assign: RIEN },
  navigator: { language: langue, languages: [langue], userAgent: "node", serviceWorker: { register: RIEN }, clipboard: { writeText: RIEN }, mediaDevices: {}, onLine: true },
  history: { pushState: RIEN, replaceState: RIEN, back: RIEN },
  // ⚠️ AUCUN MINUTEUR NE PART. On veut l'etat de la page au premier affichage,
  // pas ce qu'elle deviendra apres un delai — et surtout aucune attente.
  setTimeout: RIEN, setInterval: RIEN, clearTimeout: RIEN, clearInterval: RIEN,
  requestAnimationFrame: RIEN, cancelAnimationFrame: RIEN,
  fetch: () => new Promise(() => {}),         // ne se resout jamais : rien ne suit
  MutationObserver: class { observe() {} disconnect() {} },
  IntersectionObserver: class { observe() {} disconnect() {} },
  ResizeObserver: class { observe() {} disconnect() {} },
  speechSynthesis: { speak: RIEN, cancel: RIEN, getVoices: () => [] },
  SpeechSynthesisUtterance: class {},
  matchMedia: () => ({ matches: false, addEventListener: RIEN, addListener: RIEN }),
  addEventListener: RIEN, removeEventListener: RIEN,
  print: RIEN, alert: RIEN, confirm: () => false, prompt: () => null,
  open: RIEN, scrollTo: RIEN, getComputedStyle: () => ({ getPropertyValue: () => "" }),
  URLSearchParams, URL, JSON, Math, Date, console,
  crypto: { getRandomValues: (a) => a, randomUUID: () => "0" },
  innerWidth: 1280, innerHeight: 800, devicePixelRatio: 1,
};
fenetre.window = fenetre;
fenetre.self = fenetre;
fenetre.globalThis = fenetre;

const contexte = vm.createContext(fenetre);

// Les scripts en ligne, dans l'ordre du document.
const scripts = [...html.matchAll(/<script\b(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)]
  .map((m) => m[1]);

for (const [i, code] of scripts.entries()) {
  try {
    new vm.Script(code, { filename: `${fichier}#${i}` }).runInContext(contexte, { timeout: 5000 });
  } catch (e) {
    // Un script qui echoue n'annule pas les autres : on note et on continue.
    soucis.push(`script #${i} : ${e.message}`);
  }
  // La langue ne doit jamais deriver : le script d'entete la recalcule.
  racine.lang = langue;
}

process.stdout.write(JSON.stringify({
  langue, titre, description, ecrits, options, soucis,
  nb: Object.keys(ecrits).length,
}, null, 1));
