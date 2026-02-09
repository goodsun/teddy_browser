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

## エディタ（editor.note.com）

### セレクタ
| 要素 | セレクタ |
|---|---|
| タイトル入力 | `textarea`（最初の1つ） |
| 本文（ProseMirror） | `.ProseMirror` |
| 下書き保存 | `button:has-text("下書き保存")` |
| 公開に進む | `button:has-text("公開に進む")` ※JSクリック推奨 |

### ⚠️ 注意点
- **セッション跨ぎで内容がリセットされる**: ページを再読み込みするとタイトル・本文が消える
- `fill()` でタイトルは入るが、本文は `document.execCommand('insertText')` が必要
- `ClipboardEvent` ペーストはProseMirrorに効かない
- **「公開に進む」ボタン**: JSクリックが効かないケースあり。タイトル・本文が空だとバリデーションモーダル表示
- **結論**: 記事投稿は `note_publish.py`（API、HTTP/2）のほうが確実。エディタUI操作は今後改善

### Cookie更新フロー（teddy_browser活用）
1. `teddy_browser -p note_teddy` でログイン
2. プロファイルから `_note_session_v5` を抽出 → `~/.config/note/cookies` に保存
3. `note_publish.py` が新Cookieで動く

```python
# Cookie抽出ワンライナー
import json; from pathlib import Path
p = json.loads((Path.home()/".config/teddy_browser/profiles/note_teddy.json").read_text())
c = next(c["value"] for c in p["cookies"] if c["name"] == "_note_session_v5")
(Path.home()/".config/note/cookies").write_text(c)
```

## 記事ページのセレクタ（TODO）
- いいねボタン:
- コメント欄:
- フォローボタン:

## メモ
- セッションはプロファイル `note_teddy` に保存済み
- Cookie有効期限: 約3ヶ月（teddy_browserで再ログインすれば更新可能）
- 下書きが大量に生成される可能性あり → 定期的に手動削除
