<template>
  <!-- Main navigation bar component -->
  <v-app-bar
    :extended="!showDrawer"
    :extension-height="showDrawer ? 0 : 48"
    scroll-behavior="elevate"
  >
    <!-- <template v-slot:image>
      <v-img
        gradient="to top right, rgba(19,84,122,.8), rgba(128,208,199,.8)"
      ></v-img>
    </template> -->
    <!-- Application title -->
    <component
      :is="name === 'xs' ? 'h4' : 'h2'"
      class="me-4 font-weight-light"
    >
      推廣管路灌溉設施管理資料庫
    </component>
    <!-- Logo section -->
    <template #prepend>
      <img
        :src="logoConfig.src"
        :width="logoConfig.width"
        alt="Logo"
        class="ma-2"
      >
    </template>
    <!-- Navigation tabs for desktop view -->
    <template #extension>
      <v-tabs
        v-if="!showDrawer"
        v-model="activeTab"
        :grow="true"
      >
        <v-tab
          v-for="item in navigationItems"
          :key="item.value"
          :to="item.to"
          :value="item.value"
          :text="item.title"
          size="x-large"
        />
      </v-tabs>
    </template>
    <v-spacer />
    <v-chip
      v-if="!showDrawer"
      class="ma-2"
      color="primary"
      variant="outlined"
      rounded
    >
      <strong>林洪陳</strong>&nbsp;
      <span>(農工中心)</span>
      <v-icon
        icon="mdi-account"
        end
      />
    </v-chip>
    <v-btn
      v-if="!showDrawer"
      :icon="themeStore.theme === 'light' ? 'mdi-logout' : 'mdi-login'"
      text="登出系統"
      slim
      rounded="circl"
      @click="handleLogout"
    />
    <!-- Mobile menu button - only shows on small screens -->
    <template v-if="showDrawer">
      <v-btn
        icon="mdi-dots-vertical"
        variant="text"
        rounded="circl"
        @click.stop="drawer = !drawer"
      />
    </template>
    <!-- Theme toggle button (currently disabled) -->
    <!-- <v-btn
      :prepend-icon="themeStore.theme === 'light' ? 'mdi-weather-sunny' : 'mdi-weather-night'"
      text="Toggle Theme"
      slim
      @click="themeStore.toggleTheme"
    /> -->
  </v-app-bar>
  <!-- Mobile navigation drawer -->
  <v-navigation-drawer
    v-model="drawer"
    location="right"
    temporary
  >
    <v-list>
      <v-list-item
        subtitle="農工中心"
        title="林洪陳"
      >
        <template #prepend>
          <v-avatar color="primary">
            <v-icon
              color="white"
              size="large"
            >
              mdi-account
            </v-icon>
          </v-avatar>
        </template>
      </v-list-item>
    </v-list>

    <v-divider />
    <v-list
      v-model:selected="activeTab"
    >
      <v-list-item
        v-for="item in navigationItems"
        :key="item.value"
        :value="item.value"
        :title="item.title"
        :to="item.to"
        :prepend-icon="item.icon"
      />
    </v-list>
    <!-- Logout button -->
    <template #append>
      <div class="pa-0 ma-0">
        <v-btn
          block
          prepend-icon="mdi-logout"
          @click="handleLogout"
        >
          登出系統
        </v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script lang="ts" setup>
  // Core imports
  import { useDisplay } from 'vuetify'
  import { useThemeStore } from '@/stores/theme'

  // Asset imports
  import logoXL from '@/assets/logo-xl.png'
  import logoS from '@/assets/logo-s.png'

  // Route and theme setup
  const route = useRoute()
  const router = useRouter()
  const themeStore = useThemeStore()

  // Component state
  const activeTab = ref('index')
  const drawer = ref(false)

  const handleLogout = async () => {
    try {
      // Add your logout API call here if needed
      console.log('User logged out')
      await router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }
  // Navigation items configuration
  const navigationItems = [
    {
      title: '首頁',
      value: 'index',
      to: { path: '/' },
      icon: 'mdi-home'
    },
    {
      title: '補助申請',
      value: 'grants',
      to: { path: '/grants' },
      icon: 'mdi-file-sign'
    },
    {
      title: '申請資格預查',
      value: 'qualification',
      to: { path: '/qualification' },
      icon: 'mdi-account-check'
    },
    {
      title: '統計報表',
      value: 'statistics',
      to: { path: '/statistics' },
      icon: 'mdi-chart-bar'
    },
    {
      title: '材料管理',
      value: 'supplies',
      to: { path: '/supplies' },
      icon: 'mdi-package-variant-closed'
    },
    {
      title: 'GIS圖台',
      value: 'maps',
      to: { path: '/maps' },
      icon: 'mdi-layers-triple'
    },
    {
      title: '系統管理',
      value: 'config',
      to: { path: '/config' },
      icon: 'mdi-cog'
    }
  ]

  // Responsive display setup
  const { name } = useDisplay()

  // Computed property for responsive logo configuration
  const logoConfig = computed(() => {
    switch (name.value) {
      case 'xs':
      case 'sm':
        return {
          src: logoS,
          width: 43
        }
      case 'md':
      case 'lg':
      case 'xl':
      case 'xxl':
        return {
          src: logoXL,
          width: 250
        }
      default:
        return {
          src: logoS,
          width: 43
        }
    }
  })

  // Computed property to control drawer visibility based on screen size
  const showDrawer = computed(() => {
    return name.value === 'xs' || name.value === 'sm'
  })

  // Watch for screen size changes to auto-close drawer on larger screens
  watch(
    showDrawer,
    (newValue) => {
      if (!newValue && drawer.value) {
        drawer.value = false
      }
    }
  )

  // Sync active tab with current route
  watch(
    () => route.path,
    (newPath) => {
      activeTab.value = newPath === '/' ? 'index' : newPath.substring(1)
    },
    { immediate: true }
  )
</script>

<style scoped>
</style>
