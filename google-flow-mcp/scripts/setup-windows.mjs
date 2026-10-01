// Writes config/flow.config.json and registers the MCP server in Claude Desktop.
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const email = process.argv[2] || '';

// 1) config
const example = JSON.parse(fs.readFileSync(path.join(root, 'config/flow.config.example.json'), 'utf8'));
const cfgPath = path.join(root, 'config/flow.config.json');
const cfg = fs.existsSync(cfgPath) ? JSON.parse(fs.readFileSync(cfgPath, 'utf8')) : example;
if (email) cfg.expectedAccount = email;
cfg.headless = false;
cfg.locale = 'en';
cfg.flowUrl = 'https://labs.google/fx/tools/flow';
fs.writeFileSync(cfgPath, JSON.stringify(cfg, null, 2));
console.log('Config written:', cfgPath);

// 2) Claude Desktop registration (normal install + Microsoft Store install)
const dirs = [];
if (process.env.APPDATA) dirs.push(path.join(process.env.APPDATA, 'Claude'));
const pk = process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, 'Packages');
if (pk && fs.existsSync(pk)) {
  for (const d of fs.readdirSync(pk)) {
    if (/^(Claude|Anthropic)/i.test(d)) dirs.push(path.join(pk, d, 'LocalCache', 'Roaming', 'Claude'));
  }
}
let done = 0;
for (const dir of dirs) {
  if (!fs.existsSync(dir)) continue;
  const f = path.join(dir, 'claude_desktop_config.json');
  let json = {};
  if (fs.existsSync(f)) {
    fs.copyFileSync(f, f + '.backup');
    try { json = JSON.parse(fs.readFileSync(f, 'utf8') || '{}'); } catch { console.log('Could not parse', f, '- skipped'); continue; }
  }
  json.mcpServers = json.mcpServers || {};
  json.mcpServers['google-flow'] = { command: process.execPath, args: [path.join(root, 'src/index.js')] };
  fs.writeFileSync(f, JSON.stringify(json, null, 2));
  console.log('Registered in Claude Desktop:', f);
  done++;
}
if (!done) console.log('Claude Desktop config folder not found (is Claude Desktop installed and opened once?).');
console.log('\nFor Claude Code on your PC run:\n  claude mcp add google-flow -- "' + process.execPath + '" "' + path.join(root, 'src/index.js') + '"');
