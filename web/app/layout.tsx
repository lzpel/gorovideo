import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

export const metadata: Metadata = {
  title: "gorogoro動画",
  description: "当時の投稿動画アーカイブ",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ja">
      <head>
        <link
          rel="stylesheet"
          href={`${BASE}/vendor/bootstrap/css/bootstrap.min.css`}
        />
      </head>
      <body>
        <nav
          className="navbar navbar-default navbar-static-top"
          style={{ marginBottom: 0 }}
        >
          <div className="container">
            <ul className="nav navbar-nav">
              <li>
                <Link href="/" style={{ paddingTop: 0, paddingBottom: 0 }}>
                  gorogoro動画
                  <br />
                  _(:3 」∠)_
                </Link>
              </li>
              <li className="hidden-xs">
                <a>＜　アーカイブ版</a>
              </li>
            </ul>
            <ul className="nav navbar-nav navbar-right">
              <li>
                <Link href="/find/">
                  <i
                    className="glyphicon glyphicon-search"
                    aria-hidden="true"
                  />
                  <span className="hidden-xs"> 検索</span>
                </Link>
              </li>
              <li>
                <Link href="/dead/">
                  <i
                    className="glyphicon glyphicon-trash"
                    aria-hidden="true"
                  />
                  <span className="hidden-xs"> 供養</span>
                </Link>
              </li>
            </ul>
          </div>
        </nav>
        <div className="container">{children}</div>
      </body>
    </html>
  );
}
