# Frontend

React + TypeScript client for the First Aid AI Chatbot.

This is the part of the system the user sees. It is responsible for:

- collecting questions
- showing grounded answers
- highlighting emergencies clearly
- displaying citations
- exposing the admin/source-management workflow

## Main Views

- chat page for end users
- emergency warning banner
- collapsible source/citation cards
- admin/source-management page with shared-key sign-in

## Important Files

- `src/pages/ChatPage.tsx`
- `src/pages/AdminPage.tsx`
- `src/components/ChatWindow.tsx`
- `src/components/EmergencyBanner.tsx`
- `src/components/SourceCitations.tsx`
- `src/styles.css`

If you want to understand the frontend quickly, start with:

1. `src/App.tsx`
2. `src/pages/ChatPage.tsx`
3. `src/services/api.ts`
4. `src/components/ChatBubble.tsx`
5. `src/pages/AdminPage.tsx`

## Local Start

```powershell
cd frontend
npm install
npm run dev
```

If `5173` is busy, Vite may choose another port such as `5174`.

## Admin Access

The admin page now requires a shared admin key. Sign in from the admin screen with the same `ADMIN_API_KEY` configured in the backend.

## Current Limitations

- the frontend depends on the backend being available at the configured API base URL
- if the backend database has not been seeded through ingestion, the admin page will show zero sources and the chatbot may refuse otherwise supported topics
- the admin flow uses a shared key rather than a full login/session system
