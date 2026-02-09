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

## 記事ページの操作

### コメント投稿
⚠️ `paste:` はnoteのtextareaに反映されない。JS直接書き込みが必要。

```
# 1. 記事ページを開く
url:https://note.com/{user}/n/{key}
wait:5000

# 2. ページ最下部にスクロール（コメント欄を表示）
eval:window.scrollTo(0, document.body.scrollHeight)
wait:2000

# 3. コメント欄をクリック（フォーカス）
click:textarea.o-noteCommentForm__inputMessage
wait:500

# 4. JS nativeInputValueSetter でテキスト入力（paste:は効かない）
eval:(() => { const ta = document.querySelector('textarea.o-noteCommentForm__inputMessage'); const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set; setter.call(ta, '{コメント本文}'); ta.dispatchEvent(new Event('input', { bubbles: true })); return ta.value.length; })()
wait:1000

# 5. 送信ボタン（aria-label="送信"の丸いボタン）をクリック
eval:(() => { const btn = Array.from(document.querySelectorAll('button')).find(b => b.getAttribute('aria-label') === '送信'); if(btn && !btn.disabled) { btn.click(); return 'SENT'; } return 'FAILED'; })()
wait:3000
```

### セレクタまとめ
| 要素 | セレクタ / 方法 |
|---|---|
| コメント欄 | `textarea.o-noteCommentForm__inputMessage` |
| 送信ボタン | `button[aria-label="送信"]`（eval経由でクリック） |
| キャンセルボタン | `button[aria-label="キャンセル"]` |
| スキ（いいね）ボタン | `button.o-noteLikeV3__iconButton`（複数あり、記事本文直後のものを使う） |
| スキ取り消し | テキスト「スキを取り消す」のaria-labelで判定 |
| フォローボタン | `button:has-text("フォロー")` / `button.a-button:has-text("フォロー中")` |

### いいね（スキ）
```
# 記事ページでスクロール後
eval:(() => { const btn = document.querySelector('button.o-noteLikeV3__iconButton'); if(btn) { btn.click(); return 'LIKED'; } return 'NOT FOUND'; })()
wait:2000
```

### 注意事項
- **コメント入力**: `paste:` / `type:` ではtextareaに反映されない場合あり。`nativeInputValueSetter` + `input` イベント発火が確実
- **送信ボタン**: CSSクラスなし、`aria-label="送信"` で特定。`click:` セレクタでは拾えない → `eval:` 必須
- **コメントレート制限**: 15秒以上間隔を空ける（429回避）
- **スキボタン**: ページに複数存在（記事末尾 + サイドバー等）。最初の1つをクリックすれば全連動

## メモ
- セッションはプロファイル `note_teddy` に保存済み
- Cookie有効期限: 約3ヶ月（teddy_browserで再ログインすれば更新可能）
- 下書きが大量に生成される可能性あり → 定期的に手動削除
