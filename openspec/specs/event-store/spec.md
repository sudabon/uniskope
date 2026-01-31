# event-store Specification

## Purpose
TBD - created by archiving change add-core-capabilities. Update Purpose after archive.
## Requirements
### Requirement: 不変イベントストレージ

システムは、すべてのイベントを変更または削除できない不変レコードとして保存しなければならない（SHALL）。

#### Scenario: イベントが正常に作成される
- **GIVEN** 有効なWebhookペイロード
- **WHEN** イベントが保存される
- **THEN** 一意のIDを持つ新しいイベントレコードが作成される
- **AND** レコードには `provider`、`event_type`、`event_id`、`received_at`、`raw_payload` が含まれる

#### Scenario: イベントの変更が防止される
- **GIVEN** ストア内の既存イベント
- **WHEN** イベントを変更しようとする試みが行われる
- **THEN** 変更は拒否される
- **AND** 元のイベントは変更されない

#### Scenario: イベントの削除が防止される
- **GIVEN** ストア内の既存イベント
- **WHEN** イベントを削除しようとする試みが行われる
- **THEN** 削除は拒否される
- **AND** イベントはストアに残る

### Requirement: イベントスキーマ

各イベントレコードには以下のフィールドが含まれなければならない（SHALL）。

#### Scenario: 必須イベントフィールド
- **WHEN** イベントが保存される
- **THEN** レコードには以下が含まれる：
  - `id`: 一意の内部識別子（UUID）
  - `provider`: ソースプロバイダー名（stripe, paddle, lemonsqueezy）
  - `event_type`: プロバイダー固有のイベントタイプ文字列
  - `event_id`: プロバイダーの一意のイベント識別子
  - `received_at`: イベントが受信されたタイムスタンプ
  - `raw_payload`: 受信した完全なJSONペイロード

### Requirement: イベントの一意性

システムは、providerとevent_idの組み合わせに対して一意性を強制しなければならない（SHALL）。

#### Scenario: 一意制約が適用される
- **GIVEN** provider "stripe" とevent_id "evt_123" のイベントが存在する
- **WHEN** 同じproviderとevent_idを持つ別のイベントが挿入される
- **THEN** 挿入は拒否されるか無視される（冪等な動作）

### Requirement: IDによるイベントクエリ

システムは、内部IDによる単一イベントの取得をサポートしなければならない（SHALL）。

#### Scenario: IDでイベントを検索
- **GIVEN** ID "abc-123" のイベントがストアに存在する
- **WHEN** イベントID "abc-123" のクエリが行われる
- **THEN** 完全なイベントレコードが返される

#### Scenario: イベントが見つからない
- **GIVEN** ID "nonexistent" のイベントが存在しない
- **WHEN** イベントID "nonexistent" のクエリが行われる
- **THEN** 「見つからない」結果が返される

### Requirement: ページネーション付きイベントクエリ

システムは、設定可能なページサイズでイベントのページネーションクエリをサポートしなければならない（SHALL）。

#### Scenario: ページネーション付きイベントリスト
- **GIVEN** ストアに100件のイベントが存在する
- **WHEN** page_size=20、page=1でクエリが行われる
- **THEN** 最初の20件のイベントが返される（最新順）
- **AND** ページネーションメタデータに合計件数とページ数が示される

#### Scenario: 空のページ
- **GIVEN** ストアに50件のイベントが存在する
- **WHEN** page_size=20、page=5でクエリが行われる
- **THEN** 空の結果セットが返される

### Requirement: イベントフィルタリング

システムは、provider、イベントタイプ、日付範囲によるイベントのフィルタリングをサポートしなければならない（SHALL）。

#### Scenario: providerでフィルタリング
- **GIVEN** 複数のプロバイダーからのイベントが存在する
- **WHEN** provider="stripe" でフィルタリングしてクエリする
- **THEN** Stripeイベントのみが返される

#### Scenario: イベントタイプでフィルタリング
- **GIVEN** 様々なタイプのイベントが存在する
- **WHEN** event_type="subscription.created" でフィルタリングしてクエリする
- **THEN** そのタイプのイベントのみが返される

#### Scenario: 日付範囲でフィルタリング
- **GIVEN** 複数の日付のイベントが存在する
- **WHEN** since="2024-01-01"、until="2024-01-31" でフィルタリングしてクエリする
- **THEN** その日付範囲内に受信されたイベントのみが返される

#### Scenario: 複合フィルター
- **GIVEN** 様々なイベントが存在する
- **WHEN** provider、event_type、日付範囲フィルターを組み合わせてクエリする
- **THEN** すべての条件に一致するイベントのみが返される

### Requirement: 時系列順序

イベントはデフォルトで時系列順に保存・取得されなければならない（SHALL）。

#### Scenario: デフォルトの順序
- **WHEN** 明示的な順序指定なしでイベントをクエリする
- **THEN** 結果はreceived_atの降順で返される（最新が最初）

#### Scenario: 昇順オプション
- **WHEN** order="asc" でイベントをクエリする
- **THEN** 結果はreceived_atの昇順で返される（最古が最初）

