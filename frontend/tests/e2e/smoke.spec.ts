import { expect, test } from "@playwright/test";

test("investigates and reviews an alert", async ({ page }) => {
  const browserIssues: string[] = [];
  page.on("console", (message) => {
    if (["error", "warning"].includes(message.type()))
      browserIssues.push(`${message.type()}: ${message.text()}`);
  });
  page.on("pageerror", (error) =>
    browserIssues.push(`pageerror: ${error.message}`),
  );

  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Visão geral de risco" }),
  ).toBeVisible();
  await expect(
    page.getByText("Volume monitorado", { exact: true }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Alertas", exact: true }).click();
  await expect(page).toHaveURL(/\/alerts$/);
  await page
    .getByRole("combobox", { name: "Severidade" })
    .selectOption("crítica");
  await page.getByRole("button", { name: "Aplicar filtros" }).click();
  await page
    .getByRole("link", { name: /Investigar alerta/ })
    .first()
    .click();
  await expect(
    page.getByText("Por que este evento foi sinalizado?"),
  ).toBeVisible();
  await page.getByLabel("Comentário da análise").fill("Revisão e2e sintética.");
  await page.getByRole("button", { name: "Marcar falso positivo" }).click();
  await expect(page.getByRole("status")).toContainText("sucesso");
  await page.getByRole("link", { name: /ACC-/ }).first().click();
  await expect(page.getByText("Linha do tempo transacional")).toBeVisible();
  await page.getByRole("link", { name: "Modelo" }).click();
  await expect(page.getByText(/IsolationForest/)).toBeVisible();
  expect(browserIssues).toEqual([]);
});
