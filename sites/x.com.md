# x.com — サイト情報

## プロファイル
- **名前:** (未作成)
- **アカウント:** @teddy_bonsoleil（シャドウバン中）、@mythOfTragedy（運用中）
- **認証:** Cookie認証（`~/.config/twitter/credentials`）

## セレクタ（TODO）
- ツイート入力欄:
- ツイートボタン:
- 引用RT:
- リプライ:
- いいね:
- リツイート:
- フォローボタン:

## 主要ページ

| ページ | URL |
|---|---|
| ホーム | `https://x.com/home` |
| プロフィール | `https://x.com/teddy_bonsoleil` |
| 通知 | `https://x.com/notifications` |
| 検索 | `https://x.com/search?q={query}` |

## メモ
- 現在はPlaywright内fetch（x_post.py）で投稿
- ブラウザ操作での投稿はbot検知リスクあり → 要検証
- Cookie: auth_token + ct0 が必要
