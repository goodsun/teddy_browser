#!/usr/bin/env python3
"""teddy_browser.py — テディ専用ヘッドレスブラウザ

スクリーンショットで画面を確認しながらブラウザを操作する。
05_chrome_launcher.py をベースに、AI操作に最適化。

特徴:
  - ヘッドレス専用（EC2対応）
  - 毎コマンド後に自動スクリーンショット
  - プロファイルでセッション（Cookie/localStorage）を維持
  - stdin対話モード（テディがリアルタイム操作）

コマンド:
  url:<URL>              指定URLに遷移
  click:<selector>       要素をクリック
  select:<selector>      要素を選択（テキスト表示）
  input:<text>           選択中の要素にテキスト入力（\\nで改行）
  type:<text>            ページ全体にキーボード入力（フォーカス不問）
  press:<key>            キー送信（Enter, Tab, Escape等）
  scroll:<direction>     スクロール（up/down/top/bottom）
  wait:<ms>              待機（ミリ秒）
  ss                     スクリーンショット保存（パス表示）
  title                  ページタイトルとURL表示
  html                   ページの主要テキストを抽出（200行まで）
  links                  ページ内リンク一覧
  save                   セッションをプロファイルに保存
  eval:<js>              JavaScriptを実行
  quit                   終了（自動保存）

使い方:
  python3 teddy_browser.py -p teddy
  python3 teddy_browser.py -p teddy -u https://example.com
  python3 teddy_browser.py -p teddy -f commands.txt
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

PROFILES_DIR = Path.home() / ".config" / "teddy_browser" / "profiles"
SCREENSHOTS_DIR = Path.home() / ".config" / "teddy_browser" / "screenshots"
LOGS_DIR = Path.home() / ".config" / "teddy_browser" / "logs"


def auto_screenshot(page, label: str = "") -> str:
    """スクリーンショットを撮る。常に latest.png を上書き。"""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREENSHOTS_DIR / "latest.png"
    page.screenshot(path=str(path), full_page=False)
    return str(path)


def execute_command(cmd: str, page, context, profile_name: str, state: dict) -> bool:
    """コマンドを1つ実行。Falseで終了。"""
    selected = state.get("selected")

    try:
        if cmd == "quit":
            return False

        elif cmd == "help":
            print("COMMANDS:")
            print("  url:<URL>          遷移")
            print("  click:<selector>   クリック")
            print("  select:<selector>  要素選択＆テキスト表示")
            print("  input:<text>       選択要素にテキスト入力")
            print("  type:<text>        キーボード入力（フォーカス不問）")
            print("  paste:<text>       ペースト（contenteditable対応、高速）")
            print("  press:<key>        キー送信（Enter,Tab,Escape等）")
            print("  scroll:<dir>       スクロール（up/down/top/bottom）")
            print("  wait:<ms>          待機")
            print("  ss                 スクリーンショット（latest.png上書き）")
            print("  save_ss:<name>     名前付きスクショ保存")
            print("  title              タイトル＆URL")
            print("  html               主要テキスト抽出")
            print("  links              リンク一覧")
            print("  save               セッション保存")
            print("  eval:<js>          JavaScript実行")
            print("  quit               終了")

        elif cmd.startswith("url:"):
            url = cmd[4:].strip()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            print(f"NAVIGATED: {page.title()} | {page.url}")
            path = auto_screenshot(page, "nav")
            print(f"SCREENSHOT: {path}")

        elif cmd.startswith("click:"):
            selector = cmd[6:].strip()
            loc = page.locator(selector)
            count = loc.count()
            if count == 0:
                print(f"NOT_FOUND: {selector}")
            else:
                loc.first.click()
                page.wait_for_timeout(1500)
                print(f"CLICKED: {selector} | {page.url}")
                path = auto_screenshot(page, "click")
                print(f"SCREENSHOT: {path}")

        elif cmd.startswith("select:"):
            selector = cmd[7:].strip()
            loc = page.locator(selector)
            count = loc.count()
            if count == 0:
                print(f"NOT_FOUND: {selector}")
                state["selected"] = None
            else:
                state["selected"] = loc.first
                tag = loc.first.evaluate("el => el.tagName")
                text = (loc.first.text_content() or "").strip()
                print(f"SELECTED: <{tag}> ({count} matches)")
                if text:
                    print(f"TEXT: {text[:500]}")

        elif cmd.startswith("input:"):
            text = cmd[6:]
            if state.get("selected") is None:
                print("ERROR: No element selected. Use select: first.")
            else:
                text = text.replace("\\n", "\n")
                state["selected"].click()
                state["selected"].fill(text)
                page.wait_for_timeout(500)
                print(f"INPUT: {len(text)} chars")
                path = auto_screenshot(page, "input")
                print(f"SCREENSHOT: {path}")

        elif cmd.startswith("type:"):
            text = cmd[5:].replace("\\n", "\n")
            for ch in text:
                page.keyboard.type(ch)
                page.wait_for_timeout(random.randint(50, 150))
            print(f"TYPED: {len(text)} chars")
            path = auto_screenshot(page, "type")
            print(f"SCREENSHOT: {path}")

        elif cmd.startswith("paste:"):
            text = cmd[6:].replace("\\n", "\n")
            # ClipboardEvent paste — contenteditable (X, note.com等) 対応
            page.evaluate("""(text) => {
                const el = document.activeElement;
                if (!el) return;
                const dt = new DataTransfer();
                dt.setData('text/plain', text);
                const event = new ClipboardEvent('paste', {
                    clipboardData: dt, bubbles: true, cancelable: true
                });
                el.dispatchEvent(event);
            }""", text)
            page.wait_for_timeout(800)
            print(f"PASTED: {len(text)} chars")
            path = auto_screenshot(page, "paste")
            print(f"SCREENSHOT: {path}")

        elif cmd.startswith("press:"):
            key = cmd[6:].strip()
            page.keyboard.press(key)
            page.wait_for_timeout(500)
            print(f"PRESSED: {key}")
            path = auto_screenshot(page, "press")
            print(f"SCREENSHOT: {path}")

        elif cmd.startswith("scroll:"):
            direction = cmd[7:].strip().lower()
            if direction == "down":
                page.evaluate("window.scrollBy(0, window.innerHeight)")
            elif direction == "up":
                page.evaluate("window.scrollBy(0, -window.innerHeight)")
            elif direction == "top":
                page.evaluate("window.scrollTo(0, 0)")
            elif direction == "bottom":
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            else:
                print(f"ERROR: Unknown direction: {direction}")
                return True
            page.wait_for_timeout(500)
            print(f"SCROLLED: {direction}")
            path = auto_screenshot(page, "scroll")
            print(f"SCREENSHOT: {path}")

        elif cmd.startswith("wait:"):
            ms = int(cmd[5:].strip())
            page.wait_for_timeout(ms)
            print(f"WAITED: {ms}ms")

        elif cmd in ("screenshot", "ss"):
            # 名前なし → latest.png
            path = auto_screenshot(page)
            print(f"SCREENSHOT: {path}")

        elif cmd.startswith("save_ss:"):
            # 名前付き保存（永続）
            name = cmd[8:].strip().replace("/", "_").replace(" ", "_")
            if not name:
                name = datetime.now().strftime("%Y%m%d_%H%M%S")
            SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
            path = SCREENSHOTS_DIR / f"{name}.png"
            page.screenshot(path=str(path), full_page=False)
            print(f"SAVED_SS: {path}")

        elif cmd == "title":
            print(f"TITLE: {page.title()}")
            print(f"URL: {page.url}")

        elif cmd == "html":
            text = page.evaluate("""() => {
                const sel = 'main, article, [role="main"], .content, #content, body';
                const el = document.querySelector(sel);
                return el ? el.innerText : document.body.innerText;
            }""")
            lines = text.strip().split("\n")[:200]
            print(f"HTML_TEXT ({len(lines)} lines):")
            for line in lines:
                print(f"  {line}")

        elif cmd == "links":
            links = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a[href]')).slice(0, 50).map(a => ({
                    text: a.innerText.trim().substring(0, 80),
                    href: a.href
                }));
            }""")
            print(f"LINKS ({len(links)}):")
            for i, link in enumerate(links):
                print(f"  [{i}] {link['text']} → {link['href']}")

        elif cmd == "save":
            PROFILES_DIR.mkdir(parents=True, exist_ok=True)
            path = PROFILES_DIR / f"{profile_name}.json"
            context.storage_state(path=str(path))
            print(f"SAVED: {path}")

        elif cmd.startswith("eval:"):
            js = cmd[5:].strip()
            result = page.evaluate(js)
            print(f"EVAL_RESULT: {json.dumps(result, ensure_ascii=False, default=str)[:2000]}")

        else:
            print(f"UNKNOWN: {cmd}")

    except Exception as e:
        print(f"ERROR: {e}")

    sys.stdout.flush()
    return True


