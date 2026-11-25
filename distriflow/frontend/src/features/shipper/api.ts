import { api } from '../../shared/api/client'
import { command } from '../../shared/api/commands'
import type { Task } from '../../shared/types/domain'
export const getMyTasks = () => api<Task[]>('/pickup-tasks')
export const taskCommand = (id: string, action: string, body: unknown) => command<Task>(`/pickup-tasks/${id}/${action}`, body)
