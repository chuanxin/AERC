import { ref, computed, onUnmounted } from 'vue'
import { io, type Socket } from 'socket.io-client'
import { useAuthStore } from '@/stores/auth'
import type { Bid, BidUpdate } from '@/types/bid'

export function useBidding(auctionId: number) {
  const auth = useAuthStore()
  const socket = ref<Socket | null>(null)
  const currentPrice = ref(0)
  const bidCount = ref(0)
  const endTime = ref('')
  const bidIncrement = ref(0)
  const recentBids = ref<Bid[]>([])
  const isConnected = ref(false)

  const minBid = computed(() => currentPrice.value + bidIncrement.value)

  function connect() {
    socket.value = io('/ws', {
      auth: { token: auth.token },
    })

    socket.value.on('connect', () => {
      isConnected.value = true
      socket.value?.emit('join_auction', { auction_id: auctionId })
    })

    socket.value.on('bid_update', (data: BidUpdate) => {
      currentPrice.value = parseFloat(data.current_price)
      bidCount.value = data.bid_count
      endTime.value = data.end_time
      recentBids.value.unshift({
        id: data.bid_id,
        auction_id: auctionId,
        amount: parseFloat(data.amount),
        user_id: data.user_id,
        is_winning: true,
        created_at: new Date().toISOString(),
      })
    })

    socket.value.on('auction_ended', () => {
      // Parent component handles UI update
    })

    socket.value.on('disconnect', () => {
      isConnected.value = false
    })
  }

  function disconnect() {
    socket.value?.emit('leave_auction', { auction_id: auctionId })
    socket.value?.disconnect()
  }

  onUnmounted(disconnect)

  return {
    connect,
    disconnect,
    currentPrice,
    bidCount,
    endTime,
    bidIncrement,
    recentBids,
    isConnected,
    minBid,
  }
}
