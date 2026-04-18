"""Re-fetch orphan BlobInfo blobs (direct to .mp4 with dead_ prefix, skip empties)."""
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
META = ROOT / "data" / "meta"
DEAD = ROOT / "data" / "dead"
DEAD.mkdir(parents=True, exist_ok=True)

GCLOUD = r"C:\Users\smith\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
BUCKET = "gs://video-161819.appspot.com"

orphans = json.load((META / "orphans.json").open(encoding="utf-8"))
bi_orphans = orphans["blobinfo_orphans"]


def gs_to_object(gs):
    m = re.match(r"^/[^/]+/(.*)$", gs)
    return m.group(1) if m else gs


def quality_of(f):
    f = f or ""
    if "1280x0720" in f or "1920x1080" in f: return "hq"
    if "0640x0360" in f or "0854x0480" in f: return "lq"
    return "u"


def dt(v):
    if isinstance(v, dict) and "__dt__" in v: return v["__dt__"]
    return v


index = {}
n_fetched = n_skipped = n_empty = n_failed = 0

for i, bi in enumerate(bi_orphans):
    obj = gs_to_object(bi.get("gs_object_name") or "")
    q = quality_of(bi.get("filename") or "")
    dst_name = f"dead_{i:03d}_{q}.mp4"
    dst = DEAD / dst_name
    if dst.exists() and dst.stat().st_size > 0:
        n_skipped += 1
    else:
        src = f"{BUCKET}/{obj}"
        if dst.exists(): dst.unlink()
        r = subprocess.run([GCLOUD, "storage", "cp", src, str(dst)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            n_failed += 1
            continue
        if dst.stat().st_size == 0:
            dst.unlink()
            n_empty += 1
            continue
        n_fetched += 1
        if n_fetched % 10 == 0:
            print(f"  fetched {n_fetched}")
    # record only files that exist
    if dst.exists():
        index[dst_name] = {
            "blobkey": bi["__name__"],
            "gs_object": obj,
            "origFilename": bi.get("filename"),
            "size": dst.stat().st_size,
            "creation": dt(bi.get("creation")),
            "quality": q,
        }

(DEAD / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"done: fetched={n_fetched} skipped={n_skipped} empty={n_empty} failed={n_failed}")
print(f"final index entries: {len(index)}")

# Write site + public data/dead.json
dead_list = []
for fname, meta in sorted(index.items()):
    dead_list.append({
        "filename": fname,
        "origFilename": meta.get("origFilename"),
        "size": meta.get("size"),
        "quality": meta.get("quality"),
        "creation": meta.get("creation"),
    })
(ROOT / "data" / "site" / "dead.json").write_text(
    json.dumps(dead_list, ensure_ascii=False, indent=1), encoding="utf-8"
)
(ROOT / "web" / "public" / "data" / "dead.json").write_text(
    json.dumps(dead_list, ensure_ascii=False, indent=1), encoding="utf-8"
)
print(f"wrote {len(dead_list)} dead entries")
