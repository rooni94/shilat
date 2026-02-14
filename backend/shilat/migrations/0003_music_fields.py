from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("shilat", "0002_schools_and_lexicon"),
    ]

    operations = [
        migrations.AddField(model_name="voiceconversionjob", name="add_music", field=models.BooleanField(default=False)),
        migrations.AddField(model_name="voiceconversionjob", name="music_provider", field=models.CharField(choices=[("none","none"),("sunoapi","sunoapi")], default="none", max_length=16)),
        migrations.AddField(model_name="voiceconversionjob", name="music_task_id", field=models.CharField(blank=True, max_length=128)),
        migrations.AddField(model_name="voiceconversionjob", name="music_audio_url", field=models.URLField(blank=True)),
        migrations.AddField(model_name="voiceconversionjob", name="music_volume_db", field=models.FloatField(default=-10.0)),
    ]
