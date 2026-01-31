# public-api Specification

## Purpose
TBD - created by archiving change add-core-capabilities. Update Purpose after archive.
## Requirements
### Requirement: API認証

APIは、すべてのリクエストでAPIキーによる認証を要求しなければならない（SHALL）。

#### Scenario: 有効なAPIキーが受け入れられる
- **GIVEN** ヘッダー `Authorization: Bearer <有効なAPIキー>` を持つリクエスト
- **WHEN** APIが呼び出される
- **THEN** リクエストは処理される

#### Scenario: APIキーがない場合は拒否される
- **GIVEN** Authorizationヘッダーのないリクエスト
- **WHEN** APIが呼び出される
- **THEN** HTTP 401 Unauthorizedが返される

#### Scenario: 無効なAPIキーは拒否される
- **GIVEN** 無効なAPIキーを持つリクエスト
- **WHEN** APIが呼び出される
- **THEN** HTTP 401 Unauthorizedが返される

### Requirement: ユーザーエンタイトルメントエンドポイント

APIは、ユーザーのエンタイトルメントをクエリするエンドポイントを提供しなければならない（SHALL）。

#### Scenario: ユーザーエンタイトルメントを取得
- **GIVEN** ID "user_123" のユーザーがエンタイトルメントを持っている
- **WHEN** `GET /api/users/user_123/entitlements` が呼び出される
- **THEN** HTTP 200とエンタイトルメントのJSON配列が返される：
  ```json
  {
    "user_id": "user_123",
    "entitlements": [
      { "feature_key": "api_access", "enabled": true },
      { "feature_key": "premium_support", "enabled": false }
    ]
  }
  ```

#### Scenario: ユーザーが見つからない
- **GIVEN** ID "nonexistent" のユーザーが存在しない
- **WHEN** `GET /api/users/nonexistent/entitlements` が呼び出される
- **THEN** HTTP 404 Not Foundが返される

#### Scenario: 特定のエンタイトルメントを確認
- **GIVEN** ID "user_123" のユーザー
- **WHEN** `GET /api/users/user_123/entitlements/api_access` が呼び出される
- **THEN** HTTP 200と以下が返される：
  ```json
  {
    "user_id": "user_123",
    "feature_key": "api_access",
    "enabled": true
  }
  ```

### Requirement: ユーザーサブスクリプションエンドポイント

APIは、ユーザーのサブスクリプションをクエリするエンドポイントを提供しなければならない（SHALL）。

#### Scenario: ユーザーサブスクリプションを取得
- **GIVEN** ID "user_123" のユーザーがアクティブサブスクリプションを持っている
- **WHEN** `GET /api/users/user_123/subscription` が呼び出される
- **THEN** HTTP 200と以下が返される：
  ```json
  {
    "user_id": "user_123",
    "subscription": {
      "id": "sub_456",
      "plan_id": "pro_monthly",
      "status": "active",
      "started_at": "2024-01-15T00:00:00Z",
      "ended_at": null
    }
  }
  ```

#### Scenario: ユーザーにサブスクリプションがない
- **GIVEN** ID "user_123" のユーザーにサブスクリプションがない
- **WHEN** `GET /api/users/user_123/subscription` が呼び出される
- **THEN** HTTP 200と以下が返される：
  ```json
  {
    "user_id": "user_123",
    "subscription": null
  }
  ```

#### Scenario: ユーザーが見つからない
- **GIVEN** ID "nonexistent" のユーザーが存在しない
- **WHEN** `GET /api/users/nonexistent/subscription` が呼び出される
- **THEN** HTTP 404 Not Foundが返される

### Requirement: イベントクエリエンドポイント

APIは、イベントをクエリするエンドポイントを提供しなければならない（SHALL）。

#### Scenario: 最近のイベントを一覧表示
- **WHEN** `GET /api/events` が呼び出される
- **THEN** HTTP 200とページネーションされたイベントが返される（最新順）

#### Scenario: 日付でイベントをフィルタリング
- **WHEN** `GET /api/events?since=2024-01-01&until=2024-01-31` が呼び出される
- **THEN** その日付範囲内のイベントのみが返される

#### Scenario: プロバイダーでイベントをフィルタリング
- **WHEN** `GET /api/events?provider=stripe` が呼び出される
- **THEN** Stripeイベントのみが返される

