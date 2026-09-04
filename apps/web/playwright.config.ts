import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  retries: 0,
  reporter: "line",
  use: { baseURL: "http://127.0.0.1:3210", trace: "retain-on-failure" },
  webServer: { command: "./node_modules/.bin/next start -p 3210", url: "http://127.0.0.1:3210", reuseExistingServer: true, timeout: 30_000 },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
