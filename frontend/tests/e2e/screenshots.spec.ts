import { expect, test } from "@playwright/test";

test("captures portfolio views", async ({ page }) => {
  const browserIssues: string[] = [];
  page.on("console", (message) => {
    if (["error", "warning"].includes(message.type()))
      browserIssues.push(`${message.type()}: ${message.text()}`);
  });
  page.on("pageerror", (error) =>
    browserIssues.push(`pageerror: ${error.message}`),
  );

  await page.setViewportSize({ width: 1440, height: 960 });
  await page.goto("/");
  await page.locator(".recharts-wrapper").first().waitFor();
  await page.waitForTimeout(700);
  await page.screenshot({ path: "../docs/images/overview.png" });
  await page.goto("/alerts");
  await page.screenshot({ path: "../docs/images/alerts.png" });
  const alertLink = page
    .getByRole("link", { name: /Investigar alerta/ })
    .first();
  if (await alertLink.count()) {
    await alertLink.click();
    await page.screenshot({ path: "../docs/images/alert-detail.png" });
  }
  await page.goto("/network");
  await page.locator(".react-flow__node").first().waitFor();
  await page.waitForTimeout(500);
  await page.screenshot({ path: "../docs/images/network.png" });
  await page.goto("/model");
  await page.locator(".recharts-wrapper").first().waitFor();
  await page.waitForTimeout(700);
  await page.screenshot({ path: "../docs/images/model.png" });
  await page.setViewportSize({ width: 1200, height: 627 });
  await page.goto("/social-card");
  await page.screenshot({ path: "../docs/images/linkedin-cover.png" });
  expect(browserIssues).toEqual([]);
});
