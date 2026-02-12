<template>
  <v-container v-if="auction">
    <v-row>
      <!-- Auction images -->
      <v-col cols="12" md="7">
        <v-card>
          <v-img
            :src="primaryImage"
            height="400"
            cover
          >
            <template #placeholder>
              <v-row align="center" justify="center" class="fill-height">
                <v-icon size="80" color="grey">mdi-image</v-icon>
              </v-row>
            </template>
          </v-img>
        </v-card>
        <v-card class="mt-4">
          <v-card-title>Description</v-card-title>
          <v-card-text>{{ auction.description }}</v-card-text>
        </v-card>
      </v-col>

      <!-- Bid panel -->
      <v-col cols="12" md="5">
        <v-card>
          <v-card-title class="text-h5">{{ auction.title }}</v-card-title>
          <v-card-text>
            <div class="text-h4 text-primary font-weight-bold mb-2">
              NT$ {{ bidding.currentPrice.value.toLocaleString() }}
            </div>
            <v-chip :color="countdown.isUrgent.value ? 'error' : 'primary'" class="mb-4">
              <v-icon start>mdi-clock</v-icon>
              {{ countdown.display.value }}
            </v-chip>
            <div class="text-body-2 text-grey mb-4">
              {{ bidding.bidCount.value }} bids
            </div>

            <v-divider class="mb-4" />

            <v-text-field
              v-model.number="bidAmount"
              type="number"
              label="Your Bid (NT$)"
              :min="bidding.minBid.value"
              variant="outlined"
              :hint="`Minimum: NT$ ${bidding.minBid.value.toLocaleString()}`"
              persistent-hint
            />
            <v-btn
              color="secondary"
              size="large"
              block
              class="mt-2"
              :disabled="!auth.isLoggedIn || countdown.isEnded.value"
              @click="submitBid"
            >
              <v-icon start>mdi-gavel</v-icon>
              Place Bid
            </v-btn>
          </v-card-text>
        </v-card>

        <!-- Bid history -->
        <v-card class="mt-4">
          <v-card-title>Bid History</v-card-title>
          <v-list density="compact">
            <v-list-item
              v-for="bid in bidding.recentBids.value.slice(0, 10)"
              :key="bid.id"
            >
              <v-list-item-title>
                NT$ {{ bid.amount.toLocaleString() }}
              </v-list-item-title>
              <v-list-item-subtitle>
                User #{{ bid.user_id }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuctionStore } from '@/stores/auction'
import { useAuthStore } from '@/stores/auth'
import { useBidding } from '@/composables/useBidding'
import { useCountdown } from '@/composables/useCountdown'
import { bidService } from '@/services/bidService'

const route = useRoute()
const auctionStore = useAuctionStore()
const auth = useAuthStore()

const auctionId = Number(route.params.id)
const bidding = useBidding(auctionId)
const countdown = useCountdown(bidding.endTime)
const bidAmount = ref(0)

const auction = computed(() => auctionStore.currentAuction)
const primaryImage = computed(() => {
  const img = auction.value?.images?.find((i) => i.is_primary) || auction.value?.images?.[0]
  return img?.url || ''
})

async function submitBid() {
  await bidService.place(auctionId, bidAmount.value)
  bidAmount.value = bidding.minBid.value
}

onMounted(async () => {
  await auctionStore.fetchAuction(auctionId)
  if (auction.value) {
    bidding.currentPrice.value = auction.value.current_price
    bidding.bidCount.value = auction.value.bid_count
    bidding.bidIncrement.value = auction.value.bid_increment
    bidding.endTime.value = auction.value.end_time
    bidAmount.value = auction.value.current_price + auction.value.bid_increment
  }
  bidding.connect()
  countdown.start()
})
</script>
