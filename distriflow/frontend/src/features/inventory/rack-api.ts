import { api } from '../../shared/api/client'
import { command } from '../../shared/api/commands'

export type RackStatus = 'empty' | 'occupied' | 'reserved' | 'unavailable'
export interface RackItem {
  id: string; skuCode: string; skuName: string; ownerName: string; unit: string
  onHand: number; reserved: number; unavailable: number; available: number
}
export interface RackLocation {
  id: string; code: string; row: number; level: number; column: number
  status: RackStatus; items: RackItem[]
}
export interface RackMap {
  warehouse: { id: string; name: string } | null
  layout: { rows: number; levels: number; columns: number; rackType: 'single'; totalPositions: number }
  locations: RackLocation[]; otherLocationCount: number; unmappedBalanceCount: number
}
export const getRackMap = () => api<RackMap>('/inventory/rack-map')
export const initializeRacks = (warehouseId: string) => command<{ created: number; configured: number }>(
  '/inventory/rack-map/initialize', { warehouse_id: warehouseId, total_positions: 800 },
)
