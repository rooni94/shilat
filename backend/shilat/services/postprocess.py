import io
import uuid
import requests
from django.core.files.base import ContentFile
from pydub import AudioSegment

def _download(url: str) -> bytes:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.content

def mix_voice_with_music(voice_mp3: bytes, music_mp3: bytes, music_volume_db: float = -10.0) -> bytes:
    voice = AudioSegment.from_file(io.BytesIO(voice_mp3), format="mp3")
    music = AudioSegment.from_file(io.BytesIO(music_mp3), format="mp3")

    if len(music) < len(voice):
        loops = (len(voice) // len(music)) + 1
        music = (music * loops)[:len(voice)]
    else:
        music = music[:len(voice)]

    music = music + float(music_volume_db)
    mixed = music.overlay(voice)

    out = io.BytesIO()
    mixed.export(out, format="mp3", bitrate="192k")
    return out.getvalue()

def post_process_audio(tts_audio_bytes: bytes, job):
    final_bytes = tts_audio_bytes
    meta = {"format": "mp3"}

    if getattr(job, "add_music", False) and getattr(job, "music_provider", "none") == "suno_vocal":
        try:
            from shilat.services.music_providers.sunoapi import SunoApiProvider
            provider = SunoApiProvider()

            school = job.melody.school.key if job.melody.school else "samri"
            style = "Gulf, Shilat, Vocal, Traditional"
            title = f"Shilat Vocal - {school}"
            lyrics = getattr(job.submission, "raw_text", "") or getattr(job.submission, "cleaned_text", "")

            task_id = provider.generate_vocal(lyrics=lyrics, style=style, title=title, model="V4_5ALL")
            job.music_task_id = task_id
            job.save(update_fields=["music_task_id"])

            audio_url = provider.wait_for_audio_url(task_id)
            job.music_audio_url = audio_url
            job.save(update_fields=["music_audio_url"])

            final_bytes = _download(audio_url)
            meta.update({"music_task_id": task_id, "music_audio_url": audio_url, "mode": "vocal"})
        except Exception as e:
            meta["music_error"] = str(e)

    elif getattr(job, "add_music", False) and getattr(job, "music_provider", "none") == "sunoapi":
        try:
            from shilat.services.music_providers.sunoapi import SunoApiProvider
            provider = SunoApiProvider()

            school = job.melody.school.key if job.melody.school else "samri"
            prompt = f"Traditional Saudi/Gulf percussion and instrumental bed for shilat. School: {school}. Rhythm: {job.melody.rhythm_key}. Tempo around {job.tempo} BPM."
            style = "Gulf, Traditional, Percussion, Shilat"
            title = f"Shilat Bed - {school}"

            task_id = provider.generate_instrumental(prompt=prompt, style=style, title=title, model="V4_5ALL")
            job.music_task_id = task_id
            job.save(update_fields=["music_task_id"])

            audio_url = provider.wait_for_audio_url(task_id)
            job.music_audio_url = audio_url
            job.save(update_fields=["music_audio_url"])

            music_bytes = _download(audio_url)
            final_bytes = mix_voice_with_music(tts_audio_bytes, music_bytes, getattr(job,"music_volume_db",-10.0))
            meta.update({"music_task_id": task_id, "music_audio_url": audio_url})
        except Exception as e:
            meta["music_error"] = str(e)

    # Try to infer format for duration/metadata
    fmt = "mp3"
    if getattr(job, "music_provider", "") == "suno_vocal" and getattr(job, "music_audio_url", ""):
        ext = job.music_audio_url.split("?")[0].split(".")[-1].lower()
        if ext in ("mp3", "m4a", "aac", "wav", "ogg"):
            fmt = ext
    try:
        duration = AudioSegment.from_file(io.BytesIO(final_bytes), format=fmt if fmt != "auto" else None).duration_seconds
    except Exception:
        duration = 0.0
    filename = f"{uuid.uuid4()}.{fmt if fmt!='auto' else 'mp3'}"
    django_file = ContentFile(final_bytes, name=filename)
    meta["duration"] = float(duration)
    meta["django_file"] = django_file
    return meta