def main():
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(description="Teddy Browser — AI専用ヘッドレスブラウザ")
    parser.add_argument("-p", type=str, default="default", help="プロファイル名")
    parser.add_argument("-u", type=str, help="初期URL")
    parser.add_argument("-f", type=str, help="コマンドファイル")
    parser.add_argument("--no-auto-ss", action="store_true", help="自動スクリーンショットを無効化")
    args = parser.parse_args()

    profile_name = args.p
    profile_path = PROFILES_DIR / f"{profile_name}.json"

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--lang=ja-JP"]
        )

        # プロファイル復元
        if profile_path.exists():
            context = browser.new_context(
                storage_state=str(profile_path),
                viewport={"width": 1280, "height": 720},
                locale="ja-JP",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            )
            print(f"PROFILE_LOADED: {profile_name}")
        else:
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                locale="ja-JP",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            )
            print(f"PROFILE_NEW: {profile_name}")

        page = context.new_page()

        # 初期URL
        if args.u:
            page.goto(args.u, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            print(f"NAVIGATED: {page.title()} | {page.url}")
            path = auto_screenshot(page, "init")
            print(f"SCREENSHOT: {path}")

        # コマンドファイル実行
        if args.f:
            fpath = Path(args.f)
            if fpath.exists():
                print(f"RUNNING_FILE: {args.f}")
                lines = fpath.read_text().splitlines()
                file_state = {"selected": None}
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    i += 1
                    if not line or line.startswith("#"):
                        continue
                    # ヒアドキュメント（input:<<EOF / paste:<<EOF）
                    for prefix in ("input:<<", "paste:<<"):
                        if line.startswith(prefix):
                            delimiter = line[len(prefix):].strip()
                            base_cmd = prefix.split(":")[0] + ":"
                            body = []
                            while i < len(lines):
                                if lines[i].strip() == delimiter:
                                    i += 1
                                    break
                                body.append(lines[i])
                                i += 1
                            line = base_cmd + "\n".join(body)
                            break
                    print(f"CMD: {line}")
                    if not execute_command(line, page, context, profile_name, file_state):
                        break
            else:
                print(f"FILE_NOT_FOUND: {args.f}")

        # 対話モード（stdin）
        if not args.f or True:  # ファイル実行後も対話可能
            state = {"selected": None}
            print("READY: Waiting for commands on stdin")
            sys.stdout.flush()

            stdin_lines = list(sys.stdin)
            i = 0
            while i < len(stdin_lines):
                cmd = stdin_lines[i].strip()
                i += 1
                if not cmd or cmd.startswith("#"):
                    continue
                # ヒアドキュメント対応（input:<<EOF / paste:<<EOF）
                for prefix in ("input:<<", "paste:<<"):
                    if cmd.startswith(prefix):
                        delimiter = cmd[len(prefix):].strip()
                        base_cmd = prefix.split(":")[0] + ":"  # "input:" or "paste:"
                        body = []
                        while i < len(stdin_lines):
                            if stdin_lines[i].strip() == delimiter:
                                i += 1
                                break
                            body.append(stdin_lines[i].rstrip("\n"))
                            i += 1
                        cmd = base_cmd + "\n".join(body)
                        break
                print(f"CMD: {cmd}")
                sys.stdout.flush()
                if not execute_command(cmd, page, context, profile_name, state):
                    break

        # 終了時に自動保存
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(profile_path))
        print(f"PROFILE_SAVED: {profile_name}")

        context.close()
        browser.close()

    print("EXIT")


if __name__ == "__main__":
    main()
