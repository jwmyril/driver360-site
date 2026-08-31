// Driver360 — cache statique. Les appels au Worker passent toujours par le reseau.
const CACHE = "driver360-v13";  // v6 : donnees du coach, offres elargies, telechargement
const CORE = [
  "/", "/index.html", "/404.html", "/jobs.html", "/terms.html", "/privacy.html", "/wout.html", "/setdi.html", "/vivye.html", "/anplwaye.html",
  "/assets/style.css", "/assets/theme.css", "/assets/script.js",
  // Les exercices du coach : sans ces deux fichiers la section ne se
  // traduit pas ET les exercices ne marchent pas (voir tools/verif_actifs.py).
  "/assets/komand.json", "/assets/pemi-questions.json", "/assets/suite.js",
  "/assets/brand/logo-dark-96.png", "/assets/brand/icon-192.png",
];
self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((n) =>
    Promise.all(n.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  const u = new URL(e.request.url);
  // Le coach, le vivier et le portail parlent au Worker : jamais de cache.
  if (u.origin !== location.origin || e.request.method !== "GET") return;
  // ⚠️ LES PAGES EN *NETWORK-FIRST*, LE RESTE EN CACHE-FIRST.
  //
  // Le cache-first sans revalidation gardait une page perimee jusqu'au
  // prochain changement de nom de cache. C'est exactement ce qui m'a fait
  // croire, le 31/08/2026, que le menu de langue etait casse : le navigateur
  // servait un fichier d'avant mes corrections. Un visiteur deja venu aurait
  // vu la meme chose, sans savoir pourquoi.
  //
  // Les ressources (CSS, images, donnees) restent en cache-first : elles
  // portent un `?v=` qui change quand leur contenu change.
  const estPage = e.request.mode === "navigate"
    || (e.request.headers.get("accept") || "").includes("text/html");
  if (estPage) {
    e.respondWith(
      fetch(e.request).then((rep) => {
        if (rep && rep.ok) { const c = rep.clone(); caches.open(CACHE).then((ch) => ch.put(e.request, c)); }
        return rep;
      }).catch(() => caches.match(e.request).then((r) => r || caches.match("/index.html")))
    );
    return;
  }
  e.respondWith(
    caches.match(e.request).then((r) => r || fetch(e.request).then((rep) => {
      if (rep.ok) { const c = rep.clone(); caches.open(CACHE).then((ch) => ch.put(e.request, c)); }
      return rep;
    }).catch(() => caches.match("/index.html")))
  );
});
