<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RefreshCw, Layers, Info } from 'lucide-vue-next'
import { getRackMap, initializeRacks, type RackMap, type RackLocation } from './rack-api'
import { coordinateKey, matchesRack, rackStatusLabels, suggestedCode } from './rack-map'

const data = ref<RackMap | null>(null)
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const notice = ref('')
const row = ref(1)
const search = ref('')
const status = ref('')
const selectedKey = ref('')
const updatedAt = ref('')
const locations = computed(() => new Map((data.value?.locations ?? []).map(l => [coordinateKey(l.row, l.level, l.column), l])))
const levels = computed(() => Array.from({ length: data.value?.layout.levels ?? 0 }, (_, i) => (data.value?.layout.levels ?? 0) - i))
const configured = computed(() => data.value?.locations.length ?? 0)
const occupied = computed(() => data.value?.locations.filter(l => l.items.length).length ?? 0)
const selected = computed(() => locations.value.get(selectedKey.value))
const rowSummaries = computed(() => Array.from({ length: data.value?.layout.rows ?? 0 }, (_, i) => {
  const number = i + 1
  const cells = data.value?.locations.filter(l => l.row === number) ?? []
  return { number, configured: cells.length, occupied: cells.filter(l => l.items.length).length }
}))
const cells = computed(() => levels.value.map(level => ({ level, slots: Array.from({ length: data.value?.layout.columns ?? 0 }, (_, i) => {
  const column = i + 1
    const key = coordinateKey(row.value, level, column)
    const location = locations.value.get(key)
    return { key, column, location, code: location?.code ?? suggestedCode(row.value, level, column),
      matches: matchesRack(location, search.value, status.value) }
  })
})))
const matchCount = computed(() => cells.value.reduce((n, level) => n + level.slots.filter(s => s.matches).length, 0))
function statusLabel(location?: RackLocation) { return rackStatusLabels[location?.status ?? 'unconfigured'] }
async function load() {
  loading.value = true; error.value = ''
  try { data.value = await getRackMap(); updatedAt.value = new Date().toLocaleTimeString('vi-VN') }
  catch (e) { data.value = null; error.value = e instanceof Error ? e.message : 'Không tải được bản đồ kệ' }
  finally { loading.value = false }
}
async function initialize() {
  if (!data.value?.warehouse || saving.value) return
  if (!window.confirm('Khai báo đủ 800 vị trí kệ đơn (8 hàng × 10 tầng × 10 cột) trong kho này? Không tạo hàng tồn và không ghi đè vị trí cũ.')) return
  saving.value = true; error.value = ''; notice.value = ''
  try {
    const result = await initializeRacks(data.value.warehouse.id)
    notice.value = `Đã khai báo ${result.created} vị trí mới. Tổng ${result.configured} vị trí kệ đơn; không thêm hàng tồn.`
    await load()
  } catch (e) { error.value = e instanceof Error ? e.message : 'Không khai báo được vị trí' }
  finally { saving.value = false }
}
onMounted(load)
</script>

