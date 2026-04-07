import type { ChatReply, ChatRequest } from "../types/chat";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function sendChatMessage(payload: ChatRequest): Promise<ChatReply> {
  // Keep API access in one place so the UI components stay focused on presentation.
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
