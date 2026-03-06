/**
 * @file chrome_merge_runner.mjs
 * @brief Node-side runner for Copilot features+premium merge path.
 * @details Parses both source pages and executes mergeCopilotPayloads in one process.
 */

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

/**
 * @brief Parse two HTML fixtures and return merged Copilot payload.
 * @returns {Promise<void>} Completion promise.
 */
async function main() {
  const [featuresPath, premiumPath] = process.argv.slice(2);
  if (!featuresPath || !premiumPath) {
    throw new Error("Usage: node chrome_merge_runner.mjs <featuresPath> <premiumPath>");
  }

  const parserModuleUrl = pathToFileURL(
    path.resolve(process.cwd(), "src/aibar/chrome-extension/parsers.mjs")
  ).href;
  const parserModule = await import(parserModuleUrl);

  const featuresHtml = fs.readFileSync(path.resolve(featuresPath), "utf-8");
  const premiumHtml = fs.readFileSync(path.resolve(premiumPath), "utf-8");

  const featuresPayload = parserModule.parseCopilotFeaturesHtml(featuresHtml);
  const premiumPayload = parserModule.parseCopilotPremiumHtml(premiumHtml);
  const mergedPayload = parserModule.mergeCopilotPayloads(featuresPayload, premiumPayload);

  process.stdout.write(JSON.stringify(mergedPayload));
}

await main();
