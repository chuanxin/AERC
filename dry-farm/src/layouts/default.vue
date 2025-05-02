<template>
  <NavBar />
  <v-main>
    <!-- <v-card
      v-if="route.path !== '/'"
      flat
      class="breadcrumbs-wrapper mx-auto px-0"
      style="max-width: 96%"
    > -->
    <v-breadcrumbs
      v-if="route.path !== '/'"
      :items="breadcrumbItems"
      class="pl-10 px-2 py-1"
      density="compact"
      active-class="primary--text"
      bg-color="rgba(255, 255, 255, 1)"
      tile
    >
      <template #divider>
        <v-icon
          icon="mdi-chevron-right"
          size="small"
          class="mx-n1 pb-1"
          color="#3ea0a3"
        />
      </template>
      <template #title="{ item }">
        <a
          :href="item.href"
          class="text-decoration-none d-inline-flex align-center px-1"
          :class="[
            item.disabled ? 'breadcrumb-disabled' : 'breadcrumb-active',
            'breadcrumb-link'
          ]"
          @click.prevent="!item.disabled && item.href && navigateTo(item.href)"
        >
          <v-icon
            v-if="item.href === '/'"
            icon="mdi-home"
            size="small"
            class="ma-0"
            :color="item.disabled ? 'grey-darken-1' : '#3ea0a3'"
          />
          <span v-if="item.href !== '/'">{{ item.title }}</span>
        </a>
      </template>
    </v-breadcrumbs>
    <!-- </v-card> -->

    <router-view />
  </v-main>
  <!-- <ReportBugButton /> -->
  <AppFooter />
</template>

<script lang="ts" setup>
  const router = useRouter()
  const route = useRoute()

  const navigateTo = (path: string) => {
    router.push(path)
  }

  const breadcrumbItems = computed(() => {
    const items = [
      {
        title: '首頁',
        disabled: false,
        href: '/'
      }
    ]

    // Map route path to breadcrumb title
    const pathTitles: Record<string, string> = {
      '/grants': '補助申請',
      '/grants/new': '建立新案件',
      '/grants/edit': '案件編輯',
      '/qualification': '申請資格預查',
      '/statistics': '統計報表',
      '/supplies': '材料管理',
      '/maps': 'GIS圖台',
      '/config': '系統管理',
      '/bug-report': '回報問題',
      '/budget': '預算執行即時資訊',
    }

    // Split the current path into segments and build breadcrumbs
    const pathSegments = route.path.split('/').filter(Boolean) // Remove empty segments
    let currentPath = ''

    pathSegments.forEach(segment => {
      currentPath += `/${segment}`

      if (pathTitles[currentPath]) {
        items.push({
          title: pathTitles[currentPath],
          disabled: currentPath === route.path,
          href: currentPath === route.path ? '' : currentPath
        })
      }
    })

    return items
  })
</script>

<style scoped>
.breadcrumbs-wrapper {
  margin-top: 16px;
  margin-bottom: 12px;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(62, 160, 163, 0.1);
  transition: all 0.3s ease;
}

.breadcrumbs-wrapper:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(62, 160, 163, 0.2);
}

.breadcrumb-link {
  font-size: 0.875rem;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.breadcrumb-active {
  color: #3ea0a3;
  font-weight: 500;
}

.breadcrumb-disabled {
  color: rgba(0, 0, 0, 0.6);
  font-weight: 600;
}

.breadcrumb-link:not(.breadcrumb-disabled):hover {
  background-color: rgba(62, 160, 163, 0.1);
  transform: translateY(-1px);
}

:deep(.v-breadcrumbs-divider) {
  padding-inline: 4px;
}

/* 全局樣式確保 OpenLayers 正確顯示 */
.ol-viewport {
  position: relative;
  overflow: hidden;
  width: 100%;
  height: 100%;
}

.ol-layer {
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
}
</style>
