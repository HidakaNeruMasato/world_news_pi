# Security & Permission Audit Report

## 1. Secret Scan & Git Repository Integrity
- **Committed Secret Scan**: Checked git history for API keys, passwords, tokens, private keys, and webhooks.
- **Result**: **0 Secrets Committed** (100% Passed). `.env` and local credentials are strictly gitignored.

---

## 2. Network Exposure & CORS Audit
- **API Exposure**: Bound to LAN IP (`192.168.0.185:8080` / `127.0.0.1:8080`). NOT exposed to public WAN Internet.
- **CORS Configuration**: Explicit origin whitelist (`http://localhost:5173`, `http://localhost:8080`, `http://127.0.0.1:8080`). Wildcard `*` disabled for production.

---

## 3. File System Permissions Audit
- **Ownership**: All project files, SQLite DBs, models, logs, and venvs are owned by non-root user `hidakamasato:hidakamasato`.
- **Root Dependency**: No services run under `root` privileges.
- **Status**: **PASS**
