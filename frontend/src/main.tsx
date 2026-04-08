// Frontend bootstrap file.
//
// This is the browser entry point that mounts the React app and loads the shared
// stylesheet used by both the chat and admin pages.
import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  // StrictMode helps catch risky patterns during development.
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
