// Local-only Graphviz/WASM renderer. Prints SVG; never uploads schema.
import { readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createRequire } from 'node:module'

const root = fileURLToPath(new URL('../../', import.meta.url))
const require = createRequire(import.meta.url)
const { instance } = require(resolve(root, 'distriflow/.tools/erd-renderer/node_modules/@viz-js/viz'))
const input = process.argv[2]
if (!input) throw new Error('Usage: node docs/diagrams/render-erd.mjs path/to/erd.dot')
const viz = await instance()
const svg = viz.renderString(readFileSync(resolve(input), 'utf8'), { format: 'svg', engine: 'dot' })
if (process.argv[3] === '--output' && process.argv[4]) {
  writeFileSync(resolve(process.argv[4]), svg, 'utf8')
  process.stdout.write(`Rendered ${process.argv[4]}\n`)
} else {
  process.stdout.write(svg)
}
