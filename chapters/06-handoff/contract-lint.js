#!/usr/bin/env node
// contract-lint.js -- Chapter 6. Does this handoff close the four gaps + carry a
// gate threshold, or ship a guess? Prints ok/GAP per section, then a verdict.
//
// This is a STRUCTURAL check: it sees whether the sections and the threshold
// column exist, not whether what's inside them is specific enough to type from.
//
// Usage: node contract-lint.js ../../worked-examples/handoff.md
// Runs offline, zero keys. Node built-ins only (fs).
"use strict";

const fs = require("fs");

const path = process.argv[2] || "handoff.md";
const md = fs.readFileSync(path, "utf8");

const checks = [
  ["Context",        /^##\s+Context/im],       // read-only ground truth present?
  ["Task",           /^##\s+Task/im],           // the typing steps present?
  ["Constraints",    /^##\s+Constraints/im],    // frozen boundaries present?
  ["Escalation",     /^##\s+Escalation/im],     // the stop-and-hand-back valve present?
  ["Gate threshold", /\|\s*Threshold\s*\|/i],   // does the gate carry a number, not an opinion?
];

let gaps = 0;
for (const [name, re] of checks) {
  const ok = re.test(md);
  if (!ok) gaps++;
  console.log((ok ? "ok  " : "GAP ") + name);
}
console.log(gaps === 0
  ? "all 5 structural checks pass (a vague constraint still needs your eyes)"
  : gaps + " gap(s): the executor fills each with a guess");
