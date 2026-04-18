"""Cross-reference base.doga <-> BlobInfo <-> local bucket, produce plan."""
import json
import pathlib
import re
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
META = ROOT / "data" / "meta"
BLOB_DIR = ROOT / "data" / "blob"

base = json.load((META / "base.json").open(encoding="utf-8"))
blobinfo = json.load((META / "BlobInfo.json").open(encoding="utf-8"))

dogas = [e for e in base if e.get("anal") == "doga"]

# blobkey (__name__) -> BlobInfo
bi_by_key = {bi["__name__"]: bi for bi in blobinfo}

# local bucket filenames present
local_files = {p.name for p in BLOB_DIR.iterdir() if p.is_file()}

# GCS object name stored in BlobInfo.gs_object_name starts with "/<bucket>/<object>"
def gs_to_object(gs):
    # e.g. "/video-161819.appspot.com/ABPtcPoc..."  -> "ABPtcPoc..."
    m = re.match(r"^/[^/]+/(.*)$", gs)
    return m.group(1) if m else gs


# Classify quality by filename (AppEngine uploads used r30s0640x0360 / r60s1280x0720 etc)
def quality_of(bi):
    f = (bi or {}).get("filename") or ""
    if "1280x0720" in f or "1920x1080" in f:
        return "hq"
    if "0640x0360" in f or "0854x0480" in f:
        return "lq"
    return "u"  # unknown


videos = []
missing = []
for d in dogas:
    vid = d.get("__id__")
    blob_keys = d.get("blob") or []
    blobs = []
    for bk in blob_keys:
        bi = bi_by_key.get(bk)
        if not bi:
            missing.append({"video_id": vid, "blobkey": bk, "reason": "no BlobInfo"})
            continue
        obj = gs_to_object(bi.get("gs_object_name") or "")
        present = obj in local_files
        blobs.append({
            "blobkey": bk,
            "gs_object": obj,
            "size": bi.get("size"),
            "filename": bi.get("filename"),
            "quality": quality_of(bi),
            "present_locally": present,
        })
        if not present:
            missing.append({"video_id": vid, "blobkey": bk, "gs_object": obj, "reason": "not in local bucket"})
    videos.append({
        "id": vid,
        "name": d.get("name"),
        "text": d.get("text"),
        "icon": d.get("icon"),  # base64 thumbnail
        "kusr": (d.get("kusr") or {}).get("__key__", {}).get("id") if d.get("kusr") else None,
        "view": d.get("view"),
        "qual": d.get("qual"),
        "bone": d.get("bone"),
        "tlen": d.get("tlen"),
        "tpos": d.get("tpos"),
        "attr": d.get("attr") or [],
        "blobs": blobs,
    })

# Orphan BlobInfo: not referenced by any doga
referenced_keys = {b for d in dogas for b in (d.get("blob") or [])}
orphans_bi = [bi for bi in blobinfo if bi["__name__"] not in referenced_keys]

# Orphan bucket objects: in local_files but not referenced by any doga's BlobInfo
referenced_objects = set()
for d in dogas:
    for bk in d.get("blob") or []:
        bi = bi_by_key.get(bk)
        if bi:
            referenced_objects.add(gs_to_object(bi.get("gs_object_name") or ""))
orphan_files = sorted(local_files - referenced_objects - {"_export"})

# Special: some orphan bucket objects might be tracked by orphan BlobInfo
orphan_bi_objs = {gs_to_object(bi.get("gs_object_name") or "") for bi in orphans_bi}

print("=== VIDEOS ===")
print(f"total doga: {len(videos)}")
print(f"blob refs: {sum(len(v['blobs']) for v in videos)}")
print(f"missing locally: {len(missing)}")
print()
print("=== ORPHANS ===")
print(f"orphan BlobInfo: {len(orphans_bi)}")
print(f"orphan bucket files (not referenced by live doga): {len(orphan_files)}")
print(f"  of which tracked by orphan BlobInfo: {len(set(orphan_files) & orphan_bi_objs)}")
print()
print("=== MISSING SAMPLE ===")
for m in missing[:5]:
    print(" ", m)

# Write outputs
(META / "videos.json").write_text(
    json.dumps(videos, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
)
(META / "missing.json").write_text(
    json.dumps(missing, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
)
(META / "orphans.json").write_text(
    json.dumps({"blobinfo_orphans": orphans_bi, "bucket_orphan_files": orphan_files},
               ensure_ascii=False, indent=1, default=str),
    encoding="utf-8",
)
print("wrote videos.json, missing.json, orphans.json")
