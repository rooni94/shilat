import os
from django.conf import settings
from google.cloud import texttospeech


class GoogleTTSProvider:
    """
    Google Cloud Text-to-Speech (Service Account via GOOGLE_APPLICATION_CREDENTIALS).
    """

    def __init__(self):
        # GOOGLE_APPLICATION_CREDENTIALS must point to a service-account JSON.
        creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds or not os.path.exists(creds):
            raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS غير موجود أو المسار غير صحيح")

        self.client = texttospeech.TextToSpeechClient()
        self.language = getattr(settings, "GOOGLE_TTS_LANGUAGE", "ar-XA")
        self.default_voice = getattr(settings, "GOOGLE_TTS_VOICE_NAME", "")
        self.default_encoding = getattr(settings, "GOOGLE_TTS_AUDIO_ENCODING", "MP3").upper()

    def list_voices(self, language_code: str | None = None, gender: str | None = None):
        """يجلب الأصوات المتاحة، يمكن فلترة language_code (مثل ar-XA) و gender (MALE/FEMALE/NEUTRAL)."""
        req = texttospeech.ListVoicesRequest(language_code=language_code or self.language)
        res = self.client.list_voices(request=req)

        gender = (gender or "").upper()
        allowed_gender = {"MALE", "FEMALE", "NEUTRAL"}

        out = []
        for v in res.voices:
            g = texttospeech.SsmlVoiceGender(v.ssml_gender).name
            if gender and gender in allowed_gender and g != gender:
                continue
            out.append(
                {
                    "voice_id": v.name,
                    "name": f"{v.name} — {g}",
                    "category": "google-tts",
                    "preview_url": "",
                    "labels": {
                        "language": ",".join(v.language_codes),
                        "gender": g,
                        "provider": "google",
                    },
                    "verified_languages": [],
                }
            )
        return out

    def synthesize(self, text: str, voice_id: str | None = None, language_code: str | None = None,
                  speaking_rate: float = 1.0, pitch: float = 0.0):
        if not text:
            raise RuntimeError("النص فارغ")

        voice_name = voice_id or self.default_voice
        if not voice_name:
            raise RuntimeError("لم يتم تحديد اسم صوت Google TTS (voice_id أو GOOGLE_TTS_VOICE_NAME)")

        lang = language_code or self.language

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(language_code=lang, name=voice_name)

        encoding_enum = getattr(texttospeech.AudioEncoding, self.default_encoding, texttospeech.AudioEncoding.MP3)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=encoding_enum,
            speaking_rate=speaking_rate,
            pitch=pitch,
        )

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )
        return response.audio_content
