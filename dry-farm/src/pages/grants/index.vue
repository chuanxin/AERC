<template>
  <v-container class="pt-0">
    <v-card class="pa-0 mb-6">
      <v-card-title class="d-flex align-center pe-2">
        <v-icon
          icon="mdi-file-table"
        />
        &nbsp; 申請案件列表
        <v-spacer />
        <v-text-field
          v-model="search"
          density="compact"
          label="Search"
          prepend-inner-icon="mdi-magnify"
          variant="solo-filled"
          flat
          hide-details
          single-line
          clearable
          width="100"
        >
          <template #append>
            <v-btn
              :icon="isSmallScreen"
              rounded="circl"
              to="/grants/new"
            >
              <v-icon
                icon="mdi-plus"
              />
              <span v-if="!isSmallScreen">建立新案件</span>
            </v-btn>

            <v-divider vertical class="ma-2" />

            <v-btn
              :icon="isSmallScreen"
              rounded="circl"
              to="/grants/edit"
            >
              <v-icon
                icon="mdi-content-copy"
              />
              <span v-if="!isSmallScreen">批次跨年度</span>
            </v-btn>
          </template>
        </v-text-field>
      </v-card-title>
      <v-divider />
      <v-data-table-virtual
        fixed-header
        :headers="headers"
        :items="filteredItems"
        :loading="loading"
        :search="search"
        :height="500"
        class="elevation-1"
        density="compact"
        item-value="name"
        v-model:selected="selected"
        show-select
        :item-selectable="item => item.iron !== '0'"
      >
        <!-- You can add custom slot templates if needed -->
        <template #['header.data-table-select']>
          <span class="ml-2">選取</span>
        </template>

        <template #[`item.protein`]="{ item }">
          <div class="ma-0 pa-0 d-flex gap-2 justify-end">
            <v-icon icon="mdi-pencil" size="small" @click="editItem(item.value)"></v-icon>
            <v-icon icon="mdi-delete" size="small" @click="deleteItem(item.value)"></v-icon>
          </div>
        </template>
      </v-data-table-virtual>
    </v-card>
  </v-container>
</template>

<script lang="ts" setup>
  import { useDisplay } from 'vuetify'

  const allItems = ref<any[]>([])
  const loading = ref(true)
  const search = ref('')
  const selected = ref<string[]>([])
  const router = useRouter()

  const headers = ref([
  { title: '申請年度', key: 'year', align: 'start' },
  { title: '案號', key: 'id', align: 'start' },
  { title: '申請人姓名', key: 'name', align: 'start' },
  { title: '末端形式', key: 'calories', align: 'end' },
  { title: '施作面積 (m²)', key: 'fat', align: 'end' },
  { title: '案件狀態', key: 'carbs', align: 'end' },
  { title: '公告狀態（農民卡）', key: 'card', align: 'end' },
  { title: '編輯', key: 'protein', align: 'end' },
])

  const { name } = useDisplay()
  const isSmallScreen = computed(() => name.value === 'xs' || name.value === 'sm')

  // Sample data
  const apply = [
    {
      name: '許大利',
      calories: '滴灌',  // 更新末端類型
      fat: 1900,        // 施作面積
      carbs: '完成申請人資料', // 案件狀態
      card: '已受理',    // 農民卡狀態
      protein: 4,
      iron: '1',
      year: 113,        // 申請年度
      id: '11301001',  // 案號
    },
    {
      name: '陳大明',
      calories: '穿孔管',
      fat: 4000,
      carbs: '完成灌溉調控設施',
      card: '審查中',
      protein: 4,
      iron: '1',
      year: 113,
      id: '11301002',
    },
    {
      name: '劉台北',
      calories: '其他',  // 更新末端類型
      fat: 2800,
      carbs: '完成田間管路',
      card: '審查中',
      protein: 4,
      iron: '1',
      year: 113,
      id: '11301003',
    },
    {
      name: '彭大吉',
      calories: '噴灌',  // 更新末端類型
      fat: 4000,
      carbs: '完成現場勘查',
      card: '審查通過',  // 隨機分配
      protein: 4,
      iron: '1',
      year: 113,
      id: '11301004',
    },
    {
      name: '林正雄',
      calories: '滴灌',
      fat: 3500,
      carbs: '完成申請人資料',
      card: '已受理',
      protein: 4,
      iron: '1',
      year: 112,
      id: '11201042',
    },
    {
      name: '王美蓮',
      calories: '噴灌',  // 更新末端類型
      fat: 2600,
      carbs: '完成土地資料',
      card: '審查中',
      protein: 4,
      iron: '1',
      year: 112,
      id: '11201085',
    },
    {
      name: '張水源',
      calories: '微噴',
      fat: 3200,
      carbs: '完成現場勘查',
      card: '結案流程',  // 隨機分配
      protein: 4,
      iron: '2',
      year: 111,
      id: '11101126',
    },
    {
      name: '李農田',
      calories: '其他',
      fat: 1800,
      carbs: '完成現場勘查',
      card: '撥款作業',  // 隨機分配
      protein: 4,
      iron: '0',
      year: 111,
      id: '11101152',
    },
    {
      name: '黃水利',
      calories: '滴灌',
      fat: 5200,
      carbs: '完成田間管路',
      card: '審查中',
      protein: 4,
      iron: '1',
      year: 111,
      id: '11101023',
    },
    {
      name: '吳田野',
      calories: '微噴',  // 更新末端類型，原先為霧化器
      fat: 4800,
      carbs: '完成田間管路',
      card: '審查中',
      protein: 4,
      iron: '1',
      year: 110,
      id: '11001078',
    }
  ]

  // Filter items based on search
  const filteredItems = computed(() => {
    if (!search.value) return allItems.value

    const searchTerm = search.value.toLowerCase()
    return allItems.value.filter(item => {
      return (
        item.name.toLowerCase().includes(searchTerm) ||
        item.id.toLowerCase().includes(searchTerm) ||
        String(item.year).includes(searchTerm)
      )
    })
  })

  // Load all data at once
  const loadAllItems = () => {
    loading.value = true
    // Simulate API call
    setTimeout(() => {
      allItems.value = apply
      loading.value = false
    }, 500)
  }

  // // Toggle selection of an item
  // const toggleSelect = (itemName: string) => {
  //   const index = selected.value.indexOf(itemName)
  //   if (index === -1) {
  //     selected.value.push(itemName)
  //   } else {
  //     selected.value.splice(index, 1)
  //   }
  // }

  const editItem = (itemName: string) => {
    router.push(`/grants/edit?id=${itemName}`)
    console.log('Edit item:', itemName)
    // Implement edit functionality
  }

  const deleteItem = (itemName: string) => {
    console.log('Delete item:', itemName)
    // Implement delete functionality
    allItems.value = allItems.value.filter(item => item.name !== itemName)
  }

  // Load data when component is mounted
  onMounted(() => {
    loadAllItems()
  })

  </script>

<style scoped>

</style>

