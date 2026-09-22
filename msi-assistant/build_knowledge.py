"""Build the MSI Assistant knowledge base and bake it into worker.js.

  python build_knowledge.py <site_folder>          e.g.  python build_knowledge.py ../site
  python build_knowledge.py <site_folder> --crawl  also crawl machinesolutions.com (needs internet)

Reads every troubleshooter app in the site folder (<app>/index.html, the KB the app was built from),
plus website_content.json (and, with --crawl, pages from machinesolutions.com/sitemap.xml).
Writes knowledge.json and worker.js (worker_template.js with the knowledge embedded).

Public-safe by design: only operator-level fixes are included in full. Causes marked for service
technicians are listed with who to contact, never the repair procedure. Internal source references
and review notes are left out.
"""
import os, re, sys, json, html as htmllib, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))

APPS = {  # folder -> (product label, brand)
    "tip-forming": ("Tip forming (PlasticWeld and Vante tipping systems)", "Vante / PlasticWeld Systems"),
    "braiding": ("Braiding (Steeger USA braiders)", "Steeger USA"),
    "bwtec-2711": ("BW-TEC 2711 automatic necking machine", "BW-TEC"),
    "hblt": ("HBLT hydraulic burst and leak testers", "Crescent Design"),
}


def load_kb(path):
    h = open(path, encoding="utf-8").read()
    m = re.search(r"const KB\s*=\s*(\{.*?\});\s*\n", h, re.S)
    kb = json.loads(m.group(1))
    for k in ("images", "tr", "review"):
        kb.pop(k, None)
    return kb


def clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


def app_chunks(folder, key):
    product, brand = APPS[key]
    kb = load_kb(os.path.join(folder, key, "index.html"))
    ui = kb["ui"]
    support = f"{ui.get('supportName', 'MSI Service')} ({ui.get('supportContact', '')})".strip()
    chunks, catalog = [], []
    tips = ui.get("introTips") or []
    if tips:
        chunks.append({"id": f"{key}:tips", "app": key, "title": f"{product}: general tips before troubleshooting",
                       "url": f"/{key}/", "text": " ".join(f"- {clean(t)}" for t in tips) + f" Support contact: {support}."})
    for L in kb["lines"]:
        lid, lname = L["id"], L.get("name", "")
        sections = L.get("sections") or kb.get("sections") or {}
        models = {m["id"]: m["name"] for m in (L.get("models") or [])}
        rem, cau = L.get("remedies", {}), L.get("cautions", {})
        if models:
            chunks.append({"id": f"{key}:{lid}:models", "app": key, "title": f"{product}: {lname} models",
                           "url": f"/{key}/", "text": "; ".join(f"{m['name']}: {clean(m.get('note'))}" for m in L["models"])})
        for d in L["defects"]:
            sec = sections.get(d.get("section"), d.get("section", ""))
            url = f"/{key}/#{lid}/{d['id']}"
            parts = [f"Symptom: {clean(d['name'])}."]
            if d.get("desc"):
                parts.append(clean(d["desc"]))
            if d.get("models") and models:
                parts.append("Applies to: " + ", ".join(models.get(m, m) for m in d["models"]) + ".")
            for i, c in enumerate(d["causes"], 1):
                if c.get("level", "operator") == "operator":
                    steps = " ".join(clean(rem.get(r, r)) for r in c.get("remedies", []))
                    line = f"Cause {i}: {clean(c['cause'])}. Fix: {steps}"
                    if c.get("hmi"):
                        line += f" Screen: {clean(c['hmi'] if isinstance(c['hmi'], str) else '; '.join(map(str, c['hmi'])))}."
                    if c.get("note"):
                        line += f" Note: {clean(c['note'])}"
                    cs = [clean(cau.get(x, x)) for x in c.get("cautions", [])]
                    if cs:
                        line += " SAFETY: " + " ".join(cs)
                else:
                    line = (f"Cause {i}: {clean(c['cause'])}. This cause requires a service technician; "
                            f"do not attempt it. Contact {support} and mention this cause.")
                parts.append(line)
            chunks.append({"id": f"{key}:{lid}:{d['id']}", "app": key,
                           "title": f"{product} / {lname} / {sec}: {clean(d['name'])}", "url": url, "text": " ".join(parts)})
            catalog.append(f"{lname}: {clean(d['name'])} -> {url}")
        for g in L.get("glossary") or []:
            chunks.append({"id": f"{key}:{lid}:g:{len(chunks)}", "app": key,
                           "title": f"{product}: {clean(g.get('group'))} - {clean(g.get('term'))}",
                           "url": f"/{key}/", "text": clean(g.get("text"))})
    return chunks, {"key": key, "product": product, "brand": brand, "support": support, "symptoms": catalog}


def crawl_site(limit=80):
    out = []
    try:
        sm = urllib.request.urlopen("https://www.machinesolutions.com/sitemap.xml", timeout=20).read().decode()
    except Exception as e:
        print("crawl skipped:", e)
        return out
    urls = [u for u in re.findall(r"<loc>(.*?)</loc>", sm) if "/legal/" not in u][:limit]
    for u in urls:
        try:
            page = urllib.request.urlopen(u, timeout=20).read().decode("utf-8", "ignore")
        except Exception:
            continue
        title = clean(htmllib.unescape((re.search(r"<title>(.*?)</title>", page, re.S) or [None, u])[1]))
        body = re.sub(r"(?is)<(script|style|nav|footer|header|noscript)[^>]*>.*?</\1>", " ", page)
        text = clean(htmllib.unescape(re.sub(r"<[^>]+>", " ", body)))
        for i in range(0, min(len(text), 6000), 1500):
            out.append({"title": title, "url": u, "text": text[i:i + 1500]})
    print("crawled", len(urls), "pages")
    return out


def main():
    site = sys.argv[1]
    chunks, products = [], []
    for key in APPS:
        if os.path.exists(os.path.join(site, key, "index.html")):
            c, p = app_chunks(site, key)
            chunks += c
            products.append(p)
    web = json.load(open(os.path.join(HERE, "website_content.json")))
    if "--crawl" in sys.argv:
        web += crawl_site()
    for i, w in enumerate(web):
        chunks.append({"id": f"web:{i}", "app": "web", "title": w["title"], "url": w["url"], "text": clean(w["text"])})
    kb = {"products": products, "chunks": chunks}
    json.dump(kb, open(os.path.join(HERE, "knowledge.json"), "w"), indent=1)
    tpl = open(os.path.join(HERE, "worker_template.js"), encoding="utf-8").read()
    open(os.path.join(HERE, "worker.js"), "w", encoding="utf-8").write(
        tpl.replace("/*KNOWLEDGE*/null", json.dumps(kb, separators=(",", ":"), ensure_ascii=False)))
    print(f"{len(chunks)} chunks, {sum(len(c['text']) for c in chunks):,} chars -> worker.js")


if __name__ == "__main__":
    main()
