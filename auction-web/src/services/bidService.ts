import api from './api'
import type { Bid } from '@/types/bid'

export const bidService = {
  async place(auctionId: number, amount: number): Promise<Bid> {
    const { data } = await api.post(`/auctions/${auctionId}/bids`, { amount })
    return data
  },

  async list(auctionId: number, limit = 50): Promise<Bid[]> {
    const { data } = await api.get(`/auctions/${auctionId}/bids`, { params: { limit } })
    return data
  },
}
