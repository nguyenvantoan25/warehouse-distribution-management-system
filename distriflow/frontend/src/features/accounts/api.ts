import { api } from '../../shared/api/client'
import { command } from '../../shared/api/commands'
export interface AccountScope { id: string; username: string; role: string; warehouseName: string; organizationIds: string[]; active: boolean }
export const getAccounts = () => api<AccountScope[]>('/accounts')
export const setScope = (id: string, body: { warehouse_id: string; organization_id: string | null }) => command(`/accounts/${id}/scope`, body)
