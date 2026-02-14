from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shilat", "0004_voice_provider_field"),
    ]

    operations = [
        migrations.AlterField(
            model_name="voiceconversionjob",
            name="music_provider",
            field=models.CharField(
                choices=[("none", "none"), ("sunoapi", "sunoapi"), ("suno_vocal", "suno_vocal")],
                default="none",
                max_length=16,
            ),
        ),
    ]
