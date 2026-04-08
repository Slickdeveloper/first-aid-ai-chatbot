// Collapsible source card.
//
// Source details are collapsed by default so evidence is available without making
// the sidebar feel visually heavy.
import { useState } from "react";

import type { Citation } from "../types/chat";

type SourceCardProps = {
  citation: Citation;
};

export function SourceCard({ citation }: SourceCardProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <article className="source-card">
      <div className="source-card-header">
        <div>
          <p className="source-organization">{citation.organization}</p>
          <p className="source-title">{citation.title}</p>
        </div>
        <button
          className="source-toggle"
          type="button"
          onClick={() => setIsOpen((current) => !current)}
        >
          {isOpen ? "Hide details" : "Show details"}
        </button>
      </div>
      <p className="source-snippet">{citation.excerpt}</p>
      {isOpen ? (
        <div className="source-details">
          <p className="source-excerpt">{citation.excerpt}</p>
          <a className="source-link" href={citation.url} target="_blank" rel="noreferrer">
            View Source
          </a>
        </div>
      ) : null}
    </article>
  );
}
