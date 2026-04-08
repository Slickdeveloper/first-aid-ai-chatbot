// Main user-facing chat page.
//
// This component coordinates:
// - the message input
// - conversation history
// - emergency UI state
// - source/citation display for the most recent answer
import { FormEvent, useEffect, useState } from "react";

import { ChatWindow } from "../components/ChatWindow";
import { EmergencyBanner } from "../components/EmergencyBanner";
import { SourceCitations } from "../components/SourceCitations";
import { sendChatMessage } from "../services/api";
import type { ChatMessage, ChatReply } from "../types/chat";

type ChatPageProps = {
  onOpenAdmin: () => void;
};

const QUICK_PROMPTS = [
  // Suggested prompts reduce empty-state friction for first-time users.
  "Someone is bleeding heavily, what should I do?",
  "Someone is choking and can't breathe!",
  "How do I perform CPR?",
  "What should I do if someone's face is drooping?",
];

const DEMO_SUCCESS_REPLY: ChatReply = {
  answer:
    "Step 1: Cool the burned area under cool running water for at least 20 minutes as soon as possible. Step 2: Remove rings, watches, or tight clothing near the burn before swelling begins, but do not remove anything stuck to the skin. Step 3: Cover the burn loosely with clean cling film or a sterile, non-fluffy dressing. Step 4: Do not apply ice, butter, toothpaste, or oily creams to the burn. Step 5: Seek urgent medical help for burns on the face, hands, feet, genitals, very large burns, or if the person has trouble breathing.",
  citations: [
    {
      title: "Burns First Aid (Chunk 1)",
      organization: "World Health Organization",
      url: "https://www.who.int/news-room/fact-sheets/detail/burns/",
      excerpt:
        "Stop the burning process by removing smouldering clothing if it is safe to do so and by cooling the burn. Use cool running water to reduce the temperature of the burn.",
    },
  ],
  disclaimer:
    "This chatbot provides first-aid guidance from approved sources and does not replace professional medical diagnosis, treatment, or certified training.",
  emergency: false,
  recommended_action: null,
};

const DEMO_EMERGENCY_REPLY: ChatReply = {
  answer:
    "This may be an emergency. Call 112 in Ghana immediately. Police: 191, Fire: 192, Ambulance: 193. and follow the first-aid steps below while help is on the way.\n\nStep 1: Protect the person from nearby hazards during the seizure. Step 2: Do not restrain their movements and do not put anything in the mouth. Step 3: When the seizure stops, place the person on their side if safe. Step 4: Call emergency services if the seizure lasts longer than 5 minutes.",
  citations: [
    {
      title: "Seizures (paraphrased from IFRC guidelines, Chunk 1)",
      organization: "IFRC",
      url: "https://www.ifrc.org/document/international-first-aid-resuscitation-and-education-guidelines",
      excerpt:
        "Protect the person from nearby hazards during the seizure. Do not restrain their movements and do not put anything in the mouth. When the seizure stops, place the person on their side and monitor breathing.",
    },
  ],
  disclaimer:
    "This chatbot provides first-aid guidance from approved sources and does not replace professional medical diagnosis, treatment, or certified training.",
  emergency: true,
  recommended_action:
    "Call 112 in Ghana immediately. Police: 191, Fire: 192, Ambulance: 193.",
};

export function ChatPage({ onOpenAdmin }: ChatPageProps) {
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [reply, setReply] = useState<ChatReply | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Demo query parameters create stable screenshot-ready states without needing
    // live typing every time.
    const params = new URLSearchParams(window.location.search);
    const demo = params.get("demo");

    if (demo === "successful") {
      setMessages([
        {
          id: "demo-success-user",
          role: "user",
          content: "I burned my hand, what should I do?",
        },
        {
          id: "demo-success-assistant",
          role: "assistant",
          content: DEMO_SUCCESS_REPLY.answer,
        },
      ]);
      setReply(DEMO_SUCCESS_REPLY);
      return;
    }

    if (demo === "emergency") {
      setMessages([
        {
          id: "demo-emergency-user",
          role: "user",
          content: "Someone is having a seizure, what should I do?",
        },
        {
          id: "demo-emergency-assistant",
          role: "assistant",
          content: DEMO_EMERGENCY_REPLY.answer,
        },
      ]);
      setReply(DEMO_EMERGENCY_REPLY);
    }
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    // Main frontend -> backend chat flow.
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
    setError(null);
    setReply(null);

    try {
      // The backend returns the answer, citations, disclaimer, and emergency flag together.
      const response = await sendChatMessage({
        session_id: "demo-session",
        message: trimmed,
      });

      setReply(response);
      // Append the assistant reply only after the API succeeds so the chat history
      // reflects actual backend responses.
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.answer,
        },
      ]);
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : "The chatbot could not reach the backend.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="hero-card">
        <div>
          <h1 className="hero-title">First Aid AI Chatbot</h1>
          <p className="hero-subtitle">
            Calm, source-backed first-aid guidance from approved medical references.
          </p>
        </div>
        <div className="hero-actions">
          <button className="secondary-button" type="button" onClick={onOpenAdmin}>
            Manage sources
          </button>
        </div>
      </header>

      <div className="page-grid">
        <section className="conversation-panel panel-card">
          <EmergencyBanner
            emergency={reply?.emergency ?? false}
            recommendedAction={reply?.recommended_action}
          />

          <div className="chat-panel-header">
            <div>
              <h2 className="panel-title">Chat</h2>
              <p className="section-copy">
                Grounded guidance with clear actions, emergency escalation, and citations.
              </p>
            </div>
          </div>

          <ChatWindow messages={messages} isLoading={isLoading} />

          {messages.length === 0 ? (
            <div className="quick-prompts">
              <p className="quick-prompts-label">Suggested prompts</p>
              <div className="quick-prompt-row">
                {QUICK_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    className="quick-prompt-chip"
                    type="button"
                    onClick={() => setInput(prompt)}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          <section className="composer-card">
            <form className="input-form" onSubmit={handleSubmit}>
              <textarea
                id="chat-input"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                rows={3}
                placeholder="Ask a first aid question…"
              />
              <div className="input-actions">
                <span className="muted-text">Answers come only from approved medical sources.</span>
                <button type="submit" disabled={isLoading}>
                  Send
                </button>
              </div>
            </form>

            {error ? <p className="error-text">{error}</p> : null}
          </section>
        </section>

        <aside>
          {/* Source list for the most recent assistant reply */}
          <SourceCitations citations={reply?.citations ?? []} />

          <footer className="panel-card disclaimer">
            <h3 className="panel-title">Safety note</h3>
            <p className="muted-text">
              {reply?.disclaimer ??
                "This chatbot provides first-aid guidance from approved sources and does not replace professional medical diagnosis, treatment, or certified training."}
            </p>
          </footer>
        </aside>
      </div>
    </main>
  );
}
