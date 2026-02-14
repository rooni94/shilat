# Shilat App
منصة لتحويل القصائد العربية إلى شيلات صوتية عبر:
- تحليل النص العربي وتنظيفه.
- تخمين البحر واقتراح الإيقاع المناسب.
- توليد صوت (TTS) عبر `ElevenLabs` أو `Google TTS`.
- المعالجة اللاحقة ودمج الإيقاع/الموسيقى (اختياري).
- تشغيل غير متزامن للمهام باستخدام `Celery + Redis`.

## المزايا
- واجهة React (Vite + TypeScript + Tailwind).
- Backend بـ Django REST Framework.
- قواعد بيانات PostgreSQL.
- Queue Worker بـ Celery.
- دعم مدارس الشيلات (عرضة، سامري، دحة، غزل، موال).
- قاموس تحسين نطق للهجات (`najdi`, `hijazi`, `khaliji`).
- خيار إضافة موسيقى عبر `SunoAPI` (اختياري).

## المعمارية
- `frontend/`: واجهة المستخدم.
- `backend/`: API + منطق الأعمال + المهام.
- `deploy/nginx/`: عكس التوجيه (Reverse Proxy).
- `deploy/postgres-init/`: سكربتات تهيئة PostgreSQL.
- `deploy/creds/`: ملفات اعتماد مزودات خارجية (لا يجب رفعها).

تدفق العمل:
1. المستخدم يسجل الدخول من الواجهة.
2. يرسل النص إلى `/api/submit-text/`.
3. يختار النمط/المدرسة/الإيقاع/الصوت.
4. يبدأ التوليد عبر `/api/generate/`.
5. الـ Worker ينفذ المهمة ويخزن الناتج.
6. الواجهة تتابع الحالة من `/api/job-status/<id>/` ثم التنزيل من `/api/download/<id>/`.

## المتطلبات
- Docker + Docker Compose.
- أو (بدون Docker): Python 3.11، Node 20، PostgreSQL 16، Redis 7، FFmpeg.

## التشغيل السريع (Docker)
```bash
cp .env.example .env
docker compose up --build
```

الروابط:
- التطبيق: `http://localhost:8080`
- API: `http://localhost:8080/api/`
- Django Admin: `http://localhost:8080/admin/`

## إنشاء مستخدم إداري
بعد تشغيل الحاويات:
```bash
docker compose exec backend python manage.py createsuperuser
```

ثم استخدم نفس الحساب في شاشة تسجيل الدخول داخل الواجهة.

## تشغيل واختبار (بدون Docker)
### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_rhythms
python manage.py runserver 0.0.0.0:8000
```

### Celery Worker
```bash
cd backend
celery -A app.celery_app worker -l info --concurrency=2
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

> عند التشغيل المحلي بدون Nginx، تأكد أن `VITE_API_BASE` يشير إلى عنوان الـ API الصحيح.

## متغيرات البيئة
انسخ من `.env.example` ثم عدّل القيم:

### Django
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG` (`1` أو `0`)
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CORS_ALLOWED_ORIGINS`

### PostgreSQL
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

### Redis / Celery
- `REDIS_URL`

### مزودات الصوت
- `ELEVENLABS_API_KEY`
- `ELEVENLABS_VOICE_ID` (اختياري)
- `ELEVENLABS_MODEL_ID`
- `GOOGLE_APPLICATION_CREDENTIALS`
- `GOOGLE_TTS_API_KEY` (اختياري عند استخدام Service Account)
- `GOOGLE_TTS_LANGUAGE`
- `GOOGLE_TTS_VOICE_NAME`
- `GOOGLE_TTS_AUDIO_ENCODING`

### الموسيقى (اختياري)
- `SUNOAPI_TOKEN`

## API الأساسية
### المصادقة
- `POST /api/auth/token/` للحصول على Token.
- `GET /api/auth/me/` معلومات المستخدم الحالي (يتطلب Token).

