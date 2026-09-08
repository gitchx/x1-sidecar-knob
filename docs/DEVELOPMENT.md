# 開発方針

## Phase 1 の技術選定

Phase 1 は CircuitPython を採用します。

確認した内容（2026-09-08時点）:

- Raspberry Pi Pico 2 向けの公式 CircuitPython 安定版が配布されている。
- Pico 2 は CircuitPython の `analogio` と `usb_midi` の対応対象に含まれる。
- `usb_midi` は通常デフォルトで有効で、`PortOut.write()` から MIDI バイト列を送信できる。
- したがって、Phase 1 の ADC 読み取りと USB MIDI CC には追加ライブラリが不要である。

公式情報:

- [CircuitPython for Raspberry Pi Pico 2](https://circuitpython.org/board/raspberry_pi_pico2/)
- [`analogio` documentation](https://docs.circuitpython.org/en/latest/shared-bindings/analogio/)
- [`usb_midi` documentation](https://docs.circuitpython.org/en/latest/shared-bindings/usb_midi/)
- [Raspberry Pi Pico 2 Datasheet](https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf)

現時点で CircuitPython を避ける明確な問題は確認されていないため、MicroPython や Pico SDK への変更は行いません。USB 列挙、レイテンシ、安定性、メモリなどに実機上の問題が見つかった場合は、再現条件と計測結果を Issue に記録してから代替方式を評価します。

## ファームウェア構造

- `config.py`: MIDI チャンネル、CC、ピン、しきい値、平滑化係数
- `x1_sidecar.py`: ハードウェア非依存の変換・状態管理・MIDI メッセージ生成
- `code.py`: ADC と USB MIDI を接続する薄い実行層
- `boot.py`: USB MIDI インターフェースを起動前に設定

`CONTROL_CONFIGS` の各要素から `AnalogKnob` を生成します。直接 ADC のノブを増やす際は設定要素を増やし、同じ処理のコピーを避けます。アナログマルチプレクサを導入するときは、入力取得部分を抽象化し、変換・デッドバンド・MIDI 出力は再利用します。

## ADC 処理

処理順は次のとおりです。

1. `analogio.AnalogIn.value` の 0〜65535 の値を読む。
2. 指数移動平均を1回更新する。
3. 最後に送信した ADC 値との差がしきい値未満なら送らない。
4. 校正範囲を 0〜127 へ丸めて変換する。
5. 前回と同じ MIDI 値なら送らない。
6. 変化した場合だけ Control Change を送信する。

デフォルトの `SMOOTHING_ALPHA = 0.25` は控えめな平滑化です。`1.0` にすると無効化できます。`ADC_CHANGE_THRESHOLD = 256` は 16-bit 表現の約 0.4% です。これらは推測だけで強く調整せず、実機ログを基に変更します。

起動直後は現在位置を1回送信します。以降は「しきい値を超えた」と「MIDI 値が変わった」の両方を満たす場合だけ送信します。

## USB MIDI

Control Change は次の標準3バイトです。

```text
0xB0 | (channel - 1), cc_number, value
```

初期設定は Channel 1、CC 20 です。外部ライブラリを使わず、CircuitPython 組み込みの USB MIDI 出力ポートへ直接書き込みます。Phase 1 の依存関係を最小化しつつ、一般的な MIDI 対応ソフトウェアで扱えるデータを送ります。

## 代替方式を検討する条件

以下のいずれかが実測で問題になった場合、CircuitPython 継続と代替方式を同じ Issue で比較します。

- 8〜16ノブの走査で必要な応答速度を満たせない。
- USB MIDI が対象 OS で安定して列挙・再接続できない。
- マルチプレクサ、LED、ボタン追加後にメモリや処理時間が不足する。
- より細かな USB descriptor や MIDI 機能が必要になる。

候補は MicroPython、Pico SDK + TinyUSB、Arduino-Pico 等です。変更時は、再現手順、比較結果、移行理由、利用ライブラリとバージョンを README または Issue に残します。
