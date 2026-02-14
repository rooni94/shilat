from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret")
DEBUG = os.getenv("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS","localhost").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin","django.contrib.auth","django.contrib.contenttypes",
    "django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles",
    "corsheaders","rest_framework","rest_framework.authtoken",
    "accounts","shilat",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [{
    "BACKEND":"django.template.backends.django.DjangoTemplates",
    "DIRS":[],
    "APP_DIRS":True,
    "OPTIONS":{"context_processors":[
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

WSGI_APPLICATION = "app.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB","shilat"),
        "USER": os.getenv("POSTGRES_USER","shilat"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD","shilatpass"),
        "HOST": os.getenv("POSTGRES_HOST","db"),
        "PORT": os.getenv("POSTGRES_PORT","5432"),
        "CONN_MAX_AGE": 60,
    }
}

LANGUAGE_CODE = "ar-sa"
TIME_ZONE = "Asia/Riyadh"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = [o.strip() for o in os.getenv("DJANGO_CORS_ALLOWED_ORIGINS","").split(",") if o.strip()]
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticatedOrReadOnly"],
}

CELERY_BROKER_URL = os.getenv("REDIS_URL","redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL","redis://redis:6379/0")
CELERY_TASK_TIME_LIMIT = 120

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY","")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID","")
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID","eleven_multilingual_v2")
GOOGLE_TTS_API_KEY = os.getenv("GOOGLE_TTS_API_KEY","")
GOOGLE_TTS_LANGUAGE = os.getenv("GOOGLE_TTS_LANGUAGE","ar-XA")
GOOGLE_TTS_VOICE_NAME = os.getenv("GOOGLE_TTS_VOICE_NAME","")
GOOGLE_TTS_AUDIO_ENCODING = os.getenv("GOOGLE_TTS_AUDIO_ENCODING","MP3")

# SunoAPI.org (Third-party) token for AI music generation
SUNOAPI_TOKEN = os.getenv('SUNOAPI_TOKEN', '')
