export interface Auction {
  id: number
  seller_id: number
  title: string
  description: string | null
  category_id: number | null
  starting_price: number
  current_price: number
  bid_increment: number
  bid_count: number
  status: 'draft' | 'active' | 'ended' | 'sold' | 'cancelled'
  start_time: string
  end_time: string
  auto_extend: boolean
  winner_id: number | null
  created_at: string
  images: AuctionImage[]
}

export interface AuctionImage {
  id: number
  url: string
  sort_order: number
  is_primary: boolean
}

export interface AuctionListResponse {
  items: Auction[]
  total: number
  page: number
  page_size: number
}

export interface AuctionCreate {
  title: string
  description?: string
  category_id?: number
  starting_price: number
  reserve_price?: number
  bid_increment: number
  start_time: string
  end_time: string
  auto_extend?: boolean
}
