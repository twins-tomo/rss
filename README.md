# gundam-rss

GUNDAM Official Website（https://gundam-official.com/news）の非公式 RSS フィード。
GitHub Pages で配信し、GitHub Actions が1時間に1回自動更新する。

フィード URL: `https://<GitHubユーザー名>.github.io/gundam-rss/gundam_news.xml`

## セットアップ手順（最初に1回だけ）

1. GitHub で **Public** リポジトリ `gundam-rss` を新規作成する（README 等は追加しない）。
2. このフォルダの中身をすべてリポジトリへアップロード（push）する。
   - `.github/workflows/update-feed.yml`、`generate_rss.py`、`gundam_news.xml`、`.nojekyll`、`README.md`
3. リポジトリの **Settings → Pages** で、Source を **Deploy from a branch**、
   Branch を **main / (root)** にして Save する。
4. 数分待つと `https://<GitHubユーザー名>.github.io/gundam-rss/gundam_news.xml` で
   フィードが公開される。その URL を RSS リーダー（Livemarks）に登録する。
5. 以後の更新は自動。動作確認したいときは **Actions** タブから
   「Update Gundam News Feed」を **Run workflow** で手動実行できる。

## メモ
- 更新スケジュール: 1時間に1回（毎時17分ごろ、Actions の仕様で遅れる場合がある）。新着が無ければコミットは作られない
- フィードは最新 54 件（3ページ分）。生成方法は `generate_rss.py` を参照
- リポジトリは Public が必要（無料プランの GitHub Pages の制約）
- フィードの中身は公式サイトで公開されているニュースのタイトルとリンクのみ
