import type { ChatMessage } from "../types/chat";

type MessageListProps = {
  messages: ChatMessage[];
};

export function MessageList({ messages }: MessageListProps) {
  return (
    <div>
      {messages.map((message) => (
        <article key={message.id}>
          <strong>{message.role === "user" ? "You" : "Assistant"}</strong>
          <p>{message.content}</p>
        </article>
      ))}
    </div>
  );
}
