# x.com — サイト情報

## プロファイル
- **名前:** (未作成)
- **アカウント:** @teddy_bonsoleil（シャドウバン中）、@mythOfTragedy（運用中）
- **認証:** Cookie認証（`~/.config/twitter/credentials`）

## セレクタ

| 要素 | セレクタ |
|---|---|
| ツイート入力欄 | `[data-testid="tweetTextarea_0"]` |
| ポストするボタン | `[data-testid="tweetButtonInline"]` |
| サイドバーのポストボタン | `[data-testid="SideNav_NewTweet_Button"]` |
| アカウント切替 | `[data-testid="SideNav_AccountSwitcher_Button"]` |
| 引用RT | TODO |
| リプライ | TODO |
| いいね | TODO |
| リツイート | TODO |
| フォローボタン | TODO |

### 投稿手順（検証済み ✅）
```
url:https://x.com/home
wait:3000
select:[data-testid="tweetTextarea_0"]
input:{投稿テキスト}
wait:1000
click:[data-testid="tweetButtonInline"]
wait:5000
```
- EC2ヘッドレスから投稿成功（2026-02-09）
- 344/226エラーなし
- Cookie（auth_token + ct0）をプロファイルに注入して使用

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
