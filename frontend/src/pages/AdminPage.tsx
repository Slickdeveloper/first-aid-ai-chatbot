// Admin/source-management page.
//
// This screen manages the chatbot knowledge base. The public chat reads from the
// approved sources maintained here, but only admins can create or modify them.
import { FormEvent, useEffect, useState } from "react";

import {
  clearAdminKey,
  createApprovedSource,
  hasAdminKey,
  deleteApprovedSource,
  ingestApprovedSource,
  listApprovedSources,
  storeAdminKey,
  updateApprovedSource,
} from "../services/api";
import type { ApprovedSource, ApprovedSourceCreate } from "../types/admin";

const EMPTY_FORM: ApprovedSourceCreate = {
  // Shared blank form state used after successful creation.
  title: "",
  organization: "",
  source_url: "",
  content_path: "",
  summary: "",
  raw_content: "",
};

type AdminPageProps = {
  onBackToChat: () => void;
};

export function AdminPage({ onBackToChat }: AdminPageProps) {
  const [sources, setSources] = useState<ApprovedSource[]>([]);
  const [form, setForm] = useState<ApprovedSourceCreate>(EMPTY_FORM);
  const [adminKeyInput, setAdminKeyInput] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(hasAdminKey());
  const [isAddSourceOpen, setIsAddSourceOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Only load admin data after authentication succeeds.
    if (isAuthenticated) {
      void loadSources();
      return;
    }

    setIsLoading(false);
  }, [isAuthenticated]);

  async function loadSources() {
    // Pull the latest source state from the backend for this admin session.
    setIsLoading(true);
    setError(null);

    try {
      const nextSources = await listApprovedSources();
      setSources(nextSources);
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : "The admin page could not load approved sources.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleAdminLogin(event: FormEvent<HTMLFormElement>) {
    // Validate the shared admin key by attempting a protected API call.
    event.preventDefault();
    const trimmed = adminKeyInput.trim();
    if (!trimmed) {
      setError("Enter the admin access key to continue.");
      return;
    }

    setError(null);
    setIsLoading(true);
    storeAdminKey(trimmed);

    try {
      const nextSources = await listApprovedSources();
      setSources(nextSources);
      setIsAuthenticated(true);
      setAdminKeyInput("");
    } catch (caughtError) {
      clearAdminKey();
      setIsAuthenticated(false);
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : "Admin authentication failed.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    // Create a new approved source from the form and prepend it to the visible list.
    event.preventDefault();
    setIsSaving(true);
    setError(null);

    try {
      const created = await createApprovedSource(form);
      setSources((current) => [created, ...current]);
      setForm(EMPTY_FORM);
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : "The new source could not be saved.";
      setError(message);
    } finally {
      setIsSaving(false);
    }
  }

  async function handleApprovalToggle(source: ApprovedSource) {
    // Approval state directly controls whether retrieval can use the source.
    try {
      const updated = await updateApprovedSource(source.id, {
        is_approved: !source.is_approved,
      });
      setSources((current) =>
        current.map((entry) => (entry.id === updated.id ? updated : entry)),
      );
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : "The source approval state could not be updated.";
      setError(message);
    }
  }

  async function handleDelete(sourceId: number) {
    // Remove the record locally after the backend confirms deletion.
    try {
      await deleteApprovedSource(sourceId);
      setSources((current) => current.filter((entry) => entry.id !== sourceId));
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : "The source could not be deleted.";
      setError(message);
    }
  }

  async function handleIngest(sourceId: number) {
    // Re-ingest updates the searchable chunks without recreating the source entry.
    try {
      const updated = await ingestApprovedSource(sourceId);
      setSources((current) =>
        current.map((entry) => (entry.id === updated.id ? updated : entry)),
      );
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : "The source could not be ingested.";
      setError(message);
    }
  }

  function handleLogout() {
    // Logging out affects only the admin session, not the public chat page.
    clearAdminKey();
    setIsAuthenticated(false);
    setSources([]);
    setError(null);
    setIsAddSourceOpen(false);
  }

  if (!isAuthenticated) {
    // Public users never need to see the admin list, so we render a small sign-in view first.
    return (
      <main className="app-shell">
        <header className="hero-card">
          <div>
            <h1 className="hero-title">Approved Sources Admin</h1>
            <p className="hero-subtitle">
              Admin authentication is required before source-management tools can be used.
            </p>
          </div>
          <div className="hero-actions">
            <button className="secondary-button" type="button" onClick={onBackToChat}>
              Back to chat
            </button>
          </div>
        </header>

        <section className="panel-card admin-login-card">
          <h2 className="panel-title">Admin sign in</h2>
          <p className="section-copy">
            Enter the shared admin key to view, ingest, approve, or delete source documents.
          </p>
          <form className="input-form" onSubmit={handleAdminLogin}>
            <label className="field-label" htmlFor="admin-key">
              Admin access key
              <input
                id="admin-key"
                type="password"
                value={adminKeyInput}
                onChange={(event) => setAdminKeyInput(event.target.value)}
                placeholder="Enter admin key"
              />
            </label>
            <div className="input-actions">
              <span className="muted-text">This does not affect the public chat page.</span>
              <button type="submit" disabled={isLoading}>
                {isLoading ? "Checking..." : "Sign in"}
              </button>
            </div>
          </form>
          {error ? <p className="error-text">{error}</p> : null}
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="hero-card">
        <div>
          <h1 className="hero-title">Approved Sources Admin</h1>
          <p className="hero-subtitle">
            Review and maintain the approved first-aid sources behind the chatbot.
          </p>
        </div>
        <div className="hero-actions">
          <button className="secondary-button" type="button" onClick={handleLogout}>
            Log out
          </button>
          <button className="secondary-button" type="button" onClick={onBackToChat}>
            Back to chat
          </button>
        </div>
      </header>

      <div className="admin-layout">
        <div className="admin-grid">
          <section className="panel-card">
            <h2 className="panel-title">Knowledge base overview</h2>
            <p className="muted-text">
              Approved topics become searchable after ingestion. Use re-ingest whenever content
              changes.
            </p>
            <div className="stat-grid">
              <article className="stat-card">
                <span className="stat-label">Total sources</span>
                <strong className="stat-value">{sources.length}</strong>
              </article>
              <article className="stat-card">
                <span className="stat-label">Primary sources</span>
                <strong className="stat-value">
                  {sources.filter((source) => source.source_tier === "primary").length}
                </strong>
              </article>
              <article className="stat-card">
                <span className="stat-label">Supporting sources</span>
                <strong className="stat-value">
                  {sources.filter((source) => source.source_tier === "supporting").length}
                </strong>
              </article>
              <article className="stat-card">
                <span className="stat-label">Searchable topics</span>
                <strong className="stat-value">
                  {sources.filter((source) => source.is_searchable).length}
                </strong>
              </article>
            </div>
          </section>

          <section className="panel-card">
            <div className="collapsible-header">
              <div>
                <h2 className="panel-title">Add approved source</h2>
                <p className="section-copy">
                  Add reviewed source content only when it has been checked for accuracy and fit.
                  Store canonical source files under <code>data/sources/</code>.
                </p>
              </div>
              <button
                className="secondary-button"
                type="button"
                onClick={() => setIsAddSourceOpen((current) => !current)}
              >
                {isAddSourceOpen ? "Hide form" : "Add source"}
              </button>
            </div>

            {isAddSourceOpen ? (
              <form className="form-grid admin-form" onSubmit={handleSubmit}>
                <label className="field-label" htmlFor="source-title">
                  Title
                  <input
                    id="source-title"
                    value={form.title}
                    onChange={(event) =>
                      setForm((current) => ({ ...current, title: event.target.value }))
                    }
                    required
                  />
                </label>

                <label className="field-label" htmlFor="source-organization">
                  Organization
                  <input
                    id="source-organization"
                    value={form.organization}
                    onChange={(event) =>
                      setForm((current) => ({ ...current, organization: event.target.value }))
                    }
                    required
                  />
                </label>

                <label className="field-label" htmlFor="source-url">
                  Official source URL
                  <input
                    id="source-url"
                    type="url"
                    value={form.source_url}
                    onChange={(event) =>
                      setForm((current) => ({ ...current, source_url: event.target.value }))
                    }
                    required
                  />
                </label>

                <label className="field-label" htmlFor="source-path">
                  Local content path
                  <input
                    id="source-path"
                    value={form.content_path}
                    onChange={(event) =>
                      setForm((current) => ({ ...current, content_path: event.target.value }))
                    }
                    placeholder="data/sources/my-approved-topic.md"
                    required
                  />
                </label>

                <label className="field-label" htmlFor="source-summary">
                  Summary
                  <textarea
                    id="source-summary"
                    rows={3}
                    value={form.summary}
                    onChange={(event) =>
                      setForm((current) => ({ ...current, summary: event.target.value }))
                    }
                  />
                </label>

                <label className="field-label field-span-full" htmlFor="source-content">
                  Approved source content
                  <textarea
                    id="source-content"
                    rows={8}
                    value={form.raw_content}
                    onChange={(event) =>
                      setForm((current) => ({ ...current, raw_content: event.target.value }))
                    }
                    placeholder="Paste the reviewed first-aid content that should be chunked for retrieval."
                    required
                  />
                </label>

                <div className="admin-form-actions field-span-full">
                  <button type="submit" disabled={isSaving}>
                    {isSaving ? "Saving and ingesting..." : "Add source"}
                  </button>
                </div>
              </form>
            ) : null}
          </section>
        </div>

        <section className="panel-card">
          <h2 className="panel-title">Approved topic list</h2>
          {isLoading ? <p className="help-text">Loading approved sources...</p> : null}
          {error ? <p className="error-text">{error}</p> : null}

          {!isLoading && sources.length === 0 ? (
            <p className="muted-text">No approved sources have been added yet.</p>
          ) : null}

          <div className="admin-source-grid">
            {sources.map((source) => (
              <article className="admin-source-card" key={source.id}>
                <div className="source-card-header">
                  <div>
                    <h3 className="source-title">{source.title}</h3>
                    <p className="source-organization">{source.organization}</p>
                  </div>
                  <span
                    className={`tier-badge ${
                      source.source_tier === "primary"
                        ? "tier-primary"
                        : source.source_tier === "supporting"
                          ? "tier-supporting"
                          : "tier-other"
                    }`}
                  >
                    {source.source_tier}
                  </span>
                </div>
                <p className="source-summary">{source.summary}</p>
                <div className="source-chip-row">
                  <span className="source-chip">
                    Status: {source.is_approved ? "Approved" : "Not approved"}
                  </span>
                  <span className="source-chip">Chunks: {source.chunk_count}</span>
                  <span className="source-chip">
                    Searchable: {source.is_searchable ? "Yes" : "No"}
                  </span>
                </div>
                <details className="source-meta">
                  <summary>Show details</summary>
                  <p>
                    <a href={source.source_url} target="_blank" rel="noreferrer">
                      Open official source
                    </a>
                  </p>
                  <p className="muted-text">Local content path: {source.content_path}</p>
                </details>
                <div className="source-actions">
                  <button
                    className="primary-action-button"
                    type="button"
                    onClick={() => handleIngest(source.id)}
                  >
                    Re-ingest
                  </button>
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => handleApprovalToggle(source)}
                  >
                    {source.is_approved ? "Unapprove" : "Approve"}
                  </button>
                  <button
                    className="danger-button"
                    type="button"
                    onClick={() => handleDelete(source.id)}
                  >
                    Delete
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
