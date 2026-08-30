import { expect, test } from "@playwright/test";

test("completes the mock P0 research path", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Today" })).toBeVisible();
  await page.getByLabel("Ask a research question").fill("Which agent infrastructure layers can become durable platforms over three years?");
  await page.getByRole("button", { name: /Set up research/ }).click();
  await expect(page).toHaveURL(/\/new-research\?question=/);
  await page.getByRole("button", { name: "Continue to research plan" }).click();
  await expect(page.getByRole("heading", { name: "Review the research plan" })).toBeVisible();
  await page.getByRole("button", { name: "Start Research" }).click();
  await expect(page).toHaveURL(/\/research\/case-value-pools/);
  await expect(page.getByText("Structured findings before prose")).toBeVisible();

  await page.goto("/evidence");
  await expect(page.getByText("Supporting Evidence")).toBeVisible();
  await expect(page.getByText("Counter Evidence")).toBeVisible();
  await page.goto("/companies/figure");
  await expect(page.getByText("Material company signals")).toBeVisible();
  await page.goto("/thesis");
  await expect(page.getByText("When the thesis is wrong")).toBeVisible();
  await page.goto("/risks");
  await expect(page.getByRole("heading", { name: "Catalysts" })).toBeVisible();
  await page.goto("/monitor");
  await expect(page.getByText("What to monitor next")).toBeVisible();
  await page.goto("/review");
  await expect(page.getByText("Needs analyst decision")).toBeVisible();
  await page.goto("/brief");
  await expect(page.getByRole("heading", { name: "Executive Summary" })).toBeVisible();
  await page.goto("/versions");
  await expect(page.getByText("Structured version diff")).toBeVisible();
  await page.goto("/library");
  await expect(page.getByText("Scaling synthetic-to-real transfer")).toBeVisible();
});

test("keeps primary navigation usable on a mobile viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page.getByRole("link", { name: "Library" }).click();
  await expect(page).toHaveURL(/\/library/);
  await expect(page.getByRole("heading", { name: "Library" })).toBeVisible();
});
