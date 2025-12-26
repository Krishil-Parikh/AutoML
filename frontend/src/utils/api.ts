import { API_BASE_URL } from '../config';

export const api = {
  upload: (formData: FormData) =>
    fetch(`${API_BASE_URL}/upload`, { method: 'POST', body: formData }),

  getInfo: (sessionId: string) =>
    fetch(`${API_BASE_URL}/info/${sessionId}`),

  dropColumns: (sessionId: string, columnIds: number[]) =>
    fetch(`${API_BASE_URL}/clean/drop`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, column_ids: columnIds }),
    }),

  getMissingSuggestions: (sessionId: string) =>
    fetch(`${API_BASE_URL}/suggestions/missing/${sessionId}`),

  applyMissingPlan: (sessionId: string, plan: Record<string, number[]>) =>
    fetch(`${API_BASE_URL}/clean/missing`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, plan }),
    }),

  getOutliersSuggestions: (sessionId: string) =>
    fetch(`${API_BASE_URL}/suggestions/outliers/${sessionId}`),

  applyOutliersPlan: (sessionId: string, plan: Record<string, number[]>) =>
    fetch(`${API_BASE_URL}/clean/outliers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, plan }),
    }),

  applyCorrelationPlan: (sessionId: string, threshold: number, autoDrop: boolean) =>
    fetch(`${API_BASE_URL}/clean/correlation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, threshold, auto_drop: autoDrop }),
    }),

  getEncodingSuggestions: (sessionId: string) =>
    fetch(`${API_BASE_URL}/suggestions/encoding/${sessionId}`),

  applyEncodingPlan: (sessionId: string, plan: Record<string, number[]>) =>
    fetch(`${API_BASE_URL}/clean/encoding`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, plan }),
    }),

  getScalingSuggestions: (sessionId: string) =>
    fetch(`${API_BASE_URL}/suggestions/scaling/${sessionId}`),

  applyScalingPlan: (sessionId: string, plan: Record<string, number[]>) =>
    fetch(`${API_BASE_URL}/clean/scaling`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, plan }),
    }),

  getHeatmap: (sessionId: string, method = 'pearson') =>
    fetch(`${API_BASE_URL}/plots/bivariate/heatmap/${sessionId}?method=${method}`),

  downloadCSV: (sessionId: string) =>
    window.open(`${API_BASE_URL}/download/csv/${sessionId}`, '_blank'),

  downloadNotebook: (sessionId: string, filename = 'preprocessing_workflow') =>
    fetch(`${API_BASE_URL}/download/notebook`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, filename }),
    }),
};
