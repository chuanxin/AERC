import { defineStore } from 'pinia'
import { ref } from 'vue'
import { auctionService } from '@/services/auctionService'
import type { Auction } from '@/types/auction'

export const useAuctionStore = defineStore('auction', () => {
  const auctions = ref<Auction[]>([])
  const currentAuction = ref<Auction | null>(null)
  const total = ref(0)
  const loading = ref(false)

  async function fetchAuctions(page = 1, pageSize = 20, categoryId?: number) {
    loading.value = true
    try {
      const response = await auctionService.list(page, pageSize, categoryId)
      auctions.value = response.items
      total.value = response.total
    } finally {
      loading.value = false
    }
  }

  async function fetchAuction(id: number) {
    loading.value = true
    try {
      currentAuction.value = await auctionService.getById(id)
    } finally {
      loading.value = false
    }
  }

  return { auctions, currentAuction, total, loading, fetchAuctions, fetchAuction }
})
