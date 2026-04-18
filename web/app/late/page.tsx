import Link from "next/link";
import VideoCard from "../../components/VideoCard";
import { getVideos } from "../../lib/data";

export default function Late() {
  const videos = [...getVideos()].sort((a, b) => (b.bone ?? "").localeCompare(a.bone ?? ""));
  return (
    <div>
      <ul className="nav nav-tabs" style={{ marginBottom: 12 }}>
        <li>
          <Link href="/">人気</Link>
        </li>
        <li className="active">
          <Link href="/late/">新着</Link>
        </li>
        <li>
          <Link href="/find/">検索・タグ</Link>
        </li>
      </ul>
      <div className="row">
        {videos.map((v) => (
          <div className="col-xs-6 col-sm-4 col-md-3" key={v.id}>
            <VideoCard v={v} />
          </div>
        ))}
      </div>
    </div>
  );
}
