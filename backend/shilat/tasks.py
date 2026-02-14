from celery import shared_task
from django.db import transaction
from shilat.models import VoiceConversionJob, GeneratedAudio
from django.conf import settings
from shilat.services.voice_providers.elevenlabs import ElevenLabsProvider
from shilat.services.voice_providers.google_tts import GoogleTTSProvider
from shilat.services.postprocess import post_process_audio
from shilat.services.dialect import apply_dialect_lexicon

@shared_task(bind=True, max_retries=1)
def generate_shilat_audio(self, job_id: str):
    job = VoiceConversionJob.objects.get(id=job_id)
    job.status = "running"
    job.save(update_fields=["status"])
    try:
        job.submission.cleaned_text = apply_dialect_lexicon(job.submission.cleaned_text, job.cultural_style.key)

        # If we will generate a full vocal track via Suno, skip TTS
        if job.music_provider == "suno_vocal":
            audio_bytes = b""
        elif job.voice_provider == "google":
            g = GoogleTTSProvider()
            audio_bytes = g.synthesize(
                job.submission.cleaned_text,
                voice_id=job.voice_actor or getattr(settings, "GOOGLE_TTS_VOICE_NAME", ""),
                language_code=getattr(settings, "GOOGLE_TTS_LANGUAGE", "ar-XA"),
            )
        else:
            provider = ElevenLabsProvider()
            audio_bytes = provider.synthesize_shilat(job, pronunciation_dictionary_locators=None)

        meta = post_process_audio(audio_bytes, job)

        with transaction.atomic():
            GeneratedAudio.objects.update_or_create(
                job=job,
                defaults={
                    "audio_file": meta["django_file"],
                    "format": meta.get("format","mp3"),
                    "duration_sec": meta.get("duration",0.0),
                    "meta_json": {k:v for k,v in meta.items() if k != "django_file"},
                }
            )
            job.status = "succeeded"
            job.save(update_fields=["status"])
        return True
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)
        job.save(update_fields=["status","error_message"])
        raise
