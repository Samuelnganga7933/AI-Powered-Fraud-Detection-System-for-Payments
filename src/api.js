const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || `Request failed (${response.status})`);
  return payload;
}

export function predictTransaction(features) {
  return request("/predict", {
    method: "POST",
    body: JSON.stringify({ features: features.map(Number) }),
  });
}

export function getModelInfo() {
  return request("/model-info");
}
