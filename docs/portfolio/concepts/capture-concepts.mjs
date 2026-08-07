import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const conceptDirectory = path.dirname(fileURLToPath(import.meta.url));
const htmlPath = path.join(conceptDirectory, "concepts.html");
const requireFromFrontend = createRequire(
  path.resolve(conceptDirectory, "../../../frontend/package.json"),
);
const { chromium } = requireFromFrontend("@playwright/test");

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({
  viewport: { width: 1200, height: 1450 },
  deviceScaleFactor: 1,
});

try {
  await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);

  const concepts = page.locator(".concept");
  const count = await concepts.count();
  if (count !== 3) {
    throw new Error(`Expected 3 concepts, found ${count}.`);
  }

  for (let index = 0; index < count; index += 1) {
    const concept = concepts.nth(index);
    const outputName = await concept.getAttribute("data-output");
    const box = await concept.boundingBox();

    if (!outputName || !box) {
      throw new Error(`Concept ${index + 1} is missing output metadata.`);
    }
    if (Math.round(box.width) !== 1080 || Math.round(box.height) !== 1350) {
      throw new Error(
        `${outputName} has ${box.width}x${box.height}; expected 1080x1350.`,
      );
    }

    const brokenImages = await concept.evaluate((element) =>
      Array.from(element.querySelectorAll("img"))
        .filter((image) => !image.complete || image.naturalWidth === 0)
        .map((image) => image.getAttribute("src")),
    );
    if (brokenImages.length) {
      throw new Error(`${outputName} has broken images: ${brokenImages}`);
    }

    await concept.screenshot({
      path: path.join(conceptDirectory, outputName),
      animations: "disabled",
      caret: "hide",
    });
    console.log(`Created ${outputName} (1080x1350)`);
  }
} finally {
  await browser.close();
}
