<template>
  <v-card :to="`/auctions/${auction.id}`" hover>
    <v-img
      :src="primaryImage"
      height="200"
      cover
    >
      <template #placeholder>
        <v-row align="center" justify="center" class="fill-height bg-grey-lighten-3">
          <v-icon size="48" color="grey">mdi-image</v-icon>
        </v-row>
      </template>
      <v-chip
        :color="statusColor"
        class="ma-2"
        size="small"
      >
        {{ auction.status }}
      </v-chip>
    </v-img>
    <v-card-title class="text-truncate">{{ auction.title }}</v-card-title>
    <v-card-text>
      <div class="text-h6 text-primary">
        NT$ {{ auction.current_price.toLocaleString() }}
      </div>
      <div class="text-body-2 text-grey">
        {{ auction.bid_count }} bids
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Auction } from '@/types/auction'

const props = defineProps<{ auction: Auction }>()

const primaryImage = computed(() => {
  const img = props.auction.images?.find((i) => i.is_primary) || props.auction.images?.[0]
  return img?.url || ''
})

const statusColor = computed(() => {
  const map: Record<string, string> = {
    active: 'success',
    ended: 'grey',
    sold: 'primary',
    draft: 'warning',
    cancelled: 'error',
  }
  return map[props.auction.status] || 'grey'
})
</script>
