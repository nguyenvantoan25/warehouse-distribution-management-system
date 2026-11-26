import { api } from '../../shared/api/client'
import { command } from '../../shared/api/commands'
export type ManagedRole = 'SHIPPER' | 'SUPPLIER' | 'RETAILER_OWNER'
export interface DirectoryAccount {
  id: string; username: string; name: string; role: ManagedRole; active: boolean; deleted: boolean
  warehouseName: string; version: number; organizationId: string | null; organizationCount: number; suppliedGoods: string | null
}
export interface UnlinkedPartner { id: string; name: string; kind: 'SUPPLIER' | 'RETAILER'; suppliedGoods: string | null }
export interface DirectoryData { accounts: DirectoryAccount[]; unlinkedPartners: UnlinkedPartner[] }
export interface ProfileInput { username: string; name: string; supplied_goods: string | null; password?: string }
export const getDirectory = () => api<DirectoryData>('/directory')
export const createAccount = (body: ProfileInput & { role: ManagedRole; password: string; organization_id: string | null }) => command<DirectoryAccount>('/directory', body)
export const updateAccount = (id: string, body: ProfileInput & { version: number }) => command<DirectoryAccount>(`/directory/${id}/update`, body)
export const deleteAccount = (account: DirectoryAccount) => command<DirectoryAccount>(`/directory/${account.id}/delete`, { version: account.version })
