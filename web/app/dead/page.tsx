import Link from "next/link";
import { deadVideoUrl, getDead } from "../../lib/data";

export default function DeadPage() {
  const items = getDead();
  return (
    <div>
      <h3>供養（失われた動画たち）</h3>
      <p className="text-muted">
        データベース上は削除されていたがストレージに残っていたBlob、ないし変換失敗で放置されていたファイルです。
        メタデータは残っていません。
      </p>
      {items.length === 0 ? (
        <p>（未生成）</p>
      ) : (
        <div className="row">
          {items.map((d) => (
            <div className="col-xs-12 col-sm-6 col-md-4" key={d.filename}>
              <div className="panel panel-default">
                <div className="panel-body">
                  <video
                    src={deadVideoUrl(d.filename)}
                    controls
                    preload="none"
                    style={{ width: "100%", height: "auto", background: "#000" }}
                  />
                  <div>
                    <small>
                      {d.filename} ・ {d.quality} ・{" "}
                      {(d.size / 1024 / 1024).toFixed(1)} MiB
                    </small>
                  </div>
                  <div>
                    <small className="text-muted">
                      {d.creation
                        ? new Date(d.creation).toLocaleDateString("ja-JP")
                        : ""}
                    </small>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      <p style={{ marginTop: 16 }}>
        <Link href="/">← ホームに戻る</Link>
      </p>
    </div>
  );
}
