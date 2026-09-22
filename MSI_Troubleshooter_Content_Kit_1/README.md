# MSI Troubleshooter content kit

Everything needed to edit and rebuild the Tip Forming Troubleshooter and the HBLT Troubleshooter without touching code.

```
Tipping/Tipping_Content.xlsx   <- edit this (PlasticWeld + Vante content)
Tipping/images/                <- pictures referenced from the workbook (file name = image id)
HBLT/HBLT_Content.xlsx         <- edit this (HBLT content)
HBLT/images/                   <- pictures for HBLT (empty today)
tools/                         <- template + build scripts (no need to edit)
```

## Editing
Open the workbook and edit the cream cells. The README sheet inside each workbook explains every column.
To add a picture: drop a JPG/PNG into the images folder, then type its file name (without extension) in the
`images` column of the Problems sheet (defect photos, `id:caption | id:caption`), the `image` column of the
Steps sheet (a photo for one specific step), or the `image` column of the Glossary sheet.

## Rebuilding
Requires Python 3 with `openpyxl` and `pillow` (`pip install openpyxl pillow`).

```
python tools/build_from_excel.py Tipping/Tipping_Content.xlsx Tipping/images Tipping/out
python tools/build_from_excel.py HBLT/HBLT_Content.xlsx HBLT/images HBLT/out
```
Each run writes `<name>_standalone.html` (post to SharePoint; the .aspx trick applies) and `<name>_artifact.html`
(send to Claude, or paste into a Claude session, to republish the hosted page at its existing link).

## Or skip the tooling
Send the edited workbook (and any new pictures) to Claude and ask for a rebuild — the same scripts run there.
