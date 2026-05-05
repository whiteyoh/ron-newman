export async function fetchJson(url, options) {
  let res;
  try {
    res = await fetch(url, options);
  } catch (err) {
    throw new Error(`Network error while requesting ${url}: ${err instanceof Error ? err.message : 'request failed'}`);
  }
  let data;
  try {
    data = await res.json();
  } catch {
    throw new Error(`Malformed JSON response from ${url}`);
  }
  if (!res.ok) {
    const msg = data?.error || `Backend returned ${res.status}`;
    const error = new Error(msg);
    error.requestId = data?.request_id;
    error.code = data?.code;
    error.status = res.status;
    error.field = data?.field;
    throw error;
  }
  return data;
}

export const loadStartupData = () =>
  Promise.all([
    fetchJson('/api/levels'),
    fetchJson('/api/use-cases'),
    fetchJson('/api/agentic-maturity'),
  ]);

export const runLevelRequest = (payload) =>
  fetchJson('/api/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
