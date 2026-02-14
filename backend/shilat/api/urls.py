from django.urls import path
from .views import (
    submit_text, rhythms, styles, schools, voices, lexicon,
    generate, job_status, download_audio
)

urlpatterns = [
    path("submit-text/", submit_text),
    path("rhythms/", rhythms),
    path("styles/", styles),
    path("schools/", schools),
    path("voices/", voices),
    path("lexicon/", lexicon),
    path("generate/", generate),
    path("job-status/<uuid:job_id>/", job_status),
    path("download/<uuid:job_id>/", download_audio),
]
