import type { RackLocation } from './rack-api'

export const rackStatusLabels = {
  unconfigured: 'Chưa khai báo', empty: 'Chưa ghi nhận hàng', occupied: 'Có hàng',
  reserved: 'Có hàng đã giữ', unavailable: 'Có hàng không khả dụng',
}
export function coordinateKey(row: number, level: number, column: number) {
  return `${row}:${level}:${column}`
}
export function suggestedCode(row: number, level: number, column: number) {
  return `H${String(row).padStart(2, '0')}-T${String(level).padStart(2, '0')}-C${String(column).padStart(2, '0')}`
}
export function matchesRack(location: RackLocation | undefined, search: string, status: string) {
  if (status && (location?.status ?? 'unconfigured') !== status) return false
  if (!search.trim()) return true
  return !!location && [location.code, ...location.items.flatMap(i => [i.skuCode, i.skuName, i.ownerName])]
    .join(' ').toLocaleLowerCase('vi').includes(search.trim().toLocaleLowerCase('vi'))
}
