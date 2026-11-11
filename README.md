# rss — GUNDAM ニュース RSS（GitHub Pages 配信）

GUNDAM Official Website（https://gundam-official.com/news）の非公式 RSS フィード。
GitHub Pages で配信し、GitHub Actions が1時間に1回自動更新する。

フィード URL: https://twins-tomo.github.io/rss/gundam_news.xml
リポジトリ: https://github.com/twins-tomo/rss

## 現在の状態（2026-11-07 セットアップ完了）
- リポジトリ `twins-tomo/rss`（Public。当初の `gundam-rss` からリネーム）で運用中
- Settings → Pages は Deploy from a branch / main / (root) で公開
- 配信が `Content-Type: application/xml` でインライン表示されることを確認済み（最新54件）
- RSS リーダー（Firefox の Livemarks）にフィード URL を登録し、表示できることを確認済み

## セットアップ手順（実施済み・記録）
1. GitHub で **Public** リポジトリを作成する（README 等は追加しない）。
2. このフォルダの中身をすべてリポジトリへアップロード（push）する。
   - `.github/workflows/update-feed.yml`、`generate_rss.py`、`gundam_news.xml`、`.nojekyll`、`README.md`
3. リポジトリの **Settings → Pages** で、Source を **Deploy from a branch**、
   Branch を **main / (root)** にして Save する。
4. 数分待つとフィード URL で公開される。その URL を RSS リーダー（Livemarks）に登録する。
5. 以後の更新は自動。動作確認したいときは **Actions** タブから
   「Update Gundam News Feed」を **Run workflow** で手動実行できる。

## メモ
- 更新スケジュール: 1時間に1回（毎時17分ごろ、Actions の仕様で遅れる場合がある）。新着が無ければコミットは作られない
- フィードは最新 54 件（3ページ分、約10日分）。10日以上更新が空くと、その間の記事がフィードに入らない場合がある。生成方法は `generate_rss.py` を参照
- リポジトリは Public が必要（無料プランの GitHub Pages の制約）
- フィードの中身は公式サイトで公開されているニュースのタイトルとリンクのみ
