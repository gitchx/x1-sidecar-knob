# Hardware

将来の回路図、PCB、BOM、筐体データを置くディレクトリです。

Phase 1 はブレッドボード上でポテンショメータ1個を Pico 2 の ADC0 へ直接接続します。現時点で未検証の回路図や PCB データを確定成果物として置かない方針です。配線は [`docs/WIRING.md`](../docs/WIRING.md) を参照してください。

今後の想定:

```text
hardware/
  bom/          部品表
  schematics/   回路図
  pcb/          PCB設計データ
  enclosure/    ケース・Sidecar形状データ
```
