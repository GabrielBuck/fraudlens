import { mkdir } from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const sourceDirectory = path.dirname(fileURLToPath(import.meta.url));
const outputDirectory = path.resolve(sourceDirectory, "../assets");
const htmlPath = path.resolve(sourceDirectory, "carousel.html");

const requireFromFrontend = createRequire(
  path.resolve(sourceDirectory, "../../../frontend/package.json"),
);
const { chromium } = requireFromFrontend("@playwright/test");

await mkdir(outputDirectory, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({
  viewport: { width: 1200, height: 1450 },
  deviceScaleFactor: 1,
});

try {
  await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);

  const slides = page.locator(".slide");
  const count = await slides.count();
  if (count !== 7) {
    throw new Error(`Expected 7 slides, found ${count}.`);
  }

  for (let index = 0; index < count; index += 1) {
    const slide = slides.nth(index);
    const outputName = await slide.getAttribute("data-output");
    const box = await slide.boundingBox();

    if (!outputName || !box) {
      throw new Error(`Slide ${index + 1} is missing output metadata.`);
    }
    if (Math.round(box.width) !== 1080 || Math.round(box.height) !== 1350) {
      throw new Error(
        `${outputName} has ${box.width}x${box.height}; expected 1080x1350.`,
      );
    }

    const visualIssues = await slide.evaluate((element) => {
      const slideBounds = element.getBoundingClientRect();
      const textOverflow = Array.from(element.querySelectorAll("*"))
        .filter((node) =>
          Array.from(node.childNodes).some(
            (child) =>
              child.nodeType === Node.TEXT_NODE && child.textContent?.trim(),
          ),
        )
        .filter((node) => {
          const bounds = node.getBoundingClientRect();
          return (
            bounds.left < slideBounds.left - 1 ||
            bounds.top < slideBounds.top - 1 ||
            bounds.right > slideBounds.right + 1 ||
            bounds.bottom > slideBounds.bottom + 1
          );
        })
        .map((node) => node.textContent?.trim().slice(0, 80));

      const brokenImages = Array.from(element.querySelectorAll("img"))
        .filter((image) => !image.complete || image.naturalWidth === 0)
        .map((image) => image.getAttribute("src"));

      return { textOverflow, brokenImages };
    });

    if (visualIssues.textOverflow.length || visualIssues.brokenImages.length) {
      throw new Error(
        `${outputName} visual validation failed: ${JSON.stringify(visualIssues)}`,
      );
    }

    await slide.screenshot({
      path: path.join(outputDirectory, outputName),
      animations: "disabled",
      caret: "hide",
    });
    console.log(`Created ${outputName} (1080x1350)`);
  }
} finally {
  await browser.close();
}
