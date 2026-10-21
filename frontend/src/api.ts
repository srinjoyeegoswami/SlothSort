/**
 * SlothSort — API Client Hooks
 * Typed fetch wrappers for the FastAPI backend.
 */

const API_BASE = '/api';

export interface StatusResponse {
  state: string;
  cpu_percent: number;
  memory_percent: number;
  is_system_busy: boolean;
  ollama_online: boolean;
  ollama_models: string[];
  watch_folder: string;
  sorted_folder: string;
  files_sorted: number;
  text_model: string;
  vision_model: string;
  last_activity: HistoryRecord | null;
}

export interface HistoryRecord {
  id: string;
  timestamp: string;
  original_path: string;
  original_name: string;
  new_path: string;
  new_name: string;
  category: string;
  summary: string;
  model_used: string;
  undone?: boolean;
  undone_at?: string;
}

export interface HistoryResponse {
  count: number;
  records: HistoryRecord[];
}

async function fetchJSON<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...opts,
    headers: { 'Content-Type': 'application/json', ...opts?.headers },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export async function getStatus(): Promise<StatusResponse> {
  return fetchJSON<StatusResponse>(`${API_BASE}/status`);
}

export async function toggleDaemon(action: 'start' | 'pause' | 'sort_one') {
  return fetchJSON<any>(`${API_BASE}/toggle`, {
    method: 'POST',
    body: JSON.stringify({ action }),
  });
}

export async function generateSandbox() {
  return fetchJSON<{ message: string; files: string[] }>(`${API_BASE}/generate-sandbox`, {
    method: 'POST',
  });
}

export async function getHistory(): Promise<HistoryResponse> {
  return fetchJSON<HistoryResponse>(`${API_BASE}/history`);
}

export async function undoSingle(id: string) {
  return fetchJSON<any>(`${API_BASE}/undo/${id}`, { method: 'POST' });
}

export async function undoAll() {
  return fetchJSON<any>(`${API_BASE}/undo-all`, { method: 'POST' });
}
