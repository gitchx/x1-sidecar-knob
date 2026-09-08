# X1-Sidecar-knob

Native Instruments Traktor X1 MK3 の横に置き、不足する物理ノブを補う小型 USB MIDI コントローラーです。Raspberry Pi Pico 2 と一般的なポテンショメータから始め、将来は Traktor、Ableton Live、その他の MIDI 対応ソフトウェアで使える汎用コントローラーへ発展させます。

このリポジトリは GPL-3.0 で公開しています。

## 現在の開発ステータス

**Phase 1: 1ノブ USB MIDI プロトタイプ（macOS実機検証済み）**

実装済み:

- Pico 2 の GP26 / ADC0 を読み取る CircuitPython ファームウェア
- 16-bit ADC 値から MIDI CC 0〜127 への変換
- 小さな ADC 変化を無視するしきい値
- 応答を損ねにくい簡単な指数移動平均
- MIDI 値が変化したときだけ送信する処理
- 複数コントロールを設定リストへ追加できる構造
- PC 上で実行できる変換・状態管理・MIDI メッセージの単体テスト

実機確認済み（2026-09-08）:

- Raspberry Pi Pico 2 H / CircuitPython 10.3.0 / macOS 15.7.3
- MIDI Monitor 1.5.4で Channel 1 / CC 20を受信
- ノブ全域でCC 0〜127へ連続的に変化
- USBの抜き差し後もMIDI入力を再認識
- 停止中に不要なCCの連続送信なし
- デフォルトのしきい値256、平滑化係数0.25で明らかな遅れや引っ掛かりなし
- GP26とAGND間の0.1 µFコンデンサにより、中央付近の生ADCジッター幅が624から176へ減少

実測値、表示されたUSB MIDI名、コンデンサ有無の比較は [Phase 1実機検証結果](docs/PHASE1_VALIDATION.md) に記録しています。

## 採用環境

- Raspberry Pi Pico 2
- CircuitPython（Pico 2 用の現行安定版を推奨）
- 組み込みモジュール: `analogio`, `usb_midi`
- 追加 CircuitPython ライブラリ: なし

Pico 2 には公式の CircuitPython ビルドがあり、`analogio` と `usb_midi` の対象ボードにも含まれます。そのため、Phase 1 は CircuitPython で進めます。判断根拠と代替案は [開発方針](docs/DEVELOPMENT.md) に記録しています。

## 使用ハードウェア

- Raspberry Pi Pico 2 × 1（ブレッドボード用ヘッダーピン実装済み、または別途 2×20 ピンヘッダー）
- 10 kΩ Bカーブ（リニア）ポテンショメータ × 1
- ブレッドボード × 1
- ジャンパーワイヤー × 3以上
- データ通信対応 USB ケーブル × 1
- 0.1 µF（100 nF）セラミックコンデンサ × 1（実機比較の結果、Phase 1では使用）

## 1ノブ版の配線

Pico 2 の USB を外した状態で配線してください。

| ポテンショメータ端子 | Pico 2 | 物理ピン | 用途 |
| --- | --- | ---: | --- |
| 外側の端子 A | 3V3(OUT) | 36 | ADC 用 3.3 V |
| 中央端子（ワイパー） | GP26 / ADC0 | 31 | アナログ値 |
| 外側の端子 B | AGND | 33 | アナログ GND |

ポテンショメータの中央端子は、ノブ位置に応じて電圧が変わる「ワイパー」です。両外側を逆に配線しても壊れませんが、値が増える回転方向が逆になります。時計回りで値が減る場合は、USB を外してから外側の2本だけを入れ替えてください。

0.1 µF コンデンサは、中央端子（GP26）と AGND の間へ接続します。実機比較では中央付近の生ADCジッター幅が624から176へ減少し、操作感の悪化もなかったため、Phase 1の検証済み構成では使用します。図と注意点は [配線ガイド](docs/WIRING.md) を参照してください。

> [!WARNING]
> ADC へ 3.3 V を超える電圧を入力しないでください。VBUS（USB の 5 V）や VSYS をポテンショメータへ接続しないでください。

## Pico 2へのセットアップ

