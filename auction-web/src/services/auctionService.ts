import api from './api'
import type { Auction, AuctionCreate, AuctionListResponse } from '@/types/auction'

export const auctionService = {
  async list(page = 1, pageSize = 20, categoryId?: number): Promise<AuctionListResponse> {
    const params: Record<string, unknown> = { page, page_size: pageSize }
    if (categoryId) params.category_id = categoryId
    const { data } = await api.get('/auctions', { params })
    return data
  },

  async getById(id: number): Promise<Auction> {
    const { data } = await api.get(`/auctions/${id}`)
    return data
  },

  async create(auction: AuctionCreate): Promise<Auction> {
    const { data } = await api.post('/auctions', auction)
    return data
  },

  async activate(id: number): Promise<Auction> {
    const { data } = await api.post(`/auctions/${id}/activate`)
    return data
  },
}
