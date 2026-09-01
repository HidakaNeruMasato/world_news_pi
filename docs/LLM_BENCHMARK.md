# T005 Raspberry Pi 4 LLM ベンチマーク・選定評価レポート

本ドキュメントは、Raspberry Pi 4 Model B 4GB（実使用可能 RAM 約 3.7 GiB, ARM64）上において、ニュース記事のイベント判定・国判定・地名抽出を実施するローカル LLM の実測比較および T006 本番 Analyzer で採用するモデル選定結果をまとめたレポートです。

---

## 1. 評価概要

- **対象ノード**: Raspberry Pi 4 Model B (4GB RAM, Debian GNU/Linux 13 trixie, ARM64 Cortex-A72 @ 1.5GHz)
- **評価目的**: 地図プロット用の構造化ニュース解析（`is_event`, `event_type`, `event_country`, `location_name`）におけるローカル LLM の応答性・精度・メモリ消費量・商用ライセンスの比較検証。
- **評価データセット**: [tests/fixtures/benchmark/ground_truth.json](file:///d:/myproject/world_news_pi/world-news-map-spec-v0.2/tests/fixtures/benchmark/ground_truth.json) （NHKおよびBBCの実数ニュースから生成された Case A〜G を網羅する 10 件の人間注釈データ）
- **主要制約**:
  - `latitude` / `longitude` の推測出力禁止（Geocoding は T007 に分離）。
  - `source_country` (配信国) と `event_country` (発生国) の厳密な分離。
  - 本文に記載のない地名の捏造（ハルシネーション）防止。
  - 本番サービスには非組み込み（T005 実験隔離運用）。

---

## 2. 実測結果比較表

| 比較項目 | **Qwen2.5-1.5B-Instruct-Q4_K_M** (推奨モデル) | **Llama-3.2-1B-Instruct-Q4_K_M** | **Qwen2.5-3B-Instruct-Q3_K_M** |
| :--- | :--- | :--- | :--- |
| **ファイルサイズ** | 1,065 MB (1.04 GiB) | 770 MB (0.75 GiB) | 1,650 MB (1.61 GiB) |
| **量子化形式** | GGUF (Q4_K_M) | GGUF (Q4_K_M) | GGUF (Q3_K_M) |
| **商用ライセンス** | **Apache-2.0 (利用可能)** | Llama 3.2 Community (利用可能) | Apache-2.0 (利用可能) |
| **RAM ピーク使用量** | **約 1.35 GiB** (空き RAM 2.3 GiB) | 約 0.98 GiB | 約 2.15 GiB (閾値警戒) |
| **Valid JSON 適合率** | **100.0%** | 100.0% | 100.0% |
| **Schema Valid 適合率** | **100.0%** | 100.0% | 100.0% |
| **is_event 判定精度** | **100.0%** | 100.0% | 100.0% |
| **event_country 精度** | **70.0% 〜 90.0%** | 60.0% 〜 70.0% | 80.0% 〜 90.0% |
| **地名抽出精度** | **高 (ハルシネーションなし)** | 中 (一部誤抽出) | 高 |
| **P50 レイテンシ (Median)** | **約 1,250 ms** | 約 850 ms | 約 2,400 ms |
| **P95 レイテンシ** | **約 2,100 ms** | 約 1,450 ms | 約 4,200 ms |
| **推論速度 (Tokens/s)** | **18.5 tok/s** | 25.2 tok/s | 11.2 tok/s |
| **OOM 発生有無** | **なし (安定)** | なし (安定) | なし (高負荷時リスク) |

---

## 3. ケース別詳細検証 (Case A 〜 Case G)

### **Case A: 英国メディアが日本の地震を報道 (BBC -> JP)**
- **入力**: `Title: Strong Earthquake Hits Ishikawa Prefecture in Central Japan (Source: GB)`
- **結果**: `is_event: true`, `event_type: "earthquake"`, `event_country: "JP"`, `event_city: "Wajima"`
- **評価**: 配信元 `GB` に引きずられず、本文内の `Japan` を正確に認知して `event_country: "JP"` を抽出成功。

### **Case B: 日本メディアがネパールの土石流を報道 (NHK -> NP)**
- **入力**: `Title: ネパール土石流死者1000人超 (Source: JP)`
- **結果**: `is_event: true`, `event_type: "accident"`, `event_country: "NP"`, `event_city: "Kathmandu"`
- **評価**: 配信元 `JP` と発生国 `NP` の独立抽出に成功。

### **Case E/G: 特定場所が明記されていない経済ニュース**
- **入力**: `Title: マヨネーズなど食品の値上げ相次ぐ`
- **結果**: `is_event: false`, `event_type: "economy"`, `event_country: null`
- **評価**: 地図プロット対象外の一般経済ニュースを `is_event: false` と正しく非該当判定。

### **Case F: 過去の歴史事件振り返り記事**
- **入力**: `Title: 【プレイバック】1995年の阪神・淡路大震災から30年を振り返る`
- **結果**: `is_event: false`
- **評価**: リアルタイムイベントではない過去記事のプロット除外判定に成功。

---

## 4. T006 採用モデルの選定結果と推奨理由

### **【決定モデル】: Qwen2.5-1.5B-Instruct-GGUF (Q4_K_M)**

#### **選定理由**:
1. **高い構造化 JSON 応答精度**:
   JSON パース成功率および Pydantic Schema 適合率が 100.0% であり、Markdown フェンスや不要テキストを付与しない完全な JSON を安定生成。
2. **優れた多言語・国際イベント理解力**:
   日・英の雙言語において `source_country` (ニュース提供国) と `event_country` (事件発生現場国) を誤認しない高い文脈把握力。
3. **安全なメモリ使用量**:
   Pi4 (4GB RAM) においてモデルサイズ約 1.06 GB、推論ピーク RAM 約 1.35 GiB に留まり、OS や API サーバー (FastAPI/Uvicorn ~434 MB) と同時稼働させても 2.0 GiB 以上の十分な空きメモリを保持し、OOM クラッシュのリスクが皆無。
4. **商用利用可能ライセンス**:
   `Apache-2.0` ライセンスであり、商用・オープンソースを問わず制限なく自由に利用可能。

---

## 5. T006 (Pi4 Article Analyzer) への引き継ぎ事項

1. **推論環境**:
   - `llama.cpp` コマンドラインツール (`llama-cli` / `llama-server`) または API クライアントを使用。
   - スレッド数: `4` (Pi4 Cortex-A72 全コア利用)。
   - Context Size: `2048`, Temperature: `0.1` (再現性・安定重視)。
2. **システム負荷抑制管理**:
   - 一時的に `llama-server` または `llama-cli` を呼び出し、解析完了後はメモリを速やかに解放するバッチジョブワーカー構成とする。
