"""Cleanup dupe files, rename .dat -> .mp4 for upload, regenerate dead index."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LIVE = ROOT / "data" / "live"
DEAD = ROOT / "data" / "dead"

# 1) Remove dupe orig-named files in data/dead/ (leave only NNN_q.dat + index.json)
removed = 0
for p in DEAD.iterdir():
    if not p.is_file(): continue
    if p.name == "index.json": continue
    # Indexed files match \d{3}_[a-z]{1,2}\.dat
    if len(p.name) < 12 and "_" in p.name:
        continue
    import re
    if re.match(r"^\d{3}_[a-z]{1,2}\.dat$", p.name):
        continue
    p.unlink()
    removed += 1
print(f"removed {removed} dupe files from data/dead/")

# 2) Rename .dat -> .mp4 in both dirs
def rename_dat_to_mp4(d: pathlib.Path):
    n = 0
    for p in d.iterdir():
        if p.is_file() and p.suffix == ".dat":
            new = p.with_suffix(".mp4")
            p.rename(new)
            n += 1
    return n

n_live = rename_dat_to_mp4(LIVE)
n_dead = rename_dat_to_mp4(DEAD)
print(f"renamed {n_live} live, {n_dead} dead .dat -> .mp4")

# 3) Prefix dead files with 'dead_' so release namespace doesn't collide with live video_id pattern
n_prefix = 0
for p in DEAD.iterdir():
    if p.is_file() and p.suffix == ".mp4" and not p.name.startswith("dead_"):
        p.rename(p.with_name(f"dead_{p.name}"))
        n_prefix += 1
print(f"prefixed {n_prefix} dead files with 'dead_'")

# 4) Regenerate dead index.json: keep only entries whose file exists
idx_path = DEAD / "index.json"
if idx_path.exists():
    idx = json.load(idx_path.open(encoding="utf-8"))
    keep = {}
    for fname, meta in idx.items():
        new_name = f"dead_{fname.replace('.dat', '.mp4')}"
        if (DEAD / new_name).exists():
            meta = dict(meta)
            meta["file"] = new_name
            keep[new_name] = meta
    idx_path.write_text(
        json.dumps(keep, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"kept {len(keep)}/{len(idx)} dead entries in index.json")

# 5) Rewrite data/site/dead.json to match
site_dead = ROOT / "data" / "site" / "dead.json"
public_dead = ROOT / "web" / "public" / "data" / "dead.json"
dead_list = []
if idx_path.exists():
    idx = json.load(idx_path.open(encoding="utf-8"))
    for fname, meta in sorted(idx.items()):
        dead_list.append({
            "filename": fname,
            "origFilename": meta.get("filename"),
            "size": meta.get("size"),
            "quality": meta.get("quality"),
            "creation": (meta.get("creation") or {}).get("__dt__") if isinstance(meta.get("creation"), dict) else meta.get("creation"),
        })
site_dead.write_text(
    json.dumps(dead_list, ensure_ascii=False, indent=1), encoding="utf-8"
)
public_dead.write_text(
    json.dumps(dead_list, ensure_ascii=False, indent=1), encoding="utf-8"
)
print(f"wrote {len(dead_list)} entries to data/site/dead.json and web/public/data/dead.json")

# Summary
print()
print(f"live mp4: {len(list(LIVE.glob('*.mp4')))}")
print(f"dead mp4: {len(list(DEAD.glob('*.mp4')))}")
