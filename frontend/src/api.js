export const API_URL = (process.env.REACT_APP_API_URL || "http://127.0.0.1:8080/api/v1").replace(/\/$/, "");

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
    if (accessToken) localStorage.setItem(TOKEN_KEY, accessToken);
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

function buildQuery(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.set(key, String(value));
    }
  });
  return query.toString();
}

async function readPayload(response) {
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return {};
  }
  return response.json().catch(() => ({}));
}

function extractError(payload, response) {
  if (payload?.error?.message) {
    return new ApiError(payload.error.message, response.status, payload.error.details);
  }
  return new ApiError(`Błąd API (${response.status})`, response.status, payload);
}

async function fetchEnvelope(path, options = {}) {
  const {
    method = "GET",
    body,
    auth = true,
    headers = {},
    tokenOverride = null,
  } = options;

  const requestHeaders = { ...headers };

  if (body !== undefined && !(body instanceof FormData)) {
    requestHeaders["Content-Type"] = "application/json";
  }

  const token = tokenOverride ?? (auth ? authStorage.getToken() : null);
  if (token) {
    requestHeaders.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(buildUrl(path), {
    method,
    headers: requestHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const payload = await readPayload(response);

  if (!response.ok) {
    throw extractError(payload, response);
  }

  return payload;
}

let refreshPromise = null;

async function refreshSessionInternal() {
  if (refreshPromise) return refreshPromise;

  const refreshToken = authStorage.getRefreshToken();
  if (!refreshToken) {
    throw new ApiError("Sesja wygasła. Zaloguj się ponownie.", 401);
  }

  refreshPromise = fetchEnvelope("/auth/refresh", {
    method: "POST",
    auth: false,
    tokenOverride: refreshToken,
  })
    .then((payload) => {
      const accessToken = payload?.data?.accessToken;
      if (!accessToken) {
        throw new ApiError("Nie udało się odświeżyć sesji.", 401, payload);
      }
      authStorage.saveSession({
        accessToken,
        refreshToken,
        user: authStorage.getUser(),
      });
      return accessToken;
    })
    .catch((error) => {
      authStorage.clear();
      throw error;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}

async function apiEnvelope(path, options = {}) {
  const auth = options.auth !== false;

  try {
    return await fetchEnvelope(path, { ...options, auth });
  } catch (error) {
    const canRetry =
      auth &&
      error?.status === 401 &&
      !options.skipRefreshRetry &&
      authStorage.getRefreshToken();

    if (!canRetry) {
      throw error;
    }

    await refreshSessionInternal();
    return fetchEnvelope(path, {
      ...options,
      auth,
      skipRefreshRetry: true,
    });
  }
}

function unwrapList(payload) {
  return {
    items: payload?.data || [],
    meta: payload?.meta || null,
  };
}

export const api = {
  health: async () => {
    const payload = await apiEnvelope("/health", { auth: false });
    return payload.data;
  },

  refreshSession: refreshSessionInternal,

  register: async (payload) => {
    const response = await apiEnvelope("/auth/register", {
      method: "POST",
      body: payload,
      auth: false,
    });
    return response.data;
  },

  login: async (email, password) => {
    const response = await apiEnvelope("/auth/login", {
      method: "POST",
      body: { email, password },
      auth: false,
    });
    return response.data;
  },

  logout: async () => {
    const response = await apiEnvelope("/auth/logout", {
      method: "POST",
    });
    return response.data;
  },

  me: async () => {
    const response = await apiEnvelope("/users/me");
    return response.data;
  },

  services: async () => {
    const response = await apiEnvelope("/services", { auth: false });
    return response.data;
  },

  service: async (serviceId) => {
    const response = await apiEnvelope(`/services/${serviceId}`, { auth: false });
    return response.data;
  },

  therapists: async (params = {}) => {
    const query = buildQuery(params);
    const response = await apiEnvelope(`/therapists${query ? `?${query}` : ""}`, { auth: false });
    return response.data;
  },

  therapistsForService: async (serviceId) => {
    const response = await apiEnvelope(`/services/${serviceId}/therapists`, { auth: false });
    return response.data;
  },

  therapist: async (therapistId) => {
    const response = await apiEnvelope(`/therapists/${therapistId}`, { auth: false });
    return response.data;
  },

  reviews: async (therapistId, params = {}) => {
    const query = buildQuery({ page: 1, pageSize: 5, ...params });
    const response = await apiEnvelope(`/therapists/${therapistId}/reviews?${query}`, { auth: false });
    return unwrapList(response);
  },

  availability: async ({ serviceId, therapistId, from, to }) => {
    const query = buildQuery({ serviceId, therapistId, from, to });
    const response = await apiEnvelope(`/availability?${query}`, { auth: false });
    return response.data;
  },

  createAppointment: async (payload) => {
    const response = await apiEnvelope("/appointments", {
      method: "POST",
      body: payload,
    });
    return response.data;
  },

  myAppointments: async (params = {}) => {
    const query = buildQuery({ scope: "all", page: 1, pageSize: 10, ...params });
    const response = await apiEnvelope(`/appointments/me?${query}`);
    return unwrapList(response);
  },

  appointmentDetails: async (appointmentId) => {
    const response = await apiEnvelope(`/appointments/${appointmentId}`);
    return response.data;
  },

  cancelAppointment: async (appointmentId, reason) => {
    const response = await apiEnvelope(`/appointments/${appointmentId}/cancel`, {
      method: "POST",
      body: { reason },
    });
    return response.data;
  },

  consultations: async (params = {}) => {
    const query = buildQuery({ page: 1, pageSize: 50, ...params });
    const response = await apiEnvelope(`/consultations/me?${query}`);
    return unwrapList(response);
  },

  createReview: async (appointmentId, payload) => {
    const response = await apiEnvelope(`/appointments/${appointmentId}/review`, {
      method: "POST",
      body: payload,
    });
    return response.data;
  },

  staffDashboard: async (params = {}) => {
    const query = buildQuery(params);
    const response = await apiEnvelope(`/staff/dashboard${query ? `?${query}` : ""}`);
    return response.data;
  },

  staffAppointments: async (params = {}) => {
    const query = buildQuery({ page: 1, pageSize: 10, ...params });
    const response = await apiEnvelope(`/staff/appointments?${query}`);
    return unwrapList(response);
  },

  updateAppointmentStatus: async (appointmentId, status) => {
    const response = await apiEnvelope(`/staff/appointments/${appointmentId}/status`, {
      method: "PATCH",
      body: { status },
    });
    return response.data;
  },

  upsertConsultationSummary: async (appointmentId, summaryText) => {
    const response = await apiEnvelope(`/staff/appointments/${appointmentId}/consultation-summary`, {
      method: "PUT",
      body: { summaryText },
    });
    return response.data;
  },
};