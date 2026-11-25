import { api } from '../../shared/api/client'
import { command } from '../../shared/api/commands'
export interface Partner { id: string; name: string; kind: 'RETAILER' | 'SUPPLIER'; active: boolean }
export interface Sku { id: string; code: string; name: string; ownerId: string; baseUnit: string }
export interface Warehouse { id: string; name: string }
export interface Location { id: string; warehouseId: string; code: string }
export interface Supply { id: string; supplier_id: string; owner_id: string; sku_id: string }
export async function getCatalog() {
  const [partners, skus, warehouses, locations, supplies] = await Promise.all([
    api<Partner[]>('/partners'), api<Sku[]>('/skus'), api<Warehouse[]>('/warehouses'), api<Location[]>('/locations'), api<Supply[]>('/supply-relationships'),
  ])
  return { partners, skus, warehouses, locations, supplies }
}
export const createCatalogRecord = (path: string, body: unknown) => command(path, body)
