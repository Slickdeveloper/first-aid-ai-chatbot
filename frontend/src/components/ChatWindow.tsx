import type { ChatMessage } from "../types/chat";
import { MessageList } from "./MessageList";

type ChatWindowProps = {
  messages: ChatMessage[];
  isLoading: boolean;
};

export function ChatWindow({ messages, isLoading }: ChatWindowProps) {
  return (
    <section>
      <h2>Chat</h2>
      {/* Render the full conversation history in one place. */}
      <MessageList messages={messages} />
      {isLoading ? <p>Loading response from approved sources...</p> : null}
    </section>
  );
}
