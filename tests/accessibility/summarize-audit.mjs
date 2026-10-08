import fs from "node:fs";

const file = process.argv[2];
let rows = [];
try {
  const raw = fs.readFileSync(file, "utf8").trim();
  rows = raw ? JSON.parse(raw) : [];
} catch (_) {}

const pages = Array.isArray(rows) ? rows : [];
const issues = pages.flatMap(page => (page.issues || []).map(issue => ({...issue, page: page.pageUrl || page.url || "unknown"})));
const byType = {error:0, warning:0, notice:0};
for (const issue of issues) {
  const key = String(issue.type || "").toLowerCase();
  if (key in byType) byType[key] += 1;
}

console.log("## Workforce Wonkery accessibility audit");
console.log("");
console.log(`Pages checked: **${pages.length}**`);
console.log(`Automated issues: **${issues.length}** (errors ${byType.error}, warnings ${byType.warning}, notices ${byType.notice})`);
console.log("");
console.log("This automated scan is evidence, not a complete WCAG conformance claim. Manual keyboard, zoom, screen-reader, motion, and content review remain required.");
if (issues.length) {
  console.log("");
  console.log("### First 20 findings");
  for (const issue of issues.slice(0,20)) {
    console.log(`- **${issue.type || "issue"}** on ${issue.page}: ${String(issue.message || issue.code || "").replace(/\s+/g," ").trim()}`);
  }
}
