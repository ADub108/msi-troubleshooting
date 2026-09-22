# Deploying the troubleshooter apps to machinesolutions.com

Each app is a folder of static files — no server code, no database. Hand these to whoever manages the website.

## What to upload
```
Tipping/out/Tipping_pwa/   ->  https://www.machinesolutions.com/troubleshooter/tip-forming/
HBLT/out/HBLT_pwa/         ->  https://www.machinesolutions.com/troubleshooter/hblt/
```
(Any path works — the files use relative links — but keep each app in its own folder and keep the folder name stable, because that URL is what customers' phones will have pinned.)

Each folder contains: `index.html`, `manifest.webmanifest`, `sw.js`, `icons/`, `version.txt`.

## Requirements for the "install as an app" and offline behaviour
1. **HTTPS.** Service workers only run on https:// (the main site already is).
2. **Serve the files with these content types** (most servers do this automatically; IIS sometimes needs the first one added):
   - `.webmanifest` -> `application/manifest+json`
   - `.js` -> `text/javascript`, `.html` -> `text/html`, `.png` -> `image/png`
3. **Do not cache `sw.js` or `index.html` for long at the CDN/server** (send `Cache-Control: no-cache` or max-age of a few minutes). The service worker handles caching on the phone; long server caching would delay updates reaching customers.
4. No authentication in front of the folder if customers are meant to reach it. If it is for staff only, put it behind the normal site login — the service worker still works once the page has loaded.

## How customers install it
- **iPhone / iPad (Safari):** open the link, tap Share, then "Add to Home Screen". The page shows this hint automatically the first time.
- **Android (Chrome / Edge / Samsung Internet):** open the link; an "Install" button appears in the app's banner (and Chrome offers its own install prompt).
- **Windows / Mac (Chrome / Edge):** an install icon appears in the address bar.
After installing, it opens full-screen from its own icon and works without a connection. Whatever they saw last is cached; when they open it with a connection it silently fetches the latest version.

## Updating content
Edit the workbook, rebuild (`python tools/build_from_excel.py ...`), and upload the new `<name>_pwa` folder over the old one. `version.txt` changes on every build, which is what makes installed copies refresh. Nothing customers need to do.

## Optional
- Add a link to each app from the relevant product pages ("Troubleshoot your process").
- A QR code to the URL on the machine's front panel or in the operator manual is the easiest way onto a phone on the shop floor.
