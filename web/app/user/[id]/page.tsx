import Link from "next/link";
import { notFound } from "next/navigation";
import VideoCard from "../../../components/VideoCard";
import { getUser, getVideos, withBasePath } from "../../../lib/data";

export function generateStaticParams() {
  // Only authors who have at least one live video
  const authorIds = new Set<number>();
  for (const v of getVideos()) {
    if (v.authorId != null) authorIds.add(v.authorId);
  }
  return Array.from(authorIds).map((id) => ({ id: String(id) }));
}

export default async function UserPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const u = getUser(id);
  if (!u) notFound();
  const mine = getVideos()
    .filter((v) => v.authorId === u.id)
    .sort((a, b) => (b.qual ?? 0) - (a.qual ?? 0));
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", marginBottom: 16 }}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={withBasePath(u.icon ?? "/nail.png")}
          alt=""
          width={72}
          height={72}
          style={{ marginRight: 12 }}
        />
        <div>
          <h3 style={{ margin: 0 }}>{u.name || "noname"}</h3>
          <p style={{ whiteSpace: "pre-wrap", margin: "4px 0 0 0" }}>{u.text}</p>
        </div>
      </div>
      <h4>投稿動画（{mine.length}）</h4>
      <div className="row video-grid">
        {mine.map((v) => (
          <div className="col-xs-6 col-sm-4 col-md-3" key={v.id}>
            <VideoCard v={v} />
          </div>
        ))}
      </div>
      <p>
        <Link href="/">← ホームに戻る</Link>
      </p>
    </div>
  );
}
