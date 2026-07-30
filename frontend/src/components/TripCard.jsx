import { useState } from "react";

const HEADER_FIELDS = [
  ["booking_ref", "Booking Ref"],
  ["console", "Console"],
  ["free_port", "Free Port"],
  ["received", "Received"],
  ["loading_date", "Loading Date"],
  ["ets", "ETS"],
  ["eta", "ETA"],
  ["mersin_arrival", "Mersin Varis"],
  ["famagusta_arrival", "Famagusta Varis"],
  ["container", "Container"],
  ["uk", "UK"],
];

const VEHICLE_TEXT_FIELDS = [
  ["ref", "Ref"],
  ["consignee", "Consignee"],
  ["model", "Model"],
  ["reg", "Reg"],
  ["location", "Location"],
];

const VEHICLE_CHECK_FIELDS = [
  ["inst", "Inst"],
  ["invoice", "Invoice"],
  ["v5", "V5"],
];

function TripCard({ trip, onUpdateTrip, onDeleteTrip, onAddVehicle, onUpdateVehicle, onDeleteVehicle, onPrint }) {
  const [expanded, setExpanded] = useState(true);

  const ready = trip.vehicles.filter((v) => v.inst && v.invoice && v.v5).length;
  const noted = trip.vehicles.filter((v) => v.notes.trim() !== "").length;
  const total = trip.vehicles.length;

  return (
    <div className="trip-card rounded-lg bg-white shadow" data-trip-id={trip.id}>
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <button
          onClick={() => setExpanded((e) => !e)}
          className="text-left font-semibold text-slate-900"
        >
          {expanded ? "▾" : "▸"} {trip.booking_ref || "(Yeni Sevkiyat)"}
        </button>
        <div className="no-print flex items-center gap-3 text-sm text-slate-500">
          <span>
            Hazir: <strong className="text-green-700">{ready}</strong> / Notlu:{" "}
            <strong className="text-amber-700">{noted}</strong> / Toplam: {total}
          </span>
          <button onClick={() => onPrint(trip.id)} className="rounded border border-slate-300 px-2 py-1 hover:bg-slate-50">
            Yazdir
          </button>
          <button
            onClick={() => onDeleteTrip(trip.id)}
            className="rounded border border-red-200 px-2 py-1 text-red-600 hover:bg-red-50"
          >
            Sil
          </button>
        </div>
      </div>

      {expanded && (
        <div className="p-4">
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {HEADER_FIELDS.map(([field, label]) => (
              <label key={field} className="text-xs text-slate-500">
                {label}
                <input
                  type="text"
                  defaultValue={trip[field]}
                  onBlur={(e) => onUpdateTrip(trip.id, field, e.target.value)}
                  className="mt-1 block w-full rounded border border-slate-300 px-2 py-1 text-sm text-slate-900 focus:border-blue-500 focus:outline-none"
                />
              </label>
            ))}
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[900px] border-collapse text-sm">
              <thead>
                <tr className="text-left text-slate-500">
                  {VEHICLE_TEXT_FIELDS.map(([, label]) => (
                    <th key={label} className="px-2 py-1">{label}</th>
                  ))}
                  {VEHICLE_CHECK_FIELDS.map(([, label]) => (
                    <th key={label} className="px-2 py-1 text-center">{label}</th>
                  ))}
                  <th className="px-2 py-1">Received</th>
                  <th className="px-2 py-1">Notes</th>
                  <th className="no-print px-2 py-1"></th>
                </tr>
              </thead>
              <tbody>
                {trip.vehicles.map((vehicle) => (
                  <tr key={vehicle.id} className="border-t border-slate-100">
                    {VEHICLE_TEXT_FIELDS.map(([field]) => (
                      <td key={field} className="px-2 py-1">
                        <input
                          type="text"
                          defaultValue={vehicle[field]}
                          onBlur={(e) => onUpdateVehicle(vehicle.id, field, e.target.value)}
                          className="w-full rounded border border-transparent px-1 py-0.5 hover:border-slate-300 focus:border-blue-500 focus:outline-none"
                        />
                      </td>
                    ))}
                    {VEHICLE_CHECK_FIELDS.map(([field]) => (
                      <td key={field} className="px-2 py-1 text-center">
                        <input
                          type="checkbox"
                          checked={vehicle[field]}
                          onChange={(e) => onUpdateVehicle(vehicle.id, field, e.target.checked)}
                        />
                      </td>
                    ))}
                    <td className="px-2 py-1">
                      <input
                        type="text"
                        defaultValue={vehicle.received}
                        onBlur={(e) => onUpdateVehicle(vehicle.id, "received", e.target.value)}
                        className="w-full rounded border border-transparent px-1 py-0.5 hover:border-slate-300 focus:border-blue-500 focus:outline-none"
                      />
                    </td>
                    <td className="px-2 py-1">
                      <input
                        type="text"
                        defaultValue={vehicle.notes}
                        onBlur={(e) => onUpdateVehicle(vehicle.id, "notes", e.target.value)}
                        className="w-full rounded border border-transparent px-1 py-0.5 hover:border-slate-300 focus:border-blue-500 focus:outline-none"
                      />
                    </td>
                    <td className="no-print px-2 py-1 text-right">
                      <button
                        onClick={() => onDeleteVehicle(vehicle.id)}
                        className="text-xs text-red-500 hover:underline"
                      >
                        Sil
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <button
            onClick={() => onAddVehicle(trip.id)}
            className="no-print mt-3 rounded border border-dashed border-slate-300 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-50"
          >
            + Arac Ekle
          </button>
        </div>
      )}
    </div>
  );
}

export default TripCard;
