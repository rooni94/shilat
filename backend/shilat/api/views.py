from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.conf import settings

from shilat.models import (
    PoemTextSubmission, MelodyTemplate, CulturalStyle, ShilaSchool,
    VoiceConversionJob, GeneratedAudio, DialectLexiconRule
)
from shilat.services.text_prep import clean_arabic_text
from shilat.services.meter import detect_bahr
from shilat.services.melody_engine import suggest_rhythms
from shilat.tasks import generate_shilat_audio
from shilat.services.voice_providers.elevenlabs import ElevenLabsProvider
from shilat.services.voice_providers.google_tts import GoogleTTSProvider

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_text(request):
    raw = (request.data.get("text") or "").strip()
    title = (request.data.get("title") or "").strip()
    if not raw:
        return Response({"detail": "النص مطلوب"}, status=400)

    cleaned = clean_arabic_text(raw)
    bahr, conf, details = detect_bahr(cleaned)

    sub = PoemTextSubmission.objects.create(
        user=request.user,
        title=title,
        raw_text=raw,
        cleaned_text=cleaned,
        meter_guess=bahr,
        meter_confidence=conf,
        meter_details=details,
    )

    suggestions = [s.__dict__ for s in suggest_rhythms(bahr)]
    return Response(
        {
            "id": str(sub.id),
            "meter_guess": bahr,
            "meter_confidence": conf,
            "meter_details": details,
            "suggested_rhythms": suggestions,
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(["GET"])
@permission_classes([AllowAny])
def rhythms(request):
    school = request.query_params.get("school")
    qs = MelodyTemplate.objects.select_related("school").all()
    if school:
        qs = qs.filter(school__key=school)
    data = []
    for r in qs:
        data.append(
            {
                "rhythm_key": r.rhythm_key,
                "name_ar": r.name_ar,
                "school_key": r.school.key if r.school else None,
                "school_name_ar": r.school.name_ar if r.school else "",
                "recommended_buhur": r.recommended_buhur,
                "pattern_json": r.pattern_json,
            }
        )
    return Response(data)

@api_view(["GET"])
@permission_classes([AllowAny])
def styles(request):
    qs = CulturalStyle.objects.all().values(
        "key", "name_ar", "description_ar", "default_tempo", "default_reverb"
    )
    return Response(list(qs))

@api_view(["GET"])
@permission_classes([AllowAny])
def schools(request):
    qs = ShilaSchool.objects.all().values("key", "name_ar", "description_ar")
    return Response(list(qs))

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def voices(request):
    provider_key = (request.query_params.get("provider") or "elevenlabs").strip().lower()
    lang = request.query_params.get("lang", getattr(settings, "GOOGLE_TTS_LANGUAGE", "ar"))
    dialect = request.query_params.get("dialect")
    scope = (request.query_params.get("scope") or "all").strip().lower()
    include_community = scope in ("all", "community", "public")
    support = (request.query_params.get("support") or "0").strip().lower()
    include_verified = support in ("1", "true", "yes", "y")
    catalog = (request.query_params.get("catalog") or "0").strip().lower() in ("1", "true", "yes", "y")
    gender = (request.query_params.get("gender") or "").strip()
    lang_norm = (lang or "").strip().lower()
    if not lang_norm.startswith("ar"):
        dialect = None
    if provider_key == "google":
        provider = GoogleTTSProvider()
        return Response(provider.list_voices(language_code=lang, gender=gender))
    provider = ElevenLabsProvider()
    return Response(
        provider.list_voices(
            language=lang,
            dialect=dialect,
            include_community=include_community,
            include_verified=include_verified,
            include_catalog=catalog,
        )
    )

@api_view(["GET"])
@permission_classes([AllowAny])
def lexicon(request):
    dialect = request.query_params.get("dialect")
    qs = DialectLexiconRule.objects.filter(is_active=True)
    if dialect:
        qs = qs.filter(dialect=dialect)
    return Response(list(qs.values("dialect", "source", "alias", "notes")))

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate(request):
    submission_id = request.data.get("submission_id")
    style_key = request.data.get("style_key")
    rhythm_key = request.data.get("rhythm_key")

    if not all([submission_id, style_key, rhythm_key]):
        return Response({"detail": "submission_id و style_key و rhythm_key مطلوبة"}, status=400)

    style = get_object_or_404(CulturalStyle, key=style_key)
    melody = get_object_or_404(MelodyTemplate, rhythm_key=rhythm_key)
    sub = get_object_or_404(PoemTextSubmission, id=submission_id, user=request.user)

    voice_actor = (request.data.get("voice_actor") or "male_01").strip()
    voice_provider = (request.data.get("voice_provider") or "elevenlabs").strip().lower()
    add_music = bool(request.data.get("add_music", False))
    music_provider = (request.data.get("music_provider") or ("sunoapi" if add_music else "none")).strip()[:16]
    music_volume_db = float(request.data.get("music_volume_db", -10.0))

    job = VoiceConversionJob.objects.create(
        submission=sub,
        cultural_style=style,
        melody=melody,
        voice_actor=voice_actor,
        voice_provider=voice_provider,
        vocal_mode=request.data.get("vocal_mode", "حماسي"),
        tempo=int(request.data.get("tempo", style.default_tempo)),
        pitch=float(request.data.get("pitch", 0.0)),
        intensity=float(request.data.get("intensity", 0.7)),
        add_percussion=bool(request.data.get("add_percussion", True)),
        intro_adhan_style=bool(request.data.get("intro_adhan_style", False)),
        add_music=add_music,
        music_provider=music_provider if add_music else "none",
        music_volume_db=music_volume_db,
        status="queued",
    )

    generate_shilat_audio.delay(str(job.id))
    return Response({"job_id": str(job.id)}, status=202)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def job_status(request, job_id):
    job = get_object_or_404(VoiceConversionJob, id=job_id, submission__user=request.user)
    audio_exists = GeneratedAudio.objects.filter(job=job).exists()
    return Response(
        {
            "job_id": str(job.id),
            "status": job.status,
            "error_message": job.error_message,
            "has_audio": audio_exists,
            "add_music": job.add_music,
            "music_provider": job.music_provider,
            "music_task_id": job.music_task_id,
            "music_audio_url": job.music_audio_url,
        }
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_audio(request, job_id):
    job = get_object_or_404(VoiceConversionJob, id=job_id, submission__user=request.user)
    try:
        audio = GeneratedAudio.objects.get(job=job)
    except GeneratedAudio.DoesNotExist:
        raise Http404("الصوت غير جاهز بعد")
    return FileResponse(audio.audio_file.open("rb"), as_attachment=True, filename=f"shilat-{job_id}.mp3")
