# Roadmap

[Issue #1](https://github.com/gitchx/x1-sidecar-knob/issues/1) の全体構想を、実装・検証しやすい単位へ分割して進めます。

## [Phase 1: 1ノブ USB MIDI prototype](https://github.com/gitchx/x1-sidecar-knob/issues/2)

- ADC0 へ直接接続した1ノブを読み取る
- Channel 1 / CC 20 / 0〜127を送る
- デッドバンドと簡単な平滑化を実機調整する
- PC / Mac、MIDI Monitor / DAW で確認する

ファームウェアと手順は作成済みです。現在は実機検証待ちです。

## [Phase 2: 複数ノブ対応](https://github.com/gitchx/x1-sidecar-knob/issues/6)

- Pico 2 の直接 ADC 入力で2〜3ノブを検証する
- コントロールごとの CC 割り当てを文書化する
- 同時操作時の走査周期、ジッター、MIDI 量を確認する

## [Phase 3: アナログマルチプレクサ対応](https://github.com/gitchx/x1-sidecar-knob/issues/3)

- 候補部品と必要チャンネル数を決める
- 8〜16ノブの走査層を実装する
- セトリング時間、クロストーク、電源・デカップリングを評価する

## [Phase 4: Traktor X1 MK3 マッピング検証](https://github.com/gitchx/x1-sidecar-knob/issues/5)

- Traktor で Sidecar を認識させる
- MIDI Learn と `.tsi` マッピングを検証する
- 実際の DJ 操作でレスポンスと割り当てを評価する

## [Phase 5: ケース / Sidecar形状の設計](https://github.com/gitchx/x1-sidecar-knob/issues/4)

- X1 MK3 の寸法と設置条件を実測する
- ノブ間隔、ノブ高さ、USB ケーブル取り回しを決める
- 仮筐体で操作感を確認する

## [Phase 6: PCB化](https://github.com/gitchx/x1-sidecar-knob/issues/7)

- 確定した回路と BOM を整理する
- PCB、コネクタ、機械固定を設計する
- 組立性、USB 周辺強度、長時間安定性を検証する

ボタン、LED、設定保存などは上記の基盤を確認した後に個別 Issue として判断します。
