from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.conf import settings

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="CulturalStyle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.SlugField(unique=True)),
                ("name_ar", models.CharField(max_length=64)),
                ("description_ar", models.TextField(blank=True)),
                ("default_tempo", models.PositiveIntegerField(default=96)),
                ("default_reverb", models.FloatField(default=0.25)),
            ],
        ),
        migrations.CreateModel(
            name="MelodyTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rhythm_key", models.SlugField(unique=True)),
                ("name_ar", models.CharField(max_length=64)),
                ("pattern_json", models.JSONField()),
                ("recommended_buhur", models.JSONField(default=list)),
            ],
        ),
        migrations.CreateModel(
            name="PoemTextSubmission",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("title", models.CharField(max_length=120, blank=True)),
                ("raw_text", models.TextField()),
                ("cleaned_text", models.TextField(blank=True)),
                ("meter_guess", models.CharField(max_length=32, blank=True)),
                ("meter_confidence", models.FloatField(default=0.0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="VoiceConversionJob",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("voice_actor", models.CharField(default="male_01", max_length=64)),
                ("vocal_mode", models.CharField(default="حماسي", max_length=32)),
                ("tempo", models.PositiveIntegerField(default=96)),
                ("pitch", models.FloatField(default=0.0)),
                ("intensity", models.FloatField(default=0.7)),
                ("add_percussion", models.BooleanField(default=True)),
                ("intro_adhan_style", models.BooleanField(default=False)),
                ("provider_job_id", models.CharField(blank=True, max_length=128)),
                ("status", models.CharField(choices=[("queued","queued"),("running","running"),("succeeded","succeeded"),("failed","failed")], default="queued", max_length=16)),
                ("error_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("cultural_style", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="shilat.culturalstyle")),
                ("melody", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="shilat.melodytemplate")),
                ("submission", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="shilat.poemtextsubmission")),
            ],
        ),
        migrations.CreateModel(
            name="GeneratedAudio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("audio_file", models.FileField(upload_to="generated/")),
                ("format", models.CharField(default="mp3", max_length=8)),
                ("duration_sec", models.FloatField(default=0.0)),
                ("meta_json", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("job", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="shilat.voiceconversionjob")),
            ],
        ),
    ]
