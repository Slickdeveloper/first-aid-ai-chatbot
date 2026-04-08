// Citation panel for the latest assistant answer.
//
// Keeping citations separate from the message bubble helps users inspect evidence
// without interrupting the chat flow.
import type { Citation } from "../types/chat";
import { SourceCard } from "./SourceCard";

type SourceCitationsProps = {
  citations: Citation[];
};

export function SourceCitations({ citations }: SourceCitationsProps) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <section className="panel-card">
      <h3 className="panel-title">Sources / Citations</h3>
      {/* Citations reinforce that medical guidance came from approved material. */}
      <div className="source-grid">
        {citations.map((citation) => (
          <SourceCard
            key={`${citation.organization}-${citation.url}-${citation.title}`}
            citation={citation}
          />
        ))}
      </div>
    </section>
  );
}
