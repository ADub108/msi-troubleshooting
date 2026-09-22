"""Build the troubleshooter web app from the editable Excel workbook.

  python build_from_excel.py Tipping_Content.xlsx images out/

Writes  out/<name>_artifact.html   (page body for republishing the hosted claude.ai page)
        out/<name>_standalone.html (complete page for SharePoint / local use)
        out/<name>_kb.json         (the knowledge base the page was built from)
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import excel_io, pwa

xlsx, img_dir, out_dir = sys.argv[1:4]
name = os.path.splitext(os.path.basename(xlsx))[0].replace("_Content", "")
os.makedirs(out_dir, exist_ok=True)
kb_path = os.path.join(out_dir, f"{name}_kb.json")
excel_io.import_(xlsx, img_dir, kb_path)
kb = json.load(open(kb_path))

tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html"), encoding="utf-8").read()
body = tpl.replace("/*TITLE*/", kb["ui"]["title"]).replace("/*KB*/", json.dumps(kb, separators=(",", ":")))
open(os.path.join(out_dir, f"{name}_artifact.html"), "w", encoding="utf-8").write(body)

head, rest = body.split('<div class="top">', 1)
standalone = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
{head}
</head>
<body>
<div class="top">{rest}
</body>
</html>"""
open(os.path.join(out_dir, f"{name}_standalone.html"), "w", encoding="utf-8").write(standalone)
PWA = {"Tipping": ("Tip Forming Troubleshooter", "Tip Forming", "TIP", "Guided troubleshooting for PlasticWeld and Vante tip-forming defects."),
       "HBLT":    ("HBLT Troubleshooter", "HBLT", "HBLT", "Guided troubleshooting for HBLT burst/leak testers."),
       "BWTEC2711": ("BW-TEC 2711 Troubleshooter", "2711 Necker", "2711", "Guided troubleshooting for the BW-TEC 2711 automatic necking machine.")}
if name in PWA:
    n, sn, ic, de = PWA[name]
    ver = pwa.make_pwa(os.path.join(out_dir, f"{name}_standalone.html"), os.path.join(out_dir, f"{name}_pwa"), n, sn, ic, de)
    print("PWA folder:", os.path.join(out_dir, f"{name}_pwa"), "version", ver)
print("built", name, "->", out_dir)
