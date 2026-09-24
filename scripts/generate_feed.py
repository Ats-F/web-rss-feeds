"""
e☆イヤホン ブログ RSS 自動生成スクリプト
対象サイト: https://e-earphone.blog/
出力先: docs/e_earphone.xml (GitHub Pages公開用)
"""

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

# Windows環境でのコンソール出力エンコーディング対策
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

JST = timezone(timedelta(hours=9))

def generate_e_earphone_feed(output_dir: Path):
    target_url = "https://e-earphone.blog/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.7,en;q=0.3"
    }

    print(f"[INFO] Fetching target URL: {target_url}")
    response = requests.get(target_url, headers=headers, timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    # フィードメタデータの設定
    fg = FeedGenerator()
    fg.id(target_url)
    fg.title("イヤホン・ヘッドホン専門店e☆イヤホンのブログ（非公式RSS）")
    fg.author({"name": "e☆イヤホン", "email": "info@e-earphone.blog"})
    fg.link(href=target_url, rel="alternate")
    fg.subtitle("e☆イヤホンの最新ブログ記事・新製品・イベント情報を配信するRSSフィードです。")
    fg.language("ja")

    # 記事要素のパース
    articles = soup.select("article.archive-list")
    print(f"[INFO] Found {len(articles)} articles.")

    for art in articles:
        # タイトル & リンク
        title_el = art.select_one(".archive-header-title a")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        link = title_el.get("href", "").strip()
        if not link:
            continue

        # 公開日
        time_el = art.select_one("time.date")
        pub_date = None
        if time_el and time_el.get("datetime"):
            try:
                date_str = time_el["datetime"].strip()
                # ISOフォーマット YYYY-MM-DD
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                pub_date = dt.replace(hour=12, minute=0, second=0, tzinfo=JST)
            except Exception as e:
                print(f"[WARN] Failed to parse date '{time_el.get('datetime')}': {e}")
        if pub_date is None:
            pub_date = datetime.now(JST)

        # サムネイル画像
        img_el = art.select_one(".eye-catch img")
        img_url = img_el.get("src", "").strip() if img_el else None

        # カテゴリ
        cat_el = art.select_one(".cat-name a")
        category_name = cat_el.get_text(strip=True) if cat_el else "ブログ"

        # 著者
        author_el = art.select_one(".archive-header .author .fn a")
        author_name = author_el.get_text(strip=True) if author_el else "e☆イヤホン"

        # 記事の抜粋・HTML説明文（Feedlyカードビューでサムネイルとカテゴリを表示）
        desc_parts = []
        if img_url:
            desc_parts.append(f'<p><img src="{img_url}" alt="{title}" style="max-width:100%; height:auto;" /></p>')
        desc_parts.append(f'<p><strong>【カテゴリ】</strong> {category_name} | <strong>【投稿者】</strong> {author_name}</p>')
        desc_parts.append(f'<p><a href="{link}" target="_blank">記事全文をe☆イヤホンブログで読む &raquo;</a></p>')
        description_html = "\n".join(desc_parts)

        # エントリ追加
        fe = fg.add_entry()
        fe.id(link)
        fe.title(title)
        fe.link(href=link)
        fe.published(pub_date)
        fe.updated(pub_date)
        fe.category(term=category_name)
        fe.author({"name": author_name})
        fe.description(description_html)

        # 画像エンクロージャ（RSSリーダーのサムネイル認識補助）
        if img_url:
            mime = "image/webp" if img_url.endswith(".webp") else "image/jpeg"
            fe.enclosure(img_url, 0, mime)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "e_earphone.xml"
    fg.rss_file(str(out_file), pretty=True)
    print(f"[SUCCESS] Feed XML generated at: {out_file} (Size: {out_file.stat().st_size} bytes)")

    # index.xml (デフォルト用) としてもコピー作成
    index_file = output_dir / "index.xml"
    fg.rss_file(str(index_file), pretty=True)

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    docs_dir = base_dir / "docs"
    generate_e_earphone_feed(docs_dir)
