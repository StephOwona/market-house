const API_BASE = "";

async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("mh_token");
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  // 15-second timeout to prevent infinite spinning
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 15000);

  try {
    const res = await fetch(API_BASE + path, { ...options, headers, signal: controller.signal });
    clearTimeout(timeoutId);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.error || `Erreur ${res.status}`);
    }
    return data;
  } catch (err) {
    clearTimeout(timeoutId);
    if (err.name === "AbortError") throw new Error("Délai dépassé — vérifiez votre connexion");
    throw err;
  }
}

const api = {
  post: (path, body) => apiFetch(path, { method: "POST", body: JSON.stringify(body) }),
  get: (path) => apiFetch(path, { method: "GET" }),
  put: (path, body) => apiFetch(path, { method: "PUT", body: JSON.stringify(body) }),
  delete: (path) => apiFetch(path, { method: "DELETE" }),
};
