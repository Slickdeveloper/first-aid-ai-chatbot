// Frontend API helpers.
//
// These functions keep network calls out of UI components so the data flow stays
// easy to explain:
// page/component -> API helper -> FastAPI endpoint -> JSON response -> UI update
import type { ApprovedSource, ApprovedSourceCreate, ApprovedSourceUpdate } from "../types/admin";
import type { ChatReply, ChatRequest } from "../types/chat";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  `${window.location.protocol}//${window.location.hostname}:8000`;
const ADMIN_KEY_STORAGE_KEY = "first-aid-admin-key";

function getStoredAdminKey(): string | null {
  // Session storage is enough for the lightweight shared-key admin flow.
  return window.sessionStorage.getItem(ADMIN_KEY_STORAGE_KEY);
}

function buildAdminHeaders(): HeadersInit {
  // Only admin routes need this header; public chat stays open.
  const adminKey = getStoredAdminKey();
  return adminKey ? { "X-Admin-Key": adminKey } : {};
}

export function storeAdminKey(adminKey: string): void {
  // Save the admin key for the current browser session.
  window.sessionStorage.setItem(ADMIN_KEY_STORAGE_KEY, adminKey);
}

export function clearAdminKey(): void {
  window.sessionStorage.removeItem(ADMIN_KEY_STORAGE_KEY);
}

export function hasAdminKey(): boolean {
  return Boolean(getStoredAdminKey());
}

export async function sendChatMessage(payload: ChatRequest): Promise<ChatReply> {
  // Send one user question to the backend and receive a structured grounded reply.
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch chat response.");
  }

  return response.json() as Promise<ChatReply>;
}


export async function listApprovedSources(): Promise<ApprovedSource[]> {
  // Load all source records needed by the admin dashboard.
  const response = await fetch(`${API_BASE_URL}/admin/sources`, {
    headers: buildAdminHeaders(),
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Admin login required.");
    }
    throw new Error("Failed to load approved sources.");
  }

  return response.json() as Promise<ApprovedSource[]>;
}


export async function createApprovedSource(
  payload: ApprovedSourceCreate,
): Promise<ApprovedSource> {
  // Create a source record and, when content is included, trigger initial ingestion.
  const response = await fetch(`${API_BASE_URL}/admin/sources`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAdminHeaders(),
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Admin login required.");
    }
    throw new Error("Failed to create approved source.");
  }

  return response.json() as Promise<ApprovedSource>;
}


export async function updateApprovedSource(
  sourceId: number,
  payload: ApprovedSourceUpdate,
): Promise<ApprovedSource> {
  // PATCH sends only the changed fields instead of rewriting the whole record.
  const response = await fetch(`${API_BASE_URL}/admin/sources/${sourceId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...buildAdminHeaders(),
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Admin login required.");
    }
    throw new Error("Failed to update approved source.");
  }

  return response.json() as Promise<ApprovedSource>;
}


export async function deleteApprovedSource(sourceId: number): Promise<void> {
  // Delete is reserved for records the admin wants removed entirely.
  const response = await fetch(`${API_BASE_URL}/admin/sources/${sourceId}`, {
    method: "DELETE",
    headers: buildAdminHeaders(),
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Admin login required.");
    }
    throw new Error("Failed to delete approved source.");
  }
}


export async function ingestApprovedSource(sourceId: number): Promise<ApprovedSource> {
  // Re-ingestion rebuilds searchable chunks after source content changes.
  const response = await fetch(`${API_BASE_URL}/admin/sources/${sourceId}/ingest`, {
    method: "POST",
    headers: buildAdminHeaders(),
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error("Admin login required.");
    }
    throw new Error("Failed to ingest approved source.");
  }

  return response.json() as Promise<ApprovedSource>;
}
