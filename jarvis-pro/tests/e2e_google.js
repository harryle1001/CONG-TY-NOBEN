// End-to-end test against tests/fake_google.py: OAuth (authorize → callback → code exchange → token saved → refresh),
// Gmail + Calendar reads, error display, demo mode untouched. Run from jarvis-pro/:  node tests/e2e_google.js
"use strict";
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs"), os = require("os"), path = require("path");

const ROOT = path.resolve(__dirname, "..");
const FAKE = 9631, REAL = 8631, DEMO = 8632;
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), "jarvis-g-"));
const TOKEN = path.join(TMP, "token.json");
const procs = [];
let failed = 0;
const ok = (c, m) => { console.log((c ? "  PASS " : "  FAIL ") + m); if (!c) failed++; };
const sleep = ms => new Promise(r => setTimeout(r, ms));

function start(args, env) {
  const p = spawn("python3", args, { cwd: ROOT, env: { ...process.env, ...env }, stdio: ["ignore", "pipe", "pipe"] });
  p.stdout.on("data", d => process.stdout.write("    | " + d));
  p.stderr.on("data", d => process.stdout.write("    ! " + d));
  procs.push(p); return p;
}
async function up(url) { for (let i = 0; i < 100; i++) { try { await fetch(url); return; } catch { await sleep(100); } } throw new Error("not up: " + url); }
const control = q => fetch(`http://127.0.0.1:${FAKE}/_control?${q}`).then(r => r.json());

async function lastReply(page) { await page.waitForSelector("#reply .say:not(:has(.dots))"); return page.locator("#reply").innerText(); }

