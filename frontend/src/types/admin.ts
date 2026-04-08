// Shared admin-related frontend types.
//
// These mirror the backend admin schemas used by the source-management page.
export type ApprovedSource = {
  id: number;
  title: string;
  organization: string;
  source_tier: "primary" | "supporting" | "other";
  source_url: string;
  content_path: string;
  summary: string;
  is_approved: boolean;
  chunk_count: number;
  is_searchable: boolean;
};

export type ApprovedSourceCreate = {
  title: string;
  organization: string;
  source_url: string;
  content_path: string;
  summary: string;
  raw_content: string;
};

export type ApprovedSourceUpdate = Partial<ApprovedSourceCreate> & {
  is_approved?: boolean;
};
