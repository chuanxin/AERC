<template>
  <v-container>
    <v-row align="center" class="mb-4">
      <v-col>
        <h1 class="text-h4">My Auctions</h1>
      </v-col>
      <v-col cols="auto">
        <v-btn color="primary" to="/auctions/create">
          <v-icon start>mdi-plus</v-icon>
          Create Auction
        </v-btn>
      </v-col>
    </v-row>
    <v-card>
      <v-card-text class="text-center text-grey py-12">
        <v-icon size="64" color="grey-lighten-1">mdi-storefront</v-icon>
        <p class="mt-4">Your auctions will appear here.</p>
      </v-card-text>
    </v-card>
  </v-container>
</template>
