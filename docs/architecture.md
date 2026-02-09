# Teddy Browser — アーキテクチャ

## ディレクトリ構成

### リポジトリ（コードのみ）

```
teddy_browser/
├── teddy_browser.py       # メインスクリプト
├── README.md              # 使い方
├── LICENSE                # MIT
├── .gitignore
├── docs/                  # ドキュメント
│   ├── concept.md         # コンセプト・ビジョン
│   └── architecture.md    # この文書
└── sites/                 # サイト別ナレッジ
    ├── note.com.md
    ├── x.com.md
    └── google.md
```

### データディレクトリ（`~/.config/teddy_browser/`）

リポジトリ外。セッション情報やスクリーンショットなど、ユーザー固有のデータを保存。

```
~/.config/teddy_browser/
├── profiles/              # Playwrightセッション（Cookie/localStorage）
│   ├── note_teddy.json    # note.comログイン済みプロファイル
│   └── default.json       # デフォルトプロファイル
├── screenshots/           # スクリーンショット
│   └── latest.png         # 最新1枚のみ（常に上書き）
└── logs/                  # コマンドログ
```

### 分離の理由

| 場所 | 内容 | Git管理 |
|---|---|---|
| リポジトリ | コード、ドキュメント、サイト情報 | ✅ |
| `~/.config/` | セッション、認証情報、スクショ | ❌ |

- **セキュリティ**: Cookie等の認証情報がリポジトリに入らない
- **ポータビリティ**: コードだけcloneすればどこでも動く
- **クリーンさ**: 一時ファイルでリポジトリが汚れない

## スクリーンショット管理

- `latest.png`: 毎コマンド実行時に上書き。テディの「今見えてる画面」
- `save_ss:<name>`: 名前付きで永続保存。記録として残したい時のみ

人間の目と同じ。見たら消える。大事なものだけ記憶する。

## プロファイル

Playwrightの `storage_state` 形式（JSON）。Cookie・localStorageを含む。

- ログイン済みのセッションを保存・復元
- サイトごとにプロファイルを分ける（`note_teddy`, `x_teddy` 等）
- 有効期限はサイトのCookie次第（note: 約3ヶ月）

## コマンドフロー

```
テディ(exec) → stdin → teddy_browser.py → Playwright → ブラウザ操作
                                              ↓
                                        latest.png
                                              ↓
                                    テディ(image) → 画面確認
                                              ↓
                                    テディ(message) → Telegramに送信
```
