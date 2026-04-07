import type { Citation } from "../types/chat";

type SourceCitationsProps = {
  citations: Citation[];
};

export function SourceCitations({ citations }: SourceCitationsProps) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <section>
      <h3>Sources</h3>
      {/* Citations reinforce that medical guidance came from approved material. */}
      <ul>
        {citations.map((citation) => (
          <li key={`${citation.organization}-${citation.url}`}>
            <a href={citation.url} target="_blank" rel="noreferrer">
              {citation.organization}: {citation.title}
            </a>
            <p>{citation.excerpt}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
