# NijiVoice MCP

FastMCPを使用した[にじボイスAPI](https://nijivoice.com/api)のMCPサーバー実装です。

## 概要

このMCPサーバーは、にじボイスAPIを利用して音声合成を行うための機能を提供します。主な機能は以下の通りです：

- 利用可能な声優（Voice Actor）の一覧取得
- テキストから音声ファイルを生成
- クレジット残高の確認

## 前提条件

- Python 3.12以上
- [uv](https://github.com/astral-sh/uv) - 高速なPythonパッケージマネージャーとインストーラー
- [fastmcp](https://github.com/jlowin/fastmcp) v2.2.8以上
- にじボイスAPIのAPIキー

## インストール方法

1. リポジトリをクローンします：
   ```bash
   git clone https://github.com/ryoooo/nijivoice-mcp-beta.git
   cd nijivoice-mcp-beta
   ```

2. [uv](https://github.com/astral-sh/uv) を使用して仮想環境を作成して依存関係をインストールします：
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/Mac
   # または
   .venv\Scripts\activate  # Windows
   
   uv pip install -e .
   ```

3. `.env`ファイルを作成し、にじボイスAPIのキーを設定します：
   ```
   NIJIVOICE_API_KEY=your_api_key_here
   ```

## 使い方

### MCPサーバーの起動

開発モードでサーバーを起動するには：

```bash
uv run fastmcp dev server.py
```

本番モードでサーバーを起動するには：

```bash
uv run fastmcp run server.py
```

### インストールして使用

MCPサーバーをインストールして使用するには：

```bash
uv run fastmcp install server.py
```

### 機能

以下の機能が利用可能です：

#### ツール（Tools）

- `get_voice_actors()`: 利用可能な声優の一覧を取得
- `generate_voice(script, actor_id, speed, emotional_level, sound_duration, format)`: 音声を生成
- `get_credit_balance()`: クレジット残高を取得

#### リソース（Resources）

- `voice-actors://list`: 声優一覧リソース
- `voice-actors://{actor_id}`: 特定の声優の情報を取得
- `credit://balance`: クレジット残高リソース

#### プロンプト（Prompt）

- `voice_generation_prompt()`: 音声生成に関するプロンプトを提供

## 音声生成パラメータ

音声生成時に以下のパラメータを指定できます：

- `script`: 読み上げるテキスト（最大3,000文字）（必須）
- `actor_id`: 使用する声優のID（省略時は最初の声優を使用）
- `speed`: 読み上げスピード（0.4～3.0、デフォルト: 1.0）
- `emotional_level`: 感情レベル（0.0～1.5、デフォルト: -1.0 = 声優のデフォルト設定を使用）
- `sound_duration`: 音素発音の長さ（0.0～1.7、デフォルト: -1.0 = 声優のデフォルト設定を使用）
- `format`: 音声フォーマット（"mp3"または"wav"、デフォルト: "mp3"）

## レスポンス形式

音声生成時のレスポンス形式は以下の通りです：

```json
{
  "generatedVoice": {
    "audioFileUrl": "音声再生用のURL",
    "audioFileDownloadUrl": "音声ダウンロード用のURL",
    "duration": 1312, // 音声の長さ（ミリ秒）
    "remainingCredits": 3613 // 生成後の残りクレジット
  }
}
```

## テスト

テストを実行するには：

```bash
uv run pytest
```

詳細なテスト結果を表示するには：

```bash
uv run pytest -v
```

カバレッジレポートを生成するには：

```bash
uv run pytest --cov=nijivoice
```

## ライセンス

[MIT](LICENSE)

## 謝辞

- [fastmcp](https://github.com/jlowin/fastmcp) - MCP (Model Context Protocol) サーバーを構築するためのPythonフレームワーク
- [にじボイスAPI](https://nijivoice.com/api) - 高品質な音声合成を提供するAPI