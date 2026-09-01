# ENVIRONMENT.md

T001の環境調査結果（2026-09-01最新化）です。

## Windows PC

- OS: Microsoft Windows 10 Pro 64ビット (Build 19045)
- Python: 3.14.3
- Git: git version 2.55.0.windows.3
- Antigravity: 稼働中 (Gemini 3.6 Flash)
- SSH client: OpenSSH_for_Windows_9.5p1 (LibreSSL 3.8.2)
- Repository path: `d:\myproject\world_news_pi\world-news-map-spec-v0.2`
- SSH alias: 設定完了 (`~/.ssh/config` に `worldnews-pi3`, `worldnews-pi4` 定義)

## Pi3 (worldnews-pi3)

- Hostname: `RasPi3-masato`
- OS: Debian GNU/Linux 13 (trixie)
- Kernel: 6.18.34+rpt-rpi-v8 (64-bit)
- Python: Python 3.13.5
- RAM: 全体 905 MiB (使用中 262 MiB, 利用可能 642 MiB)
- Storage: 117 GB (使用中 5.2 GB)
- Free storage: 107 GB (空き率 95%)
- CPU temperature: 47.2°C
- LAN address: `192.168.0.149`
- SSH alias: `worldnews-pi3` (鍵認証設定完了)
- Available ports: 22 (SSH), 111 (rpcbind), 5353 (mDNS)
- systemd capability: systemd 257 (257.13-1~deb13u1)

## Pi4 (worldnews-pi4)

- Hostname: `RasPi4-masato`
- OS: Debian GNU/Linux 13 (trixie)
- Kernel: 6.18.34+rpt-rpi-v8 (64-bit)
- Python: Python 3.13.5
- RAM: 全体 3.7 GiB (使用中 386 MiB, 利用可能 3.3 GiB)
- Storage: 227 GB (使用中 6.6 GB)
- Free storage: 211 GB (空き率 96%)
- CPU temperature: 44.8°C
- LAN address: `192.168.0.185`
- SSH alias: `worldnews-pi4` (鍵認証設定完了)
- Available ports: 22 (SSH), 111 (rpcbind), 5353 (mDNS)
- systemd capability: systemd 257 (257.13-1~deb13u1)

## Network

- LAN subnet: `192.168.0.0/24` (Windows PC: `192.168.0.225`)
- Pi3 -> Pi4 connectivity: 正常 (Ping応答確認, 損失率 0%)
- PC -> Pi3 connectivity: 正常 (SSH `worldnews-pi3` 鍵認証接続成功)
- PC -> Pi4 connectivity: 正常 (SSH `worldnews-pi4` 鍵認証接続成功)

## ステータス

- T001 環境調査: **完了 (100%)**
- SSH 接続設定: **完了 (公開鍵認証設定済み・スクリプト連携可)**
