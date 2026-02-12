import { ref, computed, onUnmounted, watch } from 'vue'
import dayjs from 'dayjs'

export function useCountdown(endTimeRef: ReturnType<typeof ref<string>>) {
  const remaining = ref(0) // seconds
  let timer: ReturnType<typeof setInterval> | null = null

  const display = computed(() => {
    if (remaining.value <= 0) return '00:00:00'
    const h = Math.floor(remaining.value / 3600)
    const m = Math.floor((remaining.value % 3600) / 60)
    const s = remaining.value % 60
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  })

  const isUrgent = computed(() => remaining.value > 0 && remaining.value < 300)
  const isEnded = computed(() => remaining.value <= 0)

  function tick() {
    if (!endTimeRef.value) return
    const diff = dayjs(endTimeRef.value).diff(dayjs(), 'second')
    remaining.value = Math.max(0, diff)
    if (remaining.value <= 0 && timer) {
      clearInterval(timer)
      timer = null
    }
  }

  function start() {
    tick()
    timer = setInterval(tick, 1000)
  }

  watch(endTimeRef, () => {
    tick()
  })

  onUnmounted(() => {
    if (timer) clearInterval(timer)
  })

  return { remaining, display, isUrgent, isEnded, start }
}
