# RSS Generator (Web-to-RSS 自動生成パイプライン)

RSSフィードを提供していない（または無効化されている）Webサイトから新着記事を自動抽出し、RSS 2.0形式のXMLフィードを生成して Feedly 等のRSSリーダーで購読可能にする自動化プロジェクトです。

---

## 1. プロジェクト構成

```
rss_generator/
├── .github/
│   └── workflows/
│       └── update_feeds.yml  # GitHub Actions 定期実行ワークフロー（毎朝JST 07:00）
├── docs/                     # GitHub Pages 配信ディレクトリ
│   ├── e_earphone.xml        # e☆イヤホン ブログのRSSフィード
│   └── index.xml             # デフォルトフィード
├── scripts/
│   └── generate_feed.py      # スクレイピング & フィード生成スクリプト
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 2. Feedlyへの登録手順（3ステップ）

### ステップ1: GitHubにリポジトリを作成してプッシュ
本ディレクトリ（`D:\misc\rss_generator`）をGitHubの新規リポジトリ（例: `web-rss-feeds`）にプッシュします。

```powershell
cd D:\misc\rss_generator
git remote add origin https://github.com/<あなたのユーザー名>/web-rss-feeds.git
git branch -M main
git push -u origin main
```

### ステップ2: GitHub Pages の有効化
1. リポジトリの **Settings** > **Pages** を開きます。
2. **Build and deployment** の Source で **Deploy from a branch** を選択。
3. Branch を **`main`**、フォルダを **`/docs`** に設定して **Save** をクリックします。
4. 数分後、以下の公開URLが発行されます：
   ```
   https://<あなたのユーザー名>.github.io/web-rss-feeds/e_earphone.xml
   ```

### ステップ3: Feedly にフィードURLを登録
1. Feedly を開き、左サイドバーの「**Follow Sources**」（または検索バー）を開きます。
2. 上記の GitHub Pages URL（またはリポジトリの Raw URL）を貼り付けます。
3. 「**イヤホン・ヘッドホン専門店e☆イヤホンのブログ（非公式RSS）**」が表示されたら「**Follow**」をクリックして任意のフォルダに追加します。

---

## 3. ローカル環境での実行方法

Anaconda の専用仮想環境 `misc` を使用します。

```powershell
# フィード生成スクリプトの実行
& "D:\Anaconda3\envs\misc\python.exe" "D:\misc\rss_generator\scripts\generate_feed.py"
```

---

## 4. 他のWebサイトを新規追加する方法

`scripts/generate_feed.py` 内に新しい収集関数を追加するか、対象サイト用のスクリプトを作成して `docs/<サイト識別名>.xml` に出力するようにします。

1. **HTML要素の確認**: 対象サイトのトップページから、記事一覧のコンテナ要素、タイトル、リンク、公開日を特定。
2. **パースロジックの記述**: `BeautifulSoup` で要素を抽出し、`feedgen` のエントリに追加。
3. **ワークフローへの登録**: `.github/workflows/update_feeds.yml` の実行ステップに追加。
