<template>
  <v-card>
    <v-card-title>Bid History</v-card-title>
    <v-list v-if="bids.length" density="compact">
      <v-list-item v-for="bid in bids" :key="bid.id">
        <template #prepend>
          <v-icon :color="bid.is_winning ? 'success' : 'grey'" size="small">
            {{ bid.is_winning ? 'mdi-check-circle' : 'mdi-circle-outline' }}
          </v-icon>
        </template>
        <v-list-item-title>
          NT$ {{ bid.amount.toLocaleString() }}
        </v-list-item-title>
        <v-list-item-subtitle>
          User #{{ bid.user_id }}
        </v-list-item-subtitle>
      </v-list-item>
    </v-list>
    <v-card-text v-else class="text-center text-grey">
      No bids yet
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import type { Bid } from '@/types/bid'

defineProps<{ bids: Bid[] }>()
</script>
