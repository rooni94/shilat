import re
from dataclasses import dataclass
from .text_prep import strip_diacritics

AR_LETTERS = re.compile(r"[\u0621-\u064A]+")
PUNCT = re.compile(r"[\u060C\u061B\u061F\!\?\,\.;:…\-]+")
SPACES = re.compile(r"\s+")

LONG_VOWELS = set("اويآ")
HAMZA_FORMS = set("أإؤئء")

@dataclass
class MeterResult:
    bahr: str
    score: float
    pattern: str

BAHR_PATTERNS = {
    "tawil":   "--U--U--|--U--U--",
    "kamil":   "--U--U--|--U--U--",
    "basit":   "-U--U--|-U--U--",
    "mutaqarib":"-U--U--U--U--U-",
    "rajaz":   "-U--U--U--U-",
}

def _normalize(text: str) -> str:
    t = strip_diacritics(text)
    t = t.replace("أ","ا").replace("إ","ا").replace("آ","ا")
    t = t.replace("ى","ي")
    t = PUNCT.sub(" ", t)
    t = SPACES.sub(" ", t).strip()
    return t

def _syllable_pattern(line: str) -> str:
    tokens = []
    for w in line.split():
        m = AR_LETTERS.search(w)
        if not m:
            continue
        ww = m.group(0)
        for ch in ww:
            if ch in LONG_VOWELS:
                tokens.append("-")
            elif ch in HAMZA_FORMS:
                tokens.append("U")
            else:
                tokens.append("U")
    if not tokens:
        return ""
    compressed = []
    for i, x in enumerate(tokens):
        if i and x == "U" and tokens[i-1] == "U":
            if compressed and compressed[-1] == "U":
                compressed[-1] = "-"
            else:
                compressed.append("-")
        else:
            compressed.append(x)
    return "".join(compressed)[:48]

def _score(pattern: str, templ: str) -> float:
    t = templ.replace("|","")
    if not pattern or not t:
        return 0.0
    best = 0.0
    for start in range(0, max(1, len(pattern)-len(t)+1)):
        window = pattern[start:start+len(t)]
        matches = sum(1 for a,b in zip(window, t) if a==b)
        best = max(best, matches/len(t))
    if len(pattern) < len(t):
        matches = sum(1 for a,b in zip(pattern, t[:len(pattern)]) if a==b)
        best = max(best, matches/max(1,len(t)))
    return best

def detect_bahr(text: str):
    t = _normalize(text)
    lines = [x.strip() for x in t.split("\n") if x.strip()]
    if not lines:
        return ("", 0.0, {})

    sample = " ".join(lines[:2])
    pat = _syllable_pattern(sample)

    results = []
    for bahr, templ in BAHR_PATTERNS.items():
        results.append(MeterResult(bahr=bahr, score=_score(pat, templ), pattern=templ))
    results.sort(key=lambda x: x.score, reverse=True)
    best = results[0]
    gap = best.score - (results[1].score if len(results)>1 else 0.0)
    conf = max(0.0, min(0.98, best.score*0.75 + gap*0.35))
    details = {
        "sample_pattern": pat,
        "candidates": [{"bahr":r.bahr,"score":round(r.score,3),"template":r.pattern} for r in results[:5]],
    }
    return (best.bahr, float(round(conf,3)), details)
