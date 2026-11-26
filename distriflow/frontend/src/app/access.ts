import { reactive } from 'vue'
import { api, ApiError, setCsrfToken } from '../shared/api/client'
import { roleHome } from './portals'

export interface AccessUser { id: string; username: string; role: string; access: string[]; csrfToken: string }
export const auth = reactive<{ user: AccessUser | null; loaded: boolean }>({ user: null, loaded: false })
export function can(permission: string) { return auth.user?.access.includes(permission) ?? false }
function assign(user: AccessUser | null) { auth.user = user; auth.loaded = true; setCsrfToken(user?.csrfToken ?? '') }
export async function restoreSession() {
  try { assign(await api<AccessUser>('/auth/me')) }
  catch (error) { if (error instanceof ApiError && error.status === 401) assign(null); else throw error }
}
export async function login(username: string, password: string) {
  assign(await api<AccessUser>('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }))
}
export async function logout() { await api<void>('/auth/logout', { method: 'POST' }); assign(null) }
export function homePath() { return roleHome(auth.user?.role) }
