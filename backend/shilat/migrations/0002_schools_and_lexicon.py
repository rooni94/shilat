from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("shilat", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShilaSchool",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.SlugField(unique=True)),
                ("name_ar", models.CharField(max_length=64)),
                ("description_ar", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="DialectLexiconRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("dialect", models.CharField(choices=[("najdi","najdi"),("hijazi","hijazi"),("khaliji","khaliji")], max_length=16)),
                ("source", models.CharField(max_length=80)),
                ("alias", models.CharField(max_length=120)),
                ("notes", models.CharField(blank=True, max_length=200)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"unique_together": {("dialect","source")}},
        ),
        migrations.AddField(
            model_name="poemtextsubmission",
            name="meter_details",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="melodytemplate",
            name="school",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name="rhythms", to="shilat.shilaschool"),
        ),
    ]
