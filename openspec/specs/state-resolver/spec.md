# state-resolver Specification

## Purpose
TBD - created by archiving change add-core-capabilities. Update Purpose after archive.
## Requirements
### Requirement: ユーザー状態の解決

システムは、関連するイベントからユーザーレコードを作成・更新しなければならない（SHALL）。

#### Scenario: チェックアウトイベントからユーザーが作成される
- **GIVEN** 顧客ID "cus_123" を持つ `checkout.session.completed` イベント
- **WHEN** イベントが処理される
- **THEN** 以下を持つユーザーレコードが作成される：
  - `external_customer_id`: "cus_123"
  - `provider`: イベントのprovider
  - `status`: "active"

#### Scenario: ユーザーが既に存在する
- **GIVEN** external_customer_id "cus_123" のユーザーが既に存在する
- **WHEN** 同じ顧客IDを参照する新しいイベントが発生する
- **THEN** 既存のユーザーレコードが使用される（重複は作成されない）

#### Scenario: ユーザーステータスが更新される
- **GIVEN** ステータスが "active" の既存ユーザー
- **WHEN** そのユーザーのすべてのサブスクリプションがキャンセルされる
- **THEN** ユーザーステータスが "inactive" に更新される

### Requirement: サブスクリプション状態の解決

システムは、サブスクリプションイベントからサブスクリプションレコードを作成・更新しなければならない（SHALL）。

#### Scenario: サブスクリプションが作成される
- **GIVEN** `subscription.created` イベント
- **WHEN** イベントが処理される
- **THEN** 以下を持つサブスクリプションレコードが作成される：
  - `user_id`: 関連するユーザーにリンク
  - `plan_id`: イベントペイロードから
  - `status`: イベントステータスからマッピング
  - `started_at`: サブスクリプション開始タイムスタンプ

#### Scenario: サブスクリプションが更新される
- **GIVEN** 既存サブスクリプションの `subscription.updated` イベント
- **WHEN** イベントが処理される
- **THEN** サブスクリプションレコードが新しい値で更新される
- **AND** 状態遷移が記録される

#### Scenario: サブスクリプションがキャンセルされる
- **GIVEN** `subscription.deleted` または `subscription.canceled` イベント
- **WHEN** イベントが処理される
- **THEN** サブスクリプションステータスが "canceled" に設定される
- **AND** `ended_at` にキャンセルタイムスタンプが設定される

### Requirement: サブスクリプションステータスのライフサイクル

システムは、有効なサブスクリプションステータス遷移を強制しなければならない（SHALL）。

#### Scenario: 有効なステータス値
- **WHEN** サブスクリプションが作成または更新される
- **THEN** ステータスは以下のいずれかでなければならない（MUST）：
  - `trialing`: トライアル期間中
  - `active`: アクティブにサブスクライブし、支払い済み
  - `past_due`: 支払い失敗、猶予期間
  - `canceled`: サブスクリプション終了

#### Scenario: trialingからのステータス遷移
- **GIVEN** ステータスが "trialing" のサブスクリプション
- **WHEN** トライアルが成功した支払いで終了する
- **THEN** ステータスは "active" に遷移する

#### Scenario: past_dueへのステータス遷移
- **GIVEN** ステータスが "active" のサブスクリプション
- **WHEN** 支払い失敗イベントが受信される
- **THEN** ステータスは "past_due" に遷移する

#### Scenario: canceledへのステータス遷移
- **GIVEN** 任意のステータスのサブスクリプション
- **WHEN** キャンセルイベントが受信される
- **THEN** ステータスは "canceled" に遷移する

### Requirement: エンタイトルメントの導出

システムは、ユーザーの現在のサブスクリプション状態からエンタイトルメントを導出しなければならない（SHALL）。

#### Scenario: アクティブサブスクリプションでエンタイトルメントが有効になる
- **GIVEN** プラン "pro" のアクティブサブスクリプションを持つユーザー
- **AND** プラン "pro" には機能 "api_access" が含まれる
- **WHEN** エンタイトルメントが解決される
- **THEN** 以下を持つエンタイトルメントレコードが存在する：
  - `user_id`: ユーザーのID
  - `feature_key`: "api_access"
  - `enabled`: true

#### Scenario: サブスクリプションがキャンセルされるとエンタイトルメントが無効になる
- **GIVEN** サブスクリプションがキャンセルされたばかりのユーザー
- **WHEN** エンタイトルメントが解決される
- **THEN** そのユーザーのすべてのエンタイトルメントは `enabled`: false になる

#### Scenario: エンタイトルメントクエリ
- **GIVEN** ID "user_123" のユーザー
- **WHEN** ユーザーのエンタイトルメントがクエリされる
- **THEN** すべての機能キーとその有効状態のリストが返される

### Requirement: 状態遷移の記録

システムは、監査目的ですべての状態遷移を記録しなければならない（SHALL）。

#### Scenario: ステータス変更時に遷移が記録される
- **GIVEN** "active" から "past_due" に変更するサブスクリプション
- **WHEN** 状態変更が処理される
- **THEN** 以下を持つstate_transitionレコードが作成される：
  - `entity_type`: "subscription"
  - `entity_id`: サブスクリプションID
  - `from_state`: "active"
  - `to_state`: "past_due"
  - `event_id`: トリガーとなったイベントID
  - `transitioned_at`: 遷移のタイムスタンプ

#### Scenario: 作成時に遷移が記録される
- **GIVEN** 新しいサブスクリプションが作成される
- **WHEN** 作成が処理される
- **THEN** 以下を持つstate_transitionレコードが作成される：
  - `from_state`: null
  - `to_state`: 初期ステータス

### Requirement: イベントリプレイ機能

システムは、イベントを順番にリプレイして状態を再構築することをサポートしなければならない（SHALL）。

#### Scenario: 完全な状態再構築
- **GIVEN** イベントストア内のすべてのイベント
- **WHEN** 完全な状態再構築がトリガーされる
- **THEN** すべてのUser、Subscription、Entitlementレコードが再作成される
- **AND** 最終状態は再構築前の現在の状態と一致する

#### Scenario: チェックポイントからの部分リプレイ
- **GIVEN** 時刻T1の状態スナップショットが存在する
- **WHEN** T1以降のイベントがリプレイされる
- **THEN** 現在の状態が正しく導出される
- **AND** パフォーマンスは完全リプレイより良好

### Requirement: プロバイダー非依存のマッピング

システムは、プロバイダー固有のイベントフォーマットを内部モデルにマッピングしなければならない（SHALL）。

#### Scenario: Stripeイベントのマッピング
- **GIVEN** Stripeの `customer.subscription.created` イベント
- **WHEN** イベントが処理される
- **THEN** Stripe固有のフィールドが内部Subscriptionモデルにマッピングされる

#### Scenario: Paddleイベントのマッピング
- **GIVEN** Paddleのサブスクリプションイベント
- **WHEN** イベントが処理される
- **THEN** Paddle固有のフィールドが内部Subscriptionモデルにマッピングされる
- **AND** 結果の状態は同等のStripeイベントと一貫している

#### Scenario: Lemon Squeezyイベントのマッピング
- **GIVEN** Lemon Squeezyのサブスクリプションイベント
- **WHEN** イベントが処理される
- **THEN** Lemon Squeezy固有のフィールドが内部Subscriptionモデルにマッピングされる

