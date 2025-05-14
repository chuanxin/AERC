<template>
  <v-container class="pt-0">
    <v-card class="pa-0 mb-6">
      <v-card-title class="d-flex align-center pe-2">
        <v-icon icon="mdi-pipe-valve"/>
        &nbsp; 管路灌溉材料列表
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
              <span v-if="!isSmallScreen">新增材料</span>
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
      >
        <!-- You can add custom slot templates if needed -->
        <!-- <template #['header.data-table-select']>
          <span class="ml-2">選取</span>
        </template> -->

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
  import { ref, computed, watch, onMounted } from 'vue'
  import { useDisplay } from 'vuetify'

  const allItems = ref<any[]>([])
  const loading = ref(true)
  const search = ref('')
  const selected = ref<string[]>([])

  const headers = ref([
    {
      title: '申請案件',
      align: 'center' as const,
      children: [
        { title: '申請年度', key: 'year', align: 'start' as const },
        { title: '案號', key: 'id', align: 'start' as const },
        { title: '申請人姓名', key: 'name', align: 'start' as const },
      ],
    },
    { title: '末端形式', key: 'calories', align: 'end' as const },
    { title: '施作面積 (m²)', key: 'fat', align: 'end' as const },
    { title: '案件狀態', key: 'carbs', align: 'end' as const },
    { title: '公告狀態（農民卡）', key: 'carbs', align: 'end' as const },
    { title: '編輯', key: 'protein', align: 'end' as const },
  ])

  const { name } = useDisplay()
  const isSmallScreen = computed(() => name.value === 'xs' || name.value === 'sm')

  // Sample data
  const desserts = [
    {
      name: 'Frozen Yogurt',
      calories: 159,
      fat: 6,
      carbs: 24,
      protein: 4,
      iron: '1',
      year: 2023,
      id: 'A001',
    },
    {
      name: 'Jelly bean',
      calories: 375,
      fat: 0,
      carbs: 94,
      protein: 0,
      iron: '0',
      year: 2023,
      id: 'A002',
    },
    {
      name: 'KitKat',
      calories: 518,
      fat: 26,
      carbs: 65,
      protein: 7,
      iron: '6',
      year: 2022,
      id: 'B001',
    },
    {
      name: 'Eclair',
      calories: 262,
      fat: 16,
      carbs: 23,
      protein: 6,
      iron: '7',
      year: 2022,
      id: 'B002',
    },
    {
      name: 'Gingerbread',
      calories: 356,
      fat: 16,
      carbs: 49,
      protein: 3.9,
      iron: '16',
      year: 2021,
      id: 'C001',
    },
    {
      name: 'Ice cream sandwich',
      calories: 237,
      fat: 9,
      carbs: 37,
      protein: 4.3,
      iron: '1',
      year: 2021,
      id: 'C002',
    },
    {
      name: 'Lollipop',
      calories: 392,
      fat: 0.2,
      carbs: 98,
      protein: 0,
      iron: '2',
      year: 2020,
      id: 'D001',
    },
    {
      name: 'Cupcake',
      calories: 305,
      fat: 3.7,
      carbs: 67,
      protein: 4.3,
      iron: '8',
      year: 2020,
      id: 'D002',
    },
    {
      name: 'Honeycomb',
      calories: 408,
      fat: 3.2,
      carbs: 87,
      protein: 6.5,
      iron: '45',
      year: 2019,
      id: 'E001',
    },
    {
      name: 'Donut',
      calories: 452,
      fat: 25,
      carbs: 51,
      protein: 4.9,
      iron: '22',
      year: 2019,
      id: 'E002',
    },
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
      allItems.value = desserts
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

  // Edit and delete functions
  const editItem = (itemName: string) => {
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

