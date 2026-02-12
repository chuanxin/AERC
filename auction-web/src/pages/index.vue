<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h3 mb-4">Featured Auctions</h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col
        v-for="auction in store.auctions"
        :key="auction.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <auction-card :auction="auction" />
      </v-col>
    </v-row>
    <v-row v-if="store.loading" justify="center">
      <v-progress-circular indeterminate color="primary" />
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuctionStore } from '@/stores/auction'
import AuctionCard from '@/components/auction/AuctionCard.vue'

const store = useAuctionStore()

onMounted(() => {
  store.fetchAuctions()
})
</script>
