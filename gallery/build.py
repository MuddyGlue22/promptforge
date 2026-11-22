#!/usr/bin/env python3
"""Build the gallery from gallery/characters.json.

Usage (from the repo root):  python3 gallery/build.py

Writes:
- public/gallery/img/<slug>-600.webp and <slug>-full.webp (resized only, never cropped)
- public/gallery/original/<slug>.<ext>  (byte-for-byte copy of the download, provenance data intact)
- public/gallery/index.html            (overview grid)
- public/gallery/<page>/index.html     (one page per character, e.g. /gallery/tiefling-warlock/)
- public/sitemap.xml and public/robots.txt

Originals live in gallery/images/<slug>.<ext>. Needs `cwebp` (brew install webp) and macOS `sips`.
"""
import html
import json
import pathlib
import re
import shutil
import subprocess
from urllib.parse import urlencode

ROOT = pathlib.Path(__file__).resolve().parent.parent
GALLERY = ROOT / "gallery"
PUBLIC = ROOT / "public"
OUT = PUBLIC / "gallery"
SITE = "https://tavernportraits.com"

SURFACE = {"Clank": "Metal plating", "Drakona": "Scales", "Wyrmling": "Scales", "Dragonborn": "Scales",
           "Lizardfolk": "Scales", "Katari": "Fur", "Tengu": "Feathers", "Leshy": "Bark"}
NUMBERS = {12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen", 16: "Sixteen"}

e = lambda s: html.escape(str(s), quote=True)


def size(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
                         capture_output=True, text=True, check=True).stdout
    vals = [int(line.split()[-1]) for line in out.splitlines() if "pixel" in line]
    return vals[0], vals[1]


def webp(src, dest, width, quality):
    subprocess.run(["cwebp", "-quiet", "-q", str(quality), "-resize", str(width), "0",
                    str(src), "-o", str(dest)], check=True)


FORMATS = {"jpeg": "jpg", "png": "png", "webp": "webp", "org.webmproject.webp": "webp"}


def image_format(path):
    out = subprocess.run(["sips", "-g", "format", str(path)], capture_output=True, text=True, check=True).stdout
    fmt = out.strip().split()[-1].lower()
    return FORMATS.get(fmt, path.suffix.lstrip(".").lower())


def human_size(n):
    return f"{n / 1_000_000:.1f} MB" if n >= 1_000_000 else f"{n // 1000} KB"


def family(model):
    return re.sub(r"\s[\d.]+$", "", model)  # "Seedream 5.5" -> "Seedream"


def page_name(slug):
    return re.sub(r"^\d+-", "", slug)  # "04-tiefling-warlock" -> "tiefling-warlock"


def trait(s, key):
    value = s.get(key)
    return s.get(f"{key}-other", value) if value == "Other" else value


def settings_rows(s):
    rows = [("Ruleset", s["ruleset"]), ("Ancestry", s["ancestry"]), ("Class", s["class"]),
            ("Gender", s["gender"]), ("Age", s["age"]), ("Build", s["build"])]
    if s.get("hair"):
        rows.append(("Hair", trait(s, "hair")))
    rows += [("Eyes", trait(s, "eyes")), (SURFACE.get(s["ancestry"], "Skin"), trait(s, "skin")),
             ("Expression", s["expression"]), ("Weapon", s["weapon"]), ("Armour", s["armour"]),
             ("Accessories", ", ".join(s.get("accessories", [])) or "None"),
             ("Framing", s["framing"]), ("Setting", s["setting"]), ("Lighting", s["lighting"]),
             ("Pose", s["pose"]), ("Art style", s["style"]), ("Image model", s["target-model"])]
    return "\n".join(f"        <dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in rows)


def try_url(s):
    params = {k: (",".join(v) if isinstance(v, list) else v) for k, v in s.items()}
    return "/?" + urlencode(params)


def fill(template, values):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], template)


