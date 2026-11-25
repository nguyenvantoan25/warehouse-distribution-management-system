import { ref, onMounted, computed } from 'vue'
import { getCatalog, type Partner, type Sku, type Warehouse, type Location, type Supply } from './api'
export function useCatalog() {
  const partners = ref<Partner[]>([]); const skus = ref<Sku[]>([]); const warehouses = ref<Warehouse[]>([]); const locations = ref<Location[]>([]); const supplies = ref<Supply[]>([])
  const loading = ref(true); const error = ref('')
  async function load() {
    loading.value = true; error.value = ''
    try { const data = await getCatalog(); partners.value = data.partners; skus.value = data.skus; warehouses.value = data.warehouses; locations.value = data.locations; supplies.value = data.supplies }
    catch (e) { error.value = e instanceof Error ? e.message : 'Không thể tải danh mục' }
    finally { loading.value = false }
  }
  onMounted(load)
  return { partners, skus, warehouses, locations, supplies, owners: computed(() => partners.value.filter(p => p.kind === 'RETAILER')), suppliers: computed(() => partners.value.filter(p => p.kind === 'SUPPLIER')), loading, error, load }
}
