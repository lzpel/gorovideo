# gorovideo

Google Cloud Platform 上で動いていた動画共有サイト（2017年運用開始、以後放棄）のアーカイブ。
当時のデータを抜き出して Next.js SSG で再現、GitHub Pages で公開している。

- アーカイブ公開: https://lzpel.github.io/gorovideo/
- 旧ドメイン（現在も動作）: https://video-161819.appspot.com/
- 消滅した元ドメイン: https://gorovideo.com/

![img](https://user-images.githubusercontent.com/18492524/99069407-a4f81580-25f1-11eb-9bbe-3ec7037fe937.gif)

## ディレクトリ構成

### 当時から存在していたもの

- `appengine/` — Python2.7 App Engine 本体
  - `main.py`, `moto.py` とルーティング／モデル
  - Django風テンプレート `base`/`doga`/`home*`/`user*`/`find`/`sign`
  - Bootstrap3 + MediaElement.js + mejs-feature-barrage を vendoring
- `docker/` — Blobstore にアップロードされた生動画を ffmpeg で 360p/720p MP4 に変換するコンバーター
  - `conv.py` と `Dockerfile`

### アーカイブ再構築で追加したもの

- `scripts/` — Datastore からデータを抜き出して整形するための Python ツール群。uv で管理 (`pyproject.toml`)
  - `dump_datastore.py` — 全 kind を JSON 化
  - `analyze.py` — doga ↔ BlobInfo の突き合わせ
  - `fetch_and_organize.py` / `rebuild_dead.py` — GCS から blob を取得して分類
  - `extract_site_data.py` + `extract_thumbs.py` — サイト表示用に整形＋サムネ分離
- `web/` — Next.js 16 (App Router, `output: 'export'`, basePath `/gorovideo`) で作った静的サイト
  - vendor は `public/vendor/bootstrap`
  - サムネは `public/thumb`・`public/uicon`
  - データは `public/data/*.json`
  - 動画は GitHub Releases から直参照
- `.github/workflows/deploy.yml` — `master` push で `web/` をビルドして GitHub Pages にデプロイ
- `.gitignore` — `data/` 配下（復元ローカル作業ディレクトリ）と `env.sh`（gcloud CLI のエイリアス）を除外

動画ファイル本体（計 8.1 GiB）は **GitHub Releases の `v1-archive` タグ**に添付されている（174 ファイル）。

## `data/` 配下の中身（gitignored）

ローカルで復元作業を走らせた結果物で、リポジトリにはコミットされない。再生成したい場合は `scripts/` を順に実行する。

### `data/blob/`
`gcloud storage cp -r gs://video-161819.appspot.com/ data/blob/` でバケットを丸ごと落とした生ファイル置き場。オブジェクト名のまま（例: `ABPtcPoc...`、`L2FwcGhvc3Rpbmdf...`）保存されている。
- `ABPtcPoc...` 系は短いハッシュ、`L2FwcGhvc3Rpbmdf...` 系は base64 で `/apphosting_asia-northeast1/blobs/AEnB2U...` を符号化した旧式の名前
- 後者は Windows の MAX_PATH (260 文字) を超えるためパス含みで CP が失敗する。復元時は blob キー経由で個別取得する
- 最終的には `data/live/` と `data/dead/` にリネーム・再配置されるので、このディレクトリは中間生成物

### `data/meta/`
Datastore の生の JSON ダンプ。

- `base.json` — すべての `base` エンティティ（3529件）
  - `anal` 列で種別判定: `doga` 動画74件 / `user` 会員1526件（大半は2025年以降のボット登録）/ `clip` プレイリスト1527件 / `rice` コメント288件 / `attr` タグ114件
- `BlobInfo.json` — `__BlobInfo__` kind（185件）
  - blob キーと GCS オブジェクトパスのマッピング、元アップロードファイル名・サイズ・MIME・作成日時
- `GsFileInfo.json` — `__GsFileInfo__` kind（このプロジェクトでは0件）
- `videos.json` — `analyze.py` で doga のみ抜き出し、`blob[]` を BlobInfo と照合してローカルでの存在状況を記録した中間形式
- `missing.json` / `orphans.json` / `plan.json` — 再取得計画を立てるための照合結果

### `data/live/`
**現役の投稿動画（74本 / 111ファイル / 3.7 GiB）**。ファイル名は `{videoId}_{idx}.mp4`。

- `{videoId}` は Datastore の doga エンティティ ID
- `{idx}` は 2画質持ちなら `0` = 低画質(360p), `1` = 高画質(720p)、1画質なら `0` のみ
- 中身は H.264 MP4 (faststart) なので HTML5 `<video>` でそのままストリーミング再生可
- GitHub Releases `v1-archive` の添付ファイルとしてアップロード済み

### `data/dead/`
**DB上は削除済み／変換失敗のまま残された Blob（59本 / 4.4 GiB）**。ファイル名は `dead_{index:03d}_{quality}.mp4`。

- `BlobInfo` には残っているが `doga.blob[]` からはもう参照されていない blob を回収したもの
- 2024年以降の投稿ではなく、大半が 2017 年ごろの削除済み動画・アップロード失敗動画
- `index.json` に blob キー・元ファイル名・作成日時・サイズ・画質を併記
- 元の投稿者情報・タイトル・コメントは残っていない
- 全 74 件のうち 4 件は中身が 0 バイト、11 件は GCS 側から消えていたので最終 59 件

### `data/site/`
`extract_site_data.py` で生成する、Next.js が直接食べる形のクリーン JSON。
`videos.json`（74本）/ `users.json`（42人＝投稿者＋コメント主のみ）/ `comments.json`（288件、動画IDでグルーピング）/ `tags.json`（93タグ）/ `dead.json`（59件）。
`web/public/data/` にも同内容がコピーされる。

## ローカル手順

```bash
# gcloud + uv + node がある前提
source env.sh                                     # gcloud のエイリアスを貼る (自作)
gcloud auth application-default login
uv run --project scripts python scripts/dump_datastore.py
uv run --project scripts python scripts/analyze.py
uv run --project scripts python scripts/fetch_and_organize.py plan
uv run --project scripts python scripts/fetch_and_organize.py copy
uv run --project scripts python scripts/fetch_and_organize.py fetch
uv run --project scripts python scripts/rebuild_dead.py
uv run --project scripts python scripts/extract_site_data.py
uv run --project scripts python scripts/extract_thumbs.py
cd web && npm ci && npm run build                 # out/ を生成
```

リリースへの動画アップロードは `gh release upload v1-archive data/live/*.mp4 data/dead/*.mp4 --clobber` で一括。Pages は push すれば Actions が自動デプロイ。
