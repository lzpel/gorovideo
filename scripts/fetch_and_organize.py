"""Download missing blobs with short names, organize all referenced blobs into data/live/,
move orphan bucket files into data/dead/."""
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
META = ROOT / "data" / "meta"
BLOB_DIR = ROOT / "data" / "blob"
LIVE_DIR = ROOT / "data" / "live"
DEAD_DIR = ROOT / "data" / "dead"
LIVE_DIR.mkdir(parents=True, exist_ok=True)
DEAD_DIR.mkdir(parents=True, exist_ok=True)

GCLOUD = r"C:\Users\smith\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
BUCKET = "gs://video-161819.appspot.com"

videos = json.load((META / "videos.json").open(encoding="utf-8"))
orphans = json.load((META / "orphans.json").open(encoding="utf-8"))

# Plan: for each video, for each blob index, want data/live/{video_id}_{i}.dat
plan = []
for v in videos:
    for i, b in enumerate(v["blobs"]):
        dst = LIVE_DIR / f"{v['id']}_{i}.dat"
        src_local = BLOB_DIR / b["gs_object"] if b["present_locally"] else None
        plan.append({
            "video_id": v["id"],
            "idx": i,
            "quality": b["quality"],
            "blobkey": b["blobkey"],
            "gs_object": b["gs_object"],
            "present": b["present_locally"],
            "dst": str(dst),
            "src_local": str(src_local) if src_local else None,
            "size": b["size"],
        })

action = sys.argv[1] if len(sys.argv) > 1 else "plan"

if action == "plan":
    present = sum(1 for p in plan if p["present"])
    missing = sum(1 for p in plan if not p["present"])
    total_missing_size = sum(p["size"] or 0 for p in plan if not p["present"])
    total_present_size = sum(p["size"] or 0 for p in plan if p["present"])
    print(f"plan entries: {len(plan)}")
    print(f"present (copy from local): {present} ({total_present_size/1024/1024:.1f} MiB)")
    print(f"missing (fetch from gs):   {missing} ({total_missing_size/1024/1024:.1f} MiB)")
    print(f"orphan bucket files to move: {len(orphans['bucket_orphan_files'])}")
    print("use 'copy' to copy present, 'fetch' to download missing, 'orphans' to move orphans")
    (META / "plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("wrote plan.json")

elif action == "copy":
    n = 0
    for p in plan:
        if p["present"]:
            src = pathlib.Path(p["src_local"])
            dst = pathlib.Path(p["dst"])
            if not dst.exists():
                shutil.copy2(src, dst)
                n += 1
    print(f"copied {n} files from local bucket to data/live/")

elif action == "fetch":
    n = 0
    failed = []
    for p in plan:
        if not p["present"]:
            dst = pathlib.Path(p["dst"])
            if dst.exists():
                continue
            src = f"{BUCKET}/{p['gs_object']}"
            print(f"  fetching {p['video_id']}_{p['idx']} ({p['size']/1024/1024:.1f} MiB)")
            r = subprocess.run([GCLOUD, "storage", "cp", src, str(dst)],
                               capture_output=True, text=True)
            if r.returncode != 0:
                print(f"    FAILED: {r.stderr[:200]}")
                failed.append(p)
            else:
                n += 1
    print(f"fetched {n} files; failed {len(failed)}")
    if failed:
        (META / "fetch_failed.json").write_text(
            json.dumps(failed, ensure_ascii=False, indent=1), encoding="utf-8"
        )

elif action == "orphans":
    n = 0
    for name in orphans["bucket_orphan_files"]:
        src = BLOB_DIR / name
        dst = DEAD_DIR / name
        if src.exists() and not dst.exists():
            shutil.move(str(src), str(dst))
            n += 1
    print(f"moved {n} orphan files to data/dead/")

elif action == "dead_plan":
    import re
    def gs_to_object(gs):
        m = re.match(r"^/[^/]+/(.*)$", gs)
        return m.group(1) if m else gs
    bi_orphans = orphans["blobinfo_orphans"]
    total = sum(bi.get("size") or 0 for bi in bi_orphans)
    print(f"orphan BlobInfo entries: {len(bi_orphans)}")
    print(f"total size: {total/1024/1024:.1f} MiB")
    already_in_blob = {p.name for p in BLOB_DIR.iterdir() if p.is_file()}
    already_in_dead = {p.name for p in DEAD_DIR.iterdir() if p.is_file()}
    need_fetch = 0
    can_move = 0
    for bi in bi_orphans:
        obj = gs_to_object(bi.get("gs_object_name") or "")
        if obj in already_in_dead:
            continue
        if obj in already_in_blob:
            can_move += 1
        else:
            need_fetch += 1
    print(f"need fetch from gs: {need_fetch}")
    print(f"can move from data/blob: {can_move}")

elif action == "fetch_dead":
    import re
    def gs_to_object(gs):
        m = re.match(r"^/[^/]+/(.*)$", gs)
        return m.group(1) if m else gs
    def quality_of_filename(f):
        if "1280x0720" in f or "1920x1080" in f: return "hq"
        if "0640x0360" in f or "0854x0480" in f: return "lq"
        return "u"
    bi_orphans = orphans["blobinfo_orphans"]
    index = {}
    n_moved = n_fetched = n_failed = 0
    for i, bi in enumerate(bi_orphans):
        obj = gs_to_object(bi.get("gs_object_name") or "")
        q = quality_of_filename(bi.get("filename") or "")
        dst = DEAD_DIR / f"{i:03d}_{q}.dat"
        # Record mapping
        index[str(dst.name)] = {
            "blobkey": bi["__name__"],
            "gs_object": obj,
            "filename": bi.get("filename"),
            "size": bi.get("size"),
            "creation": bi.get("creation"),
            "quality": q,
        }
        if dst.exists():
            continue
        local_src = BLOB_DIR / obj
        if local_src.exists():
            shutil.move(str(local_src), str(dst))
            n_moved += 1
            continue
        src = f"{BUCKET}/{obj}"
        r = subprocess.run([GCLOUD, "storage", "cp", src, str(dst)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  FAIL {i:03d}: {r.stderr[:160].strip()}")
            n_failed += 1
        else:
            n_fetched += 1
            if n_fetched % 10 == 0:
                print(f"  fetched {n_fetched} so far")
    (DEAD_DIR / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"moved {n_moved}, fetched {n_fetched}, failed {n_failed}")

else:
    print("usage: plan | copy | fetch | orphans | dead_plan | fetch_dead")
