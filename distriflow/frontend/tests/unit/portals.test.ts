import { describe, expect, it } from 'vitest'
import { belongsToPortal, portalRoles, roleHome } from '../../src/app/portals'

describe('portal boundaries', () => {
  it.each([
    ['WAREHOUSE_ADMIN', '/admin/dashboard'],
    ['DISPATCH_MANAGER', '/admin/dashboard'],
    ['SUPPLIER', '/supplier/inbounds'],
    ['RETAILER_OWNER', '/retailer/outbounds'],
    ['SHIPPER', '/shipper/tasks'],
    ['UNKNOWN', '/forbidden'],
    [undefined, '/forbidden'],
  ])('routes %s to its own home', (role, path) => {
    expect(roleHome(role)).toBe(path)
  })

  it('places every supported role in exactly one portal', () => {
    const portals = Object.keys(portalRoles) as (keyof typeof portalRoles)[]
    for (const [portal, roles] of Object.entries(portalRoles)) {
      for (const role of roles) {
        expect(portals.filter(p => belongsToPortal(role, p))).toEqual([portal])
      }
    }
    expect(portals.some(p => belongsToPortal('UNKNOWN', p))).toBe(false)
  })
})
