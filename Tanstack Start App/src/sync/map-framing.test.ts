import test from 'node:test'
import assert from 'node:assert/strict'
import {activityMapInsets} from '../components/map-framing.ts'
test('historical route fits above the phone card rather than behind it',()=>{
 const padding=activityMapInsets(390,650,430)
 assert.ok(padding.bottom>220)
 const visibleBottom=650-padding.bottom
 assert.ok(visibleBottom<430)
 const center=(padding.top+visibleBottom)/2
 assert.ok(center<325)
 assert.equal(padding.left,padding.right)
})
test('map framing preserves a usable area on short screens and works without a card',()=>{
 const short=activityMapInsets(650,250,30)
 assert.ok(250-short.top-short.bottom>=120)
 const open=activityMapInsets(1280,700)
 assert.equal(open.top,open.bottom)
 assert.equal(open.left,open.right)
})
