// Driver360 — cache statique. Les appels au Worker passent toujours par le reseau.
const CACHE = "driver360-v4";  // v4 : navigation unique, menu de langue, offres (30/08/2026)
const CORE = [
  "/", "/index.html", "/jobs.html", "/wout.html", "/setdi.html", "/vivye.html", "/anplwaye.html",
  "/assets/style.css", "/assets/script.js", "/assets/suite.js",
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
  e.respondWith(
    caches.match(e.request).then((r) => r || fetch(e.request).then((rep) => {
      if (rep.ok) { const c = rep.clone(); caches.open(CACHE).then((ch) => ch.put(e.request, c)); }
      return rep;
    }).catch(() => caches.match("/index.html")))
  );
});
