<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="text-h5">Create Auction</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="submit">
              <v-text-field v-model="form.title" label="Title" required variant="outlined" />
              <v-textarea v-model="form.description" label="Description" variant="outlined" rows="4" />
              <v-row>
                <v-col cols="6">
                  <v-text-field v-model.number="form.starting_price" label="Starting Price (NT$)" type="number" variant="outlined" />
                </v-col>
                <v-col cols="6">
                  <v-text-field v-model.number="form.bid_increment" label="Bid Increment (NT$)" type="number" variant="outlined" />
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="6">
                  <v-text-field v-model="form.start_time" label="Start Time" type="datetime-local" variant="outlined" />
                </v-col>
                <v-col cols="6">
                  <v-text-field v-model="form.end_time" label="End Time" type="datetime-local" variant="outlined" />
                </v-col>
              </v-row>
              <v-text-field v-model.number="form.reserve_price" label="Reserve Price (optional)" type="number" variant="outlined" />
              <v-switch v-model="form.auto_extend" label="Auto-extend on late bids" color="primary" />
              <v-btn type="submit" color="primary" size="large" block>Create Auction</v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { auctionService } from '@/services/auctionService'

const router = useRouter()
const form = reactive({
  title: '',
  description: '',
  starting_price: 0,
  bid_increment: 100,
  start_time: '',
  end_time: '',
  reserve_price: undefined as number | undefined,
  auto_extend: true,
})

async function submit() {
  const auction = await auctionService.create(form)
  router.push(`/auctions/${auction.id}`)
}
</script>
