// Individual chat bubble renderer.
//
// Assistant answers are reorganized into sections so first-aid instructions are
// easier to scan than a single long paragraph.
import type { ChatMessage } from "../types/chat";

type ChatBubbleProps = {
  message: ChatMessage;
};

type AssistantSections = {
  intro: string | null;
  immediate: string[];
  emergency: string[];
  avoid: string[];
};

function splitSteps(content: string): string[] {
  // The backend formats grounded procedures as numbered "Step X:" text.
  if (!content.includes("Step 1:")) {
    return [];
  }

  return content
    .split(/(?=Step \d+:)/)
    .map((step) => step.trim())
    .filter(Boolean)
    .filter((step) => /^Step \d+:/.test(step))
    .map((step) => step.replace(/^Step \d+:\s*/, "").trim());
}

function getAssistantIntro(content: string): string | null {
  // Emergency answers often start with a warning sentence before the numbered steps.
  const [beforeSteps] = content.split(/(?=Step 1:)/);
  const trimmed = beforeSteps.trim();
  return trimmed.length > 0 && !trimmed.startsWith("Step 1:") ? trimmed : null;
}

function classifyAssistantContent(content: string): AssistantSections {
  // This is presentation-only categorization. It does not change the medical content.
  const intro = getAssistantIntro(content);
  const steps = splitSteps(content);

  if (steps.length === 0) {
    return {
      intro,
      immediate: content ? [content] : [],
      emergency: [],
      avoid: [],
    };
  }

  const immediate: string[] = [];
  const emergency: string[] = [];
  const avoid: string[] = [];

  for (const step of steps) {
    const normalized = step.toLowerCase();

    if (/\b(do not|don't|never|avoid)\b/.test(normalized)) {
      avoid.push(step);
      continue;
    }

    if (
      /\b(call|emergency|ambulance|112|urgent|seek medical|seek immediate|hospital|aed)\b/.test(
        normalized,
      )
    ) {
      emergency.push(step);
      continue;
    }

    immediate.push(step);
  }

  return { intro, immediate, emergency, avoid };
}

function SectionList({ title, items, tone }: { title: string; items: string[]; tone?: string }) {
  // Reusable list section for assistant subheadings such as "Immediate Action".
  if (items.length === 0) {
    return null;
  }

  return (
    <section className={`assistant-section ${tone ?? ""}`.trim()}>
      <h4>{title}</h4>
      <ul>
        {items.map((item) => (
          <li key={`${title}-${item}`}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

export function ChatBubble({ message }: ChatBubbleProps) {
  // Only assistant messages need section parsing; user messages are shown as typed.
  const assistantSections =
    message.role === "assistant" ? classifyAssistantContent(message.content) : null;

  return (
    <article className={`message-row ${message.role}`}>
      <div className={`message-card ${message.role === "user" ? "user" : "assistant"}`}>
        <strong className="message-label">
          {message.role === "user" ? "You" : "Assistant"}
        </strong>

        {message.role === "assistant" && assistantSections ? (
          <div className="assistant-body">
            {assistantSections.intro ? (
              <p className="assistant-intro">{assistantSections.intro}</p>
            ) : null}
            <SectionList title="Immediate Action" items={assistantSections.immediate} />
            <SectionList
              title="When to Call Emergency Services"
              items={assistantSections.emergency}
              tone="emergency"
            />
            <SectionList title="What NOT to Do" items={assistantSections.avoid} tone="avoid" />
          </div>
        ) : (
          <p className="message-copy">{message.content}</p>
        )}
      </div>
    </article>
  );
}
