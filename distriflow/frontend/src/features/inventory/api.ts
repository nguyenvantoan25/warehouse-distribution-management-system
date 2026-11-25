import { api } from '../../shared/api/client'
import { command } from '../../shared/api/commands'
export interface Balance { id: string; ownerId: string; ownerName: string; skuCode: string; skuName: string; unit: string; warehouseId: string; locationCode: string; onHand: number; reserved: number; unavailable: number; available: number }
export interface Movement { id: string; skuCode: string; ownerId: string; quantity: number; kind: string; at: string }
export const getBalances = () => api<Balance[]>('/inventory/balances')
export const getMovements = () => api<Movement[]>('/inventory/movements')
export const holdStock = (body: { balance_id: string; quantity: number; release: boolean; reason: string }) => command('/inventory/holds', body)
