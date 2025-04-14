<template>
  <NavBar />
  <v-main>
    <v-breadcrumbs
      v-if="route.path !== '/'"
      :items="breadcrumbItems"
      class="pl-10 px-2 py-1"
      density="compact"
      active-class="primary--text"
    >
      <template #divider>
        <v-icon
          icon="mdi-chevron-right"
          size="small"
          class="mx-n1 pb-1"
        />
      </template>
      <template #title="{ item }">
        <a
          :href="item.href"
          class="text-decoration-none d-inline-flex align-center px-1"
          :class="[
            item.disabled ? 'text-disabled' : 'text-primary-darken',
            'breadcrumb-link'
          ]"
          @click.prevent="!item.disabled && item.href && navigateTo(item.href)"
        >
          <v-icon
            v-if="item.href === '/'"
            icon="mdi-home"
            size="small"
            class="ma-0"
          />
          <span v-if="item.href !== '/'">{{ item.title }}</span>
        </a>
      </template>
    </v-breadcrumbs>
    <router-view />
  </v-main>
  <ReportBugButton />
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
.v-breadcrumbs {
  min-height: 36px;
}

.breadcrumb-link {
  font-size: 0.875rem;
  padding: 0 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.breadcrumb-link:not(.text-disabled):hover {
  background-color: rgba(var(--v-theme-primary), 0.04);
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