<template>
  <section class="rack-map" aria-label="Bản đồ vị trí kệ đơn">
    <div class="ops-panel rack-intro">
      <div class="rack-heading">
        <div><h2><Layers :size="20"/> Bản đồ kệ kệ đơn</h2><p>{{ data?.warehouse?.name ?? 'Kho trong phạm vi tài khoản' }} · 800 vị trí lưu hàng · Kho thủ công</p></div>
        <button class="ops-button secondary" :disabled="loading || saving" @click="load"><RefreshCw :size="15"/> Tải lại bản đồ</button>
      </div>
      <p class="rack-disclaimer"><Info :size="17"/> Sơ đồ logic: 8 hàng × 10 tầng × 10 cột, mỗi ô là một vị trí độc lập. Chưa có kích thước và lối đi thực tế.</p>
    </div>
    <p v-if="error" class="ops-alert" role="alert">{{ error }}</p>
    <p v-if="notice" class="ops-alert" role="status">{{ notice }}</p>
    <p v-if="loading" class="ops-loading">Đang tải vị trí và số dư từ cơ sở dữ liệu…</p>
    <template v-else-if="data">
      <div v-if="configured < data.layout.totalPositions" class="ops-panel rack-setup">
        <div><h3>{{ configured }} / {{ data.layout.totalPositions }} vị trí đã khai báo</h3><p>Ô nét đứt chỉ là tọa độ dự kiến, chưa phải vị trí trong cơ sở dữ liệu.</p></div>
        <button v-if="data.warehouse" class="ops-button" :disabled="saving" @click="initialize">{{ saving ? 'Đang khai báo…' : 'Khai báo đủ 800 vị trí' }}</button>
        <RouterLink v-else class="ops-button" to="/admin/warehouses">Khai báo kho trước</RouterLink>
      </div>
      <div class="rack-summary" aria-label="Thống kê vị trí">
        <div><span>Đã khai báo</span><b>{{ configured }} / {{ data.layout.totalPositions }}</b></div>
        <div><span>Vị trí ghi nhận có hàng</span><b>{{ occupied }}</b></div>
        <div><span>Chưa ghi nhận hàng</span><b>{{ configured - occupied }}</b></div>
        <div><span>Chưa khai báo</span><b>{{ data.layout.totalPositions - configured }}</b></div>
      </div>
      <p v-if="data.otherLocationCount || data.unmappedBalanceCount" class="ops-alert" role="note">
        Có {{ data.otherLocationCount }} vị trí khác ngoài sơ đồ và {{ data.unmappedBalanceCount }} dòng tồn dương chưa nằm trên sơ đồ này. Không tự chuyển hàng hoặc gán tọa độ cho vị trí cũ.
      </p>
      <div class="rack-rows" aria-label="Chọn hàng kệ">
        <button v-for="summary in rowSummaries" :key="summary.number" type="button" :aria-pressed="row === summary.number" @click="row = summary.number; selectedKey = ''">
          <b>Hàng {{ String(summary.number).padStart(2, '0') }}</b><span>{{ summary.occupied }} có hàng</span><small>{{ summary.configured }} / 100 khai báo</small>
        </button>
      </div>
      <div class="rack-workspace">
        <section class="ops-panel rack-elevation">
          <div class="rack-toolbar">
            <h3>Hàng {{ String(row).padStart(2, '0') }} · Mặt đứng quy ước</h3>
            <label class="rack-filter">Tìm mã vị trí / SKU / chủ hàng<input v-model="search" type="search" placeholder="Ví dụ H01-T01-C01 hoặc mã SKU"/></label>
            <label class="rack-filter">Lọc trạng thái<select v-model="status" aria-label="Lọc trạng thái"><option value="">Tất cả vị trí</option><option v-for="(label, key) in rackStatusLabels" :key="key" :value="key">{{ label }}</option></select></label>
          </div>
          <p class="rack-hint">Tầng 10 ở trên, tầng 01 ở dưới; cột 01–10 từ trái sang phải. {{ matchCount }} / 100 ô phù hợp bộ lọc.</p>
          <div class="rack-scroll" tabindex="0" role="region" aria-label="Lưới 100 vị trí của hàng đang chọn">
            <div class="rack-grid">
              <div class="rack-grid-header"><span>Tầng</span><b v-for="column in data.layout.columns" :key="column">Cột {{ String(column).padStart(2, '0') }}</b></div>
              <div v-for="level in cells" :key="level.level" class="rack-grid-level">
                <b class="rack-level">{{ String(level.level).padStart(2, '0') }}</b>
                  <button v-for="slot in level.slots" :key="slot.key" type="button" class="rack-slot" :class="['rack-state-' + (slot.location?.status ?? 'unconfigured'), { dimmed: !slot.matches, chosen: selectedKey === slot.key }]" :aria-pressed="selectedKey === slot.key" :aria-label="`${slot.code}: ${statusLabel(slot.location)}`" :title="`${slot.code} · ${statusLabel(slot.location)}`" @click="selectedKey = slot.key">
                    <span>{{ String(slot.column).padStart(2, '0') }}</span><small>{{ slot.location?.items.length ? `${slot.location.items.length} dòng` : slot.location ? '—' : 'Chưa tạo' }}</small>
                  </button>
              </div>
            </div>
          </div>
          <div class="rack-legend"><span v-for="(label, key) in rackStatusLabels" :key="key"><i :class="'rack-state-' + key"/>{{ label }}</span></div>
          <p class="rack-hint">Màu ưu tiên: không khả dụng → đã giữ → có hàng. “Chưa ghi nhận hàng” không thay thế kiểm kê thực tế. Số dư tính theo đơn vị của sản phẩm.</p>
        </section>
        <aside class="ops-panel rack-detail" aria-live="polite">
          <template v-if="selected">
            <p class="rack-eyebrow">CHI TIẾT VỊ TRÍ</p><h3>{{ selected.code }}</h3>
            <p>Hàng {{ selected.row }} · Tầng {{ selected.level }} · Cột {{ selected.column }}</p>
            <b>{{ statusLabel(selected) }}</b>
            <article v-for="item in selected.items" :key="item.id" class="rack-stock">
              <h4>{{ item.skuCode }} · {{ item.skuName }}</h4><p>{{ item.ownerName }}</p>
              <dl><div><dt>Tồn ghi sổ</dt><dd>{{ item.onHand }} {{ item.unit }}</dd></div><div><dt>Khả dụng</dt><dd>{{ item.available }} {{ item.unit }}</dd></div><div><dt>Đã giữ</dt><dd>{{ item.reserved }} {{ item.unit }}</dd></div><div><dt>Không khả dụng</dt><dd>{{ item.unavailable }} {{ item.unit }}</dd></div></dl>
            </article>
            <p v-if="!selected.items.length" class="rack-hint">Chưa có số dư dương ghi nhận ở vị trí này. Chọn vị trí khi cất hàng trong luồng nhập kho để ghi nhận tồn.</p>
          </template>
          <template v-else-if="selectedKey"><h3>Vị trí chưa khai báo</h3><p>Ô này chỉ là tọa độ dự kiến. Chưa có ID vị trí hoặc tồn kho trong cơ sở dữ liệu.</p></template>
          <template v-else><p class="rack-eyebrow">CHI TIẾT VỊ TRÍ</p><h3>Chọn một ô kệ</h3><p>Xem hàng, tầng, cột và từng dòng tồn được ghi nhận.</p></template>
          <small v-if="updatedAt" class="rack-updated">Tải dữ liệu lúc {{ updatedAt }} · làm mới để cập nhật</small>
        </aside>
      </div>
    </template>
  </section>
