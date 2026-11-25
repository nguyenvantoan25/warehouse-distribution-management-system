<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
const props = defineProps<{ flow: { date: string; quantity: number }[] }>()
const element = ref<HTMLDivElement | null>(null)
const width = ref(600); const height = ref(260)
let observer: ResizeObserver | undefined
onMounted(() => {
  observer = new ResizeObserver(([entry]) => { width.value = entry.contentRect.width; height.value = entry.contentRect.height })
  if (element.value) observer.observe(element.value)
})
onBeforeUnmount(() => observer?.disconnect())
const max = computed(() => Math.max(4, Math.ceil(Math.max(...props.flow.map(p => p.quantity), 0) / 4) * 4))
const baseline = computed(() => height.value - 35)
const plotHeight = computed(() => height.value - 56)
const points = computed(() => props.flow.map((point, i) => ({
  ...point, x: 30 + i * ((width.value - 46) / Math.max(1, props.flow.length - 1)),
  y: baseline.value - point.quantity / max.value * plotHeight.value,
})))
const line = computed(() => points.value.map((point, i) => `${i ? 'L' : 'M'}${point.x},${point.y}`).join(' '))
const area = computed(() => points.value.length ? `${line.value} L${points.value[points.value.length-1].x},${baseline.value} L30,${baseline.value} Z` : '')
const total = computed(() => props.flow.reduce((n, day) => n + day.quantity, 0))
const ticks = computed(() => points.value.filter((_, i) => i === 0 || i === props.flow.length-1 || i % (width.value < 400 ? 10 : 5) === 0))
const dateLabel = (date: string) => `${date.slice(8)}/${date.slice(5, 7)}`
</script>
<template>
  <div ref="element" class="df-flow-chart">
    <svg :viewBox="`0 0 ${width} ${height}`" role="img" :aria-label="`Số kiện đã bàn giao trong 30 ngày: ${total}`">
      <defs><linearGradient id="df-flow-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#2563eb" stop-opacity=".18"/><stop offset="100%" stop-color="#2563eb" stop-opacity="0"/></linearGradient></defs>
      <g v-for="i in 5" :key="i">
        <line x1="30" :y1="21+(i-1)*plotHeight/4" :x2="width-15" :y2="21+(i-1)*plotHeight/4" stroke="#e2e8f0" stroke-dasharray="4 4"/>
        <text x="18" :y="25+(i-1)*plotHeight/4" text-anchor="end">{{ max-(i-1)*max/4 }}</text>
      </g>
      <path :d="area" fill="url(#df-flow-fill)"/>
      <path :d="line" fill="none" stroke="#2563eb" stroke-width="2.5"/>
      <circle v-for="point in points.filter(p => p.quantity > 0)" :key="point.date" :cx="point.x" :cy="point.y" r="4" fill="#2563eb" stroke="white" stroke-width="2"><title>{{ dateLabel(point.date) }}: {{ point.quantity }} kiện</title></circle>
      <text v-for="tick in ticks" :key="tick.date" :x="tick.x" :y="height-10" text-anchor="middle">{{ dateLabel(tick.date) }}</text>
    </svg>
    <span v-if="!total" class="df-chart-empty">Chưa có giao dịch bàn giao trong 30 ngày qua</span>
  </div>
</template>
