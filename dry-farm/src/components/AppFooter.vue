<template>
  <v-footer
    :app="false"
    class="pa-0 d-flex flex-column transparent-footer"
    height="auto"
  >
    <!-- <a
      v-for="item in items"
      :key="item.title"
      :href="item.href"
      :title="item.title"
      class="d-inline-block mx-2 social-link"
      rel="noopener noreferrer"
      target="_blank"
    >
      <v-badge
        v-if="item.badge"
        :content="item.badge"
        color="white"
        inline
        class="pt-1"
      >
        <v-icon
          :icon="item.icon"
          :size="item.icon === 'mdi-web' ? 24 : 16"
        />
      </v-badge>
      <v-icon
        v-else
        :icon="item.icon"
        :size="item.icon === 'mdi-web' ? 24 : 16"
      />
    </a> -->

    <!-- <div
      class="text-caption text-disabled"
      style="position: absolute; right: 16px;"
    >
      &copy; {{ (new Date()).getFullYear() }} <span class="d-none d-sm-inline-block">Agricultural Engineering Research Center 財團法人農業工程研究中心</span>
      <a
        class="text-decoration-none on-surface"
        href="https://vuetifyjs.com/about/licensing/"
        rel="noopener noreferrer"
        target="_blank"
      >
        MIT License
      </a>
    </div> -->
    <div class="mb-2 footer-content d-flex flex-column justify-end">
      <div class="text-center footer-text">
        <span>本系統網站建議以Google Chrome、Edge、Firefox等瀏覽器進行最佳瀏覽使用<br>版權所有： 農業部農田水利署、系統開發：財團法人農業工程研究中心</span>
      </div>
    </div>
  </v-footer>
</template>

<script setup lang="ts">

</script>

<style scoped lang="sass">
.footer-content
  position: relative
  width: 100%
  height: 100%
  // z-index: 2
  padding-top: 120px

.footer-text
  font-size: 14px
  width: 100%
  text-align: center
  padding: 20px 0
  z-index: 2

.transparent-footer
  background-image: url('@/assets/bg_footer.svg');
  background-size: cover;
  background-repeat: no-repeat;
  width: 100%;
  min-height: 300px
  background-color: transparent
  position: relative
  z-index: 1
  background-color: rgba(255, 255, 255, 1)
  color: black
  margin-top: -120px !important
</style>
