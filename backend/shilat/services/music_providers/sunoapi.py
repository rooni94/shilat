import time
import requests
from django.conf import settings

class SunoApiProvider:
    """Third-party provider for music generation via api.sunoapi.org (not official Suno API)."""

    def __init__(self):
        self.token = getattr(settings, "SUNOAPI_TOKEN", "") or ""
        self.base_url = "https://api.sunoapi.org/api/v1"

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    def generate_instrumental(self, prompt: str, style: str, title: str, model: str = "V4_5ALL") -> str:
        if not self.token:
            raise RuntimeError("SUNOAPI_TOKEN is missing")
        url = f"{self.base_url}/generate"
        payload = {"customMode": True, "instrumental": True, "model": model, "callBackUrl": "https://example.invalid/cb",
                   "prompt": prompt or "", "style": style, "title": title}
        r = requests.post(url, json=payload, headers=self._headers(), timeout=60)
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 200:
            raise RuntimeError(f"SunoAPI error: {data}")
        return data["data"]["taskId"]

    def generate_vocal(self, lyrics: str, style: str, title: str, model: str = "V4_5ALL") -> str:
        """Generate full vocal+music (singing) track."""
        if not self.token:
            raise RuntimeError("SUNOAPI_TOKEN is missing")
        url = f"{self.base_url}/generate"
        payload = {
            "customMode": True,
            "instrumental": False,  # request vocal track
            "lyrics": lyrics or "",
            "prompt": lyrics or "",
            "style": style,
            "title": title,
            "model": model,
            "callBackUrl": "https://example.invalid/cb",
        }
        r = requests.post(url, json=payload, headers=self._headers(), timeout=60)
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 200:
            raise RuntimeError(f"SunoAPI error: {data}")
        return data["data"]["taskId"]

    def get_details(self, task_id: str) -> dict:
        url = f"{self.base_url}/generate/record-info"
        r = requests.get(url, headers=self._headers(), params={"taskId": task_id}, timeout=60)
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 200:
            raise RuntimeError(f"SunoAPI details error: {data}")
        return data.get("data") or {}

    def wait_for_audio_url(self, task_id: str, timeout_sec: int = 240, poll_sec: float = 4.0) -> str:
        t0 = time.time()
        last_status = None
        while time.time() - t0 < timeout_sec:
            info = self.get_details(task_id)
            last_status = info.get("status")
            if last_status == "SUCCESS":
                resp = (info.get("response") or {})
                suno = (resp.get("sunoData") or [])
                if suno and suno[0].get("audioUrl"):
                    return suno[0]["audioUrl"]
            time.sleep(poll_sec)
        raise RuntimeError(f"SunoAPI timeout last_status={last_status}")
