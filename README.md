# World News Event Map

Raspberry Pi 3 / 4 および Windows PC を組み合わせたセルフホスト型リアルタイム世界のニュース・イベント可視化システムです。

## システム構成

- **Windows PC**: 開発・AIエージェントコントロール・デプロイ・バックアップ
- **worldnews-pi3 (Raspberry Pi 3 B+)**: RSSニュース収集・前処理・重複除去
- **worldnews-pi4 (Raspberry Pi 4 Model B 4GB)**: ニュース解析 (LLM)・位置解決 (Geocoder)・イベント正規化・SQLite DB・REST API

## リポジトリ構造

```text
.
├── config.example.yaml     # 設定ファイルテンプレート
├── pyproject.toml          # Python パッケージ & pytest 設定
├── README.md               # プロジェクトドキュメント
├── AGENTS.md               # エージェント動作定義規約
├── SPEC.md                 # システム仕様書
├── ARCHITECTURE.md         # システムアーキテクチャ定義
├── docs/                   # 仕様・詳細ドキュメント類
├── scripts/
│   └── ops.ps1             # Windows 運用・デプロイスクリプト
├── src/
│   └── world_news/         # コア Python パッケージ
│       ├── config.py       # 設定ローダー
│       ├── logging.py      # ロギング基盤
│       ├── schemas.py      # 共通データモデル (Pydantic)
│       ├── collector/      # Pi3 収集モジュール
│       ├── analyzer/       # Pi4 解析モジュール
│       └── api/            # Pi4 REST API モジュール
├── systemd/                # systemd サービスユニット雛形
└── tests/                  # ユニットテスト類
```

## 運用スクリプト (`scripts/ops.ps1`) の使い方

PowerShell より以下のコマンドを実行可能です：

```powershell
# テストの実行 (pytest)
.\scripts\ops.ps1 -Action test

# Pi3 / Pi4 のシステムリソース・温度確認
.\scripts\ops.ps1 -Action health

# systemd サービスの状態確認
.\scripts\ops.ps1 -Action status

# Pi3 / Pi4 のディレクトリ初期化および Python 仮想環境 (venv) 作成
.\scripts\ops.ps1 -Action init-pi3
.\scripts\ops.ps1 -Action init-pi4

# ソースコード・設定・systemd ユニットの転送配備
.\scripts\ops.ps1 -Action deploy-pi3
.\scripts\ops.ps1 -Action deploy-pi4
```

## テストの実行方法

ローカル環境にて以下を実行します:

```bash
python -m pytest
```
