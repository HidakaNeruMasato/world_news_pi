# T026 UX 課題トラッキングシート & 優先度順位表 (UX Issues)

## 1. UX 課題の重要度定義

ユーザーの観察結果および発言から抽出された UI/UX 上の課題を以下の 4 段階で分類します。

* **P0 (致命的 / Blocker)**: サービスの目的が理解できない、または主要機能が利用できずタスク完遂不能。
* **P1 (重大 / Major)**: 主要タスクの達成に重大な障害や著しい遅延が発生。
* **P2 (改善推奨 / Moderate)**: 迷いや回り道が発生するが、最終的には自力で解決可能。
* **P3 (軽微 / Minor)**: 好み、見た目上の調整、または将来の機能要望。

---

## 2. 優先度スコアリング計算式

各課題の修復優先度 (`Priority Score`) は以下の式で算出します。

$$\text{Priority Score} = \text{Impact} \times \text{Frequency} \times \text{Task Importance}$$

* **Impact (影響度)**: `1` (軽微) 〜 `3` (致命的)
* **Frequency (再現度)**: `1` (1名) 〜 `3` (全3名)
* **Task Importance (タスク重要度)**: `1` (補助) 〜 `3` (Core UX)

---

## 3. 検出された UX 課題一覧

今回の外部テストにおいて **P0 (致命的) および P1 (重大) 課題は 0 件** でした。検出された P2/P3 課題は以下の通りです。

| Issue ID | 課題タイトル | Severity | Impact | Freq | Task Imp | Priority Score | 対象機能 / タスク |
|---|---|---|---|---|---|---|---|
| **ISSUE-01** | Country Filter の発見性向上 | **P2** | 2 | 2 | 2 | **8** | Region → Country 絞り込み (UJ-004) |
| **ISSUE-02** | モバイル高密度地域クラスタのタップエリア拡張 | **P2** | 2 | 1 | 2 | **4** | モバイルクラスタ操作 (UJ-014, UJ-015) |
| **ISSUE-03** | Reset All ボタンの視認性強調 | **P3** | 1 | 2 | 1 | **2** | フィルターリセット (UJ-013) |

---

## 4. 課題詳細シート (T027 改善向けデータ)

### ISSUE-01: Country Filter の発見性向上
- **Issue ID**: ISSUE-01
- **Title**: Region 選択後の Country Filter ドロップダウン発見性の向上
- **Severity**: P2 (改善推奨)
- **Affected Task**: UJ-004 (特定国への絞り込み)
- **Affected Device**: PC / Mobile 共通
- **Frequency**: 2 / 3 (T01, T02)
- **Impact**: 2 (中程度) / Task Importance: 2 (重要) -> **Score: 8**
- **Description**: Region Filter で地域を選択した際、隣の Country Filter ドロップダウンが自動的にアクティブ化・強調されないため、一部ユーザーが「国フィルターが存在する」ことに気づくまでに数秒の迷いが発生した。
- **Observed Behavior**: T02 が「ナイジェリアはどこから選ぶのだろう」と画面上部を 5 秒間探した。
- **Expected Behavior**: Region 選択後、Country ドロップダウンがハイライト表示され、スムーズに国選択へ誘導されること。
- **User Quote**: 「Region を選んだあと、国が選べることに一瞬気づきにくかった」
- **Recommendation for T027**: Region 選択時に Country ドロップダウンにアニメーション/フォーカスを当て、選択可能国数をバッジ表示する UI 改善。

---

### ISSUE-02: モバイル高密度地域クラスタのタップエリア拡張
- **Issue ID**: ISSUE-02
- **Title**: モバイル画面における密集マーカークラスタのタッチ精度向上
- **Severity**: P2 (改善推奨)
- **Affected Task**: UJ-014 (高密度地域閲覧), UJ-015 (モバイル探索)
- **Affected Device**: スマートフォン
- **Frequency**: 1 / 3 (T02)
- **Impact**: 2 (中程度) / Task Importance: 2 (重要) -> **Score: 4**
- **Description**: ヨーロッパや東アジアなどイベントが密集している地域で、ピンチアウト（拡大）しないと隣接するピンが誤タップされやすい。
- **Observed Behavior**: T02 が指でピンをタップした際、隣のマーカーが選択されたためズーム操作を挟んだ。
- **Expected Behavior**: タッチターゲット領域の拡大またはタップ時のスパイダーファイ（放射状展開）表示。
- **Recommendation for T027**: モバイル表示時に近接マーカーを放射状に展開する Spiderfy プラグインの調整またはヒット判定領域の拡張。

---

### ISSUE-03: Reset All ボタンの視認性強調
- **Issue ID**: ISSUE-03
- **Title**: 複数フィルター適用時の一括リセットボタンの強調
- **Severity**: P3 (軽微)
- **Affected Task**: UJ-013 (フィルターリセット)
- **Affected Device**: PC / Mobile 共通
- **Frequency**: 2 / 3 (T01, T03)
- **Impact**: 1 (軽微) / Task Importance: 1 (補助) -> **Score: 2**
- **Description**: 複合条件適用後に「最初の状態に戻したい」と思った際、Reset ボタンがテキストリンク風であるため目立ちにくい。
- **Recommendation for T027**: フィルター適用中のみ Reset ボタンにアクセントカラーを付与し、活性状態を明確化。
