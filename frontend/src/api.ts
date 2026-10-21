/**
 * SlothSort - API Client
 * Talks to the FastAPI backend. On GitHub Pages (or with ?demo in the URL)
 * it switches to built-in sample data so the dashboard works without a backend.
 */

const API_BASE = '/api';

export const IS_DEMO =
  typeof window !== 'undefined' &&
  (window.location.hostname.endsWith('github.io') ||
    window.location.search.includes('demo'));

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

/* ---------------------------- DEMO MODE ---------------------------- */

interface DemoFile {
  orig: string;
  name: string;
  category: string;
  summary: string;
  model: string;
}

const DEMO_FILES: DemoFile[] = [
  { orig: 'Screenshot (482).png', name: 'dashboard_revenue_chart.png', category: 'Media_And_Screenshots', summary: 'Screenshot of a revenue dashboard with a rising monthly line chart.', model: 'moondream' },
  { orig: 'final_v2_REAL(1).pdf', name: 'acme_cloud_invoice_october.pdf', category: 'Finance_And_Bills', summary: 'Monthly invoice from Acme Cloud Services, $94.38 due Nov 1st.', model: 'llama3.2:3b' },
  { orig: 'export_data(3)_FINAL.csv', name: 'customer_signups_q3.csv', category: 'Code_And_Tech', summary: 'CSV export of customer signups with dates, plans and regions.', model: 'llama3.2:3b' },
  { orig: 'notes_lecture_new.txt', name: 'operating_systems_lecture_notes.txt', category: 'Study_And_Papers', summary: 'Lecture notes covering process scheduling and virtual memory.', model: 'llama3.2:3b' },
  { orig: 'IMG_20261003_1844.jpg', name: 'hiking_trail_sunset.jpg', category: 'Media_And_Screenshots', summary: 'Photo of a hiking trail at sunset with hills in the background.', model: 'moondream' },
  { orig: 'cover letter draft.docx', name: 'cover_letter_software_intern.docx', category: 'Personal_Docs', summary: 'Draft cover letter for a software engineering internship.', model: 'llama3.2:3b' },
  { orig: 'main_old_backup.py', name: 'fastapi_server_backup.py', category: 'Code_And_Tech', summary: 'Python FastAPI server with status and history endpoints.', model: 'llama3.2:3b' },
  { orig: 'untitled(7).txt', name: 'grocery_and_todo_list.txt', category: 'Misc', summary: 'Short to-do list mixed with grocery items.', model: 'llama3.2:3b' },
];

let demoState = 'idle';
let pending: DemoFile[] = [];
let records: HistoryRecord[] = [];
let timer: ReturnType<typeof setInterval> | null = null;
let counter = 0;

function stopTimer() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
}

function sortNext(): boolean {
  const f = pending.shift();
  if (!f) {
    stopTimer();
    demoState = 'idle';
    return false;
  }
  counter += 1;
  records.push({
    id: `demo-${counter}`,
    timestamp: new Date().toISOString(),
    original_path: `demo_messy_folder/${f.orig}`,
    original_name: f.orig,
    new_path: `sorted_output/${f.category}/${f.name}`,
    new_name: f.name,
    category: f.category,
    summary: f.summary,
    model_used: f.model,
    undone: false,
  });
  if (pending.length === 0) {
    stopTimer();
    demoState = 'idle';
  }
  return true;
}

const jitter = (base: number, spread: number) =>
  Math.round((base + Math.random() * spread) * 10) / 10;

function demoStatus(): StatusResponse {
  const active = records.filter((r) => !r.undone);
  return {
    state: demoState,
    cpu_percent: jitter(8, 20),
    memory_percent: jitter(42, 6),
    is_system_busy: false,
    ollama_online: true,
    ollama_models: ['llama3.2:3b', 'moondream'],
    watch_folder: 'demo_messy_folder',
    sorted_folder: 'sorted_output',
    files_sorted: active.length,
    text_model: 'llama3.2:3b',
    vision_model: 'moondream',
    last_activity: records.length ? records[records.length - 1] : null,
  };
}

/* ---------------------------- REAL API ---------------------------- */

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
  if (IS_DEMO) return demoStatus();
  return fetchJSON<StatusResponse>(`${API_BASE}/status`);
}

export async function toggleDaemon(action: 'start' | 'pause' | 'sort_one') {
  if (IS_DEMO) {
    if (action === 'sort_one') {
      sortNext();
    } else if (action === 'start') {
      if (pending.length > 0 && !timer) {
        demoState = 'running';
        timer = setInterval(sortNext, 2500);
      }
    } else {
      stopTimer();
      demoState = 'paused';
    }
    return { state: demoState, message: `Demo: ${action}` };
  }
  return fetchJSON<any>(`${API_BASE}/toggle`, {
    method: 'POST',
    body: JSON.stringify({ action }),
  });
}

export async function generateSandbox() {
  if (IS_DEMO) {
    stopTimer();
    demoState = 'idle';
    pending = [...DEMO_FILES];
    records = [];
    return {
      message: 'Demo: generated messy files',
      files: DEMO_FILES.map((f) => f.orig),
    };
  }
  return fetchJSON<{ message: string; files: string[] }>(`${API_BASE}/generate-sandbox`, {
    method: 'POST',
  });
}

export async function getHistory(): Promise<HistoryResponse> {
  if (IS_DEMO) return { count: records.length, records: [...records] };
  return fetchJSON<HistoryResponse>(`${API_BASE}/history`);
}

export async function undoSingle(id: string) {
  if (IS_DEMO) {
    const r = records.find((x) => x.id === id);
    if (r) {
      r.undone = true;
      r.undone_at = new Date().toISOString();
    }
    return { message: 'Demo: undone', id };
  }
  return fetchJSON<any>(`${API_BASE}/undo/${id}`, { method: 'POST' });
}

export async function undoAll() {
  if (IS_DEMO) {
    const now = new Date().toISOString();
    records.forEach((r) => {
      r.undone = true;
      r.undone_at = now;
    });
    return { message: 'Demo: undone all' };
  }
  return fetchJSON<any>(`${API_BASE}/undo-all`, { method: 'POST' });
}