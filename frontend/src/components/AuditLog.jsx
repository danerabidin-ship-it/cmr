import { useEffect, useState } from "react";
import { api } from "../api";

const ACTION_LABELS = {
  trip: "sevkiyat",
  vehicle: "arac",
};

function describe(entry) {
  const kind = ACTION_LABELS[entry.entity_type] || entry.entity_type;
  if (entry.action === "created") {
    return (
      <>
        {kind} olusturdu: <strong>{entry.entity_label}</strong>
      </>
    );
  }
  if (entry.action === "deleted") {
    return (
      <>
        {kind} sildi: <strong>{entry.entity_label}</strong>
      </>
    );
  }
  return (
    <>
      <strong>{entry.entity_label}</strong> / {entry.field}:{" "}
      <span className="text-red-500 line-through">{entry.old_value || "(bos)"}</span>{" "}
      <span className="text-green-700">→ {entry.new_value || "(bos)"}</span>
    </>
  );
}

function AuditLog({ onClose }) {
  const [entries, setEntries] = useState([]);

  useEffect(() => {
    api.getAudit().then(setEntries);
  }, []);

  return (
    <div className="fixed inset-0 z-10 flex items-center justify-center bg-black/30 p-4" onClick={onClose}>
      <div
        className="max-h-[80vh] w-full max-w-2xl overflow-y-auto rounded-lg bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">Degisiklik Gecmisi</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            ✕
          </button>
        </div>

        <ul className="mt-4 space-y-2 text-sm">
          {entries.map((entry) => (
            <li key={entry.id} className="border-b border-slate-100 pb-2">
              <span className="text-slate-400">{entry.timestamp.replace("T", " ").slice(0, 19)}</span>{" "}
              <strong>{entry.username}</strong> {describe(entry)}
            </li>
          ))}
          {entries.length === 0 && <p className="text-slate-400">Kayit yok.</p>}
        </ul>
      </div>
    </div>
  );
}

export default AuditLog;
