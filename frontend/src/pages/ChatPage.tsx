import { FormEvent, useState } from "react";

import { ChatWindow } from "../components/ChatWindow";
import { EmergencyBanner } from "../components/EmergencyBanner";
import { SourceCitations } from "../components/SourceCitations";
import { sendChatMessage } from "../services/api";
import type { ChatMessage, ChatReply } from "../types/chat";

export function ChatPage() {
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [reply, setReply] = useState<ChatReply | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) {
      return;
    }

    const nextUserMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
    };

    // Show the user's message immediately so the UI feels responsive.
    setMessages((current) => [...current, nextUserMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // The backend returns the answer, citations, disclaimer, and emergency flag together.
      const response = await sendChatMessage({
        session_id: "demo-session",
        message: trimmed,
      });

      setReply(response);
      // Append the assistant reply after the API request succeeds.
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.answer,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main>
      <header>
        <h1>First Aid AI Chatbot</h1>
        <p>Grounded first-aid guidance from approved medical sources.</p>
      </header>

      <EmergencyBanner
        emergency={reply?.emergency ?? false}
        recommendedAction={reply?.recommended_action}
      />

      {/* Conversation area */}
      <ChatWindow messages={messages} isLoading={isLoading} />

      <form onSubmit={handleSubmit}>
        <label htmlFor="chat-input">Ask a first-aid question</label>
        <textarea
          id="chat-input"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          rows={4}
        />
        <button type="submit" disabled={isLoading}>
          Send
        </button>
      </form>

      {/* Source list for the most recent assistant reply */}
      <SourceCitations citations={reply?.citations ?? []} />

      <footer>
        <small>{reply?.disclaimer}</small>
      </footer>
    </main>
  );
}
