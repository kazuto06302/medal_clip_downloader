# medal_clip_dl

Medal.tv のクリップURLをクリップボードから自動で集めて `urls.txt` にまとめ、[yt-dlp](https://github.com/yt-dlp/yt-dlp) で一括ダウンロードするツールです。

## 仕組み

1. Medal でクリップのリンクをコピーするたびに、クリップボードを検知して `urls.txt` に追記する
2. 集め終わったら、`urls.txt` の全URLを yt-dlp でまとめてダウンロードする

## 必要なもの

- Python 3.10 以上
- ライブラリ

```bash
pip install pyperclip yt-dlp
```

> Linux の場合、`pyperclip` が `xclip` か `xsel`(Wayland なら `wl-clipboard`)を必要とすることがあります。

## 使い方

### 基本の流れ

```bash
python medal_clip_dl.py
```

1. 起動すると「クリップボード監視中」と表示されます
2. Medal で保存したいクリップのリンクを順番にコピーします
   - コピーするたびに `+1 件追加 (合計 N 件)` と表示されます
3. 全部コピーしたら `Ctrl+C` で監視を終了します
4. 「このままダウンロードしますか? [Y/n]」で Enter を押すと、`./medal_clips` に保存されます

### オプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--txt PATH` | URL一覧の保存先 | `urls.txt` |
| `-o`, `--out DIR` | 動画の保存先 | `./medal_clips` |
| `--no-download` | URLを集めるだけで、ダウンロードはしない | - |
| `--download-only` | 監視せず、`urls.txt` の分だけダウンロードする | - |
| `--cookies-from-browser BROWSER` | ブラウザのログイン情報を使う(例: `chrome`, `firefox`) | - |

### 使用例

```bash
# 日を分けて集める(今日は集めるだけ)
python medal_clip_dl.py --no-download

# 後日ダウンロードだけ行う
python medal_clip_dl.py --download-only

# 保存先を指定する
python medal_clip_dl.py -o D:\Videos\medal

# ログインが必要なクリップを落とす
python medal_clip_dl.py --download-only --cookies-from-browser chrome
```

## 対応するURL

次の形式のURLを認識します。複数のURLをまとめてコピーしても、すべて拾います。

```
https://medal.tv/ja/games/minecraft/clips/nEneUHh0Ld3jHXxL9?invite=cr-xxxx
https://medal.tv/games/valorant/clips/jTBFnLKdLy15K
```

- `/ja/` のような言語プレフィックスは、保存時に自動で取り除きます(yt-dlp の Medal extractor が `medal.tv/games/...` の形式しか受け付けないため)
- `?invite=...` は残します
- 同じクリップIDは1件にまとめます(何度コピーしても重複しません)

## 出力

```
./urls.txt                 集めたURL一覧(追記される)
./medal_clips/
  ├─ タイトル [クリップID].mp4
  └─ archive.txt           ダウンロード済みの記録
```

- `urls.txt` は起動時に読み込まれるので、前回の続きから追加できます
- `archive.txt` があるため、再実行しても **ダウンロード済みのクリップはスキップ**されます
- 1本失敗しても残りのダウンロードは続行されます

## トラブルシューティング

| 症状 | 対処 |
|---|---|
| URLをコピーしても追加されない | URLが上記の形式か確認してください。`medal.tv/games/<ゲーム>/clips/<ID>` の形が必要です |
| `pyperclip` のエラーが出る | Linux では `xclip` / `xsel` / `wl-clipboard` をインストールしてください |
| ダウンロードでエラーになる | まず `yt-dlp -U` で更新してください。Medal 側の仕様変更に extractor が追いついていないことがあります |
| 非公開クリップが落とせない | `--cookies-from-browser chrome` を試してください。`invite` 付きの非公開クリップが取得できるかは未確認です |
| 一部のクリップだけ失敗する | 失敗したクリップは `archive.txt` に入らないので、`--download-only` で再実行すれば再試行されます |

## 注意

- ダウンロードするのは、自分のクリップや保存を許可されているクリップに限ってください。Medal の利用規約に従って使ってください
