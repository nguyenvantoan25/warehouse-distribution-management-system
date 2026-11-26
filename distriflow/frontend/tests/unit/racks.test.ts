import { describe, expect, it } from 'vitest'
import { coordinateKey, matchesRack, suggestedCode } from '../../src/features/inventory/rack-map'
import type { RackLocation } from '../../src/features/inventory/rack-api'

describe('single rack map', () => {
  it('represents 800 independent positions across 8 rows, 10 levels and 10 columns', () => {
    const keys = new Set<string>(); const codes = new Set<string>()
    for (let row = 1; row <= 8; row++) for (let level = 1; level <= 10; level++) {
      for (let column = 1; column <= 10; column++) {
        keys.add(coordinateKey(row, level, column))
        codes.add(suggestedCode(row, level, column))
      }
    }
    expect(keys.size).toBe(800); expect(codes.size).toBe(800)
    expect(suggestedCode(8, 10, 10)).toBe('H08-T10-C10')
  })
  it('does not treat an unconfigured cell as an empty registered location', () => {
    expect(matchesRack(undefined, '', 'unconfigured')).toBe(true)
    expect(matchesRack(undefined, '', 'empty')).toBe(false)
    expect(matchesRack(undefined, 'SKU', '')).toBe(false)
  })
  it('matches real location, SKU and owner data together with status', () => {
    const location: RackLocation = { id: 'a', code: 'H01-T01-C01', row: 1, level: 1, column: 1,
      status: 'reserved', items: [{ id: 'i', skuCode: 'SKU-1', skuName: 'Hàng kiểm thử',
        ownerName: 'Chủ hàng A', unit: 'hộp', onHand: 10, reserved: 2, unavailable: 0, available: 8 }] }
    expect(matchesRack(location, 'sku-1', 'reserved')).toBe(true)
    expect(matchesRack(location, 'Chủ hàng A', '')).toBe(true)
    expect(matchesRack(location, 'sku-1', 'empty')).toBe(false)
    expect(matchesRack(location, 'không có', '')).toBe(false)
  })
})
