import Link from "next/link";
import { withBasePath } from "../lib/data";
import type { Video } from "../lib/types";

function minsec(sec: number): string {
  if (!sec || !Number.isFinite(sec)) return "";
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export default function VideoCard({ v }: { v: Video }) {
  return (
    <Link className="video-card" href={`/item/${v.id}/`}>
      <div className="thumb">
        {v.icon ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={withBasePath(v.icon)} alt="" loading="lazy" />
        ) : null}
        {v.tlen ? <span className="len">{minsec(v.tlen)}</span> : null}
      </div>
      <p
        className="title"
        title={v.name || "名前がありません"}
      >
        {v.name || "名前がありません"}
      </p>
      <small className="text-muted">視聴 {v.view ?? 0}</small>
    </Link>
  );
}
