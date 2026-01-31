MicroSaaS Control Plane OSS

1. 概要

本プロジェクトは 個人開発者・インディーハッカー向け に、
既存の決済SaaS（Stripe / Lemon Squeezy / Paddle など）の上位に被せて使う OSS として提供される。

目的は「決済をすること」ではなく、

SaaS運営に必要な“状態・事実・履歴”を、自分の手元に持つこと

である。

本OSSは SaaS運営の Single Source of Truth（SSOT） を担う。

⸻

2. 想定ユーザー
	•	個人開発者
	•	インディーハッカー
	•	マイクロSaaS運営者
	•	1人〜3人規模の小規模チーム

ユーザー特性
	•	技術リテラシーが高い
	•	OSS受容度が高い
	•	セルフホストを厭わない
	•	既存SaaSの規約・BAN・価格に不安を持っている

⸻

3. 非スコープ（重要）

以下は MVPでは明確にやらない。
	•	❌ 決済処理そのもの（課金・請求）
	•	❌ 税務/VAT/インボイス対応
	•	❌ メール配信
	•	❌ CRM / サポート管理
	•	❌ 本格的な分析基盤
	•	❌ 多言語・多通貨の完全対応

「決済SaaSの代替」ではなく「制御プレーン」であることを死守する

⸻

4. コアコンセプト

4.1 SSOT（Single Source of Truth）
	•	課金状態
	•	ユーザー状態
	•	サブスクリプション状態
	•	イベント履歴

これらを 自前DBで正規化・永続化 する。

外部SaaSの管理画面やAPIは
「入力元の一つ」に過ぎない。

⸻

5. システム構成（論理）

[Payment SaaS]
   │ (Webhook)
   ▼
[Ingest Layer]
   │
   ▼
[Event Store]
   │
   ▼
[State Resolver]
   │
   ▼
[Core DB]
   │
   ├─ Dashboard API
   └─ Public API


⸻

6. 機能仕様（MVP）

6.1 Webhook Ingest

概要
外部決済SaaSからのWebhookを受信し、生イベントとして保存する。

対応予定イベント（初期）
	•	checkout.completed
	•	subscription.created
	•	subscription.updated
	•	subscription.cancelled
	•	payment.failed
	•	refund.created

要件
	•	Raw payload を 一切加工せず保存
	•	冪等性保証（event_id）
	•	再処理可能

⸻

6.2 Event Store

概要
	•	すべてのイベントを時系列で保存
	•	削除・上書き不可

保存項目（例）
	•	id
	•	provider (stripe / paddle / etc)
	•	event_type
	•	received_at
	•	raw_payload (JSONB)

⸻

6.3 State Resolver（最重要）

概要
イベント列から 現在の正規化された状態 を生成する。

管理する状態
User
	•	user_id (internal)
	•	external_customer_id
	•	status (active / inactive / blocked)

Subscription
	•	plan_id
	•	status (trialing / active / past_due / canceled)
	•	started_at
	•	ended_at

Entitlement
	•	feature_key
	•	enabled (bool)

「今、このユーザーは何が使えるのか？」に即答できること

⸻

6.4 Dashboard（Read Only）

目的
「現状を一目で把握できる」ことだけに集中する。

表示項目
	•	現在のアクティブユーザー数
	•	アクティブサブスクリプション一覧
	•	最近のイベント（時系列）
	•	状態遷移ログ

※ 編集機能は持たない

⸻

6.5 Public API

目的
アプリケーション側から 高速に状態を問い合わせる。

代表エンドポイント

GET /api/users/{id}/entitlements
GET /api/users/{id}/subscription
GET /api/events?since=

特性
	•	Read Heavy
	•	キャッシュ前提
	•	書き込み不可

⸻

7. データモデル（概略）

Tables
	•	events
	•	users
	•	subscriptions
	•	entitlements
	•	state_transitions

※ 正規化より 可読性・追跡性優先

⸻

8. セキュリティ方針
	•	Webhook署名検証必須
	•	管理画面はローカル or VPN前提
	•	API Key スコープ制限

⸻

9. デプロイ形態

OSS版
	•	Docker Compose
	•	SQLite / PostgreSQL
	•	Single Node

Hosted版（将来）
	•	マルチテナント
	•	自動Webhook設定
	•	高可用API

⸻

10. ライセンス方針（案）
	•	OSS Core: AGPL or Apache-2.0 + CLA
	•	Hosted機能: Proprietary

⸻

11. 成功指標（OSS）
	•	READMEだけで理解できる
	•	30分でローカル起動
	•	1日で本番Webhook接続

⸻

12. 一言ビジョン

“Your SaaS, your data, your truth.”

SaaS運営の主導権を、再び開発者の手に戻す。