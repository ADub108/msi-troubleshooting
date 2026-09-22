"""Turn a built standalone troubleshooter page into an installable Progressive Web App folder.

  make_pwa(standalone_html_path, out_dir, short_name, icon_text)

Produces: index.html (with manifest link, iOS meta tags, service-worker registration and install hints),
          manifest.webmanifest, sw.js, icons/ (192, 512, maskable 512, apple-touch 180).
Relative paths only, so the folder can live at any URL path on an HTTPS site.
"""
import os, json, hashlib
from PIL import Image, ImageDraw, ImageFont

TEAL = (14, 111, 115)

def _icon(path, size, text, maskable=False):
    im = Image.new("RGB", (size, size), TEAL)
    d = ImageDraw.Draw(im)
    if not maskable:
        # rounded-square look on a white canvas so it reads well on iOS
        bg = Image.new("RGB", (size, size), (255, 255, 255))
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=size // 5, fill=255)
        bg.paste(im, (0, 0), mask); im = bg; d = ImageDraw.Draw(im)
    pad = size * (0.28 if maskable else 0.16)
    lines = text.split("\n")
    fs = int(size * (0.34 if len(max(lines, key=len)) <= 3 else 0.22))
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf", fs)
    total_h = sum(d.textbbox((0, 0), l, font=font)[3] for l in lines) + (len(lines) - 1) * size * 0.04
    y = (size - total_h) / 2
    for l in lines:
        bb = d.textbbox((0, 0), l, font=font)
        d.text(((size - bb[2]) / 2, y - bb[1]), l, font=font, fill="white")
        y += bb[3] + size * 0.04
    # small MSI wordmark strip
    f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(size * 0.075))
    bb = d.textbbox((0, 0), "MACHINE SOLUTIONS", font=f2)
    d.text(((size - bb[2]) / 2, size - pad * 0.9 - bb[3]), "MACHINE SOLUTIONS", font=f2, fill=(217, 237, 238))
    im.save(path, "PNG")

SW = """// Troubleshooter service worker — cache the whole app so it works offline; refresh from the network when online.
const CACHE = 'ts-%(ver)s';
const ASSETS = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;            // fonts etc. go straight to the network
  e.respondWith(
    fetch(e.request).then(r => { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return r; })
      .catch(() => caches.match(e.request).then(r => r || caches.match('./index.html')))
  );
});
"""

INSTALL_UI = """
<style>
#pwabar{position:fixed;left:12px;right:12px;bottom:12px;z-index:50;background:var(--ink);color:var(--bg);border-radius:8px;padding:12px 14px;font-size:.9rem;display:flex;gap:12px;align-items:center;box-shadow:0 6px 20px rgba(0,0,0,.25)}
#pwabar b{font-family:var(--display)}#pwabar button{border:0;border-radius:6px;padding:7px 12px;font-weight:600;background:var(--accent);color:#fff}#pwabar .x{background:transparent;color:var(--bg);opacity:.7;padding:4px 8px}
@media (min-width:861px){#pwabar{left:auto;max-width:420px}}
</style>
<div id="pwabar" hidden><div style="flex:1"><b data-t="Install this troubleshooter">Install this troubleshooter</b><div id="pwahint" style="opacity:.85"></div></div><button id="pwainstall" hidden data-t="Install">Install</button><button class="x" id="pwaclose" aria-label="Dismiss">✕</button></div>
<script>
(function(){
  if('serviceWorker' in navigator){ navigator.serviceWorker.register('./sw.js'); let reloaded=false; navigator.serviceWorker.addEventListener('controllerchange',()=>{ if(reloaded) return; reloaded=true; }); }
  const bar=document.getElementById('pwabar'), hint=document.getElementById('pwahint'), btn=document.getElementById('pwainstall');
  const standalone = window.matchMedia('(display-mode: standalone)').matches || navigator.standalone===true;
  let dismissed=false; try{ dismissed=localStorage.getItem('pwa.dismissed')==='1'; }catch(e){}
  if(standalone||dismissed) return;
  const isIOS=/iphone|ipad|ipod/i.test(navigator.userAgent);
  let deferred=null;
  window.addEventListener('beforeinstallprompt',e=>{ e.preventDefault(); deferred=e; hint.textContent=(typeof T==='function'?T('Works offline on the shop floor.'):'Works offline on the shop floor.'); btn.hidden=false; bar.hidden=false; });
  if(isIOS){ hint.textContent=(typeof T==='function'?T('Tap the Share button, then "Add to Home Screen".'):'Tap the Share button, then "Add to Home Screen".'); bar.hidden=false; }
  btn.addEventListener('click',async()=>{ if(!deferred) return; deferred.prompt(); await deferred.userChoice; bar.hidden=true; });
  document.getElementById('pwaclose').addEventListener('click',()=>{ bar.hidden=true; try{localStorage.setItem('pwa.dismissed','1')}catch(e){} });
})();
</script>
"""

def make_pwa(standalone_html, out_dir, name, short_name, icon_text, description):
    os.makedirs(os.path.join(out_dir, "icons"), exist_ok=True)
    html = open(standalone_html, encoding="utf-8").read()
    ver = hashlib.sha1(html.encode("utf-8")).hexdigest()[:10]
    head_extra = f"""<link rel="manifest" href="./manifest.webmanifest">
<meta name="theme-color" content="#0E6F73">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="{short_name}">
<link rel="apple-touch-icon" href="./icons/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="./icons/icon-192.png">
<meta name="description" content="{description}">
"""
    html = html.replace('<meta name="color-scheme" content="light dark">', '<meta name="color-scheme" content="light dark">\n' + head_extra, 1)
    html = html.replace("</body>", INSTALL_UI + "\n</body>", 1)
    open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8").write(html)
    manifest = {
        "name": name, "short_name": short_name, "description": description,
        "start_url": "./", "scope": "./", "display": "standalone", "orientation": "any",
        "background_color": "#F2F4F6", "theme_color": "#0E6F73",
        "icons": [
            {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "icons/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    json.dump(manifest, open(os.path.join(out_dir, "manifest.webmanifest"), "w"), indent=1)
    open(os.path.join(out_dir, "sw.js"), "w").write(SW % {"ver": ver})
    _icon(os.path.join(out_dir, "icons", "icon-192.png"), 192, icon_text)
    _icon(os.path.join(out_dir, "icons", "icon-512.png"), 512, icon_text)
    _icon(os.path.join(out_dir, "icons", "icon-512-maskable.png"), 512, icon_text, maskable=True)
    _icon(os.path.join(out_dir, "icons", "apple-touch-icon.png"), 180, icon_text, maskable=True)
    open(os.path.join(out_dir, "version.txt"), "w").write(ver)
    return ver
