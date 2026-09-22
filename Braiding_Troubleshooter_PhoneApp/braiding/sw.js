// Troubleshooter service worker — cache the whole app so it works offline; refresh from the network when online.
const CACHE = 'ts-f16c077c59';
const ASSETS = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => { const had = ks.some(k => k.startsWith('ts-') && k !== CACHE); return Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))).then(() => self.clients.claim()).then(() => self.clients.matchAll({type:'window'})).then(cs => { if (had) cs.forEach(c => c.postMessage({type:'updated', version:'f16c077c59'})); }); })); });
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;            // fonts etc. go straight to the network
  e.respondWith(
    fetch(e.request).then(r => { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return r; })
      .catch(() => caches.match(e.request).then(r => r || caches.match('./index.html')))
  );
});
