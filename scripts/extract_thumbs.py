"""Extract base64 data-URI thumbnails to actual files in web/public/thumb/
and rewrite videos.json / users.json icon field to URL paths.
"""
import base64
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "data" / "site"
THUMB = ROOT / "web" / "public" / "thumb"
UICON = ROOT / "web" / "public" / "uicon"
THUMB.mkdir(parents=True, exist_ok=True)
UICON.mkdir(parents=True, exist_ok=True)

DATA_URI = re.compile(r"^data:image/([\w+-]+);base64,(.+)$", re.DOTALL)


def extract(datauri: str):
    m = DATA_URI.match(datauri or "")
    if not m:
        return None
    ext = m.group(1).lower().replace("jpeg", "jpg")
    data = base64.b64decode(m.group(2))
    return ext, data


def rewrite_list(path: pathlib.Path, out_dir: pathlib.Path, url_prefix: str):
    items = json.load(path.open(encoding="utf-8"))
    n_written = 0
    for it in items:
        icon = it.get("icon")
        if not icon:
            continue
        res = extract(icon)
        if not res:
            # non-data icon, leave as-is
            continue
        ext, data = res
        fname = f"{it['id']}.{ext}"
        (out_dir / fname).write_bytes(data)
        it["icon"] = f"{url_prefix}/{fname}"
        n_written += 1
    path.write_text(
        json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return n_written


n_v = rewrite_list(SITE / "videos.json", THUMB, "/thumb")
n_u = rewrite_list(SITE / "users.json", UICON, "/uicon")
print(f"extracted {n_v} video thumbs → web/public/thumb/")
print(f"extracted {n_u} user icons → web/public/uicon/")

# Also refresh the copy under web/public/data/
import shutil
for f in ("videos.json", "users.json"):
    shutil.copy2(SITE / f, ROOT / "web" / "public" / "data" / f)
print("refreshed web/public/data/{videos,users}.json")
