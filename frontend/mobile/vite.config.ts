import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";

const sharedSrc = fileURLToPath(new URL("../shared/src", import.meta.url));

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // Match subpath imports "@app/shared/src/..." FIRST (longest prefix),
      // otherwise "@app/shared" -> shared/src would double the "src" segment.
      "@app/shared/src": sharedSrc,
      "@app/shared": sharedSrc,
    },
  },
  server: {
    port: 5174,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ""),
      },
    },
  },
});
