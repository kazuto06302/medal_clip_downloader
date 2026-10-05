#!/usr/bin/env python3
"""Medal.tv クリップURLをクリップボードから集めて一括ダウンロード

使い方:
  pip install pyperclip yt-dlp

  python medal_clip_dl.py                 # 監視開始。Ctrl+C で終了 → ダウンロードするか聞かれる
  python medal_clip_dl.py --no-download   # 集めるだけ
  python medal_clip_dl.py --download-only # urls.txt の分だけダウンロード

  Medalでクリップのリンクをコピーするたびに自動で urls.txt に追記されます。
  複数URLをまとめてコピーしても全部拾います。
"""
import argparse
import re
import time
from pathlib import Path

# 例: https://medal.tv/ja/games/minecraft/clips/nEneUHh0Ld3jHXxL9?invite=cr-xxx
CLIP_RE = re.compile(
    r"https?://(?:www\.)?medal\.tv/(?:[a-z]{2}(?:-[A-Za-z]+)?/)?games/[^/\s?#]+/clips/"
    r"(?P<id>[A-Za-z0-9_\-]+)(?P<query>\?[^\s#]*)?"
)


def extract_clip_urls(text: str) -> dict[str, str]:
    """テキストからクリップURLを抜き出し {clip_id: 正規化URL} で返す。
    yt-dlp の extractor は /ja/ のような言語プレフィックスを想定していないので外す。
    ?invite=... は残す。
    """
    found = {}
    for m in CLIP_RE.finditer(text):
        url = m.group(0)
        url = re.sub(r"(medal\.tv)/[a-z]{2}(?:-[A-Za-z]+)?/games/", r"\1/games/", url)
        found.setdefault(m.group("id"), url)
    return found


def load_existing(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return extract_clip_urls(path.read_text(encoding="utf-8"))


def watch_clipboard(txt_path: Path, interval: float = 0.4) -> None:
    import pyperclip

    known = load_existing(txt_path)
    print(f"クリップボード監視中(既存 {len(known)} 件)。Ctrl+C で終了。")
    last = None
    try:
        while True:
            try:
                text = pyperclip.paste()
            except Exception:
                text = ""
            if text and text != last:
                last = text
                new = {i: u for i, u in extract_clip_urls(text).items() if i not in known}
                if new:
                    with txt_path.open("a", encoding="utf-8") as f:
                        for u in new.values():
                            f.write(u + "\n")
                    known.update(new)
                    print(f"+{len(new)} 件追加 (合計 {len(known)} 件): {', '.join(new)}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n監視を終了しました。合計 {len(known)} 件")


def download(txt_path: Path, out_dir: Path, cookies_browser: str | None) -> None:
    import yt_dlp

    urls = list(load_existing(txt_path).values())
    if not urls:
        print("ダウンロード対象がありません")
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    opts = {
        "outtmpl": str(out_dir / "%(title).80s [%(id)s].%(ext)s"),
        "download_archive": str(out_dir / "archive.txt"),  # 済みの分は再実行でスキップ
        "ignoreerrors": True,  # 1本失敗しても続行
        "retries": 5,
    }
    if cookies_browser:
        opts["cookiesfrombrowser"] = (cookies_browser,)
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download(urls)


def main() -> None:
    ap = argparse.ArgumentParser(description="Medal クリップURLをクリップボードから集めてDL")
    ap.add_argument("--txt", default="urls.txt", help="URLの保存先")
    ap.add_argument("-o", "--out", default="./medal_clips", help="動画の保存先")
    ap.add_argument("--no-download", action="store_true", help="集めるだけでDLしない")
    ap.add_argument("--download-only", action="store_true", help="監視せずDLだけ行う")
    ap.add_argument("--cookies-from-browser", metavar="BROWSER", help="例: chrome / firefox")
    args = ap.parse_args()

    txt_path, out_dir = Path(args.txt), Path(args.out)

    if not args.download_only:
        watch_clipboard(txt_path)
        if args.no_download:
            return
        if input("このままダウンロードしますか? [Y/n]: ").strip().lower() == "n":
            return
    download(txt_path, out_dir, args.cookies_from_browser)


if __name__ == "__main__":
    main()
