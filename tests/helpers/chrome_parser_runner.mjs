/**
 * @file chrome_parser_runner.mjs
 * @brief Node-side runner that executes Chrome parser exports on fixture HTML.
 * @details Provides deterministic CLI bridge for pytest to validate parser behavior
 * without browser runtime dependencies.
 */

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

/**
 * @brief Resolve parser function and execute it on fixture HTML.
 * @returns {Promise<void>} Completion promise.
 */
async function main() {
  const [fnName, htmlPath, secondJsonPayload] = process.argv.slice(2);
  if (!fnName || !htmlPath) {
    throw new Error("Usage: node chrome_parser_runner.mjs <fnName> <htmlPath> [jsonPayload]");
  }

  const parserModuleUrl = pathToFileURL(
    path.resolve(process.cwd(), "src/aibar/chrome-extension/parsers.js")
  ).href;
  const parserModule = await import(parserModuleUrl);
  const target = parserModule[fnName];

  if (typeof target !== "function") {
    throw new Error(`Parser function not found: ${fnName}`);
  }

  const html = fs.readFileSync(path.resolve(htmlPath), "utf-8");
  const result = secondJsonPayload ? target(html, JSON.parse(secondJsonPayload)) : target(html);
  process.stdout.write(JSON.stringify(result));
}

await main();