1. [Pico 2 用 CircuitPython](https://circuitpython.org/board/raspberry_pi_pico2/) の安定版 UF2 をダウンロードします。
2. Pico 2 の `BOOTSEL` ボタンを押しながら USB 接続します。
3. 表示された `RPI-RP2` ドライブへ UF2 をコピーします。
4. 再起動後に表示される `CIRCUITPY` ドライブのルートへ、以下の4ファイルをコピーします。

   ```text
   firmware/circuitpython/boot.py
   firmware/circuitpython/code.py
   firmware/circuitpython/config.py
   firmware/circuitpython/x1_sidecar.py
   ```

5. USB を一度抜き差しします。`boot.py` の USB MIDI 名設定は完全な再起動後に反映されます。

追加ライブラリのコピーは不要です。CircuitPython の `usb_midi.PortOut.write()` へ標準 MIDI Control Change メッセージを直接送っています。

### 設定変更

[config.py](firmware/circuitpython/config.py) に利用者が変更する値をまとめています。

```python
MIDI_CHANNEL = 1

CONTROL_CONFIGS = (
    {
        "name": "knob_1",
        "pin": board.GP26,
        "cc": 20,
        "adc_min": 0,
        "adc_max": 65535,
    },
)
```

MIDI チャンネルは通常の表記どおり 1〜16 で指定します。CC 番号は 0〜127 です。実測した端点に合わせる場合は `adc_min` と `adc_max` を変更します。

## MIDI CC仕様

| コントロール | MIDI Channel | CC | 値 | 送信条件 |
| --- | ---: | ---: | ---: | --- |
| Knob 1 | 1 | 20 | 0〜127 | 起動時に1回、その後はしきい値を超えて MIDI 値が変化したとき |

初期値は `config.py` で変更できます。デフォルトでは 5 ms 間隔で ADC を確認しますが、毎回 MIDI を送るわけではありません。

## 最初の動作確認

1. 上表どおりに1個のポテンショメータを配線します。
2. ファームウェアをコピーし、Pico 2 を USB で PC / Mac へ接続し直します。
3. OS の MIDI デバイス一覧または DAW でPicoのMIDI入力を選びます。検証したmacOS環境では、Audio MIDI設定のデバイス名が `Pico 2`、ポート名が `CircuitPython usb_midi.ports[0]`、MIDI Monitorのソース名が `Pico 2 CircuitPython usb_midi.ports[0]` と表示されました。OSとCircuitPythonの版によって表示は異なる場合があります。
4. MIDI Monitor または DAW の MIDI 表示を開きます。
5. ノブを端から端までゆっくり回し、Channel 1 / CC 20 が 0〜127 付近で変化することを確認します。
6. ノブから手を離し、CC が連続送信されないことを確認します。
7. 必要なら `DEBUG = True` にして CircuitPython のシリアルコンソールでも送信値を確認します。

実機環境、ADC実測値、MIDI受信結果は [Phase 1実機検証結果](docs/PHASE1_VALIDATION.md) にまとめています。

## 開発者向け検証

ハードウェア非依存部分は Python 3 の標準機能だけでテストできます。

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q firmware tests
```

`code.py` の `analogio` / `usb_midi` と USB 列挙は CircuitPython と実機が必要なため、PC 上のテスト対象外です。

## リポジトリ構成

```text
firmware/
  circuitpython/       Pico 2へコピーするファームウェア
docs/
  DEVELOPMENT.md       採用技術と設計方針
  PHASE1_VALIDATION.md Phase 1実機検証結果
  ROADMAP.md           Issue単位のロードマップ
  WIRING.md            初心者向け配線ガイド
hardware/
  README.md            回路・PCB・筐体成果物の置き場所
tests/
  test_x1_sidecar.py   PCで実行する単体テスト
LICENSE                GNU GPL v3
```

## ロードマップ

- Phase 1: 1ノブ USB MIDI の実機検証
- Phase 2: 複数ノブ対応
- Phase 3: アナログマルチプレクサ対応（8〜16ノブ）
- Phase 4: Traktor X1 MK3 マッピング検証
- Phase 5: ケース / Sidecar 形状の設計
- Phase 6: 回路確定と PCB 化

全体方針は [Issue #1](https://github.com/gitchx/x1-sidecar-knob/issues/1) と [ROADMAP.md](docs/ROADMAP.md) で管理します。[Issue #2: Phase 1実機検証](https://github.com/gitchx/x1-sidecar-knob/issues/2) の結果を記録済みです。Phase 2以降には未着手で、各Phaseの実機結果を次の設計へ反映します。
