# Uniskope

**Uniskope** is an open-source, personal-first SaaS control plane for indie hackers and micro-SaaS operators.

> "Your SaaS, your data, your truth."

It provides a **Single Source of Truth (SSOT)** for subscription state, user state, and event history — without replacing your payment provider (Stripe, Lemon Squeezy, Paddle).

---

## Quick start (約30分)

### 前提

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### 1. リポジトリと環境

```bash
git clone <repo>
cd uniskope
cp backend/.env.example backend/.env
# 必要に応じて backend/.env を編集（DATABASE_URL, WEBHOOK secrets など）
```

### 2. DB とマイグレーション

```bash
docker compose up -d db
cd backend && alembic upgrade head && cd ..
```

### 3. API 起動

```bash
cd backend && uvicorn app.main:app --reload
```

別ターミナルで:

### 4. フロント（ダッシュボード）起動

```bash
cd frontend && npm install && npm run dev
```

ブラウザで http://localhost:5173 を開く。

### 5. Webhook の接続（本番向け）

- Stripe: Dashboard → Webhooks → Add endpoint → `https://your-host/webhooks/stripe`
- 署名シークレットを `backend/.env` の `STRIPE_WEBHOOK_SECRET` に設定

---

## 技術スタック

| レイヤー   | 技術 |
|-----------|------|
| Backend   | Python 3.11+, FastAPI, SQLAlchemy, Alembic |
| Frontend  | React, Vite, TypeScript, TailwindCSS |
| Database  | PostgreSQL（デフォルト）/ MySQL（オプション） |
| デプロイ  | Docker Compose, シングルノード |

---

## 主な機能

- **Webhook 取り込み** — 決済SaaSからの生イベントを保存（冪等・署名検証）
- **イベントストア** — 不変・追記専用のイベントログ
- **状態リゾルバー** — イベントから User / Subscription / Entitlement を導出
- **Public API** — 読み取り専用の状態問い合わせ（`/api/users/{id}/entitlements`, `/api/users/{id}/subscription`, `/api/events`）
- **ダッシュボード** — 読み取り専用の運用可視化（アクティブユーザー数、サブスク一覧、イベント、状態遷移ログ）

---

## Makefile

```bash
make install   # 依存関係インストール
make up       # DB 起動 + マイグレーション
make down     # DB 停止
make test     # バックエンドテスト
make lint     # バックエンド・フロントエンドのリント
```

---

## ドキュメント

- [REQUIREMENT.md](REQUIREMENT.md) — スコープと非スコープ
- [docs/SERVICE_SPEC.md](docs/SERVICE_SPEC.md) — サービス仕様
- [openspec/](openspec/) — OpenSpec による変更提案と設計

---

## ライセンス

MIT License
