import os
import logging
from logger import setup_logging
from fastmcp import FastMCP

from nijivoice.api import NijiVoiceClient
from nijivoice.models import VoiceGenerationRequest, VoiceActor, Balance

from dotenv import load_dotenv

# ロガーの設定
logger = setup_logging(level=logging.WARNING)  # 出力を最小限に抑える
load_dotenv()
client = NijiVoiceClient(api_key=os.environ.get("NIJIVOICE_API_KEY"))

# MCPの設定 - MCPのログ出力をオフにする
logging.getLogger("fastmcp").setLevel(logging.ERROR)
mcp = FastMCP("nijivoice MCP", description="MCP server for NijiVoice API")

@mcp.tool()
async def get_voice_actors() -> list:
    """
    Get the list of voice actors.
    
    Returns:
        A list of voice actors with their details.
    """
    actors = await client.get_voice_actors()
    return actors

@mcp.tool()
async def generate_voice(
    script: str,
    actor_id: str = None,
    speed: float = 1.0,
    emotional_level: float = -1.0,  # -1.0は「使用しない」を意味する特殊値
    sound_duration: float = -1.0,   # -1.0は「使用しない」を意味する特殊値
    format: str = "mp3"
) -> dict:
    """
    音声を生成してその結果を返す
    
    Args:
        script: 読み上げるテキスト（最大3,000文字）（必須）
        actor_id: 使用するVoice ActorのID（省略時は利用可能な最初のアクターを使用）
        speed: 読み上げスピード（0.4～3.0、デフォルト: 1.0）
        emotional_level: 感情レベル（0.0～1.5、デフォルト: -1.0は声優のデフォルトを使用）
        sound_duration: 音素発音の長さ（0.0～1.7、デフォルト: -1.0は声優のデフォルトを使用）
        format: 音声フォーマット（"mp3"または"wav"、デフォルト: "mp3"）
    
    Returns:
        以下を含む音声生成レスポンス：
        - audioFileUrl: 音声再生用のURL
        - audioFileDownloadUrl: 音声ダウンロード用のURL
        - duration: 音声の長さ（ミリ秒）
        - remainingCredits: 生成後の残りクレジット
    """
    # Validate format
    if format and format.lower() not in ["mp3", "wav"]:
        return {"status": "error", "message": "Format must be 'mp3' or 'wav'"}
    
    # 特殊値の処理: -1.0は「使用しない」を意味する
    actual_emotional_level = None if emotional_level == -1.0 else emotional_level
    actual_sound_duration = None if sound_duration == -1.0 else sound_duration
    
    # actor_idが指定されていない場合は、Voice Actor一覧から最初のアクターを使用
    if actor_id is None:
        actors = await get_voice_actors()
        if not actors:
            return {"status": "error", "message": "利用可能なVoice Actorが見つかりません"}
        actor_id = actors[0].id
        
    # Create voice generation request (parameters that are None will be excluded automatically)
    request = VoiceGenerationRequest(
        id=actor_id,
        script=script,
        speed=speed,
        emotional_level=actual_emotional_level,
        sound_duration=actual_sound_duration,
        format=format.lower()
    )
    
    # Generate the voice
    try:
        response = await client.generate_voice(request=request)
        return response
    except Exception as e:
        logger.error(f"Error generating voice: {str(e)}")
        return {"status": "error", "message": str(e)}
    
@mcp.tool()
async def get_credit_balance() -> int:
    """
    クレジット残高を取得
    
    Returns:
        クレジット残高
    """
    balance = await client.get_balance()
    return balance.get_credit()

@mcp.resource("voice-actors://list")
async def voice_actors_resource() -> list:
    """
    Voice Actor一覧リソース
    
    Returns:
        利用可能なVoice Actor一覧
    """
    return await get_voice_actors()

@mcp.resource("voice-actors://{actor_id}")
async def voice_actor_resource(actor_id: str) -> VoiceActor | None:
    """
    指定したIDのVoice Actorリソース
    
    Args:
        actor_id: 取得するVoice ActorのID
        
    Returns:
        Voice Actor情報（見つからない場合はNone）
    """
    actors = await get_voice_actors()
    for actor in actors:
        if actor.id == actor_id:
            return actor
    return None

@mcp.resource("credit://balance")
async def credit_balance_resource() -> dict:
    """
    クレジット残高リソース
    
    Returns:
        クレジット残高情報
    """
    balance = await client.get_balance()
    return balance

@mcp.prompt()
def voice_generation_prompt() -> str:
    """
    Prompt for generating voice using NijiVoice API.
    
    Returns:
        The prompt text.
    """
    return """# にじボイス音声生成

にじボイスAPIを使用して音声を生成します。

## 利用可能なVoice Actor
`get_voice_actors()` ツールを使用して、利用可能なVoice Actorの一覧を取得できます。

## 音声生成
音声を生成するには、以下のパラメータを指定します：

- `script`: 読み上げるテキスト（最大3,000文字）（必須）
- `actor_id`: 使用するVoice ActorのID（デフォルト: "5c7f729f-5814-436f-9e81-95aa837f9737"）
- `speed`: 読み上げスピード（0.4～3.0、デフォルト: 1.0）
- `emotional_level`: 感情レベル（0.0～1.5、デフォルト: -1.0 これはVoice Actorのデフォルト設定を使用することを意味します）
- `sound_duration`: 音素発音の長さ（0.0～1.7、デフォルト: -1.0 これはVoice Actorのデフォルト設定を使用することを意味します）
- `format`: 音声フォーマット（"mp3"または"wav"、デフォルト: "mp3"）

emotional_levelとsound_durationにVoice Actorのデフォルト設定を使用するには、-1.0を指定してください。

## 利用可能な関数
- `get_voice_actors()`: 利用可能なVoice Actorの一覧を取得
- `generate_voice(script, actor_id="5c7f729f-5814-436f-9e81-95aa837f9737", speed=1.0, emotional_level=-1.0, sound_duration=-1.0, format="mp3")`: 音声生成
- `get_credit_balance()`: クレジット残高取得

## レスポンス形式
generate_voice関数は以下の構造でレスポンスを返します：
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
"""

def main():
    # Run the server
    mcp.run()