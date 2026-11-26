// UI boundaries do not replace API permissions and data scope.
export const portalRoles = {
  operations: ['WAREHOUSE_ADMIN', 'DISPATCH_MANAGER'],
  supplier: ['SUPPLIER'],
  retailer: ['RETAILER_OWNER'],
  shipper: ['SHIPPER'],
} as const
export type Portal = keyof typeof portalRoles
export function belongsToPortal(role: string, portal: Portal): boolean {
  return (portalRoles[portal] as readonly string[]).includes(role)
}
export function roleHome(role?: string): string {
  if (role && belongsToPortal(role, 'operations')) return '/admin/dashboard'
  if (role === 'SUPPLIER') return '/supplier/inbounds'
  if (role === 'RETAILER_OWNER') return '/retailer/outbounds'
  if (role === 'SHIPPER') return '/shipper/tasks'
  return '/forbidden'
}
