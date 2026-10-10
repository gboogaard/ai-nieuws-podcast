// AI in een paar minuten — service worker: app-schil offline, afleveringen altijd vers.
const CACHE = 'ai-in-5-v2';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;
  // Audio niet onderscheppen: iOS gebruikt range-verzoeken voor mp3.
  if (url.pathname.endsWith('.mp3')) return;
  // Afleveringslijst: eerst netwerk, bij geen verbinding de laatst bekende.
  if (url.pathname.endsWith('/episodes/index.json')) {
    e.respondWith(
      fetch(e.request)
        .then((r) => { const copy = r.clone(); caches.open(CACHE).then((c) => c.put(url.pathname, copy)); return r; })
        .catch(() => caches.match(url.pathname))
    );
    return;
  }
  // De app zelf: eerst netwerk, zodat updates direct doorkomen; zonder verbinding de bewaarde versie.
  if (e.request.mode === 'navigate' || url.pathname.endsWith('.html') || url.pathname.endsWith('/')) {
    e.respondWith(
      fetch(e.request)
        .then((r) => { const copy = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, copy)); return r; })
        .catch(() => caches.match(e.request).then((hit) => hit || caches.match('index.html')))
    );
    return;
  }
  // Iconen en manifest: eerst cache, daarna netwerk.
  e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request)));
});
