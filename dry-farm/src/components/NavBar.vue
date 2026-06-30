<template>
  <!-- Main navigation bar component -->
  <v-app-bar
    :extended="!showDrawer"
    :extension-height="showDrawer ? 0 : 48"
    scroll-behavior="elevate"
  >
    <template #image>
      <!-- Background image for the app bar -->
      <v-img
        src="@/assets/bg_top.svg"
        class="d-none d-sm-block"
        height="100%"
        position="85% top "
      />
      <!-- <v-img
        gradient="to top right, rgba(19,84,122,.8), rgba(128,208,199,.8)"
      ></v-img> -->
    </template>
    <!-- Application title -->
    <component
      :is="name === 'xs' ? 'h4' : 'h1'"
      class="me-4 font-black app-title"
      style="font-family: 'Noto Sans TC', 'Microsoft JhengHei', sans-serif;"
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
        <!-- 按照 navigationItems 原始順序渲染所有項目 -->
        <template
          v-for="item in navigationItems"
          :key="item.value"
        >
          <!-- 一般選單項目（沒有子選單） -->
          <v-tab
            v-if="!item.children"
            :to="item.to"
            :value="item.value"
            :text="item.title"
            :prepend-icon="item.icon"
            :disabled="item.disabled"
            color="white"
            size="x-large"
          />

          <!-- 有子選單的項目（下拉選單） -->
          <v-menu
            v-else
            open-on-hover
            location="bottom"
            offset="0 8px"
            open-delay="0"
            transition="scale-y-transition"
            :disabled="item.disabled"
          >
            <template #activator="{ props }">
              <v-tab
                v-bind="props"
                color="white"
                size="x-large"
                :disabled="item.disabled"
                @click.stop="preventTabSelection"
              >
                <v-icon
                  :icon="item.icon"
                  class="me-2"
                />
                {{ item.title }}
                <v-icon
                  icon="mdi-chevron-down"
                  size="small"
                  class="ms-2"
                />
              </v-tab>
            </template>

            <v-list
              density="compact"
              bg-color="white"
              elevation="1"
            >
              <v-list-item
                v-for="child in item.children"
                :key="child.value"
                @click="navigateToChild(child.to)"
              >
                <template #prepend>
                  <v-icon :icon="child.icon" />
                </template>
                {{ child.title }}
              </v-list-item>
            </v-list>
          </v-menu>
        </template>
      </v-tabs>
    </template>
    <v-spacer />
    <v-chip
      v-if="!showDrawer"
      class="ma-2 h-auto py-1" 
      :color="remainingTime < 60 ? 'error' : 'primary'"
      variant="outlined"
      rounded
    >
      <v-icon
        icon="mdi-account"
        start
        class="self-center" 
      />
      
      <div class="d-flex flex-column text-start justify-center">
        <strong style="line-height: 1.2;">{{ userStore.userFullName }}，您好</strong>
        
        <span 
          v-if="formattedRemainingTime" 
          class="text-caption mt-0 text-grey-darken-3"
          style="line-height: 1; font-size: 0.7rem !important;"
        >
          倒數 : {{ formattedRemainingTime }}
        </span>
      </div>
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
    <v-list>
      <!-- 按照 navigationItems 原始順序渲染所有項目 -->
      <template
        v-for="item in navigationItems"
        :key="item.value"
      >
        <!-- 一般選單項目（沒有子選單） -->
        <v-list-item
          v-if="!item.children"
          :value="item.value"
          :title="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          :disabled="item.disabled"
        />

        <!-- 有子選單的項目 -->
        <v-list-group
          v-else
          :value="item.value"
        >
          <template #activator="{ props }">
            <v-list-item
              v-bind="props"
              :value="item.value"
              :title="item.title"
              :prepend-icon="item.icon"
              :disabled="item.disabled"
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
      </template>
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

  //added by Joya. Inorder to use ramaining time
  import { computed, onMounted, onUnmounted, ref, watch, nextTick } from 'vue'

  // Route and theme setup
  const route = useRoute()
  const router = useRouter()
  const themeStore = useThemeStore()
  const userStore = useUserStore()

  // Component state
  const activeTab = ref('index')
  const drawer = ref(false)

  //  Joya added 登出倒數計時相關邏輯
const currentTime = ref(Math.floor(Date.now() / 1000))
let timerId: number | null = null

// 計算剩餘時間 (秒)
const remainingTime = computed(() => {
  if (!userStore.token || !userStore.tokenExpiresAt) return 0
  return Math.max(0, userStore.tokenExpiresAt - currentTime.value)
})

// 格式化時間顯示 (例如：29分59秒)
const formattedRemainingTime = computed(() => {
  const seconds = remainingTime.value
  if (seconds <= 0) return ''
  
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  
  if (minutes > 0) {
    return `${minutes}分${secs}秒`
  }
  return `${secs}秒`
})

// 啟動計時器
const startTimer = () => {
  if (timerId) clearInterval(timerId)
  timerId = window.setInterval(() => {
    currentTime.value = Math.floor(Date.now() / 1000)
  }, 1000)
}

// 生命週期掛載與卸載
onMounted(() => {
  startTimer()
})

