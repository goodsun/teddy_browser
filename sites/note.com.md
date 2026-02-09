# note.com — サイト情報

## プロファイル
- **名前:** `note_teddy`
- **アカウント:** teddy_on_web (id: 13652916)
- **認証:** メール+パスワード（`~/.config/teddy_browser/note_password`）

## ログイン

```
url:https://note.com/login?redirectPath=%2F
wait:2000
select:#email
input:{email}
select:#password
input:{password}
wait:1000
eval:document.querySelectorAll('button')[3].click()
wait:5000
```

### セレクタ
| 要素 | セレクタ |
|---|---|
| メールアドレス入力 | `#email` |
| パスワード入力 | `#password` |
| ログインボタン | `document.querySelectorAll('button')[3]` ※disabled制御あり、eval経由でclick |
| Googleログイン | ボタン[0] |
| Xログイン | ボタン[1] |
| Appleログイン | ボタン[2] |

### 注意
- ログインボタンはメール・パスワード両方入力後に `disabled:false` になる
- `click:` セレクタでは拾えなかった → `eval:` でJSクリック推奨
- `input:` は `fill()` 方式なのでReactのstate更新が走る（`type:` より確実）

## 主要ページ

| ページ | URL |
|---|---|
| トップ | `https://note.com/` |
| 自分のページ | `https://note.com/teddy_on_web` |
| 記事検索 | `https://note.com/search?q={query}&context=note&mode=search` |
| ダッシュボード | `https://note.com/dashboard` |
| 記事作成 | `https://note.com/notes/new` |
| 通知 | `https://note.com/notifications` |

## 記事ページのセレクタ（TODO）
- 記事タイトル:
- 記事本文:
- いいねボタン:
- コメント欄:
- フォローボタン:

## メモ
- セッションはプロファイル `note_teddy` に保存済み
- Cookie有効期限: 約3ヶ月（要定期更新）
