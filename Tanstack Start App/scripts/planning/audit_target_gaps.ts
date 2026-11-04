/** Recompute unfinished target sections from the current running-only snapshot.
 * node --experimental-strip-types scripts/planning/audit_target_gaps.ts [targets.json] [output.json]
 * Refresh snapshots first; review addresses and Calendar before publishing the output.
 */
import fs from 'node:fs'
import path from 'node:path'
import {fileURLToPath} from 'node:url'
import {auditPlannedGaps} from '../../src/components/planned-gaps.ts'
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..')
const input=process.argv[2]||path.join(root,'raw-data/plans/current-targets.json')
const targets=JSON.parse(fs.readFileSync(input,'utf8')),tracks=JSON.parse(fs.readFileSync(path.join(root,'raw-data/runs/tracks.geojson'),'utf8'))
const output=JSON.stringify(auditPlannedGaps(targets,tracks),null,2)+'\n'
if(process.argv[3])fs.writeFileSync(process.argv[3],output);else process.stdout.write(output)
