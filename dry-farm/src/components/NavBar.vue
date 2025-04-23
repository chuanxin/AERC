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
      :is="name === 'xs' ? 'h4' : 'h1'"
      class="me-4 font-weight-black app-title"
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
        class="gradient-background"
      >
        <v-tab
          v-for="item in navigationItems.filter(i => !i.children)"
          :key="item.value"
          :to="item.to"
          :value="item.value"
          :text="item.title"
          :prepend-icon="item.icon"
          color="white"
          size="x-large"
        />

        <!-- 系統管理下拉選單 -->
        <v-menu
          v-for="item in navigationItems.filter(i => i.children)"
          :key="item.value"
          open-on-hover
          location="bottom"
          offset="0 8px"
          open-delay="0"
          transition="scale-y-transition"
        >
          <template #activator="{ props }">
            <v-tab
              v-bind="props"
              color="white"
              size="x-large"
              @click.stop="preventTabSelection"
            >
              <v-icon :icon="item.icon" class="me-2" />
              {{ item.title }}
              <v-icon icon="mdi-chevron-down" size="small" class="ms-2" />
            </v-tab>
          </template>

          <v-list density="compact" bg-color="white" elevation="1">
            <v-list-item
              v-for="child in item.children"
              :key="child.value"
              :to="child.to"
              link
            >
              <template #prepend>
                <v-icon :icon="child.icon"></v-icon>
              </template>
              {{ child.title }}
            </v-list-item>
          </v-list>
        </v-menu>
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
      <v-icon
        icon="mdi-account"
        start
      />
      <strong>{{ userStore.userFullName }}，您好</strong>&nbsp;
      <!-- <span>(農工中心)</span> -->
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
        :title="userStore.userFullName"
        :subtitle="userStore.officeName"
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
      <!-- 一般選單項目 -->
      <v-list-item
        v-for="item in navigationItems.filter(i => !i.children)"
        :key="item.value"
        :value="item.value"
        :title="item.title"
        :to="item.to"
        :prepend-icon="item.icon"
      />

      <!-- 有子選單的項目 -->
      <v-list-group
        v-for="item in navigationItems.filter(i => i.children)"
        :key="item.value"
        :value="item.value"
      >
        <template #activator="{ props }">
          <v-list-item
            v-bind="props"
            :value="item.value"
            :title="item.title"
            :prepend-icon="item.icon"
          />
        </template>

        <v-list-item
          v-for="child in item.children"
          :key="child.value"
          :value="child.value"
          :title="child.title"
          :to="child.to"
          :prepend-icon="child.icon"
        />
      </v-list-group>
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
  import { useUserStore } from '@/stores/users'

  // Asset imports
  import logoXL from '@/assets/logo-xl.png'
  import logoS from '@/assets/logo-s.png'

  // Route and theme setup
  const route = useRoute()
  const router = useRouter()
  const themeStore = useThemeStore()
  const userStore = useUserStore()

  // Component state
  const activeTab = ref('index')
  const drawer = ref(false)

  const handleLogout = async () => {
    try {
      userStore.logout()
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
      icon: 'mdi-cog',
      children: [
        {
          title: '帳號管理',
          value: 'config-accounts',
          to: { path: '/config/accounts' },
          icon: 'mdi-account-cog'
        },
        {
          title: '群組權限管理',
          value: 'config-permissions',
          to: { path: '/config/permissions' },
          icon: 'mdi-shield-account'
        },
        {
          title: '圖資管理',
          value: 'config-layers',
          to: { path: '/config/layers' },
          icon: 'mdi-map-legend'
        },
        {
          title: '首頁管理',
          value: 'config-home',
          to: { path: '/config/home' },
          icon: 'mdi-home-edit'
        }
      ]
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

  const preventTabSelection = (event: Event) => {
    // Prevent default behavior and stop propagation
    event.preventDefault();
    event.stopPropagation();

    nextTick(() => {
      const currentPath = route.path;
      if (currentPath === '/') {
        activeTab.value = 'index';
      } else {
        const mainPath = currentPath.split('/')[1];
        activeTab.value = mainPath;
      }
    });
  }

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
      if (newPath === '/') {
        activeTab.value = 'index'
      } else {
        const mainPath = newPath.split('/')[1]
        activeTab.value = mainPath

        // 檢查是否是子路徑
        if (mainPath === 'config') {
          const subPath = newPath.split('/')[2]
          if (subPath) {
            activeTab.value = `config-${subPath}`
          }
        }
      }
    },
    { immediate: true }
  )
</script>

<style scoped>
.gradient-background{
  background: linear-gradient(60deg, #0B6E99 0%, #72c4e0 100%);
  color: white;
}

.app-title {
  font-weight: 900 !important;
  letter-spacing: -0.5px;
  text-shadow: 1px 0 0 currentColor;
}

/* 下拉選單樣式 */
:deep(.v-list-item--active) {
  background-color: rgba(91, 194, 193, 0.1);
}

:deep(.v-list-group__header.v-list-item--active) {
  background-color: rgba(90, 67, 103, 0.1);
}
</style>
