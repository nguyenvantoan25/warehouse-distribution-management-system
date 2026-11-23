const baseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'
export class ApiError extends Error { constructor(public status: number, message: string) { super(message) } }
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  // Chỉ phục vụ dữ liệu seed ở môi trường local. Bản triển khai thay bằng cookie HttpOnly do API cấp.
  const response = await fetch(`${baseUrl}${path}`, { ...init, headers: { 'Content-Type': 'application/json', 'X-Demo-Actor': location.pathname.startsWith('/shipper') ? 'shipper-demo' : 'warehouse-admin-demo', ...init.headers } })
  if (!response.ok) { const body = await response.json().catch(() => null); throw new ApiError(response.status, body?.error?.message ?? 'Không thể kết nối máy chủ') }
  return response.json() as Promise<T>
}
