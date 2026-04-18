import Link from "next/link";
import { notFound } from "next/navigation";
import VideoPlayer from "../../../components/VideoPlayer";
import {
  getCommentsFor,
  getUser,
  getVideo,
  getVideos,
  liveVideoUrl,
  withBasePath,
} from "../../../lib/data";

export function generateStaticParams() {
  return getVideos().map((v) => ({ id: String(v.id) }));
}

export default async function ItemPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const v = getVideo(id);
  if (!v) notFound();
  const author = getUser(v.authorId);
  const comments = getCommentsFor(v.id);
  const sources = v.blobs.map((b) => ({
    src: liveVideoUrl(v.id, b.idx),
    label:
      b.quality === "hq" ? "高画質" : b.quality === "lq" ? "低画質" : `画質${b.idx}`,
  }));
  const related = [...getVideos()]
    .filter((x) => x.id !== v.id)
    .sort((a, b) => (b.qual ?? 0) - (a.qual ?? 0))
    .slice(0, 8);

  const date = v.bone ? new Date(v.bone) : null;

  return (
    <div className="row">
      <div className="col-md-8">
        <VideoPlayer
          sources={sources}
          poster={v.icon ? withBasePath(v.icon) : null}
          comments={comments}
        />
        <h4 style={{ marginTop: 10 }}>{v.name || "名前がありません"}</h4>
        {author ? (
          <Link href={`/user/${author.id}/`} className="pull-left">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              width={50}
              height={50}
              src={author.icon ? withBasePath(author.icon) : undefined}
              alt=""
              style={{ marginRight: 8 }}
            />
            <span>{author.name || "noname"}</span>
          </Link>
        ) : null}
        <p className="pull-right">
          視聴回数 {v.view ?? 0} 回
          {date ? (
            <>
              {" ・ "}
              {date.toLocaleDateString("ja-JP", { timeZone: "Asia/Tokyo" })}
            </>
          ) : null}
        </p>
        <div className="clearfix" />
        <div style={{ marginTop: 8 }}>
          {v.attr.map((t) => (
            <Link
              key={t}
              className="btn btn-default btn-sm"
              href={`/find/?tag=${encodeURIComponent(t)}`}
              style={{ marginRight: 4, marginBottom: 4 }}
            >
              {t}
            </Link>
          ))}
        </div>
        <hr />
        <p>品質 {v.qual?.toFixed?.(2) ?? v.qual}</p>
        <p>コメント数 {comments.length}</p>
        {v.blobs.length === 1 ? (
          <div className="alert alert-warning">
            この動画は変換を待っている状態です。正しく再生できない可能性があります。
          </div>
        ) : null}
        {v.text ? (
          <div
            style={{ whiteSpace: "pre-wrap" }}
            dangerouslySetInnerHTML={{ __html: linkify(escapeHtml(v.text)) }}
          />
        ) : null}

        <h5 style={{ marginTop: 24 }}>コメント（{comments.length}）</h5>
        <ul className="list-unstyled">
          {comments.map((c) => (
            <li key={c.id}>
              <small className="text-muted">
                {formatTime(c.tpos)} ・{" "}
                {c.bone
                  ? new Date(c.bone).toLocaleDateString("ja-JP", {
                      timeZone: "Asia/Tokyo",
                    })
                  : ""}
              </small>
              <br />
              {c.text}
            </li>
          ))}
        </ul>
      </div>
      <div className="col-md-4">
        <div className="row">
          {related.map((r) => (
            <Link
              key={r.id}
              className="col-xs-6"
              href={`/item/${r.id}/`}
              style={{ marginBottom: 8, textDecoration: "none", color: "inherit" }}
            >
              <div style={{ position: "relative" }}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={r.icon ? withBasePath(r.icon) : undefined}
                  alt=""
                  loading="lazy"
                  style={{ width: "100%", height: "auto" }}
                />
                <kbd style={{ position: "absolute", right: 4, bottom: 4 }}>
                  {formatTime(r.tlen)}
                </kbd>
              </div>
              <p
                style={{
                  overflow: "hidden",
                  whiteSpace: "nowrap",
                  textOverflow: "ellipsis",
                  fontSize: 13,
                  margin: "4px 0",
                }}
              >
                {r.name || "名前がありません"}
              </p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}

function formatTime(sec: number): string {
  if (!sec || !Number.isFinite(sec)) return "0:00";
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function linkify(s: string): string {
  return s.replace(
    /(https?:\/\/[^\s<]+)/g,
    '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
  );
}
