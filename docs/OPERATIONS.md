# OPERATIONS.md — 運用および運用制御手順書

## 1. PowerShell オペレーションスクリプト (`scripts/ops.ps1`)

開発機 (Windows) から以下のコマンドを実行して運用操作を行います:

- **全ユニットテスト実行**:
  ```powershell
  .\scripts\ops.ps1 -Action test
  ```
- **Pi3 への配備**:
  ```powershell
  .\scripts\ops.ps1 -Action deploy-pi3
  ```
- **Pi4 への配備**:
  ```powershell
  .\scripts\ops.ps1 -Action deploy-pi4
  ```
- **システムログ確認**:
  ```powershell
  .\scripts\ops.ps1 -Action logs
  ```

---

## 2. Pi4 API サービスの管理 (SSH 経由)

Pi4 (`worldnews-pi4`) 上の一般ユーザーサービス管理:

- **起動**:
  ```bash
  ssh worldnews-pi4 "systemctl --user start world-news-api.service"
  ```
- **停止**:
  ```bash
  ssh worldnews-pi4 "systemctl --user stop world-news-api.service"
  ```
- **再起動**:
  ```bash
  ssh worldnews-pi4 "systemctl --user restart world-news-api.service"
  ```
- **ステータス確認**:
  ```bash
  ssh worldnews-pi4 "systemctl --user status world-news-api.service --no-pager"
  ```
- **ヘルスチェック (curl)**:
  ```bash
  ssh worldnews-pi4 "curl -s http://localhost:8080/api/v1/health"
  ```
