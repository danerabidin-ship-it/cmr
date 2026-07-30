const BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = new Error(`Request failed (${res.status}): ${path}`);
    err.status = res.status;
    throw err;
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  getTrips: () => request("/trips"),
  createTrip: (data) => request("/trips", { method: "POST", body: JSON.stringify(data) }),
  updateTrip: (id, data) => request(`/trips/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteTrip: (id) => request(`/trips/${id}`, { method: "DELETE" }),
  createVehicle: (tripId, data) =>
    request(`/trips/${tripId}/vehicles`, { method: "POST", body: JSON.stringify(data) }),
  updateVehicle: (id, data) => request(`/vehicles/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteVehicle: (id) => request(`/vehicles/${id}`, { method: "DELETE" }),

  getMe: () => request("/auth/me"),
  login: (username, password) =>
    request("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),
  logout: () => request("/auth/logout", { method: "POST" }),

  getUsers: () => request("/users"),
  createUser: (data) => request("/users", { method: "POST", body: JSON.stringify(data) }),
  deleteUser: (id) => request(`/users/${id}`, { method: "DELETE" }),

  getAudit: () => request("/audit"),
};
