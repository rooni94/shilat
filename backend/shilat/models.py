from django.conf import settings
from django.db import models
import uuid

class CulturalStyle(models.Model):
    key = models.SlugField(unique=True)
    name_ar = models.CharField(max_length=64)
    description_ar = models.TextField(blank=True)
    default_tempo = models.PositiveIntegerField(default=96)
    default_reverb = models.FloatField(default=0.25)

class ShilaSchool(models.Model):
    """مدرسة/فن شيلات (عرضة، سامري، دحة، غزل... إلخ)."""
    key = models.SlugField(unique=True)
    name_ar = models.CharField(max_length=64)
    description_ar = models.TextField(blank=True)

class DialectLexiconRule(models.Model):
    """قواعد نطق (Alias) للهجة — لتحسين نطق كلمات محددة."""
    DIALECT_CHOICES = [("najdi","najdi"),("hijazi","hijazi"),("khaliji","khaliji")]
    dialect = models.CharField(max_length=16, choices=DIALECT_CHOICES)
    source = models.CharField(max_length=80)
    alias = models.CharField(max_length=120)
    notes = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("dialect","source")]

class MelodyTemplate(models.Model):
    rhythm_key = models.SlugField(unique=True)
    school = models.ForeignKey(ShilaSchool, on_delete=models.PROTECT, related_name="rhythms", null=True)
    name_ar = models.CharField(max_length=64)
    pattern_json = models.JSONField()
    recommended_buhur = models.JSONField(default=list)

class PoemTextSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=120, blank=True)
    raw_text = models.TextField()
    cleaned_text = models.TextField(blank=True)
    meter_guess = models.CharField(max_length=32, blank=True)
    meter_confidence = models.FloatField(default=0.0)
    meter_details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class VoiceConversionJob(models.Model):
    STATUS = [("queued","queued"),("running","running"),("succeeded","succeeded"),("failed","failed")]
    MUSIC_PROVIDERS = [("none","none"),("sunoapi","sunoapi"),("suno_vocal","suno_vocal")]
    VOICE_PROVIDERS = [("elevenlabs","elevenlabs"),("google","google")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(PoemTextSubmission, on_delete=models.CASCADE)
    cultural_style = models.ForeignKey(CulturalStyle, on_delete=models.PROTECT)
    melody = models.ForeignKey(MelodyTemplate, on_delete=models.PROTECT)

    voice_actor = models.CharField(max_length=64, default="male_01")
    voice_provider = models.CharField(max_length=16, choices=VOICE_PROVIDERS, default="elevenlabs")
    vocal_mode = models.CharField(max_length=32, default="حماسي")

    tempo = models.PositiveIntegerField(default=96)
    pitch = models.FloatField(default=0.0)
    intensity = models.FloatField(default=0.7)
    add_percussion = models.BooleanField(default=True)
    intro_adhan_style = models.BooleanField(default=False)

    # Music add-on
    add_music = models.BooleanField(default=False)
    music_provider = models.CharField(max_length=16, choices=MUSIC_PROVIDERS, default="none")
    music_task_id = models.CharField(max_length=128, blank=True)
    music_audio_url = models.URLField(blank=True)
    music_volume_db = models.FloatField(default=-10.0)

    provider_job_id = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=16, choices=STATUS, default="queued")
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class GeneratedAudio(models.Model):
    job = models.OneToOneField(VoiceConversionJob, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to="generated/")
    format = models.CharField(max_length=8, default="mp3")
    duration_sec = models.FloatField(default=0.0)
    meta_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
