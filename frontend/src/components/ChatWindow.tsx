// Conversation container.
//
// This keeps the empty state, message list, and loading state visually grouped
// so the chat area feels like one continuous panel.
import type { ChatMessage } from "../types/chat";
import { MessageList } from "./MessageList";

type ChatWindowProps = {
  messages: ChatMessage[];
  isLoading: boolean;
};

export function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  return (
    <section className="chat-window">
      {/* Render the full conversation history in one place. */}
      {messages.length === 0 ? (
        <div className="empty-chat-state">
          <p className="empty-chat-title">Welcome to the First Aid AI Chatbot.</p>
          <p className="muted-text">
            Ask a first-aid question and get a grounded answer from approved medical sources.
          </p>
        </div>
      ) : (
        <MessageList messages={messages} />
      )}
      {isLoading ? <p className="help-text">Searching approved medical sources...</p> : null}
    </section>
  );
}
