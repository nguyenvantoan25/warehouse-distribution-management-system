import { api } from '../../shared/api/client'
import { command } from '../../shared/api/commands'
import type { StockDocument } from '../../shared/types/documents'
export const getOutbounds = () => api<StockDocument[]>('/outbound-requests')
export const outboundCommand = (id: string, action: 'approve' | 'pick' | 'pack' | 'cancel', payload: unknown) => command<StockDocument>(`/outbound-requests/${id}/${action}`, payload)
