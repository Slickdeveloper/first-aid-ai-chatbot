// Conversation history renderer.
//
// The page hands message history to this component, which maps each message to
// a reusable chat bubble.
import type { ChatMessage } from "../types/chat";
import { ChatBubble } from "./ChatBubble";

type MessageListProps = {
  messages: ChatMessage[];
};

export function MessageList({ messages }: MessageListProps) {
  return (
    <div className="message-stack">
      {messages.map((message) => (
        <ChatBubble key={message.id} message={message} />
      ))}
    </div>
  );
}
