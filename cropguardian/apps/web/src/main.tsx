// Bootstrap. Stub — not yet built.
// Order: i18n (bn default) → QueryClient (retry policy aware of cold starts) → router.
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { AppRouter } from "./routes";

const root = document.getElementById("root");
if (!root) throw new Error("#root missing");

createRoot(root).render(
  <StrictMode>
    {/* TODO(sara): <I18nextProvider> <QueryClientProvider> <SyntheticBanner/> */}
    <AppRouter />
  </StrictMode>,
);
