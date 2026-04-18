import Link from "next/link";
import VideoCard from "../components/VideoCard";
import { getVideos } from "../lib/data";

export default function Home() {
  const videos = [...getVideos()].sort((a, b) => (b.qual ?? 0) - (a.qual ?? 0));
  return (
    <div>
      <ul className="nav nav-tabs" style={{ marginBottom: 12 }}>
        <li className="active">
          <Link href="/">人気</Link>
        </li>
        <li>
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
