function PrintSheet({ trip }) {
  if (!trip) return null;

  return (
    <div className="print-sheet p-8">
      <h1 className="text-xl font-bold">Yuk Listesi</h1>
      <div className="mt-2 grid grid-cols-3 gap-x-6 gap-y-1 text-sm">
        <div><strong>Booking Ref:</strong> {trip.booking_ref}</div>
        <div><strong>Console:</strong> {trip.console}</div>
        <div><strong>Container:</strong> {trip.container}</div>
        <div><strong>Loading Date:</strong> {trip.loading_date}</div>
        <div><strong>ETS:</strong> {trip.ets}</div>
        <div><strong>ETA:</strong> {trip.eta}</div>
        <div><strong>Free Port:</strong> {trip.free_port}</div>
        <div><strong>Mersin Varis:</strong> {trip.mersin_arrival}</div>
        <div><strong>Famagusta Varis:</strong> {trip.famagusta_arrival}</div>
      </div>

      <table className="mt-6 w-full border-collapse text-sm">
        <thead>
          <tr>
            {["Ref", "Consignee", "Model", "Reg", "Location", "Inst", "Invoice", "V5", "Received", "Notes"].map(
              (h) => (
                <th key={h} className="border border-black px-2 py-1 text-left">
                  {h}
                </th>
              )
            )}
          </tr>
        </thead>
        <tbody>
          {trip.vehicles.map((v) => (
            <tr key={v.id}>
              <td className="border border-black px-2 py-1">{v.ref}</td>
              <td className="border border-black px-2 py-1">{v.consignee}</td>
              <td className="border border-black px-2 py-1">{v.model}</td>
              <td className="border border-black px-2 py-1">{v.reg}</td>
              <td className="border border-black px-2 py-1">{v.location}</td>
              <td className="border border-black px-2 py-1 text-center">{v.inst ? "X" : ""}</td>
              <td className="border border-black px-2 py-1 text-center">{v.invoice ? "X" : ""}</td>
              <td className="border border-black px-2 py-1 text-center">{v.v5 ? "X" : ""}</td>
              <td className="border border-black px-2 py-1">{v.received}</td>
              <td className="border border-black px-2 py-1">{v.notes}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default PrintSheet;