#### Scenario: タイプでイベントをフィルタリング
- **WHEN** `GET /api/events?event_type=subscription.created` が呼び出される
- **THEN** そのタイプのイベントのみが返される

#### Scenario: ページネーション付きレスポンス
- **GIVEN** 100件のイベントが存在する
- **WHEN** `GET /api/events?limit=20&offset=0` が呼び出される
- **THEN** 最初の20件のイベントとページネーションメタデータが返される：
  ```json
  {
    "data": [...],
    "pagination": {
      "total": 100,
      "limit": 20,
      "offset": 0,
      "has_more": true
    }
  }
  ```

### Requirement: 読み取り専用API

APIは、書き込み操作のない読み取り専用でなければならない（SHALL）。

#### Scenario: POSTリクエストが拒否される
- **WHEN** 任意の /api/* エンドポイントにPOSTリクエストが行われる
- **THEN** HTTP 405 Method Not Allowedが返される

#### Scenario: PUTリクエストが拒否される
- **WHEN** 任意の /api/* エンドポイントにPUTリクエストが行われる
- **THEN** HTTP 405 Method Not Allowedが返される

#### Scenario: DELETEリクエストが拒否される
- **WHEN** 任意の /api/* エンドポイントにDELETEリクエストが行われる
- **THEN** HTTP 405 Method Not Allowedが返される

### Requirement: レスポンスキャッシング

APIは、パフォーマンス向上のためにキャッシングをサポートしなければならない（SHALL）。

#### Scenario: キャッシュヘッダーが含まれる
- **WHEN** 成功したAPIレスポンスが返される
- **THEN** 適切なCache-Controlヘッダーが含まれる
- **AND** 条件付きリクエスト用のETagヘッダーが含まれる

#### Scenario: 条件付きリクエストのサポート
- **GIVEN** ETag "abc123" を持つ以前のレスポンス
- **WHEN** リクエストに `If-None-Match: abc123` が含まれる
- **AND** データが変更されていない
- **THEN** HTTP 304 Not Modifiedが返される

### Requirement: APIレスポンスフォーマット

すべてのAPIレスポンスは一貫したJSONフォーマットを使用しなければならない（SHALL）。

#### Scenario: 成功レスポンスのフォーマット
- **WHEN** 成功したリクエストが行われる
- **THEN** レスポンスには以下が含まれる：
  - HTTP 2xxステータスコード
  - `Content-Type: application/json` ヘッダー
  - リクエストされたデータを含むJSONボディ

#### Scenario: エラーレスポンスのフォーマット
- **WHEN** エラーが発生する
- **THEN** レスポンスには以下が含まれる：
  - 適切なHTTPエラーステータスコード
  - エラー詳細を含むJSONボディ：
    ```json
    {
      "error": {
        "code": "NOT_FOUND",
        "message": "ユーザーが見つかりません"
      }
    }
    ```

### Requirement: ヘルスチェックエンドポイント

APIは、ヘルスチェックエンドポイントを提供しなければならない（SHALL）。

#### Scenario: ヘルスチェック成功
- **WHEN** `GET /api/health` が呼び出される
- **AND** システムが正常
- **THEN** HTTP 200と以下が返される：
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "timestamp": "2024-01-15T12:00:00Z"
  }
  ```

#### Scenario: ヘルスチェック失敗
- **WHEN** `GET /api/health` が呼び出される
- **AND** データベースが利用不可
- **THEN** HTTP 503と以下が返される：
  ```json
  {
    "status": "unhealthy",
    "database": "disconnected",
    "timestamp": "2024-01-15T12:00:00Z"
  }
  ```

### Requirement: APIレート制限

APIは、悪用を防ぐためにレート制限を実装しなければならない（SHALL）。

#### Scenario: レート制限内
- **GIVEN** クライアントが過去1分間に100リクエスト未満を行っている
- **WHEN** リクエストが行われる
- **THEN** リクエストは通常通り処理される

#### Scenario: レート制限超過
- **GIVEN** クライアントが過去1分間に100リクエストを行っている
- **WHEN** 別のリクエストが行われる
- **THEN** HTTP 429 Too Many Requestsが返される
- **AND** `Retry-After` ヘッダーがリトライ可能な時間を示す

