import re
from shilat.models import DialectLexiconRule

_word_re = re.compile(r"[\w\u0600-\u06FF]+")

def apply_dialect_lexicon(text: str, dialect: str) -> str:
    rules = DialectLexiconRule.objects.filter(dialect=dialect, is_active=True).values_list("source","alias")
    if not rules:
        return text
    mapping = {src:alias for src,alias in rules}
    def repl(m):
        w = m.group(0)
        return mapping.get(w, w)
    return _word_re.sub(repl, text)
