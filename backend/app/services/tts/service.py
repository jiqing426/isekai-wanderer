"""TTS Service for CosyVoice integration."""

import os
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# Voice configuration by emotion
VOICE_CONFIG = {
    "打招呼": {"text": "你好呀，我是{character_name}，很高兴认识你！今天想聊点什么呢？"},
    "日常对话": {"text": "今天过得怎么样呀？有什么有趣的事情想和我分享吗？"},
    "告白": {"text": "其实…我一直想告诉你。你对我来说，是很特别很特别的存在。"},
    "生气": {"text": "你怎么可以这样！我真的很失望…不想再理你了！"},
}

# Voice model mapping
VOICE_MODELS = {
    "flash": settings.tts_voice_flash,
    "plus": settings.tts_voice_plus,
}


class TTSService:
    """TTS service using curl to call CosyVoice API."""

    def __init__(self):
        self.api_key = settings.tts_api_key
        self.base_url = settings.tts_base_url
        self.model = settings.tts_model
        self.output_dir = Path(settings.tts_voice_output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def synthesize(
        self,
        text: str,
        voice_model: str = "flash",
        output_path: Optional[str] = None,
    ) -> Optional[bytes]:
        """
        Synthesize speech using curl to call CosyVoice API.

        Uses subprocess curl because Python HTTP libraries have issues
        with the Bearer token encoding in this environment.
        """
        try:
            voice_id = VOICE_MODELS.get(voice_model, voice_model)
            if not voice_id:
                voice_id = settings.tts_voice_flash

            # Build JSON payload
            import json
            payload = json.dumps({
                "model": self.model,
                "input": text,
                "voice": voice_id,
                "response_format": "mp3",
            }, ensure_ascii=False)

            # Use temp file for output
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp_path = tmp.name

            # Call curl
            result = subprocess.run(
                [
                    "curl", "-s", "-o", tmp_path,
                    "-w", "%{http_code}",
                    "-X", "POST",
                    f"{self.base_url}/audio/speech",
                    "-H", f"Authorization: Bearer {self.api_key}",
                    "-H", "Content-Type: application/json",
                    "-d", payload,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            http_code = result.stdout.strip()

            if http_code != "200":
                logger.error(f"TTS curl failed: HTTP {http_code}")
                os.unlink(tmp_path)
                return None

            # Read audio bytes
            with open(tmp_path, "rb") as f:
                audio_bytes = f.read()

            os.unlink(tmp_path)

            if not audio_bytes:
                logger.error("TTS curl returned empty audio")
                return None

            # Save to file if output_path provided
            if output_path:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(audio_bytes)
                logger.info(f"TTS synthesis saved: {output_path}")

            return audio_bytes

        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return None

    async def generate_character_voices(
        self,
        character_id: str,
        character_name: str,
        gender: str = "female",
    ) -> Dict[str, Any]:
        """Generate voice samples for all emotions for a character."""

        char_id_prefix = str(character_id)[:8]
        output_subdir = self.output_dir / char_id_prefix
        output_subdir.mkdir(parents=True, exist_ok=True)

        emotions = {}

        for emotion, config in VOICE_CONFIG.items():
            text = config["text"].format(character_name=character_name)
            filename = f"{emotion}.mp3"
            output_path = output_subdir / filename
            audio_url = f"/static/voices/{char_id_prefix}/{filename}"

            success = await self.synthesize(
                text=text,
                voice_model="flash",
                output_path=str(output_path),
            )

            if success:
                emotions[emotion] = {
                    "text": text,
                    "audio_url": audio_url,
                }
            else:
                emotions[emotion] = {
                    "text": text,
                    "audio_url": None,
                    "error": "TTS synthesis failed",
                }

        return {
            "voice": settings.tts_voice_flash,
            "emotions": emotions,
        }


# Singleton instance
tts_service = TTSService()
