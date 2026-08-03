const fs = require("fs");
const path = require("path");

function resolvePlaywright() {
  if (process.env.PLAYWRIGHT_PATH) {
    try {
      return require(process.env.PLAYWRIGHT_PATH);
    } catch {
      // fall through to standard resolution
    }
  }
  try {
    return require("playwright");
  } catch {
    // fall through to the repo-local install
  }
  try {
    return require(path.join(__dirname, "..", "node_modules", "playwright"));
  } catch {
    // fall through
  }
  throw new Error(
    "Playwright not found. Run `npm install` at the repository root, then `npx playwright install chromium`."
  );
}

const { chromium } = resolvePlaywright();

const ROOT = path.resolve(__dirname, "..");
const SHOTS = path.join(ROOT, "screenshots");
const BASE = "http://127.0.0.1:5173";
fs.mkdirSync(SHOTS, { recursive: true });

const errors = [];

function watch(page) {
  page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(`console: ${message.text()}`);
  });
}

async function shot(page, name) {
  await page.screenshot({ path: path.join(SHOTS, name), fullPage: false });
  console.log(`saved ${name}`);
}

async function loginHost(page) {
  // Start from a deterministic game state so trade steps never depend on a
  // previously persisted market day.
  const reset = await page.request.post(`${BASE}/api/game/reset`);
  if (!reset.ok()) throw new Error(`game reset failed: ${reset.status()}`);
  await page.goto(BASE, { waitUntil: "domcontentloaded" });
  await page.evaluate(() => {
    localStorage.clear();
    localStorage.setItem("cms-lang", "en");
  });
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.waitForSelector("text=Login", { timeout: 20000 });
  await page.locator(".panel input").first().fill("host");
  await page.locator(".panel input").nth(1).fill("123456");
  await page.locator(".panel > div > .btn-primary").click();
  await waitForDashboard(page);
}

async function waitForDashboard(page) {
  await page.waitForSelector("text=Portfolio value", { timeout: 20000 });
  await page.waitForSelector("text=Market movers", { timeout: 15000 });
  await page.waitForSelector("text=Era Chronicle", { timeout: 15000 });
  await page.waitForTimeout(800);
}

async function canvasCheck(page, label) {
  const result = await page.evaluate(() => {
    const canvases = [...document.querySelectorAll("canvas")];
    if (canvases.length === 0) return { ok: false, reason: "no canvas" };
    const canvas = canvases[0];
    if (canvas.width < 80 || canvas.height < 40) {
      return { ok: false, reason: `tiny canvas ${canvas.width}x${canvas.height}` };
    }
    const ctx = canvas.getContext("2d");
    const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    let painted = 0;
    for (let i = 3; i < data.length; i += 16) {
      if (data[i] > 0) painted += 1;
    }
    return { ok: painted > 200, reason: `painted samples ${painted}` };
  });
  console.log(`${label}: ${result.ok ? "ok" : result.reason}`);
  if (!result.ok) errors.push(`${label}: ${result.reason}`);
}