</template>

<style scoped>
.rack-map{display:grid;gap:16px;color:#24334b;font-size:14px}.rack-map h2,.rack-map h3,.rack-map h4,.rack-map p{margin:0}.rack-map p{line-height:1.65}.rack-map h3{font-size:16px}.rack-heading,.rack-setup{display:flex;align-items:center;justify-content:space-between;gap:16px}.rack-intro,.rack-setup{padding:20px}.rack-heading h2{display:flex;align-items:center;gap:10px;font-size:20px}.rack-heading p,.rack-setup p{color:#64748b;margin-top:6px}.rack-disclaimer{display:flex;gap:8px;align-items:flex-start;background:#f1f5f9;padding:12px;border-radius:8px;margin-top:16px!important;color:#526078}.rack-disclaimer svg{flex-shrink:0;margin-top:3px}.rack-summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.rack-summary>div{display:grid;gap:8px;background:white;border:1px solid #dbe3ed;border-radius:10px;padding:16px}.rack-summary span{color:#64748b}.rack-summary b{font-size:24px;font-variant-numeric:tabular-nums}.rack-rows{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:8px}.rack-rows button{display:grid;gap:5px;text-align:left;background:white;color:#475569;padding:12px;border:1px solid #dbe3ed;font-weight:400;min-width:0}.rack-rows button[aria-pressed=true]{border-color:#2563eb;background:#eff6ff;box-shadow:inset 0 0 0 1px #2563eb;color:#1d4ed8}.rack-rows b{font-size:14px}.rack-rows span,.rack-rows small{font-size:12px;white-space:nowrap}.rack-workspace{display:grid;grid-template-columns:minmax(0,1fr) 290px;gap:16px;align-items:start}.rack-elevation{padding:20px;min-width:0}.rack-toolbar{display:flex;flex-wrap:wrap;gap:12px;align-items:end}.rack-toolbar h3{width:100%}.rack-filter{margin:0;flex:1;min-width:170px;font-size:14px;font-weight:500}.rack-filter select{margin-top:6px;width:100%;height:44px;padding:8px;border:1px solid #dbe3ed;border-radius:8px;background:white;color:inherit;font:inherit}.rack-hint{color:#64748b;margin-top:12px!important;font-size:13px}.rack-scroll{overflow-x:auto;overscroll-behavior-x:contain;margin-top:18px;padding-bottom:6px}.rack-grid{min-width:670px}.rack-grid-header,.rack-grid-level{display:grid;grid-template-columns:40px repeat(10,minmax(0,1fr));gap:8px;align-items:center}.rack-grid-header{margin-bottom:12px;font-size:12px;text-align:center;color:#64748b}.rack-grid-level{margin-bottom:8px}.rack-level{text-align:center;color:#64748b;font-size:13px}.rack-slot{position:relative;min-width:0;min-height:52px;display:grid;align-content:center;gap:3px;padding:5px 2px;font-size:13px;border:1px solid transparent;border-radius:5px;color:#334155;background:#f1f5f9}.rack-slot small{font-size:10px;font-weight:400;color:inherit;white-space:nowrap}.rack-state-unconfigured{background:#fafbfc!important;border:1px dashed #b8c5d6!important;color:#64748b!important}.rack-state-empty{background:#f1f5f9!important;color:#526078!important}.rack-state-occupied{background:#dbeafe!important;color:#1e40af!important}.rack-state-reserved{background:#fef3c7!important;color:#92400e!important}.rack-state-unavailable{background:#fee2e2!important;color:#991b1b!important}.rack-slot.rack-state-empty{margin:0;text-align:center}.rack-slot.dimmed{opacity:.24}.rack-slot.chosen{outline:3px solid #1d4ed8;outline-offset:1px;opacity:1}.rack-slot:focus-visible{outline:3px solid #111827;outline-offset:1px}.rack-legend{display:flex;flex-wrap:wrap;gap:10px 16px;margin-top:16px;font-size:12px;color:#526078}.rack-legend span{display:flex;align-items:center;gap:6px}.rack-legend i{width:14px;height:14px;border-radius:3px;border:1px solid #cbd5e1}.rack-detail{padding:20px;overflow-wrap:anywhere}.rack-detail h3{margin:10px 0;font-size:17px}.rack-detail>p{margin-top:10px}.rack-eyebrow{font-size:11px;font-weight:700;letter-spacing:.1em;color:#64748b}.rack-stock{border-top:1px solid #e2e8f0;margin-top:16px;padding-top:16px}.rack-stock h4{font-size:14px;line-height:1.6}.rack-stock>p{font-size:13px;color:#64748b;margin-top:4px}.rack-stock dl{margin:12px 0 0;display:grid;gap:8px;font-size:13px}.rack-stock dl>div{display:flex;justify-content:space-between;gap:8px}.rack-stock dd{margin:0;text-align:right;font-weight:600}.rack-updated{display:block;margin-top:18px;color:#64748b;font-size:12px}
@media(max-width:1350px){.rack-rows{grid-template-columns:repeat(4,minmax(0,1fr))}.rack-workspace{grid-template-columns:minmax(0,1fr)}.rack-detail{min-height:130px}}@media(max-width:600px){.rack-heading,.rack-setup{align-items:flex-start;flex-direction:column}.rack-summary{grid-template-columns:repeat(2,minmax(0,1fr))}.rack-rows{grid-template-columns:repeat(2,minmax(0,1fr))}.rack-intro,.rack-elevation,.rack-detail,.rack-setup{padding:14px}.rack-heading h2{font-size:18px}}
</style>