(async () => {
  start(["tests/fake_google.py", String(FAKE)], {});
  const base = { JARVIS_DEMO: "0", JARVIS_SOURCES: path.join(ROOT, "data", "demo"), JARVIS_INBOX: "google", JARVIS_CALENDAR: "google",
    GOOGLE_API_BASE: `http://127.0.0.1:${FAKE}`, GOOGLE_CLIENT_ID: "fake-client.apps.googleusercontent.com",
    GOOGLE_CLIENT_SECRET: "fake-secret", JARVIS_GOOGLE_TOKEN: TOKEN, JARVIS_GOOGLE_CACHE_S: "0",
    ANTHROPIC_API_KEY: "", GEMINI_API_KEY: "", ELEVENLABS_API_KEY: "", JARVIS_LLM: "none" };
  start(["agent/main.py"], { ...base, JARVIS_PORT: String(REAL) });
  start(["agent/main.py"], { ...base, JARVIS_DEMO: "1", JARVIS_PORT: String(DEMO) });
  await Promise.all([up(`http://127.0.0.1:${FAKE}/_control`), up(`http://127.0.0.1:${REAL}/api/status`), up(`http://127.0.0.1:${DEMO}/api/status`)]);

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 791 } });
  const consoleErr = [];
  page.on("console", m => { if (m.type() === "error") consoleErr.push(m.text()); });
  page.on("pageerror", e => consoleErr.push(String(e)));

  console.log("REAL mode, not connected");
  await page.goto(`http://127.0.0.1:${REAL}/`);
  await page.waitForFunction(() => !document.querySelector("#b-google").hidden);
  ok((await page.textContent("#b-google")) === "GOOGLE: NOT CONNECTED", "badge says NOT CONNECTED");
  await page.click("#t-inbox");
  ok(/Google not connected/.test(await lastReply(page)), "INBOX shows 'Google not connected' on screen");
  await page.screenshot({ path: path.join(TMP, "1-not-connected.png") });

  console.log("CSRF: forged callback");
  const forged = await fetch(`http://localhost:${REAL}/auth/google/callback?code=x&state=forged`);
  ok(forged.status === 400 && /state mismatch/.test(await forged.text()), "callback with unknown state is refused (400)");

  console.log("OAuth: authorize → callback → exchange → token saved");
  await page.click("#b-google");
  await page.waitForURL(/google=connected/);
  ok(new URL(page.url()).host === `localhost:${REAL}`, "came back via loopback redirect on localhost");
  await page.waitForFunction(() => document.querySelector("#b-google").textContent === "GOOGLE: CONNECTED");
  ok(true, "badge says CONNECTED");
  const st = fs.statSync(TOKEN);
  ok((st.mode & 0o777) === 0o600, `token file chmod 600 (got ${(st.mode & 0o777).toString(8)})`);
  const tok = JSON.parse(fs.readFileSync(TOKEN, "utf8"));
  ok(tok.refresh_token && tok.access_token, "token file has access + refresh token");
  const statusTxt = await (await fetch(`http://127.0.0.1:${REAL}/api/status`)).text();
  const html = await page.content();
  ok(![tok.access_token, tok.refresh_token, "fake-secret"].some(s => statusTxt.includes(s) || html.includes(s)), "no token/secret reaches the browser");

  console.log("Gmail + Calendar reads");
  await page.click("#t-inbox");
  let r = await lastReply(page);
  ok(/2 messages, 1 unread/.test(r), "INBOX: 2 messages, 1 unread");
  ok(/● Trại tôm Sao Biển — Đặt 20 thùng Aqua Probio/.test(r), "INBOX: From + Subject, UNREAD label → ●");
  await page.click("#t-brief");
  r = await lastReply(page);
  ok(/Gọi HTX Cà Mau/.test(r) && /Tập BJJ/.test(r) && !/Đã huỷ/.test(r), "BRIEF: calendar events, cancelled dropped");
  await page.screenshot({ path: path.join(TMP, "2-connected.png") });
  const d = await page.evaluate(() => fetch("/api/ask", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: "read my inbox" }) }).then(r => r.json()));
  ok(d.cards[0].items.length === 2, "keyword route 'inbox' works too");

  console.log("Refresh");
  const before = (await control("")).log.filter(x => x[1] === "/token").length;
  await control("expire=1");                                   // Google rejects the stored access token → 401 → refresh → retry
  await page.click("#t-inbox");
  ok(/2 messages/.test(await lastReply(page)), "after server-side expiry: 401 → refresh → success");
  const t2 = JSON.parse(fs.readFileSync(TOKEN, "utf8"));
  t2.expires_at = 0; fs.writeFileSync(TOKEN, JSON.stringify(t2));   // expired locally → refreshed before the call
  await page.click("#t-inbox");
  ok(/2 messages/.test(await lastReply(page)), "after local expiry: proactive refresh → success");
  const after = (await control("")).log.filter(x => x[1] === "/token").length;
  ok(after - before === 2, `two refresh calls (${after - before})`);
  ok(JSON.parse(fs.readFileSync(TOKEN, "utf8")).refresh_token === tok.refresh_token, "refresh token kept after refresh");

  console.log("Revoked");
  await control("revoke=1"); await control("expire=1");
  await page.click("#t-inbox");
  ok(/token expired or revoked/.test(await lastReply(page)), "revoked refresh token → clear message on screen");
  await page.waitForFunction(() => document.querySelector("#b-google").textContent === "GOOGLE: ERROR");
  ok(await page.isVisible("#error"), "error banner visible");
  await page.screenshot({ path: path.join(TMP, "3-revoked.png") });

  const ctl = await control("");
  ok(ctl.writes.length === 0, "no write call ever reached Google");
  ok(ctl.log.every(([m, p]) => m === "GET" || p === "/token"), "only GET (+ POST /token)");
  ok(consoleErr.length === 0, "no console errors in real mode " + JSON.stringify(consoleErr));

  console.log("DEMO mode unchanged");
  const demo = await browser.newPage({ viewport: { width: 1280, height: 791 } });
  const demoErr = [];
  demo.on("console", m => { if (m.type() === "error") demoErr.push(m.text()); });
  demo.on("pageerror", e => demoErr.push(String(e)));
  const fakeBefore = (await control("")).log.length;
  await demo.goto(`http://127.0.0.1:${DEMO}/`);
  await demo.waitForSelector("#b-mode:text('DEMO DATA')");
  await demo.waitForTimeout(500);
  ok(await demo.isHidden("#b-google"), "no GOOGLE badge in demo");
  await demo.click("#t-brief"); r = await lastReply(demo);
  ok(/unread/.test(r), "BRIEF works in demo");
  await demo.click("#t-inbox"); r = await lastReply(demo);
  ok(/messages/.test(r), "INBOX works in demo");
  ok((await fetch(`http://localhost:${DEMO}/auth/google`)).status === 404, "/auth/google is off in demo");
  ok((await control("")).log.length - fakeBefore === 1, "demo never called Google (only our own /_control)");
  ok(demoErr.length === 0, "no console errors in demo " + JSON.stringify(demoErr));
  await demo.screenshot({ path: path.join(TMP, "4-demo.png") });

  await browser.close();
  console.log(`\nscreenshots: ${TMP}\n${failed ? failed + " FAILED" : "ALL PASS"}`);
})().catch(e => { console.error(e); failed++; }).finally(() => { procs.forEach(p => p.kill()); process.exitCode = failed ? 1 : 0; });