onUnmounted(() => {
  if (timerId) clearInterval(timerId)
})
  // Joya added end -------------------

  const handleLogout = async () => {
    try {
      userStore.logout()
      sessionStorage.removeItem('indexSearchState')   // joya added to clear session storage on logout
      console.log('User logged out')
      await router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const navigateToChild = (to: { path: string }) => {
    router.push(to.path)
  }
  // Navigation items configuration
  type NavChild = { title: string; value: string; to: { path: string }; icon: string; permission?: { module: string; action: string } }
  type NavItem = { title: string; value: string; to?: { path: string }; icon: string; permission?: { module: string; action: string }; hideWhen?: { module: string; action: string }; children?: NavChild[] }

  const _allNavItems: NavItem[] = [
    {
      title: '首頁',
      value: 'index',
      to: { path: '/' },
      icon: 'mdi-home'
    },
    {
      title: '補助申請',
      value: 'grants',
      // to: { path: '/grants' },
      icon: 'mdi-file-sign',
      children: [
        {
          title: '補助案件申請',
          value: 'grants-application',
          to: { path: '/grants' },
          icon: 'mdi-file-document-edit'
        },
        {
          title: '申請案件查詢與列印',
          value: 'grants-query',
          to: { path: '/grants/query' },
          icon: 'mdi-magnify',
          permission: { module: 'batch_print', action: 'view' }
        }
      ]
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
      icon: 'mdi-chart-bar',
      permission: { module: 'reports', action: 'view' }
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
      title: '文件下載',
      value: 'downloads',
      to: { path: '/downloads' },
      icon: 'mdi-file-download'
    },
    {
      title: '系統管理',
      value: 'config',
      icon: 'mdi-cog',
      children: [
        {
          title: '使用者管理',
          value: 'config-accounts',
          to: { path: '/config/accounts' },
          icon: 'mdi-account-cog',
          permission: { module: 'users', action: 'view' }
        },
        {
          title: '帳號資訊',
          value: 'account-profile',
          to: { path: '/profile' },
          icon: 'mdi-account-circle',
        },
      ],
    }
  ]

  const navigationItems = computed(() =>
    _allNavItems
      .map(item => {
        if (!item.children) return item
        const visibleChildren = item.children.filter(
          c => !c.permission || userStore.can(c.permission.module, c.permission.action)
        )
        if (visibleChildren.length === 0) return null
        // 單一子項時攤平為普通連結，繼承子項的 title/icon/value 避免顯示父群組名稱
        if (visibleChildren.length === 1) {
          const child = visibleChildren[0]
          return { ...item, ...child, children: undefined }
        }
        return { ...item, children: visibleChildren }
      })
      .filter((item): item is NavItem =>
        item !== null &&
        (!item.permission || userStore.can(item.permission.module, item.permission.action)) &&
        (!item.hideWhen || !userStore.can(item.hideWhen.module, item.hideWhen.action))
      )
  )

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

        // 檢查是否是子路徑
        if (mainPath === 'config') {
          const subPath = newPath.split('/')[2]
          if (subPath) {
            activeTab.value = `config-${subPath}`
          } else {
            activeTab.value = mainPath
          }
        } else if (mainPath === 'grants') {
          const subPath = newPath.split('/')[2]
          if (subPath === 'query') {
            activeTab.value = 'grants-query'
          } else {
            // 對於 /grants 主路徑，設定為 grants-application
            activeTab.value = 'grants-application'
          }
        } else {
          activeTab.value = mainPath
        }
      }
    },
    { immediate: true }
  )
</script>

<style scoped>
.gradient-background{
  /* background: linear-gradient(60deg, #0B6E99 0%, #72c4e0 100%); */
  background-color: #3ea0a3;
  color: white;
}

h1.app-title {
  font-size: 1.8rem !important;
}

h4.app-title {
  font-size: 1.2rem !important;
}

/* 下拉選單樣式 - 使用更強的選擇器 */
:deep(.v-list-item--active),
:deep(.v-list-item--selected) {
  background-color: transparent !important;
  background: transparent !important;
}

:deep(.v-list-group__header.v-list-item--active) {
  background-color: transparent !important;
  background: transparent !important;
}

/* 移除子選單項目的 hover 和 active 狀態背景色 */
:deep(.v-list .v-list-item:hover) {
  background-color: rgba(91, 194, 193, 0.05) !important;
}

:deep(.v-list .v-list-item--active:hover) {
  background-color: transparent !important;
}

/* 特別針對下拉選單中的項目，移除所有 active 和 selected 狀態 */
:deep(.v-menu .v-list .v-list-item--active),
:deep(.v-menu .v-list .v-list-item--selected) {
  background-color: transparent !important;
  background: transparent !important;
  color: inherit !important;
}

/* 移動端導航抽屜中的項目也移除 active 狀態 */
:deep(.v-navigation-drawer .v-list .v-list-item--active),
:deep(.v-navigation-drawer .v-list .v-list-item--selected) {
  background-color: transparent !important;
  background: transparent !important;
  color: inherit !important;
}

/* 針對 Vuetify 的 overlay 背景 */
:deep(.v-list-item .v-list-item__overlay) {
  opacity: 0 !important;
}

/* 強制移除所有可能的背景效果 */
:deep(.v-list-item::before),
:deep(.v-list-item::after) {
  opacity: 0 !important;
}
</style>
