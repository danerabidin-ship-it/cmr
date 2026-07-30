import { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import TripCard from "./components/TripCard";
import PrintSheet from "./components/PrintSheet";

function matchesSearch(vehicle, term) {
  const haystack = `${vehicle.ref} ${vehicle.consignee} ${vehicle.model} ${vehicle.reg} ${vehicle.notes}`.toLowerCase();
  return haystack.includes(term);
}

function App() {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [printingTripId, setPrintingTripId] = useState(null);

  useEffect(() => {
    api
      .getTrips()
      .then(setTrips)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    function handleAfterPrint() {
      setPrintingTripId(null);
    }
    window.addEventListener("afterprint", handleAfterPrint);
    return () => window.removeEventListener("afterprint", handleAfterPrint);
  }, []);

  useEffect(() => {
    if (printingTripId === null) return undefined;
    const timer = setTimeout(() => window.print(), 50);
    return () => clearTimeout(timer);
  }, [printingTripId]);

  async function handleAddTrip() {
    const trip = await api.createTrip({ booking_ref: "Yeni Sevkiyat" });
    setTrips((prev) => [{ ...trip, vehicles: [] }, ...prev]);
  }

  async function handleUpdateTrip(tripId, field, value) {
    setTrips((prev) => prev.map((t) => (t.id === tripId ? { ...t, [field]: value } : t)));
    await api.updateTrip(tripId, { [field]: value });
  }

  async function handleDeleteTrip(tripId) {
    if (!window.confirm("Bu sevkiyati silmek istediginize emin misiniz?")) return;
    setTrips((prev) => prev.filter((t) => t.id !== tripId));
    await api.deleteTrip(tripId);
  }

  async function handleAddVehicle(tripId) {
    const vehicle = await api.createVehicle(tripId, {});
    setTrips((prev) =>
      prev.map((t) => (t.id === tripId ? { ...t, vehicles: [...t.vehicles, vehicle] } : t))
    );
  }

  async function handleUpdateVehicle(vehicleId, field, value) {
    setTrips((prev) =>
      prev.map((t) => ({
        ...t,
        vehicles: t.vehicles.map((v) => (v.id === vehicleId ? { ...v, [field]: value } : v)),
      }))
    );
    await api.updateVehicle(vehicleId, { [field]: value });
  }

  async function handleDeleteVehicle(vehicleId) {
    setTrips((prev) => prev.map((t) => ({ ...t, vehicles: t.vehicles.filter((v) => v.id !== vehicleId) })));
    await api.deleteVehicle(vehicleId);
  }

  const term = search.trim().toLowerCase();
  const visibleTrips = useMemo(() => {
    if (!term) return trips;
    return trips
      .map((t) => ({ ...t, vehicles: t.vehicles.filter((v) => matchesSearch(v, term)) }))
      .filter((t) => t.vehicles.length > 0);
  }, [trips, term]);

  const printTrip = trips.find((t) => t.id === printingTripId) ?? null;

  return (
    <div className="app-shell min-h-screen bg-slate-50 py-8">
      <div className="mx-auto max-w-5xl px-4">
        <div className="no-print flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">LoadTracker</h1>
            <p className="mt-1 text-slate-500">Sevkiyat ve arac takip sistemi</p>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Ara: ref, consignee, model, reg, notes..."
              className="w-72 rounded border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />
            <button
              onClick={handleAddTrip}
              className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              + Yeni Sevkiyat
            </button>
          </div>
        </div>

        {loading && <p className="no-print mt-6 text-slate-500">Yukleniyor...</p>}
        {error && <p className="no-print mt-6 text-red-600">Hata: {error}</p>}

        <div className="no-print mt-6 space-y-4">
          {visibleTrips.map((trip) => (
            <TripCard
              key={trip.id}
              trip={trip}
              onUpdateTrip={handleUpdateTrip}
              onDeleteTrip={handleDeleteTrip}
              onAddVehicle={handleAddVehicle}
              onUpdateVehicle={handleUpdateVehicle}
              onDeleteVehicle={handleDeleteVehicle}
              onPrint={setPrintingTripId}
            />
          ))}
          {!loading && visibleTrips.length === 0 && (
            <p className="text-slate-500">Kayit bulunamadi.</p>
          )}
        </div>
      </div>

      <PrintSheet trip={printTrip} />
    </div>
  );
}

export default App;
