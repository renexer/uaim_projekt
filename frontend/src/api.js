export const API_URL = (process.env.REACT_APP_API_URL || "http://127.0.0.1:5000/api/v1").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(message, status, details) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

const TOKEN_KEY = "uaim_access_token";
const REFRESH_TOKEN_KEY = "uaim_refresh_token";
const USER_KEY = "uaim_user";

export const authStorage = {
  getToken: () => localStorage.getItem(TOKEN_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  getUser: () => {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  },
  saveSession: ({ accessToken, refreshToken, user }) => {
    localStorage.setItem(TOKEN_KEY, accessToken);
    if (refreshToken) localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clear: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
};

function buildUrl(path) {
  if (path.startsWith("http")) return path;
  return `${API_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

function extractError(payload, response) {
  if (payload?.error?.message) return payload.error.message;
  if (payload?.message) return payload.message;
  return `Błąd API (${response.status})`;
}

export async function apiRequest(path, options = {}) {
  const { method = "GET", body, auth = true, headers = {} } = options;
  const requestHeaders = { ...headers };

  if (body !== undefined) {
    requestHeaders["Content-Type"] = "application/json";
  }

  // Token JWT jest dopisywany tylko do endpointów wymagających autoryzacji.
  const token = authStorage.getToken();
  if (auth && token) {
    requestHeaders.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(buildUrl(path), {
    method,
    headers: requestHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new ApiError(extractError(payload, response), response.status, payload?.error?.details);
  }

  return payload.data;
}

export const api = {
  health: () => apiRequest("/health", { auth: false }),
  register: (payload) => apiRequest("/auth/register", { method: "POST", body: payload, auth: false }),
  login: (email, password) => apiRequest("/auth/login", { method: "POST", body: { email, password }, auth: false }),
  logout: () => apiRequest("/auth/logout", { method: "POST" }),
  me: () => apiRequest("/users/me"),
  services: () => apiRequest("/services", { auth: false }),
  service: (serviceId) => apiRequest(`/services/${serviceId}`, { auth: false }),
  therapistsForService: (serviceId) => apiRequest(`/services/${serviceId}/therapists`, { auth: false }),
  therapist: (therapistId) => apiRequest(`/therapists/${therapistId}`, { auth: false }),
  availability: ({ serviceId, therapistId, from, to }) => {
    const params = new URLSearchParams({ serviceId, from, to });
    if (therapistId) params.set("therapistId", therapistId);
    return apiRequest(`/availability?${params.toString()}`, { auth: false });
  },
  createAppointment: (payload) => apiRequest("/appointments", { method: "POST", body: payload }),
  myAppointments: (scope = "upcoming") => apiRequest(`/appointments/me?scope=${encodeURIComponent(scope)}`),
  cancelAppointment: (appointmentId, reason) => apiRequest(`/appointments/${appointmentId}/cancel`, {
    method: "POST",
    body: { reason },
  }),
  consultations: () => apiRequest("/consultations/me"),
  reviews: (therapistId) => apiRequest(`/therapists/${therapistId}/reviews`, { auth: false }),
  createReview: (appointmentId, payload) => apiRequest(`/appointments/${appointmentId}/review`, { method: "POST", body: payload }),
  staffAppointments: () => apiRequest("/staff/appointments"),
  updateAppointmentStatus: (appointmentId, status) => apiRequest(`/staff/appointments/${appointmentId}/status`, {
    method: "PATCH",
    body: { status },
  }),
  upsertConsultationSummary: (appointmentId, summaryText) => apiRequest(`/staff/appointments/${appointmentId}/consultation-summary`, {
    method: "PUT",
    body: { summaryText },
  }),
};