(async () => {
  const browser = await chromium.launch({ channel: "msedge", headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  watch(page);

  await loginHost(page);
  await shot(page, "01-dashboard.png");

  await page.getByTitle("Market Records").click();
  await page.waitForSelector("text=Stock universe", { timeout: 15000 });
  await page.waitForTimeout(1200);
  await canvasCheck(page, "market price chart");
  await shot(page, "02-market.png");

  await page.locator(".panel input[type=number]").first().fill("10");
  await page.getByRole("button", { name: "Buy shares" }).click();
  await page.waitForSelector("text=Bought 10 BeiGene", { timeout: 15000 });
  await shot(page, "03-buy-toast.png");

  await page.getByRole("button", { name: "Advance Day" }).click();
  await page.waitForSelector("text=Trading day 1", { timeout: 20000 });
  await page.waitForTimeout(1200);
  await shot(page, "04-after-advance.png");

  await page.waitForSelector("text=Retail Era Archive", { timeout: 15000 });
  await shot(page, "15-retail-story.png");
  await page.getByRole("button", { name: "Got it" }).click();

  await page.getByTitle("Investor Journal").click();
  await page.waitForSelector("text=Holdings", { timeout: 15000 });
  await page.waitForTimeout(1000);
  await canvasCheck(page, "portfolio equity chart");
  await shot(page, "05-portfolio.png");

  await page.getByTitle("Analyst Notes").click();
  await page.waitForSelector("text=Portfolio health report", { timeout: 15000 });
  await page.getByRole("button", { name: "How is my diversification?" }).click();
  await page.waitForSelector("text=Diversification scores", { timeout: 15000 });
  await page.waitForTimeout(600);
  await shot(page, "06-advisor.png");

  await page.getByTitle("Milestones").click();
  await page.waitForSelector("text=Investment milestones", { timeout: 15000 });
  await page.waitForSelector("text=The Noodle Man", { timeout: 15000 });
  await page.waitForTimeout(800);
  await shot(page, "07-achievements.png");

  await page.getByTitle("Story Archive").click();
  await page.waitForSelector("text=Retail Era Archive", { timeout: 15000 });
  await page.waitForTimeout(800);
  await shot(page, "16-archive.png");
  await page.getByRole("button", { name: "Legend Dossiers" }).click();
  await page.waitForSelector("text=LG-2000-001", { timeout: 15000 });
  await page.waitForTimeout(600);
  await shot(page, "17-legends.png");
  await page.getByRole("button", { name: "Historical Timeline" }).click();
  await page.waitForSelector("text=1988", { timeout: 15000 });
  await page.waitForTimeout(600);
  await shot(page, "18-timeline.png");
  await page.getByRole("button", { name: "Chronicle Book" }).click();
  await page.waitForSelector("text=2021", { timeout: 15000 });
  await page.waitForTimeout(600);
  await shot(page, "19-chronicle-book.png");
  await page.getByTitle("Quest Book").click();
  await page.waitForSelector("text=Cash Sentinel", { timeout: 15000 });
  await page.waitForTimeout(600);
  await shot(page, "20-quest-book.png");
  await page.getByTitle("Milestones").click();
  await page.waitForSelector("text=Investment milestones", { timeout: 15000 });

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
  watch(mobile);
  await mobile.goto(BASE, { waitUntil: "domcontentloaded" });
  await mobile.evaluate(() => localStorage.clear());
  await mobile.reload({ waitUntil: "domcontentloaded" });
  await mobile.waitForSelector("text=登录", { timeout: 20000 });
  await mobile.evaluate(() => localStorage.setItem("cms-lang", "en"));
  await mobile.reload({ waitUntil: "domcontentloaded" });
  await mobile.waitForSelector("text=Login", { timeout: 20000 });
  await mobile.locator(".panel input").first().fill("host");
  await mobile.locator(".panel input").nth(1).fill("123456");
  await mobile.locator(".panel > div > .btn-primary").click();
  await waitForDashboard(mobile);
  await shot(mobile, "08-mobile-dashboard.png");
  await mobile.getByTitle("Market Records").click();
  await mobile.waitForSelector("text=Stock universe", { timeout: 15000 });
  await mobile.waitForTimeout(1000);
  await shot(mobile, "09-mobile-market.png");
  await mobile.getByTitle("Milestones").click();
  await mobile.waitForSelector("text=Investment milestones", { timeout: 15000 });
  await mobile.waitForTimeout(600);
  await shot(mobile, "10-mobile-achievements.png");

  // Chinese language check
  await page.getByRole("button", { name: "中文" }).click();
  await page.waitForSelector("text=组合市值", { timeout: 20000 });
  await page.waitForSelector("text=档案首页", { timeout: 15000 });
  await page.waitForTimeout(1000);
  await shot(page, "11-chinese-dashboard.png");

  await page.getByTitle("行情档案").click();
  await page.waitForSelector("text=股票池", { timeout: 15000 });
  await page.waitForTimeout(1000);
  await shot(page, "12-chinese-market.png");

  await page.getByTitle("分析师笔记").click();
  await page.waitForSelector("text=组合健康报告", { timeout: 15000 });
  await page.getByRole("button", { name: "我的分散化如何？" }).click();
  await page.waitForSelector("text=分散化得分", { timeout: 15000 });
  await page.waitForTimeout(600);
  await shot(page, "13-chinese-advisor.png");

  await page.getByTitle("投资里程碑").click();
  await page.waitForSelector("text=投资里程碑", { timeout: 15000 });
  await page.waitForTimeout(600);
  await shot(page, "14-chinese-achievements.png");

  await page.getByRole("button", { name: "EN" }).click();
  await page.waitForSelector("text=Portfolio value", { timeout: 15000 });

  await browser.close();
  if (errors.length > 0) {
    console.log("\nBrowser errors:");
    errors.forEach((error) => console.log("- " + error));
    process.exit(1);
  }
  console.log("\nAll visual checks passed.");
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
