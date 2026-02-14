from django.core.management.base import BaseCommand
from shilat.models import CulturalStyle, ShilaSchool, MelodyTemplate, DialectLexiconRule

class Command(BaseCommand):
    help = "Seed cultural styles, Shilat schools, rhythms, and dialect lexicon rules."

    def handle(self, *args, **kwargs):
        styles = [
            ("najdi","نجدي","أسلوب نجدي تقليدي للشيلات.", 96, 0.22),
            ("hijazi","حجازي","لمسة حجازية وإلقاء أنعم.", 98, 0.25),
            ("khaliji","خليجي","طابع خليجي عام.", 100, 0.26),
        ]
        for key, name, desc, tempo, rev in styles:
            CulturalStyle.objects.update_or_create(
                key=key,
                defaults={"name_ar":name,"description_ar":desc,"default_tempo":tempo,"default_reverb":rev},
            )

        schools = [
            ("ardah","العرضة","مدرسة العرضة السعودية (حماسية/حربية)."),
            ("samri","السامري","السامري النجدي (مناسب للقصائد والغزل)."),
            ("dahha","الدحة","الدحة الشمالية (مقاطع قصيرة + ترديد)."),
            ("ghazal","غزل","شيلات الغزل/العاطفة (أهدأ)."),
            ("mawal","موال","موال حر (تمطيط وزخارف)."),
        ]
        school_map = {}
        for key, name, desc in schools:
            obj, _ = ShilaSchool.objects.update_or_create(
                key=key, defaults={"name_ar":name,"description_ar":desc}
            )
            school_map[key] = obj

        rhythms = [
            ("ardah_main","العرضة (رئيسي)", "ardah", ["kamil","tawil"], {"time_signature":"4/4","phrase_beats":16,"hits":[1,0,1,0,1,1,0,1],"accent":[1,0,0,0,0,1,0,1]}),
            ("samri","السامري", "samri", ["tawil","kamil","basit"], {"time_signature":"2/4","phrase_beats":16,"hits":[1,0,1,0],"accent":[1,0,0,1]}),
            ("khammari","الخماري", "samri", ["tawil","basit","rajaz"], {"time_signature":"4/4","phrase_beats":16,"hits":[1,0,0,1,1,0,1,0],"accent":[1,0,0,0,0,1,0,1]}),
            ("dahha","الدحة", "dahha", ["mutaqarib","rajaz"], {"time_signature":"2/4","phrase_beats":8,"hits":[1,1,0,1],"accent":[1,0,0,1]}),
            ("modih","مديح", "ghazal", ["kamil","basit"], {"time_signature":"4/4","phrase_beats":16,"hits":[1,0,0,0,1,0,1,0],"accent":[1,0,0,0,0,1,0,0]}),
            ("hamasi","حماسي", "ardah", ["mutaqarib","rajaz"], {"time_signature":"2/4","phrase_beats":8,"hits":[1,1,1,0],"accent":[1,0,1,0]}),
            ("atifi","عاطفي", "ghazal", ["tawil","kamil"], {"time_signature":"4/4","phrase_beats":16,"hits":[1,0,0,1,0,1,0,0],"accent":[1,0,0,0,0,1,0,0]}),
            ("mawal","موال", "mawal", ["tawil","kamil"], {"time_signature":"free","phrase_beats":0,"hits":[],"accent":[]}),
        ]
        for key, name, school_key, buhur, pattern in rhythms:
            MelodyTemplate.objects.update_or_create(
                rhythm_key=key,
                defaults={
                    "name_ar":name,
                    "school": school_map[school_key],
                    "recommended_buhur":buhur,
                    "pattern_json":pattern,
                },
            )

        rules = [
            ("najdi","وش","وِش","تقريب نطق"),
            ("najdi","تكفى","تِكفا","تخفيف/تقريب"),
            ("najdi","هالحين","هالحِيْن","تمديد"),
            ("hijazi","فين","فِين","مدّ"),
            ("khaliji","شلونك","شِلونِك","تطبيع"),
        ]
        for dialect, src, alias, notes in rules:
            DialectLexiconRule.objects.update_or_create(
                dialect=dialect, source=src,
                defaults={"alias":alias,"notes":notes,"is_active":True},
            )

        self.stdout.write(self.style.SUCCESS("Seeded styles, schools, rhythms, and lexicon rules."))
