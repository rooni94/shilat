import React, { useEffect, useMemo, useRef, useState } from "react";

type Pattern = {
  time_signature: string;
  phrase_beats: number;
  hits: number[];
  accent: number[];
};

function drawWave(canvas: HTMLCanvasElement, hits: number[], accent: number[]) {
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  ctx.globalAlpha = 0.25;
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, w, h);
  ctx.globalAlpha = 1;

  const n = Math.max(1, hits.length * 4);
  const step = w / n;

  for (let i = 0; i < n; i++) {
    const idx = Math.floor(i / 4) % hits.length;
    const isHit = hits[idx] === 1;
    const isAcc = (accent?.[idx] ?? 0) === 1;
    const amp = isAcc ? 0.95 : isHit ? 0.65 : 0.15;
    const barH = amp * (h * 0.85);
    const x = i * step;
    const y = (h - barH) / 2;

    ctx.fillStyle = isAcc ? "rgba(166,123,46,0.95)" : isHit ? "rgba(12,91,71,0.95)" : "rgba(255,255,255,0.25)";
    ctx.fillRect(x, y, Math.max(1, step - 2), barH);
  }
}

export default function RhythmPreview({ pattern, tempo }: { pattern: Pattern | null; tempo: number }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [playing, setPlaying] = useState(false);

  const audioCtxRef = useRef<AudioContext | null>(null);
  const timerRef = useRef<number | null>(null);
  const beatIndexRef = useRef(0);

  const hits = pattern?.hits ?? [];
  const accent = pattern?.accent ?? [];

  useEffect(() => {
    const c = canvasRef.current;
    if (!c || !pattern) return;
    drawWave(c, hits, accent);
  }, [pattern, hits, accent]);

  const beatMs = useMemo(() => Math.round(60000 / Math.max(40, Math.min(220, tempo))), [tempo]);

  const click = (strong: boolean) => {
    const ctx = audioCtxRef.current;
    if (!ctx) return;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = "sine";
    osc.frequency.value = strong ? 880 : 660;
    gain.gain.value = strong ? 0.12 : 0.07;
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.03);
  };

  const start = async () => {
    if (!pattern) return;
    if (!audioCtxRef.current) audioCtxRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    await audioCtxRef.current.resume();

    setPlaying(true);
    beatIndexRef.current = 0;

    timerRef.current = window.setInterval(() => {
      const idx = beatIndexRef.current % Math.max(1, hits.length);
      const isHit = (hits[idx] ?? 0) === 1;
      const isAcc = (accent?.[idx] ?? 0) === 1;
      if (isHit || isAcc) click(isAcc);
      beatIndexRef.current += 1;
    }, beatMs);
  };

  const stop = () => {
    setPlaying(false);
    if (timerRef.current) window.clearInterval(timerRef.current);
    timerRef.current = null;
  };

  useEffect(() => () => stop(), []);

  return (
    <div className="rounded-2xl border border-white/10 bg-black/30 p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="text-sm text-white/70">معاينة الإيقاع (Metronome + Waveform)</div>
        {!playing ? (
          <button onClick={start} className="px-3 py-1.5 rounded-lg bg-saudiGreen hover:opacity-90 text-sm">تشغيل</button>
        ) : (
          <button onClick={stop} className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-sm">إيقاف</button>
        )}
      </div>

      <canvas ref={canvasRef} width={900} height={140} className="w-full rounded-xl border border-white/10" />

      <div className="text-xs text-white/60">
        * هذه المعاينة تُظهر “شكل” الإيقاع حسب pattern_json وتستخدم clicks بسيطة.
      </div>
    </div>
  );
}