### المحتوى
- `GET /api/styles/`
- `GET /api/schools/`
- `GET /api/rhythms/?school=<key>`
- `GET /api/lexicon/?dialect=<najdi|hijazi|khaliji>`

### التحويل
- `POST /api/submit-text/` (يتطلب Token)
- `GET /api/voices/` (يتطلب Token)
- `POST /api/generate/` (يتطلب Token)
- `GET /api/job-status/<uuid>/` (يتطلب Token)
- `GET /api/download/<uuid>/` (يتطلب Token)

## بيانات أولية (Seed)
أمر `seed_rhythms` يضيف:
- الأنماط الثقافية.
- مدارس الشيلات.
- قوالب الإيقاع.
- قواعد قاموس اللهجات.

تشغيله:
```bash
docker compose exec backend python manage.py seed_rhythms
```

## الاختبارات
اختبار مبدئي لاكتشاف البحر موجود في:
- `backend/shilat/tests/test_meter.py`

تشغيل الاختبارات:
```bash
docker compose exec backend python manage.py test
```

## ملاحظات أمنية مهمة
- لا ترفع أبدًا أي ملف مفاتيح أو أسرار (مثل `.env` أو مفاتيح Google Service Account).
- إذا تم رفع مفتاح فعلي سابقًا إلى GitHub، يجب تدويره (Rotate/Revoke) فورًا من مزود الخدمة.
- ملف اعتماد Google يجب أن يكون خارج المستودع أو مضافًا إلى `.gitignore`.

## المساءلة القانونية عند الاستخدام التجاري
- باستخدام هذا المشروع تجاريًا، تقع المسؤولية القانونية الكاملة على الجهة المشغلة للخدمة.
- يجب الالتزام بحقوق الملكية الفكرية للنصوص، والأصوات، والمخرجات الصوتية، وأي مواد يتم رفعها أو توليدها.
- يجب الالتزام بشروط استخدام مزودي الخدمات الخارجية مثل `ElevenLabs` و`Google Cloud` و`SunoAPI`، بما في ذلك التراخيص، وسياسات المحتوى، وحدود الاستخدام.
- يجب الحصول على الموافقات النظامية اللازمة قبل استنساخ/تقليد الأصوات أو استخدام أي مواد محمية.
- يمنع استخدام المشروع في أي نشاط غير نظامي، أو ينتهك الخصوصية، أو يتضمن انتحال الهوية أو التضليل.
- يجب على الجهة المشغلة تطبيق سياسة خصوصية وشروط استخدام واضحة للمستخدمين النهائيين، والالتزام بقوانين حماية البيانات المعمول بها في نطاق عملها.
- مطورو المشروع لا يتحملون أي مسؤولية مباشرة أو غير مباشرة عن أي مطالبات، أضرار، خسائر، أو مخالفات ناتجة عن الاستخدام التجاري.
- هذا القسم لأغراض تنظيمية عامة ولا يُعد استشارة قانونية. عند الإطلاق التجاري الفعلي، يجب مراجعة مستشار قانوني مختص.

## استكشاف الأخطاء
- `401 Unauthorized`:
  تأكد من تسجيل الدخول وتخزين `Token` في الواجهة.
- فشل جلب الأصوات:
  تحقق من `ELEVENLABS_API_KEY` أو إعداد Google TTS.
- المهام لا تكتمل:
  تحقق من حالة `worker` و `redis`:
  ```bash
  docker compose ps
  docker compose logs -f worker
  ```
- فشل مزج الصوت:
  تأكد من توفر `ffmpeg` داخل بيئة التنفيذ.

## ملفات مهمة
- إعداد Docker: `docker-compose.yml`
- إعداد Django: `backend/app/settings.py`
- API: `backend/shilat/api/views.py`
- مهام Celery: `backend/shilat/tasks.py`
- واجهة التحويل: `frontend/src/pages/Convert.tsx`
