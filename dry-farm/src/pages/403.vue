<template>
  <v-container class="fill-height" fluid>
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6" class="text-center">
        <v-icon size="80" color="warning">mdi-lock-outline</v-icon>
        <h1 class="text-h4 font-weight-bold mt-4 mb-2">無存取權限</h1>
        <p class="text-body-1 text-medium-emphasis mb-6">
          您的帳號角色無法存取此頁面。如有疑問，請聯絡系統管理員。
        </p>
        <v-btn color="primary" variant="tonal" prepend-icon="mdi-home" to="/">
          返回首頁
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
</script>
