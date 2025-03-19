<template>
  <!-- Floating Report Bug Label -->
  <v-btn
    class="report-bug-btn"
    color="error"
    variant="flat"
    density="comfortable"
    prepend-icon="mdi-bug"
    @click="handleReportBug"
  >
    回報問題
  </v-btn>
</template>

<script lang="ts" setup>
const handleReportBug = () => {
  // Add your bug report logic here
  console.log('Report bug clicked')
}
</script>

<style scoped>
.report-bug-btn {
  position: fixed;
  right: -130px;
  top: 50%;
  transform: rotate(-90deg);
  transform-origin: left bottom;
  z-index: 100;
  border-radius: 4px 4px 0 0;
}
/* Optional: Add hover effect to slightly reveal the button */
.report-bug-btn:hover {
  right: -120px;
}
</style>
