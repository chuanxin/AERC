export interface Bid {
  id: number
  auction_id: number
  user_id: number
  amount: number
  is_winning: boolean
  created_at: string
}

export interface BidUpdate {
  bid_id: number
  amount: string
  user_id: number
  bid_count: number
  current_price: string
  end_time: string
}
