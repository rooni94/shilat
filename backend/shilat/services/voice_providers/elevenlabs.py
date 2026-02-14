import os
import re
import requests
from django.conf import settings

_ARABIC_RE = re.compile(r"[\u0600-\u06FF]")


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def _is_arabic_voice(v: dict, include_verified: bool = False) -> bool:
    labels = v.get("labels") or {}
    name = v.get("name") or ""
    lang = _norm(labels.get("language") or labels.get("lang") or labels.get("locale") or "")
    accent = _norm(labels.get("accent") or labels.get("dialect") or labels.get("region") or "")
    desc = _norm(labels.get("description") or v.get("description") or "")

    if lang.startswith("ar") or "arab" in lang:
        return True
    if any(k in accent for k in ["saudi", "ksa", "najdi", "hijazi", "khaleeji", "khaliji", "gulf"]):
        return True
    if _ARABIC_RE.search(name):
        return True
    if any(k in desc for k in ["arab", "saudi", "najdi", "hijazi", "gulf", "khaliji", "khaleeji"]):
        return True

    if include_verified:
        verified = v.get("verified_languages") or []
        for item in verified:
            l = _norm(item.get("language") or "")
            locale = _norm(item.get("locale") or "")
            if l.startswith("ar") or "arab" in l:
                return True
            if locale.startswith("ar"):
                return True
    return False


def _match_dialect(v: dict, dialect: str | None) -> bool:
    if not dialect:
        return True
    dialect = _norm(dialect)
    labels = v.get("labels") or {}
    hay = " ".join([
        _norm(v.get("name") or ""),
        _norm(v.get("category") or ""),
        _norm(v.get("description") or ""),
        _norm(labels.get("accent") or ""),
        _norm(labels.get("dialect") or ""),
        _norm(labels.get("region") or ""),
        _norm(labels.get("description") or ""),
    ])

    buckets = {
        "najdi": ["najdi", "najd", "saudi", "ksa", "riyadh", "qassim"],
        "hijazi": ["hijazi", "hejaz", "jeddah", "makkah", "mecca", "medina", "taif"],
        "khaliji": ["gulf", "khaleeji", "khaliji", "emirati", "kuwait", "qatari", "bahrain", "omani", "uae"],
    }
    keys = buckets.get(dialect, [dialect])
    return any(k in hay for k in keys)


class ElevenLabsProvider:
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io"
        self.model_id = settings.ELEVENLABS_MODEL_ID

    def _headers(self, accept="application/json"):
        return {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": accept,
        }

    def _pick_preview(self, v: dict) -> str:
        if v.get("preview_url"):
            return v.get("preview_url")
        verified = v.get("verified_languages") or []
        for item in verified:
            l = _norm(item.get("language") or "")
            if l.startswith("ar") and item.get("preview_url"):
                return item.get("preview_url")
        for item in verified:
            if item.get("preview_url"):
                return item.get("preview_url")
        samples = v.get("samples") or []
        return (samples[0].get("sample_url") if samples else "") or ""

    def _list_voices_v2(self, params: dict, allow_fail: bool = False):
        url = f"{self.base_url}/v2/voices"
        voices = []
        next_token = None
        for _ in range(12):
            q = dict(params)
            if next_token:
                q["next_page_token"] = next_token
            r = requests.get(url, headers=self._headers(), params=q, timeout=30)
            try:
                r.raise_for_status()
            except requests.HTTPError:
                if allow_fail and r.status_code in (401, 402, 403):
                    return []
                raise
            data = r.json()
            voices.extend(data.get("voices", []))
            if not data.get("has_more") or not data.get("next_page_token"):
                break
            next_token = data.get("next_page_token")
        return voices

    def _search_library(self, language: str | None, page_size: int = 100, max_pages: int = 10):
        """Best-effort fetch of the public catalog (like the web UI)."""
        url = f"{self.base_url}/v1/voices/search"
        voices = []
        for page in range(1, max_pages + 1):
            params = {"page": page, "page_size": page_size}
            if language and language not in ("all", "any", ""):
                params["language"] = language
            r = requests.get(url, headers=self._headers(), params=params, timeout=30)
            if r.status_code in (401, 402, 403, 404):
                break
            r.raise_for_status()
            data = r.json() or {}
            batch = data.get("voices") or data.get("items") or []
            voices.extend(batch)
            if len(batch) < page_size:
                break
        return voices

    def list_voices(
        self,
        language: str = "ar",
        dialect: str | None = None,
        include_community: bool = True,
        include_verified: bool = False,
        include_catalog: bool = False,
    ):
        if not self.api_key:
            raise RuntimeError("ELEVENLABS_API_KEY غير موجود")

        all_voices = []
        seen = set()

        base_list = self._list_voices_v2({"page_size": 100}, allow_fail=False)
        for v in base_list:
            vid = v.get("voice_id")
            if vid and vid not in seen:
                seen.add(vid)
                all_voices.append(v)

        if include_community:
            comm_params = {"page_size": 100, "voice_type": "community"}
            if language and _norm(language).startswith("ar"):
                comm_params["search"] = "arabic"
            comm_list = self._list_voices_v2(comm_params, allow_fail=True)
            for v in comm_list:
                vid = v.get("voice_id")
                if vid and vid not in seen:
                    seen.add(vid)
                    all_voices.append(v)

        if include_catalog:
            cat_list = self._search_library(_norm(language))
            for v in cat_list:
                vid = v.get("voice_id")
                if vid and vid not in seen:
                    seen.add(vid)
                    all_voices.append(v)

        lang_norm = _norm(language)
        filter_ar = lang_norm.startswith("ar") and lang_norm not in ("", "all", "any")

        out = []
        for v in all_voices:
            item = {
                "voice_id": v.get("voice_id"),
                "name": v.get("name"),
                "category": v.get("category"),
                "preview_url": self._pick_preview(v),
                "labels": v.get("labels", {}) or {},
                "fine_tuning": v.get("fine_tuning") or {},
                "verified_languages": v.get("verified_languages") or [],
            }
            if filter_ar and not _is_arabic_voice(v, include_verified=include_verified):
                continue
            if dialect and filter_ar and not _match_dialect(item, dialect):
                continue
            out.append(item)
        return out

    def synthesize_shilat(self, job, pronunciation_dictionary_locators=None):
        if not self.api_key:
            raise RuntimeError("ELEVENLABS_API_KEY غير موجود في .env")

        voice_id = (os.getenv("ELEVENLABS_VOICE_ID") or settings.ELEVENLABS_VOICE_ID or "").strip()
        if not voice_id:
            voice_id = job.voice_actor

        text = (job.submission.cleaned_text or "").strip()
        if not text:
            raise RuntimeError("النص المنظف فارغ")

        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.35,
                "similarity_boost": 0.85,
                "style": 0.55,
                "use_speaker_boost": True,
            },
        }
        if pronunciation_dictionary_locators:
            payload["pronunciation_dictionary_locators"] = pronunciation_dictionary_locators

        url = f"{self.base_url}/v1/text-to-speech/{voice_id}"
        r = requests.post(url, json=payload, headers=self._headers(accept="audio/mpeg"), timeout=90)
        r.raise_for_status()
        return r.content
