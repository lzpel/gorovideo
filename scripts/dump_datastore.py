"""Dump all Datastore entities (base + __BlobInfo__ + __GsFileInfo__) to JSON."""
import base64
import datetime
import json
import pathlib
import sys

from google.cloud import datastore


OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "meta"
OUT_DIR.mkdir(parents=True, exist_ok=True)

client = datastore.Client(project="video-161819")


def serialize(v):
    if isinstance(v, datetime.datetime):
        return {"__dt__": v.isoformat()}
    if isinstance(v, datetime.date):
        return {"__date__": v.isoformat()}
    if isinstance(v, bytes):
        return {"__b64__": base64.b64encode(v).decode()}
    if isinstance(v, datastore.Key):
        return {"__key__": {"kind": v.kind, "id": v.id, "name": v.name, "path": list(v.flat_path)}}
    if isinstance(v, datastore.Entity):
        return entity_to_dict(v)
    if isinstance(v, list):
        return [serialize(x) for x in v]
    if isinstance(v, dict):
        return {k: serialize(x) for k, x in v.items()}
    return v


def entity_to_dict(e):
    out = {
        "__kind__": e.key.kind,
        "__id__": e.key.id,
        "__name__": e.key.name,
        "__path__": list(e.key.flat_path),
    }
    for k, v in e.items():
        out[k] = serialize(v)
    return out


def dump_kind(kind: str):
    print(f"Querying kind: {kind!r}")
    q = client.query(kind=kind)
    entities = list(q.fetch())
    print(f"  {len(entities)} entities")
    out_path = OUT_DIR / f"{kind.strip('_') or 'root'}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump([entity_to_dict(e) for e in entities], f, ensure_ascii=False, indent=1, default=str)
    print(f"  wrote {out_path}")
    return entities


if __name__ == "__main__":
    kinds = sys.argv[1:] or ["base", "__BlobInfo__", "__GsFileInfo__"]
    for k in kinds:
        try:
            dump_kind(k)
        except Exception as ex:
            print(f"  ERROR on {k}: {ex}")