def main():
    chars = json.loads((GALLERY / "characters.json").read_text())
    (OUT / "img").mkdir(parents=True, exist_ok=True)
    originals = OUT / "original"
    if originals.exists():
        shutil.rmtree(originals)
    originals.mkdir()

    for c in chars:
        src = next(p for p in (GALLERY / "images").glob(c["slug"] + ".*"))
        w, _ = size(src)
        webp(src, OUT / "img" / f"{c['slug']}-600.webp", 600, 82)
        webp(src, OUT / "img" / f"{c['slug']}-full.webp", min(w, 1200), 85)
        c["thumb"] = size(OUT / "img" / f"{c['slug']}-600.webp")
        c["full"] = size(OUT / "img" / f"{c['slug']}-full.webp")
        c["page"] = page_name(c["slug"])
        ext = image_format(src)  # some downloads have the wrong extension; name by real format
        c["original"] = f"{c['slug']}.{ext}"
        shutil.copy2(src, originals / c["original"])  # exact copy, nothing re-encoded
        c["original_label"] = f"{ext.upper().replace('JPG', 'JPEG')}, {human_size(src.stat().st_size)}"

    # Remove character pages that no longer exist in characters.json.
    pages = {c["page"] for c in chars}
    for d in OUT.iterdir():
        if d.is_dir() and d.name not in ("img", "original") and d.name not in pages:
            shutil.rmtree(d)

    char_tpl = (GALLERY / "character.template.html").read_text()
    for i, c in enumerate(chars):
        s = c["settings"]
        prev, nxt = chars[i - 1], chars[(i + 1) % len(chars)]
        values = {
            "TITLE": e(c["title"]), "SLUG": e(c["slug"]), "PAGE": e(c["page"]),
            "DESCRIPTION": e(f"{c['title']} AI portrait made with {c['model']}: the exact prompt, "
                             f"builder settings and notes on how it turned out."),
            "SUBTITLE": e(f"Built with the Tavern Portraits prompt builder ({s['ruleset']} ruleset), "
                          f"then generated with {c['model']}."),
            "FULL_W": str(c["full"][0]), "FULL_H": str(c["full"][1]), "ALT": e(c["alt"]),
            "MODEL": e(c["model"]), "STYLE": e(s["style"]), "FRAMING": e(s["framing"]),
            "NOTE": e(c["note"]), "PROMPT": e(c["prompt"]), "TRY_URL": e(try_url(s)),
            "SETTINGS": settings_rows(s),
            "ORIGINAL": e(c["original"]), "ORIGINAL_LABEL": e(c["original_label"]),
            "PREV_PAGE": e(prev["page"]), "PREV_TITLE": e(prev["title"]),
            "NEXT_PAGE": e(nxt["page"]), "NEXT_TITLE": e(nxt["title"]),
        }
        (OUT / c["page"]).mkdir(exist_ok=True)
        (OUT / c["page"] / "index.html").write_text(fill(char_tpl, values))

    families = list(dict.fromkeys(family(c["model"]) for c in chars))
    filters = ['<button type="button" data-family="All" aria-pressed="true">All models</button>'] + [
        f'<button type="button" data-family="{e(f)}" aria-pressed="false">{e(f)}</button>' for f in families]
    cards = []
    for i, c in enumerate(chars):
        lazy = ' loading="lazy"' if i > 2 else ""
        cards.append(
            f'    <a class="card" href="/gallery/{e(c["page"])}/" data-family="{e(family(c["model"]))}">'
            f'<img src="/gallery/img/{e(c["slug"])}-600.webp" width="{c["thumb"][0]}" height="{c["thumb"][1]}" '
            f'alt="{e(c["alt"])}"{lazy}>'
            f'<span class="card-body"><span class="card-title">{e(c["title"])}</span>'
            f'<span class="chips"><span class="chip model">{e(c["model"])}</span>'
            f'<span class="chip">{e(c["settings"]["style"])}</span></span></span></a>')
    index = fill((GALLERY / "index.template.html").read_text(), {
        "COUNT_WORD": NUMBERS.get(len(chars), str(len(chars))),
        "FILTERS": "\n    ".join(filters), "CARDS": "\n".join(cards)})
    (OUT / "index.html").write_text(index)

    urls = ["/", "/privacy", "/gallery/"] + [f"/gallery/{c['page']}/" for c in chars]
    (PUBLIC / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    (PUBLIC / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

    print(f"Built gallery: {len(chars)} character pages, sitemap with {len(urls)} URLs")


if __name__ == "__main__":
    main()
