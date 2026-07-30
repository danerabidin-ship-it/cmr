import { useEffect, useState } from "react";
import { api } from "../api";

const EMPTY_FORM = { username: "", display_name: "", password: "", is_admin: false };

function UserManagement({ onClose }) {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getUsers().then(setUsers);
  }, []);

  async function handleAdd(e) {
    e.preventDefault();
    setError("");
    try {
      const user = await api.createUser(form);
      setUsers((prev) => [...prev, user]);
      setForm(EMPTY_FORM);
    } catch {
      setError("Kullanici eklenemedi (kullanici adi kullanimda olabilir)");
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Bu kullaniciyi silmek istediginize emin misiniz?")) return;
    await api.deleteUser(id);
    setUsers((prev) => prev.filter((u) => u.id !== id));
  }

  return (
    <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/30 p-4" onClick={onClose}>
      <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Kullanicilar</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            ✕
          </button>
        </div>

        <ul className="mt-4 max-h-48 space-y-1 overflow-y-auto text-sm">
          {users.map((u) => (
            <li key={u.id} className="flex items-center justify-between rounded border border-slate-100 px-2 py-1">
              <span>
                {u.display_name || u.username} ({u.username}){u.is_admin ? " - admin" : ""}
              </span>
              <button onClick={() => handleDelete(u.id)} className="text-xs text-red-500 hover:underline">
                Sil
              </button>
            </li>
          ))}
        </ul>

        <form onSubmit={handleAdd} className="mt-4 space-y-2 border-t border-slate-200 pt-4">
          <div className="grid grid-cols-2 gap-2">
            <input
              required
              placeholder="Kullanici adi"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              className="rounded border border-slate-300 px-2 py-1 text-sm"
            />
            <input
              placeholder="Ad Soyad"
              value={form.display_name}
              onChange={(e) => setForm({ ...form, display_name: e.target.value })}
              className="rounded border border-slate-300 px-2 py-1 text-sm"
            />
          </div>
          <input
            required
            type="password"
            placeholder="Sifre"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            className="w-full rounded border border-slate-300 px-2 py-1 text-sm"
          />
          <label className="flex items-center gap-2 text-sm text-slate-600">
            <input
              type="checkbox"
              checked={form.is_admin}
              onChange={(e) => setForm({ ...form, is_admin: e.target.checked })}
            />
            Admin yetkisi
          </label>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            className="w-full rounded bg-blue-600 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
          >
            + Kullanici Ekle
          </button>
        </form>
      </div>
    </div>
  );
}

export default UserManagement;
