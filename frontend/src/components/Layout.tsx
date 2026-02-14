import React from "react";
import { Outlet, Link, useNavigate } from "react-router-dom";
import { setToken } from "../lib/api";

export default function Layout() {
  const nav = useNavigate();
  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    nav("/login");
  };

  return (
    <div className="min-h-screen bg-geo">
      <header className="sticky top-0 z-20 backdrop-blur bg-black/40 border-b border-white/10">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/convert" className="font-bold text-lg">
            <span className="text-saudiGold">شيلات</span>{" "}
            <span className="text-white/80">| تحويل القصائد</span>
          </Link>
          <div className="flex gap-3 items-center">
            <Link to="/convert" className="text-white/80 hover:text-white">التحويل</Link>
            <Link to="/login" className="text-white/80 hover:text-white">الدخول</Link>
            <button onClick={logout} className="px-3 py-1.5 rounded-lg bg-saudiGreen hover:opacity-90">
              خروج
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        <Outlet />
      </main>

      <footer className="max-w-5xl mx-auto px-4 pb-10 text-sm text-white/50">
        واجهة عربية كاملة • شيلات • ITLAVA.com حقوق النشر محفوظة &copy; 2026
      </footer>
    </div>
  );
}
