import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { setToken } from "../lib/api";

export default function Login() {
  const nav = useNavigate();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const t = localStorage.getItem("token");
    if (t) { setToken(t); nav("/convert"); }
  }, [nav]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await api.post("/auth/token/", { username, password });
      const token = res.data.token;
      localStorage.setItem("token", token);
      setToken(token);
      nav("/convert");
    } catch {
      setError("بيانات الدخول غير صحيحة أو لم تنشئ مستخدم بعد.");
    }
  };

  return (
    <div className="max-w-md mx-auto bg-black/40 border border-white/10 rounded-2xl p-6">
      <h1 className="text-xl font-bold mb-2">تسجيل الدخول</h1>
      <p className="text-white/70 mb-6">ادخل بيانات مستخدم Django (superuser).</p>

      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-sm text-white/70 mb-1">اسم المستخدم</label>
          <input className="w-full px-3 py-2 rounded-lg bg-black/40 border border-white/10"
            value={username} onChange={(e)=>setUsername(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm text-white/70 mb-1">كلمة المرور</label>
          <input type="password" className="w-full px-3 py-2 rounded-lg bg-black/40 border border-white/10"
            value={password} onChange={(e)=>setPassword(e.target.value)} />
        </div>

        {error && <div className="text-red-300 text-sm">{error}</div>}

        <button className="w-full py-2.5 rounded-lg bg-saudiGold text-black font-bold hover:opacity-90">
          دخول
        </button>
      </form>
    </div>
  );
}
