# webhook-ingest Specification

## Purpose
TBD - created by archiving change add-core-capabilities. Update Purpose after archive.
## Requirements
### Requirement: Webhookエンドポイント

システムは、サポートされている各決済プロバイダー用のWebhookエンドポイントを `/webhooks/:provider` で提供しなければならない（SHALL）。

#### Scenario: Stripe Webhookの受信
- **GIVEN** Stripe Webhookシークレットが設定されている
- **WHEN** Stripeが有効な署名付きでPOSTリクエストを `/webhooks/stripe` に送信する
- **THEN** システムはリクエストを受け入れ、HTTP 200を返す

#### Scenario: Lemon Squeezy Webhookの受信
- **GIVEN** Lemon Squeezy Webhookシークレットが設定されている
- **WHEN** Lemon Squeezyが有効な署名付きでPOSTリクエストを `/webhooks/lemonsqueezy` に送信する
- **THEN** システムはリクエストを受け入れ、HTTP 200を返す

#### Scenario: Paddle Webhookの受信
- **GIVEN** Paddle Webhookシークレットが設定されている
- **WHEN** Paddleが有効な署名付きでPOSTリクエストを `/webhooks/paddle` に送信する
- **THEN** システムはリクエストを受け入れ、HTTP 200を返す

### Requirement: 署名検証

システムは、ペイロードを処理する前にWebhook署名を検証しなければならない（SHALL）。

#### Scenario: 有効な署名が受け入れられる
- **GIVEN** 有効な署名を持つWebhookリクエスト
- **WHEN** 設定されたシークレットに対して署名が検証される
- **THEN** リクエストは処理される

#### Scenario: 無効な署名が拒否される
- **GIVEN** 無効または欠落した署名を持つWebhookリクエスト
- **WHEN** 署名検証が失敗する
- **THEN** システムはHTTP 401でリクエストを拒否する
- **AND** イベントは保存されない

### Requirement: 生ペイロードの保存

システムは、生のWebhookペイロードを一切変更せずに保存しなければならない（SHALL）。

#### Scenario: 完全なペイロードを保存
- **GIVEN** 有効なWebhookリクエスト
- **WHEN** ペイロードが保存される
- **THEN** `raw_payload`フィールドには受信した正確なJSONが含まれる
- **AND** フィールドの追加、削除、変更は行われない

### Requirement: 冪等な処理

システムは、プロバイダーのイベントIDを使用して冪等なWebhook処理を保証しなければならない（SHALL）。

#### Scenario: イベントの初回配信
- **GIVEN** StripeからイベントID "evt_123" を持つWebhook
- **WHEN** イベントが初めて受信される
- **THEN** イベントは正常に保存される

#### Scenario: 重複配信は無視される
- **GIVEN** StripeからのID "evt_123" のイベントが既に存在する
- **WHEN** 同じイベントIDを持つWebhookが再度受信される
- **THEN** システムはHTTP 200（成功）を返す
- **AND** 重複イベントは作成されない

### Requirement: サポートされるイベントタイプ

システムは、各プロバイダーから以下のイベントタイプを受け入れて保存しなければならない（SHALL）。

#### Scenario: Stripeイベント
- **WHEN** Stripeが以下のイベントタイプのいずれかを送信する：
  - `checkout.session.completed`
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.payment_failed`
  - `charge.refunded`
- **THEN** イベントはイベントストアに保存される

#### Scenario: 不明なイベントタイプ
- **WHEN** プロバイダーがサポートリストにないイベントタイプを送信する
- **THEN** イベントは将来の互換性のために保存される
- **AND** システムはHTTP 200を返す

