// Shared chat-related frontend types.
//
// These types mirror the backend schema so components and API helpers agree on
// the shape of messages and replies.
export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export type Citation = {
  title: string;
  organization: string;
  url: string;
  excerpt: string;
};

export type ChatRequest = {
  session_id: string;
  message: string;
};

export type ChatReply = {
  // Mirrors the backend ChatResponse payload.
  answer: string;
  citations: Citation[];
  disclaimer: string;
  emergency: boolean;
  recommended_action?: string | null;
};
