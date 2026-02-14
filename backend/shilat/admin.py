from django.contrib import admin
from .models import (
    CulturalStyle, ShilaSchool, DialectLexiconRule,
    MelodyTemplate, PoemTextSubmission, VoiceConversionJob, GeneratedAudio
)
admin.site.register(CulturalStyle)
admin.site.register(ShilaSchool)
admin.site.register(DialectLexiconRule)
admin.site.register(MelodyTemplate)
admin.site.register(PoemTextSubmission)
admin.site.register(VoiceConversionJob)
admin.site.register(GeneratedAudio)
