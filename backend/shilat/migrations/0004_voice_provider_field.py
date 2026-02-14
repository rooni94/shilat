from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shilat", "0003_music_fields"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="ALTER TABLE shilat_voiceconversionjob ADD COLUMN IF NOT EXISTS voice_provider varchar(16) NOT NULL DEFAULT 'elevenlabs';",
                    reverse_sql="ALTER TABLE shilat_voiceconversionjob DROP COLUMN IF EXISTS voice_provider;",
                )
            ],
            state_operations=[
                migrations.AddField(
                    model_name="voiceconversionjob",
                    name="voice_provider",
                    field=models.CharField(
                        choices=[("elevenlabs", "elevenlabs"), ("google", "google")],
                        default="elevenlabs",
                        max_length=16,
                    ),
                ),
            ],
        ),
    ]

