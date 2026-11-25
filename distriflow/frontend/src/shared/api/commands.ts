import { api, ApiError } from './client'

// Retain the same key after a timeout. A definitive response ends that command.
const pending = new Map<string, string>()
export async function command<T>(path: string, payload: unknown): Promise<T> {
  const body = JSON.stringify(payload)
  const identity = `${path}:${body}`
  const key = pending.get(identity) ?? crypto.randomUUID()
  pending.set(identity, key)
  try {
    const result = await api<T>(path, { method: 'POST', headers: { 'Idempotency-Key': key }, body })
    pending.delete(identity)
    return result
  } catch (error) {
    if (error instanceof ApiError && error.status < 500) pending.delete(identity)
    throw error
  }
}
