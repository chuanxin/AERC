<template>
  <v-container>
    <v-row>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Filters</v-card-title>
          <v-card-text>
            <v-text-field
              v-model="search"
              label="Search"
              prepend-inner-icon="mdi-magnify"
              clearable
              variant="outlined"
              density="compact"
            />
            <v-select
              v-model="sortBy"
              :items="sortOptions"
              label="Sort By"
              variant="outlined"
              density="compact"
            />
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="9">
        <v-row>
          <v-col
            v-for="auction in store.auctions"
            :key="auction.id"
            cols="12"
            sm="6"
            lg="4"
          >
            <auction-card :auction="auction" />
          </v-col>
        </v-row>
        <v-pagination
          v-model="page"
          :length="Math.ceil(store.total / pageSize)"
          class="mt-4"
          @update:model-value="loadPage"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuctionStore } from '@/stores/auction'
import AuctionCard from '@/components/auction/AuctionCard.vue'

const store = useAuctionStore()
const search = ref('')
const sortBy = ref('newest')
const page = ref(1)
const pageSize = 20

const sortOptions = [
  { title: 'Newest', value: 'newest' },
  { title: 'Ending Soon', value: 'ending_soon' },
  { title: 'Price: Low to High', value: 'price_asc' },
  { title: 'Price: High to Low', value: 'price_desc' },
  { title: 'Most Bids', value: 'most_bids' },
]

function loadPage(p: number) {
  store.fetchAuctions(p, pageSize)
}

onMounted(() => {
  store.fetchAuctions(1, pageSize)
})
</script>
