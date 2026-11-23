export type HandoverStatus = 'ready_for_handover' | 'pending_confirmations' | 'handed_over'
export interface Task { id: string; code: string; warehouseName: string; packages: string[]; status: HandoverStatus; shipperAccepted: boolean; arrivedAtWarehouse: boolean; scannedCodes: string[]; version: number }
export interface Dashboard { available: number; reserved: number; pendingOutbound: number; readyHandover: number; tasks: Task[] }
