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
  answer: string;
  citations: Citation[];
  disclaimer: string;
  emergency: boolean;
  recommended_action?: string | null;
};
