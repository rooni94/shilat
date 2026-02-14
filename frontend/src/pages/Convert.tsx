import React, { useEffect, useMemo, useState } from "react";
import api, { setToken } from "../lib/api";
import RhythmPreview from "../components/RhythmPreview";

type Style = { key: string; name_ar: string; description_ar: string; default_tempo: number };
type School = { key: string; name_ar: string; description_ar: string };
type Rhythm = { rhythm_key: string; name_ar: string; school_key: string; school_name_ar: string; recommended_buhur: string[]; pattern_json: any };
type Voice = { voice_id: string; name: string; category: string; preview_url?: string; labels?: Record<string,string> };

export default function Convert() {
  const [step, setStep] = useState<1|2|3>(1);
  const [text, setText] = useState("يا مرحبا يا دارنا يا عزنا\nيا شيلةٍ في خاطري تنكتب\n");
  const [title, setTitle] = useState("قصيدة تجريبية");

  const [submissionId, setSubmissionId] = useState<string | null>(null);
  const [meter, setMeter] = useState<string>("");
  const [conf, setConf] = useState<number>(0);
  const [meterDetails, setMeterDetails] = useState<any>(null);

  const [styles, setStyles] = useState<Style[]>([]);
  const [schools, setSchools] = useState<School[]>([]);
  const [rhythms, setRhythms] = useState<Rhythm[]>([]);
  const [voices, setVoices] = useState<Voice[]>([]);

  const [styleKey, setStyleKey] = useState("najdi");
  const [schoolKey, setSchoolKey] = useState("samri");
  const [rhythmKey, setRhythmKey] = useState("samri");

  const [tempo, setTempo] = useState(96);
  const [voiceId, setVoiceId] = useState<string>("");
  const [voiceProvider, setVoiceProvider] = useState<"elevenlabs"|"google">("elevenlabs");
  const [voiceDialect, setVoiceDialect] = useState<""|"najdi"|"hijazi"|"khaliji">("");
  const [supportArabic, setSupportArabic] = useState(true);
  const [showAllVoices, setShowAllVoices] = useState(false);
  const [mode, setMode] = useState<"مديح"|"حماسي"|"عاطفي">("حماسي");
  const [addPerc, setAddPerc] = useState(true);

  // Music (SunoAPI.org)
  const [addMusic, setAddMusic] = useState(false);
  const [musicProvider, setMusicProvider] = useState<"sunoapi"|"suno_vocal">("sunoapi");
  const [musicVolume, setMusicVolume] = useState(-10);

  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<string>("");
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loadingBase, setLoadingBase] = useState<boolean>(false);

  const loadBaseData = async () => {
    setLoadingBase(true);
    setErr(null);
    try{
      const [s, sc, r] = await Promise.all([api.get("/styles/"), api.get("/schools/"), api.get("/rhythms/")]);
      setStyles(s.data || []);
      setSchools(sc.data || []);
      setRhythms(r.data || []);
      const st = (s.data || []).find((x:Style)=>x.key===styleKey);
      if (st) setTempo(st.default_tempo);
    }catch{
      setErr("تعذر جلب بيانات الأنماط/المدارس/الإيقاعات. اضغط إعادة المحاولة بعد اكتمال تشغيل السيرفر.");
    }finally{
      setLoadingBase(false);
    }
  };

  useEffect(() => {
    const t = localStorage.getItem("token");
    if (t) setToken(t);
    loadBaseData();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const rhythm = useMemo(()=> rhythms.find(r=>r.rhythm_key===rhythmKey) ?? null, [rhythms, rhythmKey]);

  const loadVoices = async () => {
    setErr(null);
    try{
      const q = new URLSearchParams({ scope: "all", provider: voiceProvider });
      if (voiceProvider === "elevenlabs") {
        if (showAllVoices) {
          q.set("lang", "all");
          q.set("catalog", "1");
          q.set("support", "1");
        } else {
          q.set("lang", "ar");
          if (voiceDialect) q.set("dialect", voiceDialect);
          if (supportArabic) q.set("support", "1");
        }
      } else {
        q.set("lang", showAllVoices ? "all" : "ar");
      }
      const res = await api.get(`/voices/?${q.toString()}`);
      setVoices(res.data);
      if (!voiceId && res.data?.length) setVoiceId(res.data[0].voice_id);
    }catch{
      setErr("تعذر جلب الأصوات. تأكد من تسجيل دخولك + مفاتيح المزود.");
    }
  };

  const submitText = async () => {
    setErr(null);
    try{
      const res = await api.post("/submit-text/", { text, title });
      setSubmissionId(res.data.id);
      setMeter(res.data.meter_guess);
      setConf(res.data.meter_confidence);
      setMeterDetails(res.data.meter_details);
      if (res.data.suggested_rhythms?.length) setRhythmKey(res.data.suggested_rhythms[0].rhythm_key);
      setStep(2);
    }catch{
      setErr("تأكد من تسجيل الدخول أولاً.");
    }
  };

  const startGenerate = async () => {
    setErr(null);
    setDownloadUrl(null);
    setAudioUrl(null);
    try{
      const res = await api.post("/generate/", {
        submission_id: submissionId,
        style_key: styleKey,
        rhythm_key: rhythmKey,
        voice_actor: voiceId || "male_01",
        voice_provider: voiceProvider,
        vocal_mode: mode,
        tempo,
        add_percussion: addPerc,
        add_music: addMusic,
        music_provider: addMusic ? musicProvider : "none",
        music_volume_db: musicVolume,
      });
      setJobId(res.data.job_id);
      setStep(3);
    }catch{
      setErr("تعذر بدء التوليد. راجع ELEVENLABS_API_KEY و Voice ID. وإذا مفعّل موسيقى: راجع SUNOAPI_TOKEN.");
    }
  };

  useEffect(()=>{
    if(!jobId) return;
    let stop = false;
    const timer = setInterval(async ()=>{
      try{
        const res = await api.get(`/job-status/${jobId}/`);
        if (stop) return;
        setJobStatus(res.data.status);
        if (res.data.status === "succeeded") {
          try{
            const file = await api.get(`/download/${jobId}/`, { responseType: "blob" });
            const blob = new Blob([file.data], { type: "audio/mpeg" });
            const url = URL.createObjectURL(blob);
            setAudioUrl(url);
            setDownloadUrl(url);
          }catch{
            setErr("تعذر تحميل الملف. تأكد من تسجيل الدخول.");
          }
          clearInterval(timer);
        }
        if (res.data.status === "failed") {
          clearInterval(timer);
          setErr(res.data.error_message || "فشل التوليد.");
        }
      }catch{}
    }, 1500);
    return ()=>{ stop=true; clearInterval(timer); };
  }, [jobId]);

  useEffect(()=>{
    return () => { if (audioUrl) URL.revokeObjectURL(audioUrl); };
  }, [audioUrl]);

  useEffect(()=>{
    // إعادة تحميل الأصوات عند تغيير المزود
    loadVoices();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [voiceProvider]);

  const badge = (n:number, label:string) => (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-xl border ${step===n?'border-saudiGold bg-black/40':'border-white/10 bg-black/20'}`}>
      <span className={`w-7 h-7 flex items-center justify-center rounded-full ${step===n?'bg-saudiGold text-black':'bg-white/10 text-white/70'}`}>{n}</span>
      <span className="text-sm">{label}</span>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-3">
        {badge(1,"إدخال النص")}
        {badge(2,"اختيار المدرسة/الإيقاع")}
        {badge(3,"المعاينة والتحميل")}
      </div>

      {err && <div className="p-3 rounded-xl bg-red-500/10 border border-red-400/20 text-red-200">{err}</div>}
      {err && (
        <div>
          <button onClick={loadBaseData} className="px-3 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm">
            إعادة تحميل البيانات
          </button>
        </div>
      )}

      {step===1 && (
        <div className="bg-black/40 border border-white/10 rounded-2xl p-6 space-y-4">
          <h1 className="text-xl font-bold">١) أدخل القصيدة</h1>
          <input className="w-full px-3 py-2 rounded-lg bg-black/40 border border-white/10"
            value={title} onChange={(e)=>setTitle(e.target.value)} />
          <textarea className="w-full h-48 px-3 py-2 rounded-lg bg-black/40 border border-white/10 leading-8"
            value={text} onChange={(e)=>setText(e.target.value)} />
          <button onClick={submitText} className="px-4 py-2 rounded-lg bg-saudiGreen hover:opacity-90">
            كشف البحر + متابعة
          </button>

          {submissionId && (
            <div className="space-y-2 text-sm text-white/70">
              <div>
                البحر المتوقع: <span className="text-saudiGold font-bold">{meter || "—"}</span>{" "}
                (ثقة {Math.round(conf*100)}%)
              </div>
              {meterDetails?.candidates?.length ? (
                <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                  <div className="text-xs text-white/60 mb-2">أفضل الترشيحات:</div>
                  <ul className="text-xs space-y-1">
                    {meterDetails.candidates.map((c:any)=>(
                      <li key={c.bahr} className="flex justify-between">
                        <span>{c.bahr}</span>
                        <span className="text-white/50">{Math.round(c.score*100)}%</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
          )}
        </div>
      )}

      {step===2 && (
        <div className="bg-black/40 border border-white/10 rounded-2xl p-6 space-y-5">
          <h1 className="text-xl font-bold">٢) اختر المدرسة/الإيقاع + الصوت</h1>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-white/70 mb-1">اللهجة/الطابع</label>
              <select className="w-full px-3 py-2 rounded-lg bg-black/40 border border-white/10"
                value={styleKey}
                onChange={(e)=>{
                  setStyleKey(e.target.value);
                  const st = styles.find(s=>s.key===e.target.value);
                  if (st) setTempo(st.default_tempo);
                }}>
                {styles.length ? styles.map(s=> <option key={s.key} value={s.key}>{s.name_ar}</option>) : <option value="">—</option>}
              </select>
            </div>

            <div>
              <label className="block text-sm text-white/70 mb-1">مدرسة الشيلات</label>
              <select className="w-full px-3 py-2 rounded-lg bg-black/40 border border-white/10"
                value={schoolKey}
                onChange={(e)=>{
                  const v = e.target.value;
                  setSchoolKey(v);
                  const first = rhythms.find(r=>r.school_key===v);
                  if (first) setRhythmKey(first.rhythm_key);
                }}>
                {schools.length ? schools.map(s=> <option key={s.key} value={s.key}>{s.name_ar}</option>) : <option value="">—</option>}
              </select>
            </div>

            <div>
              <label className="block text-sm text-white/70 mb-1">الإيقاع</label>
              <select className="w-full px-3 py-2 rounded-lg bg-black/40 border border-white/10"
                value={rhythmKey}
                onChange={(e)=>setRhythmKey(e.target.value)}>
                {rhythms.filter(r=>r.school_key===schoolKey).length ? (
                  rhythms.filter(r=>r.school_key===schoolKey).map(r=> (
                    <option key={r.rhythm_key} value={r.rhythm_key}>{r.name_ar}</option>
                  ))
                ) : (
                  <option value="">—</option>
                )}
              </select>
              <div className="text-xs text-white/50 mt-1">
                {rhythm ? `المدرسة: ${rhythm.school_name_ar}` : ""}
              </div>
            </div>

            <div>
              <label className="block text-sm text-white/70 mb-1">الأسلوب</label>
              <select className="w-full px-3 py-2 rounded-lg bg-black/40 border border-white/10"
                value={mode}
                onChange={(e)=>setMode(e.target.value as any)}>
                <option value="مديح">مديح</option>
                <option value="حماسي">حماسي</option>
                <option value="عاطفي">عاطفي</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
                <div className="space-y-1">
                  <label className="block text-sm text-white/70">اختيار الصوت</label>
                  <select className="px-3 py-2 rounded-lg bg-black/40 border border-white/10 text-sm"
                    value={voiceProvider}
                    onChange={(e)=>{ setVoiceProvider(e.target.value as any); setVoiceDialect(""); }}>
                    <option value="elevenlabs">ElevenLabs</option>
                    <option value="google">Google TTS</option>
                  </select>
                </div>
                <button onClick={loadVoices} className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-sm">
                  جلب الأصوات
                </button>
              </div>
              <div className="grid md:grid-cols-3 gap-3 mb-2">
                <div>
                  <label className="block text-xs text-white/60 mb-1">فلترة اللهجة (اختياري)</label>
                  <select className="w-full px-3 py-2 rounded-lg bg-black/40 border border-white/10"
                    value={voiceDialect}
                    disabled={showAllVoices || voiceProvider!=="elevenlabs"}
                    onChange={(e)=>setVoiceDialect(e.target.value as any)}>
                    <option value="">الكل</option>
                    <option value="najdi">نجدي</option>
                    <option value="hijazi">حجازي</option>
                    <option value="khaliji">خليجي</option>
                  </select>
                </div>
                <div className="text-xs text-white/50 leading-6 md:col-span-2">
                  <label className="flex items-center gap-2">
                    <input type="checkbox" checked={supportArabic} disabled={showAllVoices || voiceProvider!=="elevenlabs"} onChange={(e)=>setSupportArabic(e.target.checked)} />
                    إظهار الأصوات التي **تدعم** العربية (متعددة اللغات)
                  </label>
                  <label className="flex items-center gap-2 mt-2">
                    <input type="checkbox" checked={showAllVoices} disabled={voiceProvider!=="elevenlabs"} onChange={(e)=>setShowAllVoices(e.target.checked)} />
                    عرض جميع الأصوات المتاحة من ElevenLabs (بدون فلترة/لهجة)
                  </label>
                  {voiceProvider==="google" && (
                    <div className="mt-2 text-yellow-200/80">Google TTS: لا يوجد فلتر للهجات؛ الزر أعلاه يجلب كل اللغات.</div>
                  )}
                </div>
              </div>
              <select className="w-full px-3 py-2 rounded-lg bg-black/40 border border-white/10"
                value={voiceId}
                onChange={(e)=>setVoiceId(e.target.value)}>
                {voices.length ? voices.map(v=> (
                  <option key={v.voice_id} value={v.voice_id}>
                    {v.name} — {v.category}{v.labels?.accent ? ` (${v.labels.accent})` : ""}
                  </option>
                )) : <option value="">اضغط \"جلب الأصوات\"</option>}
              </select>
              {voices.find(v=>v.voice_id===voiceId)?.preview_url ? (
                <div className="mt-3">
                  <div className="text-xs text-white/60 mb-1">معاينة صوت (Preview)</div>
                  <audio controls className="w-full" src={voices.find(v=>v.voice_id===voiceId)!.preview_url} />
                </div>
              ) : null}
            </div>

            <div>
              <label className="block text-sm text-white/70 mb-1">السرعة (Tempo)</label>
              <input type="range" min={60} max={150} value={tempo} onChange={(e)=>setTempo(parseInt(e.target.value))}
                className="w-full" />
              <div className="text-sm text-white/70">{tempo} BPM</div>
            </div>

            <div className="flex items-center gap-3">
              <input type="checkbox" checked={addPerc} onChange={(e)=>setAddPerc(e.target.checked)} />
              <span className="text-sm text-white/70">إضافة إيقاع خلفي</span>
            </div>

            <div className="md:col-span-2">
              <RhythmPreview pattern={rhythm?.pattern_json ?? null} tempo={tempo} />
            </div>

            <div className="md:col-span-2 rounded-2xl border border-white/10 bg-black/20 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-bold">موسيقى/غناء SunoAPI (اختياري)</div>
                  <div className="text-xs text-white/60">يتطلب SUNOAPI_TOKEN في .env</div>
                </div>
                <label className="flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={addMusic} onChange={(e)=>setAddMusic(e.target.checked)} />
                  تفعيل
                </label>
              </div>

              {addMusic && (
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="block text-sm text-white/70">النمط</label>
                    <select className="w-full px-3 py-2 rounded-lg bg-black/40 border border-white/10"
                      value={musicProvider}
                      onChange={(e)=>setMusicProvider(e.target.value as any)}>
                      <option value="sunoapi">موسيقى خلفية فقط (Instrumental)</option>
                      <option value="suno_vocal">غناء كامل (Suno Vocal)</option>
                    </select>
                    {musicProvider==="sunoapi" && (
                      <div>
                        <label className="block text-sm text-white/70 mb-1">مستوى الموسيقى بالخلفية</label>
                        <input type="range" min={-24} max={-3} value={musicVolume} onChange={(e)=>setMusicVolume(parseInt(e.target.value))}
                          className="w-full" />
                        <div className="text-sm text-white/70">{musicVolume} dB</div>
                      </div>
                    )}
                  </div>
                  <div className="text-xs text-white/60 leading-6">
                    - Instrumental: يولّد إيقاع وخلفية ويخلطها مع الـ TTS.<br/>
                    - Vocal: Suno يولّد الغناء الكامل مع الإيقاع؛ يتجاهل مخرجات TTS ويستخدم غناء Suno.
                  </div>
                </div>
              )}
            </div>

          </div>

          <div className="flex gap-3">
            <button onClick={()=>setStep(1)} className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20">رجوع</button>
            <button onClick={startGenerate} className="px-4 py-2 rounded-lg bg-saudiGold text-black font-bold hover:opacity-90">
              ابدأ التوليد
            </button>
          </div>
        </div>
      )}

      {step===3 && (
        <div className="bg-black/40 border border-white/10 rounded-2xl p-6 space-y-4">
          <h1 className="text-xl font-bold">٣) المعاينة والتحميل</h1>
          <div className="text-white/70">الحالة: <span className="text-saudiGold font-bold">{jobStatus || "—"}</span></div>

          {downloadUrl ? (
            <div className="space-y-3">
              <audio controls src={audioUrl || downloadUrl} className="w-full" />
              <a href={downloadUrl} className="inline-flex px-4 py-2 rounded-lg bg-saudiGreen hover:opacity-90" download>
                تحميل MP3
              </a>
            </div>
          ) : (
            <div className="text-white/60 text-sm">يتم التوليد عبر Celery Worker…</div>
          )}

          <div className="flex gap-3">
            <button onClick={()=>setStep(2)} className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20">تعديل</button>
            <button onClick={()=>{ setStep(1); setJobId(null); setDownloadUrl(null); }} className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20">
              نص جديد
            </button>
          </div>
        </div>
      )}
    </div>
  );
}


