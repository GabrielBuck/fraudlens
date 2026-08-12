import { expect, test, type Page } from "@playwright/test";

async function gotoHydrated(page: Page, path: string) {
  await page.goto(path);
  await page.waitForLoadState("networkidle");
  await page.locator("main").waitFor();
  await page.waitForTimeout(100);
}

test("captures product views", async ({ page }) => {
  const browserIssues: string[] = [];
  page.on("console", (message) => {
    if (["error", "warning"].includes(message.type()))
      browserIssues.push(`${message.type()}: ${message.text()}`);
  });
  page.on("pageerror", (error) =>
    browserIssues.push(`pageerror: ${error.message}`),
  );

  await page.setViewportSize({ width: 1440, height: 960 });
  await gotoHydrated(page, "/");
  await page.locator(".recharts-wrapper").first().waitFor();
  await page.waitForTimeout(700);
  await page.screenshot({ path: "../docs/images/overview.png" });
  await gotoHydrated(page, "/alerts");
  await page.screenshot({ path: "../docs/images/alerts.png" });
  const alertLink = page
    .getByRole("link", { name: /Investigar alerta/ })
    .first();
  await expect(alertLink).toBeVisible();
  await alertLink.click();
  await page.waitForLoadState("networkidle");
  await expect(
    page.getByRole("heading", { name: /Prioridade de investiga/ }),
  ).toBeVisible();
  await page.screenshot({ path: "../docs/images/alert-detail.png" });
  await gotoHydrated(page, "/network");
  await page.locator(".react-flow__node").first().waitFor();
  await page.waitForTimeout(500);
  await page.screenshot({ path: "../docs/images/network.png" });
  await gotoHydrated(page, "/model");
  await page.locator(".recharts-wrapper").first().waitFor();
  await page.waitForTimeout(700);
  await page.screenshot({ path: "../docs/images/model.png" });
  await gotoHydrated(page, "/accounts");
  await page.screenshot({ path: "../docs/images/accounts.png" });
  const accountLink = page.getByRole("link", { name: /ACC-/ }).first();
  await expect(accountLink).toBeVisible();
  await accountLink.click();
  await page.waitForLoadState("networkidle");
  await expect(page.getByText("Linha do tempo transacional")).toBeVisible();
  await page.screenshot({ path: "../docs/images/account.png" });
  await page.setViewportSize({ width: 1200, height: 627 });
  await gotoHydrated(page, "/social-card");
  await page.screenshot({ path: "../docs/images/social-preview.png" });
  expect(browserIssues).toEqual([]);
});
