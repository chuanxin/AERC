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
  // const items = [
    // {
    //   title: '財團法人農業工程研究中心',
    //   icon: 'mdi-web',
    //   href: 'https://www.aerc.org.tw/',
    // },
    // {
    //   title: '中壢辦公室',
    //   icon: 'mdi-map-marker',
    //   href: 'https://g.co/kgs/KJ7LnTH',
    //   badge: '中壢'
    // },
    // {
    //   title: 'Vuetify X',
    //   icon: ['M2.04875 3.00002L9.77052 13.3248L1.99998 21.7192H3.74882L10.5519 14.3697L16.0486 21.7192H22L13.8437 10.8137L21.0765 3.00002H19.3277L13.0624 9.76874L8.0001 3.00002H2.04875ZM4.62054 4.28821H7.35461L19.4278 20.4308H16.6937L4.62054 4.28821Z'],
    //   href: 'https://x.com/vuetifyjs',
    // },
    // {
    //   title: '台北辦公室',
    //   icon: 'mdi-map-marker',
    //   href: 'https://g.co/kgs/x7i3o1v',
    //   badge: '台北'
    // },
    // {
    //   title: 'Vuetify Discord',
    //   icon: ['M22,24L16.75,19L17.38,21H4.5A2.5,2.5 0 0,1 2,18.5V3.5A2.5,2.5 0 0,1 4.5,1H19.5A2.5,2.5 0 0,1 22,3.5V24M12,6.8C9.32,6.8 7.44,7.95 7.44,7.95C8.47,7.03 10.27,6.5 10.27,6.5L10.1,6.33C8.41,6.36 6.88,7.53 6.88,7.53C5.16,11.12 5.27,14.22 5.27,14.22C6.67,16.03 8.75,15.9 8.75,15.9L9.46,15C8.21,14.73 7.42,13.62 7.42,13.62C7.42,13.62 9.3,14.9 12,14.9C14.7,14.9 16.58,13.62 16.58,13.62C16.58,13.62 15.79,14.73 14.54,15L15.25,15.9C15.25,15.9 17.33,16.03 18.73,14.22C18.73,14.22 18.84,11.12 17.12,7.53C17.12,7.53 15.59,6.36 13.9,6.33L13.73,6.5C13.73,6.5 15.53,7.03 16.56,7.95C16.56,7.95 14.68,6.8 12,6.8M9.93,10.59C10.58,10.59 11.11,11.16 11.1,11.86C11.1,12.55 10.58,13.13 9.93,13.13C9.29,13.13 8.77,12.55 8.77,11.86C8.77,11.16 9.28,10.59 9.93,10.59M14.1,10.59C14.75,10.59 15.27,11.16 15.27,11.86C15.27,12.55 14.75,13.13 14.1,13.13C13.46,13.13 12.94,12.55 12.94,11.86C12.94,11.16 13.45,10.59 14.1,10.59Z'],
    //   href: 'https://community.vuetifyjs.com/',
    // },
    // {
    //   title: 'Vuetify Reddit',
    //   icon: `mdi-reddit`,
    //   href: 'https://reddit.com/r/vuetifyjs',
    // },
  // ]
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
