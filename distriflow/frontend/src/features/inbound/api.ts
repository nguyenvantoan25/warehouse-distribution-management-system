import { api } from '../../shared/api/client'
import { command } from '../../shared/api/commands'
import type { StockDocument } from '../../shared/types/documents'
export const getInbounds = () => api<StockDocument[]>('/inbound-requests')
export const inboundCommand = (id: string, action: 'review' | 'receive' | 'putaway', payload: unknown) => command<StockDocument>(`/inbound-requests/${id}/${action}`, payload)
