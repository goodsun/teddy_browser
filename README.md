# Teddy Browser 🧸

AI専用ヘッドレスブラウザ。スクリーンショットで画面を確認しながら操作する。

## セットアップ

```bash
pip install playwright
playwright install chromium
```

## 使い方

```bash
# 対話モード（stdinからコマンド）
echo "url:https://example.com" | python3 teddy_browser.py -p myprofile

# 初期URL指定
python3 teddy_browser.py -p myprofile -u https://example.com

# コマンドファイル実行
python3 teddy_browser.py -p myprofile -f commands.txt
```

## コマンド

| コマンド | 説明 |
|---|---|
| `url:<URL>` | ページ遷移 |
| `click:<selector>` | 要素クリック |
| `select:<selector>` | 要素選択＆テキスト表示 |
| `input:<text>` | 選択要素にテキスト入力 |
| `type:<text>` | キーボード入力 |
| `press:<key>` | キー送信（Enter, Tab等） |
| `scroll:<dir>` | スクロール（up/down/top/bottom） |
| `wait:<ms>` | 待機 |
| `ss` | スクリーンショット |
| `title` | タイトル＆URL表示 |
| `html` | ページテキスト抽出 |
| `links` | リンク一覧 |
| `eval:<js>` | JavaScript実行 |
| `save` | セッション保存 |
| `quit` | 終了（自動保存） |

## AI連携のワークフロー

1. コマンドを送信（`url:`, `click:` 等）
2. 自動スクリーンショットのパスを取得
3. 画像を確認して次のアクションを決定
4. 繰り返し

## プロファイル

Cookie・localStorageがプロファイルとして保存され、次回起動時に復元される。
ログイン状態を維持したまま再利用可能。

```
~/.config/teddy_browser/
├── profiles/      # セッション保存
├── screenshots/   # スクリーンショット
└── logs/          # コマンドログ
```

## ベース

[playwrite_study](https://github.com/goodsun/playwrite_study) の `05_chrome_launcher.py` をAI操作向けに再設計。
