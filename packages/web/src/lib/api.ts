/**
 * API base URL resolution.
 * - Dev: Vite proxy strips /api → localhost:8787
 * - Vercel prod: set VITE_API_BASE to hosted API (Railway/Fly) or use /api rewrite
 */
const envBase = (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, "") ?? "";

export function apiUrl(path: string): string {
  const p = path.startsWith("/") ? path : `/${path}`;
  if (envBase) return `${envBase}${p}`;
  return `/api${p}`;
}

export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  return fetch(apiUrl(path), init);
}

export async function checkApiHealth(): Promise<{ ok: boolean; version?: string }> {
  try {
    const res = await apiFetch("/health", { signal: AbortSignal.timeout(8000) });
    if (!res.ok) return { ok: false };
    const data = await res.json();
    return { ok: true, version: data.version ?? data.engine };
  } catch {
    return { ok: false };
  }
}
