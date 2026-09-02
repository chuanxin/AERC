<template>
  <v-container
    fluid
    class="grants-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <v-row justify="center">
      <v-col cols="10" lg="10" align-self="center" class="pt-4">
        <div class="section-wrapper">
          <v-card
            class="mx-auto section-card pa-4 pb-0"
            variant="outlined"
            rounded="lg"
          >
            <v-card-item class="custom-title">
              <v-card-title class="text-h5 font-weight-black px-4">
                <v-img
                  src="@/assets/icons/news.svg"
                  alt="news icon"
                  width="24"
                  height="24"
                  class="me-2"
                />
                最新消息
              </v-card-title>
            </v-card-item>

            <v-card-text>
              <v-alert
                v-if="store.hasError"
                type="error"
                variant="outlined"
                class="mb-4"
                closable
                @click:close="store.clearError()"
              >
                {{ store.error }}
              </v-alert>

              <v-card class="table-card mb-4" elevation="0">
                <v-table class="news-table rounded-table pt-4 pb-0" hover>
                  <thead class="table-header-bold">
                    <tr>
                      <th class="text-left px-2 text-center font-weight-black">
                        發布日期
                      </th>
                      <th class="text-left text-center font-weight-black">
                        類型
                      </th>
                      <th class="text-left text-center font-weight-black">
                        標題
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-if="store.loading">
                      <td colspan="3" class="text-center py-8">
                        <v-progress-circular indeterminate color="#3ea0a3" size="32" />
                      </td>
                    </tr>
                    <tr v-else-if="store.publicItems.length === 0">
                      <td colspan="3" class="text-center py-10 text-grey text-subtitle-1">
                        目前沒有最新消息
                      </td>
                    </tr>
                    <tr
                      v-for="(item, index) in store.publicItems"
                      v-else
                      :key="item.id"
                      class="news-row text-subtitle-1"
                      :style="index % 2 === 1 ? { backgroundColor: '#62b7bb30' } : {}"
                      @click="openDetail(item.id)"
                    >
                      <td class="date-cell text-left py-3 px-3 text-grey text-subtitle-1 text-center">
                        <v-chip
                          color="#FFF8DE"
                          variant="elevated"
                          elevation="0"
                          rounded="lg"
                          class="date-chip"
                          density="comfortable"
                        >
                          {{ toRocDate(item.publish_date) }}
                        </v-chip>
                      </td>
                      <td class="type-cell text-center">
                        <v-chip
                          :color="item.type.color"
                          variant="outlined"
                          size="small"
                          label
                          class="font-weight-medium text-subtitle-1"
                        >
                          {{ item.type.name }}
                        </v-chip>
                      </td>
                      <td class="content-cell px-2">
                        <v-icon
                          v-if="item.is_pinned"
                          size="small"
                          color="amber-darken-2"
                          class="me-1"
                        >
                          mdi-pin
                        </v-icon>
                        {{ item.title }}
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card>

              <div
                v-if="store.publicTotalPages > 1"
                class="d-flex justify-center pb-4"
              >
                <v-pagination
                  v-model="page"
                  :length="store.publicTotalPages"
                  :total-visible="7"
                  rounded="lg"
                  color="#3ea0a3"
                  @update:model-value="load"
                />
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAnnouncementsStore } from '@/stores/announcements'
import { toRocDate } from '@/utils/rocDate'

const router = useRouter()
const store = useAnnouncementsStore()

const page = ref(1)
const PAGE_SIZE = 15

async function load () {
  await store.fetchPublished(page.value, PAGE_SIZE)
}

function openDetail (id: number) {
  router.push(`/announcements/${id}`)
}

onMounted(load)
</script>

<style scoped>
.section-wrapper {
  margin-top: 8px;
}

.news-row {
  cursor: pointer;
}
</style>
