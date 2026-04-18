"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useMemo, useState } from "react";
import VideoCard from "../../components/VideoCard";
import type { Tag, Video } from "../../lib/types";

type Props = {
  videos: Pick<
    Video,
    "id" | "name" | "text" | "icon" | "tlen" | "view" | "qual" | "bone" | "attr"
  >[];
  tags: Tag[];
};

function FindInner({ videos, tags }: Props) {
  const sp = useSearchParams();
  const initialTag = sp.get("tag") ?? "";
  const initialQ = sp.get("q") ?? "";
  const [q, setQ] = useState(initialQ);
  const [tag, setTag] = useState(initialTag);
  const [sort, setSort] = useState<"god" | "new" | "old">("god");

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    const out = videos.filter((v) => {
      if (tag && !v.attr.includes(tag)) return false;
      if (needle) {
        const hay =
          (v.name ?? "").toLowerCase() +
          "\n" +
          (v.text ?? "").toLowerCase() +
          "\n" +
          (v.attr ?? []).join(" ").toLowerCase();
        if (!hay.includes(needle)) return false;
      }
      return true;
    });
    out.sort((a, b) => {
      if (sort === "god") return (b.qual ?? 0) - (a.qual ?? 0);
      if (sort === "new") return (b.bone ?? "").localeCompare(a.bone ?? "");
      return (a.bone ?? "").localeCompare(b.bone ?? "");
    });
    return out;
  }, [videos, q, tag, sort]);

  return (
    <div>
      <div className="row" style={{ marginBottom: 12 }}>
        <div className="col-sm-6">
          <input
            className="form-control"
            placeholder="キーワード（題名・本文・タグ）"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
        <div className="col-sm-3">
          <input
            className="form-control"
            placeholder="タグ"
            value={tag}
            onChange={(e) => setTag(e.target.value)}
          />
        </div>
        <div className="col-sm-3">
          <select
            className="form-control"
            value={sort}
            onChange={(e) =>
              setSort(e.target.value as "god" | "new" | "old")
            }
          >
            <option value="god">品質順</option>
            <option value="new">新着順</option>
            <option value="old">古い順</option>
          </select>
        </div>
      </div>
      <div style={{ marginBottom: 12 }}>
        {tags.slice(0, 30).map((t) => (
          <button
            key={t.name}
            type="button"
            className={`btn btn-xs ${t.name === tag ? "btn-primary" : "btn-default"}`}
            style={{ marginRight: 4, marginBottom: 4 }}
            onClick={() => setTag(t.name === tag ? "" : t.name)}
          >
            {t.name} <span className="badge">{t.videoIds.length}</span>
          </button>
        ))}
      </div>
      <p className="text-muted">{filtered.length} 件</p>
      <div className="row video-grid">
        {filtered.map((v) => (
          <div className="col-xs-6 col-sm-4 col-md-3" key={v.id}>
            <VideoCard v={v as Video} />
          </div>
        ))}
      </div>
      <p style={{ marginTop: 16 }}>
        <Link href="/">← ホームに戻る</Link>
      </p>
    </div>
  );
}

export default function FindClient(props: Props) {
  return (
    <Suspense fallback={<div>loading...</div>}>
      <FindInner {...props} />
    </Suspense>
  );
}
