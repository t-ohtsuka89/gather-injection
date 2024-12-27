# Gather Injection

## インストール方法

1. このリポジトリをクローンします：
   ```
   git clone https://github.com/t-ohtsuka89/gather-injection.git
   ```

2. プロジェクトディレクトリに移動します：
   ```
   cd gather-injection
   ```

3. 必要な依存関係をインストールします：
   ```
   pip install .
   ```

4. プロジェクトを実行します：
   ```
   gather-injection -s "{JavaScriptのファイルパス（複数指定可）}"
   ```

## 設定

設定は以下の方法で行うことができます：

1. 環境変数による設定
2. `.env`ファイルによる設定

### 環境変数

主な設定項目：

#### スクリプト実行の設定
- `GATHER_SCRIPT_MAX_SIZE`: スクリプトの最大サイズ（バイト）
- `GATHER_SCRIPT_TIMEOUT`: スクリプト実行のタイムアウト時間（秒）

#### ネットワーク関連の設定
- `GATHER_WINDOW_TIMEOUT`: ウィンドウ検索のタイムアウト時間（秒）
- `GATHER_GAME_OBJECT_TIMEOUT`: ゲームオブジェクト待機のタイムアウト時間（秒）
- `GATHER_TARGET_URL`: GatherのターゲットURL
- `GATHER_MAX_ATTEMPTS_DEBUG_PORT`: デバッグポート接続の最大試行回数
- `GATHER_DEBUG_PORT_DELAY`: デバッグポート接続の試行間隔（秒）

#### アプリケーション全般の設定
- `GATHER_APP_NAME`: Gatherアプリケーションの名前
- `GATHER_LOG_LEVEL`: ログレベル（INFO/DEBUG/WARNING/ERROR）
- `GATHER_RETRY_COUNT`: 操作失敗時の再試行回数
- `GATHER_RETRY_DELAY`: 再試行間隔（秒）

### .envファイルによる設定

1. `.env.example`を`.env`にコピーします：
   ```
   cp .env.example .env
   ```

2. `.env`ファイルを編集して、必要な設定を変更します。

注意: `.env`ファイルはバージョン管理対象外です。環境ごとに適切な設定を行ってください。
