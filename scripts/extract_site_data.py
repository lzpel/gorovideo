"""Extract clean, minimal JSON for Next.js frontend.
Outputs to data/site/{videos,users,comments,tags,dead}.json
"""
import json
import pathlib
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
META = ROOT / "data" / "meta"
SITE = ROOT / "data" / "site"
SITE.mkdir(parents=True, exist_ok=True)

base = json.load((META / "base.json").open(encoding="utf-8"))
videos_full = json.load((META / "videos.json").open(encoding="utf-8"))


def _id_of_key(keyobj):
    if not keyobj: return None
    k = keyobj.get("__key__") if isinstance(keyobj, dict) else None
    if k: return k.get("id")
    return None


def iso_dt(v):
    if isinstance(v, dict) and "__dt__" in v:
        return v["__dt__"]
    return v


by_id = {e["__id__"]: e for e in base if e.get("__id__") is not None}

# Videos (live)
video_ids = {v["id"] for v in videos_full}
videos = []
for v in videos_full:
    raw = by_id.get(v["id"], {})
    videos.append({
        "id": v["id"],
        "name": v["name"] or "",
        "text": v["text"] or "",
        "icon": v["icon"],  # base64 thumbnail (data: URI)
        "authorId": v["kusr"],
        "view": v["view"] or 0,
        "qual": v["qual"] or 0,
        "bone": iso_dt(v["bone"]),  # created time
        "tlen": v["tlen"] or 0,
        "tpos": v["tpos"] or 0,
        "attr": v["attr"] or [],
        # blob urls will be computed later; for now record count & indices
        "blobs": [{"idx": i, "quality": b["quality"], "size": b["size"]}
                  for i, b in enumerate(v["blobs"])],
    })

# Comments (rice) grouped by video
comments_by_video = defaultdict(list)
for e in base:
    if e.get("anal") != "rice": continue
    vid = _id_of_key(e.get("kint"))
    if vid not in video_ids: continue  # drop comments on deleted videos
    comments_by_video[vid].append({
        "id": e["__id__"],
        "authorId": _id_of_key(e.get("kusr")),
        "text": e.get("text") or "",
        "tpos": e.get("tpos") or 0,  # timestamp in video seconds (for barrage)
        "bone": iso_dt(e.get("bone")),
    })
# sort by tpos ascending
for vid in comments_by_video:
    comments_by_video[vid].sort(key=lambda c: c["tpos"])

# Authors (users referenced by live videos + comments)
needed_user_ids = set()
for v in videos:
    if v["authorId"]: needed_user_ids.add(v["authorId"])
for cs in comments_by_video.values():
    for c in cs:
        if c["authorId"]: needed_user_ids.add(c["authorId"])

users = []
for uid in sorted(needed_user_ids):
    u = by_id.get(uid)
    if not u:
        continue
    if u.get("anal") != "user":
        continue
    users.append({
        "id": u["__id__"],
        "name": u.get("name") or "",
        "icon": u.get("icon"),
        "text": u.get("text") or "",
    })

# Tags: map tag -> video ids
tag_map = defaultdict(list)
for v in videos:
    for t in v["attr"]:
        tag_map[t].append(v["id"])
tags = [{"name": k, "videoIds": v} for k, v in sorted(tag_map.items(), key=lambda x: -len(x[1]))]

# Dead: list of (index, quality, filename, blobkey) from data/dead/index.json if exists
dead_index_path = ROOT / "data" / "dead" / "index.json"
if dead_index_path.exists():
    dead = json.load(dead_index_path.open(encoding="utf-8"))
    dead_list = []
    for fname, meta in sorted(dead.items()):
        dead_list.append({
            "filename": fname,  # e.g. "003_hq.dat" -> will become .mp4
            "origFilename": meta.get("filename"),
            "size": meta.get("size"),
            "quality": meta.get("quality"),
            "creation": iso_dt(meta.get("creation")),
        })
else:
    dead_list = []

# Write
(SITE / "videos.json").write_text(json.dumps(videos, ensure_ascii=False, indent=1), encoding="utf-8")
(SITE / "comments.json").write_text(json.dumps(dict(comments_by_video), ensure_ascii=False, indent=1), encoding="utf-8")
(SITE / "users.json").write_text(json.dumps(users, ensure_ascii=False, indent=1), encoding="utf-8")
(SITE / "tags.json").write_text(json.dumps(tags, ensure_ascii=False, indent=1), encoding="utf-8")
(SITE / "dead.json").write_text(json.dumps(dead_list, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"videos: {len(videos)}")
print(f"comments: {sum(len(cs) for cs in comments_by_video.values())} across {len(comments_by_video)} videos")
print(f"users (authors+commenters): {len(users)}")
print(f"tags: {len(tags)}")
print(f"dead: {len(dead_list)}")
print(f"wrote to {SITE}/")
