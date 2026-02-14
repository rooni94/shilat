import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Convert from "./pages/Convert";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/login" element={<Login />} />
        <Route path="/convert" element={<Convert />} />
        <Route path="/" element={<Navigate to="/convert" replace />} />
      </Route>
    </Routes>
  );
}
