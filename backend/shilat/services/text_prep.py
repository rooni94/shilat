import re
_ARABIC_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
_TATWEEL = "\u0640"

def clean_arabic_text(text: str) -> str:
    text = text.replace(_TATWEEL, "")
    text = re.sub(r"[\u200f\u200e]", "", text)
    text = text.replace("أ","ا").replace("إ","ا").replace("آ","ا")
    text = text.replace("ى","ي")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def strip_diacritics(text: str) -> str:
    return _ARABIC_DIACRITICS.sub("", text)
