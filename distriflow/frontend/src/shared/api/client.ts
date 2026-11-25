const baseUrl = import.meta.env.VITE_API_URL ?? '/api/v1'
let csrfToken = ''
export function setCsrfToken(token: string) { csrfToken = token }
export class ApiError extends Error { constructor(public status: number, message: string) { super(message) } }
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, { ...init, credentials: 'include', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrfToken, ...init.headers } })
  if (!response.ok) { const body = await response.json().catch(() => null); throw new ApiError(response.status, body?.error?.message ?? 'Không thể kết nối máy chủ') }
  return response.status === 204 ? undefined as T : response.json() as Promise<T>
}
