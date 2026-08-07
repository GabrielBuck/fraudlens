import { mkdir, readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const sourceDirectory = path.dirname(fileURLToPath(import.meta.url));
const outputDirectory = path.resolve(sourceDirectory, "../assets");
const feedDirectory = path.resolve(outputDirectory, "feed");
const htmlPath = path.resolve(sourceDirectory, "carousel.html");

const requireFromFrontend = createRequire(
  path.resolve(sourceDirectory, "../../../frontend/package.json"),
);
const { chromium } = requireFromFrontend("@playwright/test");

await mkdir(outputDirectory, { recursive: true });
await mkdir(feedDirectory, { recursive: true });

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

    await slide.evaluate((element) => {
      element.style.transform = "scale(0.3333333333)";
      element.style.transformOrigin = "top left";
    });
    const feedBox = await slide.boundingBox();
    if (
      !feedBox ||
      Math.round(feedBox.width) !== 360 ||
      Math.round(feedBox.height) !== 450
    ) {
      throw new Error(
        `${outputName} feed preview is not exactly 360x450: ${JSON.stringify(feedBox)}`,
      );
    }
    await slide.screenshot({
      path: path.join(feedDirectory, outputName),
      animations: "disabled",
      caret: "hide",
    });
    await slide.evaluate((element) => {
      element.style.removeProperty("transform");
      element.style.removeProperty("transform-origin");
    });
    console.log(`Created feed/${outputName} (360x450)`);
  }

  const slideSources = await Promise.all(
    Array.from({ length: count }, async (_, index) => {
      const outputName = await slides.nth(index).getAttribute("data-output");
      const png = await readFile(path.join(outputDirectory, outputName));
      return `data:image/png;base64,${png.toString("base64")}`;
    }),
  );
  const contactPage = await browser.newPage({
    viewport: { width: 1200, height: 2800 },
    deviceScaleFactor: 1,
  });
  await contactPage.setContent(`
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <style>
          * { box-sizing: border-box; }
          html, body { margin: 0; background: #020303; }
          .sheet {
            width: 1080px;
            padding: 42px;
            color: #e7e5df;
            background: #07090b;
            font-family: Consolas, "Courier New", monospace;
          }
          header {
            height: 88px;
            display: flex;
            align-items: start;
            justify-content: space-between;
            border-bottom: 2px solid #ff3b30;
          }
          header strong { font: 42px Impact, "Arial Narrow", sans-serif; letter-spacing: 1px; }
          header span { color: #858b8f; font-size: 11px; letter-spacing: 1px; }
          .grid {
            padding-top: 24px;
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 24px;
          }
          figure { margin: 0; }
          img { width: 486px; height: 608px; display: block; object-fit: cover; }
          figcaption {
            padding: 10px 0 2px;
            color: #858b8f;
            font-size: 10px;
            letter-spacing: 1px;
          }
        </style>
      </head>
      <body>
        <section class="sheet">
          <header><strong>FRAUDLENS / VISUAL RHYTHM</strong><span>FINANCIAL FORENSICS · 07 SLIDES</span></header>
          <div class="grid">
            ${slideSources
              .map(
                (source, index) =>
                  `<figure><img src="${source}" /><figcaption>0${index + 1} / INVESTIGATION FILE</figcaption></figure>`,
              )
              .join("")}
          </div>
        </section>
      </body>
    </html>
  `);
  await contactPage.waitForFunction(() =>
    Array.from(document.images).every(
      (image) => image.complete && image.naturalWidth > 0,
    ),
  );
  await contactPage.locator(".sheet").screenshot({
    path: path.join(outputDirectory, "carousel-contact-sheet.png"),
    animations: "disabled",
    caret: "hide",
  });
  await contactPage.close();
  console.log("Created carousel-contact-sheet.png");
} finally {
  await browser.close();
}
