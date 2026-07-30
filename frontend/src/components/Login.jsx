import { useState } from "react";
import { api } from "../api";

function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const user = await api.login(username, password);
      onLogin(user);
    } catch {
      setError("Kullanici adi veya sifre hatali");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">
      <form onSubmit={handleSubmit} className="w-80 rounded-lg bg-white p-6 shadow">
        <h1 className="text-xl font-bold text-slate-900">LoadTracker</h1>
        <p className="mt-1 text-sm text-slate-500">Devam etmek icin giris yapin</p>

        <label className="mt-4 block text-sm text-slate-600">
          Kullanici Adi
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            autoFocus
          />
        </label>
        <label className="mt-3 block text-sm text-slate-600">
          Sifre
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded border border-slate-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
        </label>

        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="mt-4 w-full rounded bg-blue-600 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-60"
        >
          Giris Yap
        </button>
      </form>
    </div>
  );
}

export default Login;
