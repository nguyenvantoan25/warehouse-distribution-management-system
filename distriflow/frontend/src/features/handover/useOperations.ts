import { ref, computed, onMounted } from 'vue'
import { api } from '../../shared/api/client'
import type { Task } from '../../shared/types/domain'

export function useOperations() {
  const tasks = ref<Task[]>([])
  const loading = ref(true)
  const error = ref('')
  async function load() {
    loading.value = true; error.value = ''
    try { tasks.value = await api<Task[]>('/pickup-tasks') }
    catch (e) { error.value = e instanceof Error ? e.message : 'Không thể tải dữ liệu' }
    finally { loading.value = false }
  }
  const warehouses = computed(() => [...new Set(tasks.value.map(task => task.warehouseName))])
  onMounted(load)
  return { tasks, loading, error, warehouses, load }
}

export function exportTasks(tasks: Task[]) {
  const cell = (value: string | number) => '"' + String(value).replace(/^[=+@-]/, "'$&").replace(/"/g, '""') + '"'
  const rows = [['Mã phiếu', 'Kho xuất', 'Shipper', 'Số kiện', 'Trạng thái'], ...tasks.map(t => [t.code, t.warehouseName, t.shipperName, t.packages.length, t.status])]
  const url = URL.createObjectURL(new Blob(['\ufeff' + rows.map(row => row.map(cell).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a'); link.href = url; link.download = 'distriflow-ban-giao.csv'; link.click(); URL.revokeObjectURL(url)
}
