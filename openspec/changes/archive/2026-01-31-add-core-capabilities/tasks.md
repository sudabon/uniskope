# タスク: コア機能の追加

## 1. プロジェクトセットアップ

### Backend (Python/FastAPI)
- [x] 1.1 Pythonプロジェクト構造の作成（pyproject.toml, uv/poetry）
- [x] 1.2 FastAPIアプリケーションの初期化
- [x] 1.3 Ruff（リンター/フォーマッター）の設定
- [x] 1.4 mypy（型チェック）の設定
- [x] 1.5 pytest（テストフレームワーク）の設定

### Frontend (React/Vite)
- [x] 1.6 Vite + React + TypeScriptプロジェクトの作成
- [x] 1.7 TailwindCSSの設定
- [x] 1.8 Shadcn/uiの初期化と基本コンポーネントのインストール
- [x] 1.9 ESLint + Prettierの設定

### インフラ
- [x] 1.10 開発用Docker Composeの設定（API + DB + Frontend）
- [x] 1.11 環境変数管理の設定（.env）

## 2. データベーススキーマ (SQLAlchemy/Alembic)

- [x] 2.1 SQLAlchemyモデルの基底クラス作成
- [x] 2.2 `Event`モデルの作成
- [x] 2.3 `User`モデルの作成
- [x] 2.4 `Subscription`モデルの作成
- [x] 2.5 `Entitlement`モデルの作成
- [x] 2.6 `StateTransition`モデルの作成
- [x] 2.7 Alembic初期化とマイグレーション作成
- [x] 2.8 一般的なクエリパターン用のインデックス追加

## 3. Webhook取り込み (specs/webhook-ingest)

- [x] 3.1 FastAPIルーター `/webhooks/{provider}` の作成
- [x] 3.2 Stripe署名検証の実装
- [x] 3.3 Lemon Squeezy署名検証の実装
- [x] 3.4 Paddle署名検証の実装
- [x] 3.5 Pydanticスキーマの定義（リクエスト/レスポンス）
- [x] 3.6 冪等性チェック付きで生ペイロードを保存
- [x] 3.7 Webhookハンドラーのpytestテスト作成

## 4. イベントストア (specs/event-store)

- [x] 4.1 イベントリポジトリの実装（CRUD操作）
- [x] 4.2 ページネーション付きイベントクエリの実装
- [x] 4.3 タイプ/日付範囲によるイベントフィルタリングの実装
- [x] 4.4 イベントリポジトリのユニットテスト作成

## 5. 状態リゾルバー (specs/state-resolver)

- [x] 5.1 各プロバイダーのイベントからユーザーへのマッピング実装
- [x] 5.2 各プロバイダーのイベントからサブスクリプションへのマッピング実装
- [x] 5.3 サブスクリプションステータスのステートマシン実装
- [x] 5.4 エンタイトルメント導出ロジックの実装
- [x] 5.5 状態遷移記録の実装
- [x] 5.6 状態解決ロジックのユニットテスト作成
- [x] 5.7 イベントリプレイテストの作成

## 6. Public API (specs/public-api)

- [x] 6.1 FastAPIルーター `/api/users/{id}/entitlements` の実装
- [x] 6.2 FastAPIルーター `/api/users/{id}/subscription` の実装
- [x] 6.3 FastAPIルーター `/api/events` の実装（クエリパラメータ対応）
- [x] 6.4 APIキー検証の依存性注入（Depends）実装
- [x] 6.5 レスポンスキャッシュの実装
- [x] 6.6 FastAPIルーター `/api/health` の実装
- [x] 6.7 OpenAPI（Swagger）ドキュメントの確認・調整
- [x] 6.8 API統合テストの作成

## 7. ダッシュボード (specs/dashboard)

- [x] 7.1 React Routerのセットアップ
- [x] 7.2 APIクライアント（fetch/axios）のセットアップ
- [x] 7.3 アクティブユーザー数表示コンポーネントの実装
- [x] 7.4 アクティブサブスクリプション一覧コンポーネントの実装
- [x] 7.5 最近のイベントタイムラインコンポーネントの実装
- [x] 7.6 状態遷移ログビューコンポーネントの実装
- [x] 7.7 Shadcn/uiコンポーネントを使用したダークテーマUI
- [x] 7.8 レスポンシブデザインの実装

## 8. ドキュメント＆デプロイ

- [x] 8.1 30分クイックスタート付きREADMEの作成
- [x] 8.2 環境変数のドキュメント化
- [x] 8.3 各プロバイダーのWebhookセットアップのドキュメント化
- [x] 8.4 Docker Compose本番設定の作成
- [x] 8.5 Makefileまたはタスクランナーの作成

## 依存関係

```
1. プロジェクトセットアップ
     ↓
2. データベーススキーマ
     ↓
3. Webhook取り込み ─────┐
     ↓                 │
4. イベントストア       │
     ↓                 │
5. 状態リゾルバー ←────┘
     ↓
├── 6. Public API
└── 7. ダッシュボード
     ↓
8. ドキュメント
```

## 並列化可能な作業

- Backend (1.1-1.5) と Frontend (1.6-1.9) のセットアップは並列実行可能
- タスク6（Public API）と7（ダッシュボード）は状態リゾルバー完了後に並列実行可能
- 各セクション内のサブタスクはほぼ順次実行
