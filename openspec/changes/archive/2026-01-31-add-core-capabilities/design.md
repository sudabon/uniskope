# 設計: コア機能アーキテクチャ

## コンテキスト

Uniskopeは、マイクロSaaS運営のためのイベントソーシングベースのコントロールプレーンとして設計されています。システムは外部決済プロバイダーからWebhookを受信し、それらを不変イベントとして保存し、イベント履歴から現在の状態を導出します。

**ステークホルダー**: インディーハッカー、個人開発者、小規模チーム（1〜3人）

**技術スタック**:
- Backend: Python + FastAPI + SQLAlchemy + Alembic
- Frontend: React + Vite + Shadcn/ui + TailwindCSS
- Database: PostgreSQL（デフォルト）/ MySQL（オプション）

**制約**:
- シングルユーザー、ローカルファーストのデプロイ
- v0.1では認証・認可なし
- PostgreSQL（デフォルト）、MySQL（オプション）で動作必須
- セルフホスト、Docker Composeデプロイ

## ゴール / 非ゴール

### ゴール
- 完全な監査証跡を持つ不変イベントストレージの提供
- サブスクリプション/エンタイトルメント状態のリアルタイムクエリの実現
- 複数の決済プロバイダー（Stripe、Lemon Squeezy、Paddle）のサポート
- 30分でローカルセットアップ、1日で本番Webhook接続を達成

### 非ゴール
- 決済処理
- マルチテナンシー
- リアルタイムUI更新
- 高度な分析

## システムアーキテクチャ

```
┌─────────────────┐
│   決済SaaS      │
│ (Stripe/Paddle) │
└────────┬────────┘
         │ Webhook
         ▼
┌─────────────────┐
│  取り込み層     │ ← 署名検証、生データ保存
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ イベントストア  │ ← 不変、追記専用
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 状態リゾルバー  │ ← イベントから現在状態を導出
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    コアDB       │ ← 正規化された現在状態
├─────────────────┤
│ • users         │
│ • subscriptions │
│ • entitlements  │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌──────────┐
│  API  │ │ダッシュ  │
│       │ │ボード    │
└───────┘ └──────────┘
```

## 決定事項

### 決定1: イベントソーシングパターン

**内容**: すべてのWebhookペイロードを不変イベントとして保存し、イベント履歴から状態を導出する。

**理由**: 
- デバッグとコンプライアンスのための完全な監査証跡
- イベントをリプレイして状態を再構築する機能
- プロバイダー固有のデータモデルからの独立

**検討した代替案**:
- 直接状態更新: シンプルだが履歴が失われ、デバッグが困難
- 別々の読み取りモデルを持つCQRS: v0.1の規模では過剰

### 決定2: イベントIDによる冪等性

**内容**: プロバイダーのイベントIDを使用して冪等なWebhook処理を保証する。

**理由**:
- Webhookは複数回配信される可能性がある
- 重複イベントや状態遷移を作成してはならない

**実装**: eventsテーブルの`(provider, event_id)`にユニーク制約。

### 決定3: PostgreSQLをデフォルトデータベースに

**内容**: シングルノードデプロイにはPostgreSQLを使用し、MySQLをオプションのパスとする。

**理由**:
- JSONBネイティブサポートによる生ペイロードの効率的な保存・クエリ
- イベントソーシングに適した高度なインデックス機能
- Docker公式イメージによる容易なセットアップ
- 広範なエコシステムとドキュメント

**トレードオフ**:
- MySQLに比べてメモリ使用量がやや多い
- 小規模環境ではオーバースペックの可能性

### 決定4: 読み取り専用ダッシュボード

**内容**: ダッシュボードは状態を表示するが、変更は許可しない。

**理由**:
- イベントソーシングの整合性を維持
- 複雑さと攻撃面を削減
- 状態変更はWebhookを通じてのみ行われるべき

### 決定5: プロバイダー非依存の内部モデル

**内容**: プロバイダー固有のイベントを内部正規化エンティティ（User、Subscription、Entitlement）にマッピングする。

**理由**:
- アプリケーションコードを変更せずにプロバイダーを切り替え可能
- 決済バックエンドに関係なく一貫したAPIを提供

## データモデル

### テーブル

```sql
-- 不変イベントログ
events (
  id              TEXT PRIMARY KEY,
  provider        TEXT NOT NULL,      -- stripe, paddle, lemonsqueezy
  event_type      TEXT NOT NULL,      -- checkout.completed, subscription.created など
  event_id        TEXT NOT NULL,      -- プロバイダーのイベントID
  received_at     TIMESTAMP NOT NULL,
  raw_payload     JSONB NOT NULL,
  UNIQUE(provider, event_id)
)

-- 導出された状態テーブル
users (
  id                    TEXT PRIMARY KEY,
  external_customer_id  TEXT NOT NULL,
  provider              TEXT NOT NULL,
  status                TEXT NOT NULL,  -- active, inactive, blocked
  created_at            TIMESTAMP NOT NULL,
  updated_at            TIMESTAMP NOT NULL
)

subscriptions (
  id          TEXT PRIMARY KEY,
  user_id     TEXT NOT NULL REFERENCES users(id),
  plan_id     TEXT NOT NULL,
  status      TEXT NOT NULL,  -- trialing, active, past_due, canceled
  started_at  TIMESTAMP,
  ended_at    TIMESTAMP,
  created_at  TIMESTAMP NOT NULL,
  updated_at  TIMESTAMP NOT NULL
)

entitlements (
  id              TEXT PRIMARY KEY,
  user_id         TEXT NOT NULL REFERENCES users(id),
  feature_key     TEXT NOT NULL,
  enabled         BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMP NOT NULL,
  updated_at      TIMESTAMP NOT NULL,
  UNIQUE(user_id, feature_key)
)

-- 状態変更の監査証跡
state_transitions (
  id              TEXT PRIMARY KEY,
  entity_type     TEXT NOT NULL,    -- user, subscription, entitlement
  entity_id       TEXT NOT NULL,
  from_state      TEXT,
  to_state        TEXT NOT NULL,
  event_id        TEXT NOT NULL REFERENCES events(id),
  transitioned_at TIMESTAMP NOT NULL
)
```

## リスク / トレードオフ

| リスク | 影響 | 緩和策 |
|--------|------|--------|
| イベントリプレイのパフォーマンス | 大規模データセットでの状態再構築が遅い | 定期的なスナップショット、遅延再構築 |
| プロバイダーのWebhookフォーマット変更 | イベント解析が壊れる | バージョン対応パーサー、生ペイロード保存 |
| v0.1での認証なし | 公開時のセキュリティリスク | localhost/VPN専用デプロイをドキュメント化 |

## 移行計画

初期実装のため該当なし。

## 未解決の質問

1. v0.1でUIからのWebhookリトライ/リプレイをサポートすべきか？
2. イベントの保持ポリシーは？（提案: v0.1では無制限）
3. エンタイトルメントはサブスクリプションプランから自動導出すべきか、手動設定か？
