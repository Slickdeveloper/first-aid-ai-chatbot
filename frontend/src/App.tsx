// Top-level app shell.
//
// This file decides whether the user sees the public chat experience or the
// admin/source-management view. For this project, a lightweight state-based
// switch is enough instead of a full routing library.
import { useMemo, useState } from "react";

import { ChatPage } from "./pages/ChatPage";
import { AdminPage } from "./pages/AdminPage";

export default function App() {
  // Read the initial page from the URL once so demo links can open directly on
  // the admin screen when needed.
  const initialPage = useMemo<"chat" | "admin">(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get("page") === "admin" ? "admin" : "chat";
  }, []);
  const [page, setPage] = useState<"chat" | "admin">(initialPage);

  // Keep public chat and admin tools in one app, but as separate page-level views.
  return page === "chat" ? (
    <ChatPage onOpenAdmin={() => setPage("admin")} />
  ) : (
    <AdminPage onBackToChat={() => setPage("chat")} />
  );
}
