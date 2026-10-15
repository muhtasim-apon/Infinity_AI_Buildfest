// Crop Guardian — Vite config. Not yet built.
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "Crop Guardian — ফসল রক্ষী",
        short_name: "ফসল রক্ষী",
        lang: "bn",
        start_url: "/app",
        display: "standalone",
        theme_color: "#1f6f43",
        background_color: "#f6f8f4",
        icons: [], // TODO(sara): 192/512 maskable icons
      },
      workbox: {
        // Cache the app shell and static disease guide; never cache API responses with personal data.
        navigateFallback: "/index.html",
        runtimeCaching: [],
      },
    }),
  ],
  build: { sourcemap: false, target: "es2020" },
});
