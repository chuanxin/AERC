<template>
  <v-container
    fluid
    class="qualification-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <v-row justify="center">
      <v-col
        cols="12"
        lg="12"
        align-self="start"
        class="pt-0"
      >
        <!-- 功能按鈕區 -->
        <div class="d-flex flex-wrap align-center pr-2">
          <v-spacer />
          <div class="d-flex gap-2">
            <v-btn
              class="action-btn"
              color="#3ea0a3"
              prepend-icon="mdi-refresh"
              variant="outlined"
              rounded="lg"
              size="large"
              :loading="isLoading"
              @click="clearAllResults"
            >
              清除結果
            </v-btn>

            <!-- <v-btn
              class="action-btn"
              color="#3ea0a3"
              prepend-icon="mdi-plus"
              to="/grants/new"
              variant="outlined"
              rounded="lg"
              size="large"
            >
              建立新案件
            </v-btn> -->
          </div>
        </div>

        <!-- 主要內容區域：查詢面板和結果面板並列 -->
        <v-row justify="center">
          <!-- 左側：重複案件查詢面板 -->
          <v-col
            cols="12"
            md="3"
            lg="3"
            class="pt-0 mt-0"
          >
            <v-card
              class="table-card mb-3"
              rounded="lg"
              elevation="0"
              variant="outlined"
            >
              <!-- 查詢表單內容 -->
              <v-card-text class="pa-3">
                <v-form @submit.prevent="searchLand">
                  <!-- 查詢類型選擇 -->
                  <div class="mb-4">
                    <div class="text-body-2 font-weight-medium mb-2">
                      查詢類型
                    </div>
                    <v-btn-toggle
                      v-model="queryType"
                      color="#3ea0a3"
                      mandatory
                      density="compact"
                      rounded="lg"
                      class="mb-2 w-100"
                      variant="outlined"
                    >
                      <v-btn
                        value="general"
                        size="small"
                        class="text-body-2 flex-grow-1"
                      >
                        歷史申請案件
                      </v-btn>
                      <v-btn
                        value="indigenous"
                        size="small"
                        class="text-body-2 flex-grow-1"
                      >
                        原民區域
                      </v-btn>
                      <v-btn
                        value="slope"
                        size="small"
                        class="text-body-2 flex-grow-1"
                      >
                        山坡地
                      </v-btn>
                    </v-btn-toggle>
                  </div>

                  <!-- 年度選擇 - 僅在一般區域查詢時顯示 -->
                  <div
                    v-if="queryType === 'general'"
                    class="mb-4"
                  >
                    <div class="text-body-2 font-weight-medium mb-2">
                      查詢年度
                    </div>
                    <div class="d-flex flex-wrap align-center gap-2 mb-2">
                      <v-chip-group
                        v-model="selectedYears"
                        multiple
                        color="#3ea0a3"
                      >
                        <v-chip
                          v-for="year in availableYears"
                          :key="year"
                          :value="year"
                          size="x-small"
                          filter
                          variant="outlined"
                          class="text-caption"
                        >
                          {{ year }}年
                        </v-chip>
                      </v-chip-group>

                      <v-btn
                        size="x-small"
                        variant="text"
                        color="#3ea0a3"
                        class="text-caption"
                        @click="clearYearSelection"
                      >
                        清除
                      </v-btn>

                      <v-btn
                        size="x-small"
                        variant="text"
                        color="#3ea0a3"
                        class="text-caption"
                        @click="selectRecentYears"
                      >
                        近3年
                      </v-btn>
                    </div>

                    <div class="text-caption text-grey-darken-1">
                      未選擇年度時將查詢所有年度 (97-114年) 的案件
                    </div>
                  </div>

                  <!-- 錯誤提示 -->
                  <div
                    v-if="error"
                    class="mb-4"
                  >
                    <v-alert
                      type="error"
                      variant="tonal"
                      color="error"
                      border="start"
                      density="compact"
                      icon="mdi-alert-circle"
                      closable
                      @click:close="qualificationStore.clearErrors"
                    >
                      {{ error }}
                    </v-alert>
                  </div>

                  <v-expand-transition>
                    <div v-if="queryType === 'general'">
                      <div class="mb-4">
                        <div class="text-body-2 font-weight-medium mb-2">
                          地段
                        </div>
                        <!-- 縣市、鄉鎮市區 - 第一排 -->
                        <div class="d-flex mb-3">
                          <v-select
                            v-model="searchParams.county"
                            :items="counties"
                            label="縣市"
                            variant="outlined"
                            density="compact"
                            hide-details
                            class="flex-grow-1"
                            bg-color="white"
                            @update:model-value="onCountyChange"
                          />

                          <v-select
                            v-model="searchParams.town"
                            :items="towns"
                            label="鄉鎮市區"
                            variant="outlined"
                            density="compact"
                            hide-details
                            class="flex-grow-1 ml-3"
                            :disabled="!searchParams.county"
                            bg-color="white"
                            @update:model-value="onTownChange"
                          />
                        </div>

                        <!-- 地段與API狀態 - 第二排 -->
                        <div class="d-flex align-center">
                          <v-select
                            v-model="searchParams.section"
                            :items="sections"
                            label="地段"
                            variant="outlined"
                            density="compact"
                            hide-details
                            class="flex-grow-1"
                            :disabled="!searchParams.town"
                            bg-color="white"
                          />

                          <!-- API連線狀態 -->
                          <div class="d-flex align-center ml-2">
                            <v-chip
                              :color="apiStatus.isOnline ? 'success' : 'error'"
                              size="small"
                              variant="outlined"
                            >
                              <v-icon
                                :icon="apiStatus.isOnline ? 'mdi-check-circle' : 'mdi-close-circle'"
                                size="small"
                                class="me-1"
                              />
                              {{ apiStatus.isOnline ? '線上' : '離線' }}
                            </v-chip>
                          </div>
                        </div>
                      </div>

                      <div class="mb-4">
                        <div class="text-body-2 font-weight-medium mb-2">
                          地號
                        </div>
                        <div class="d-flex align-center gap-2 mb-3">
                          <v-text-field
                            v-model="searchParams.parentLandNumber"
                            label="母地號 (必填)"
                            variant="outlined"
                            density="compact"
                            hide-details
                            bg-color="white"
                            maxlength="4"
                            style="flex: 1"
                            @blur="formatParentLandNumber('searchParams')"
                          />
                          <span class="text-h6 mx-2">-</span>
                          <v-text-field
                            v-model="searchParams.childLandNumber"
                            label="子地號 (選填)"
                            variant="outlined"
                            density="compact"
                            hide-details
                            bg-color="white"
                            maxlength="4"
                            style="flex: 1"
                            @blur="formatChildLandNumber('searchParams')"
                          />
                        </div>

                        <v-btn
                          color="#3ea0a3"
                          variant="flat"
                          size="large"
                          type="submit"
                          :loading="isLoading"
                          :disabled="!canSearch"
                          rounded="lg"
                          block
                        >
                          <v-icon
                            size="small"
                            class="me-1"
                          >
                            mdi-magnify
                          </v-icon>
                          查詢
                        </v-btn>
                      </div>

                      <div
                        v-if="showAlert"
                        class="mb-4"
                      >
                        <v-alert
                          variant="tonal"
                          color="#3ea0a3"
                          border="start"
                          density="compact"
                        >
                          輸入母地號（必填）和子地號（選填）即可查詢歷史歸檔記錄，包含農田水利署及水土保持署之申請紀錄。
                        </v-alert>
                      </div>
                    </div>
                  </v-expand-transition>

                  <v-expand-transition>
                    <div v-if="queryType === 'indigenous'">
                      <div class="mb-4">
                        <div class="text-body-2 font-weight-medium mb-2">
                          地段
                        </div>
                        <!-- 縣市、鄉鎮市區 -->
                        <div class="d-flex mb-3">
                          <v-select
                            v-model="indigenousParams.county"
                            :items="counties"
                            label="縣市"
                            variant="outlined"
                            density="compact"
                            hide-details
                            class="flex-grow-1"
                            bg-color="white"
                            @update:model-value="onIndigenousCountyChange"
                          />

                          <v-select
                            v-model="indigenousParams.town"
                            :items="indigenousTowns"
                            label="鄉鎮市區"
                            variant="outlined"
                            density="compact"
                            hide-details
                            class="flex-grow-1 ml-3"
                            :disabled="!indigenousParams.county"
                            bg-color="white"
                          />
                        </div>

                        <v-btn
                          color="#3ea0a3"
                          variant="flat"
                          size="large"
                          :loading="isIndigenousLoading"
                          :disabled="!canSearchIndigenous"
                          rounded="lg"
                          block
                          @click="searchIndigenous"
                        >
                          <v-icon
                            size="small"
                            class="me-1"
                          >
                            mdi-magnify
                          </v-icon>
                          查詢
                        </v-btn>
                      </div>
                    </div>
                  </v-expand-transition>

                  <v-expand-transition>
                    <div v-if="queryType === 'slope'">
                      <div class="mb-4">
                        <div class="text-body-2 font-weight-medium mb-2">
                          地段
                        </div>
                        <!-- 縣市、鄉鎮市區 - 第一排 -->
                        <div class="d-flex mb-3">
                          <v-select
                            v-model="hillsideParams.county"
                            :items="counties"
                            label="縣市"
                            variant="outlined"
                            density="compact"
                            hide-details
                            class="flex-grow-1"
                            bg-color="white"
                            @update:model-value="onHillsideCountyChange"
                          />

                          <v-select
                            v-model="hillsideParams.town"
                            :items="hillsideTowns"
                            label="鄉鎮市區"
                            variant="outlined"
                            density="compact"
                            hide-details
                            class="flex-grow-1 ml-3"
                            :disabled="!hillsideParams.county"
                            bg-color="white"
                            @update:model-value="onHillsideTownChange"
                          />
                        </div>

                        <!-- 地段與API狀態 - 第二排 -->
                        <div class="d-flex align-center gap-3">
                          <v-select
                            v-model="hillsideParams.section"
                            :items="hillsideSections"
                            label="地段"
                            variant="outlined"
                            density="compact"
                            hide-details
                            class="flex-grow-1"
                            :disabled="!hillsideParams.town"
                            bg-color="white"
                          />

                          <!-- API連線狀態 -->
                          <div class="d-flex align-center ml-2">
                            <v-chip
                              :color="apiStatus.isOnline ? 'success' : 'error'"
                              size="small"
                              variant="outlined"
                            >
                              <v-icon
                                :icon="apiStatus.isOnline ? 'mdi-check-circle' : 'mdi-close-circle'"
                                size="small"
                                class="me-1"
                              />
                              {{ apiStatus.isOnline ? '線上' : '離線' }}
                            </v-chip>
                          </div>
                        </div>
                      </div>

                      <div class="mb-4">
                        <v-btn
                          color="#3ea0a3"
                          variant="flat"
                          size="large"
                          :loading="isHillsideLoading"
                          :disabled="!canSearchHillside"
                          rounded="lg"
                          block
                          @click="searchHillside"
                        >
                          <v-icon
                            size="small"
                            class="me-1"
                          >
                            mdi-magnify
                          </v-icon>
                          查詢
                        </v-btn>
                      </div>

                      <div
                        v-if="showHillsideAlert"
                        class="mb-4"
                      >
                        <v-alert
                          type="info"
                          variant="tonal"
                          color="#3ea0a3"
                          border="start"
                          density="compact"
                          icon="mdi-information"
                        >
                          山坡地歷史歸檔記錄查詢，適用於水土保持相關補助申請案件。請輸入母地號（必填）和子地號（選填）。
                        </v-alert>
                      </div>
                    </div>
                  </v-expand-transition>
                </v-form>
              </v-card-text>
            </v-card>

            <!-- 最近查詢區域 -->
            <v-card
              class="table-card mb-3"
              rounded="lg"
              elevation="0"
              variant="outlined"
            >
              <div
                class="d-flex align-center gap-3 pa-3"
                style="background-color: #f5f5f5;"
              >
                <v-icon
                  icon="mdi-history"
                  color="#3ea0a3"
                  size="small"
                />
                <span class="text-subtitle-2 font-weight-medium">最近查詢</span>
              </div>

              <v-card-text class="pa-0">
                <v-list
                  lines="two"
                  density="compact"
                >
                  <v-list-item
                    v-for="(item, index) in recentSearches"
                    :key="index"
                    @click="loadRecentSearch(item)"
                  >
                    <v-list-item-title>
                      {{ item.county }}{{ item.town }} {{ item.landNumber || item.section }}
                    </v-list-item-title>
                    <v-list-item-subtitle class="text-caption">
                      {{ formatDate(item.searchTime) }}
                    </v-list-item-subtitle>
                  </v-list-item>

                  <v-list-item v-if="recentSearches.length === 0">
                    <v-list-item-title class="text-body-2 text-grey">
                      尚無查詢紀錄
                    </v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- 右側：查詢結果面板 -->
          <v-col
            cols="12"
            md="9"
            lg="9"
          >
            <!-- 原民區域查詢結果顯示 -->
            <v-expand-transition>
              <div
                v-if="isIndigenousAreaChecked && queryType === 'indigenous'"
                class="section-wrapper mb-4"
              >
                <v-card
                  class="mx-auto section-card pa-4"
                  variant="outlined"
                  rounded="lg"
                >
                  <v-card-item class="custom-title">
                    <v-card-title class="text-h5 font-weight-black">
                      原民區域查詢結果
                    </v-card-title>
                  </v-card-item>

                  <v-card-text>
                    <v-card
                      class="table-card"
                      rounded="lg"
                      elevation="0"
                    >
                      <v-card-text class="pa-0">
                        <div class="d-flex align-center justify-left">
                          <v-chip
                            :color="isIndigenousArea ? '#3ea0a3' : 'grey'"
                            :text-color="isIndigenousArea ? 'white' : ''"
                            size="large"
                            class="me-4"
                          >
                            <v-icon
                              :icon="isIndigenousArea ? 'mdi-check-circle' : 'mdi-close-circle'"
                              class="me-2"
                            />
                            {{ isIndigenousArea ? '是' : '非' }} 原民區域
                          </v-chip>

                          <div class="text-body-1">
                            <strong>{{ indigenousParams.county || '___' }}</strong>
                            <span class="mx-2">•</span>
                            <strong>{{ indigenousParams.town || '___' }}</strong>
                          </div>
                        </div>

                        <div
                          v-if="isIndigenousArea"
                          class="mt-4 pa-3 bg-light-green-lighten-5 rounded"
                        >
                          <div class="d-flex align-center mb-2">
                            <v-icon
                              color="success"
                              size="small"
                              class="me-2"
                            >
                              mdi-information
                            </v-icon>
                            <span class="text-body-2 font-weight-medium">此地區為原民區域</span>
                          </div>
                          <div class="text-caption text-grey-darken-1">
                            申請案件將適用原民區域相關法規與補助規範
                          </div>
                        </div>

                        <div
                          v-else
                          class="mt-4 pa-3 bg-grey-lighten-4 rounded"
                        >
                          <div class="d-flex align-center mb-2">
                            <v-icon
                              color="grey-darken-1"
                              size="small"
                              class="me-2"
                            >
                              mdi-information
                            </v-icon>
                            <span class="text-body-2 font-weight-medium">此地區非原民區域</span>
                          </div>
                          <div class="text-caption text-grey-darken-1">
                            申請案件將適用一般法規與補助規範
                          </div>
                        </div>
                      </v-card-text>
                    </v-card>
                  </v-card-text>
                </v-card>
              </div>
            </v-expand-transition>

            <!-- 預設顯示查詢說明 -->
            <div
              v-if="searchResults.length === 0 && !showNoResultMessage && (!isIndigenousAreaChecked || queryType !== 'indigenous')"
              class="section-wrapper"
            >
              <v-card
                class="mx-auto section-card pa-0"
                variant="outlined"
                rounded="lg"
              >
                <v-card-item class="custom-title">
                  <v-card-title class="text-h5 font-weight-black">
                    {{ queryInstructions.title }}
                  </v-card-title>
                </v-card-item>

                <v-card-text>
                  <v-card
                    class="table-card"
                    rounded="lg"
                    elevation="0"
                  >
                    <v-card-text class="pa-4">
                      <v-list
                        density="compact"
                        class="bg-transparent pa-0"
                      >
                        <v-list-item
                          v-for="(instruction, index) in queryInstructions.items"
                          :key="index"
                          class="px-1"
                        >
                          <template #prepend>
                            <v-icon
                              :color="instruction.color || '#3ea0a3'"
                              size="small"
                            >
                              {{ instruction.icon || 'mdi-check-circle' }}
                            </v-icon>
                          </template>
                          <v-list-item-title
                            :class="[
                              instruction.isHeader ? 'text-body-1 font-weight-bold' : 'text-body-2',
                              instruction.isContent ? 'text-caption text-wrap' : ''
                            ]"
                          >
                            <span v-if="!instruction.url">{{ instruction.text }}</span>
                            <a
                              v-else
                              :href="instruction.url"
                              target="_blank"
                              rel="noopener noreferrer"
                              class="text-decoration-none"
                              :style="{ color: instruction.color || '#3ea0a3' }"
                            >
                              {{ instruction.text }}
                              <v-icon
                                size="small"
                                class="ml-1"
                                :color="instruction.color || '#3ea0a3'"
                              >
                                mdi-open-in-new
                              </v-icon>
                            </a>
                          </v-list-item-title>
                        </v-list-item>
                      </v-list>
                    </v-card-text>
                  </v-card>
                </v-card-text>
              </v-card>
            </div>

            <!-- 查詢結果顯示區 -->
            <v-expand-transition>
              <div v-if="searchResults.length > 0 || showNoResultMessage">
                <div class="section-wrapper">
                  <v-card
                    class="mx-auto section-card pa-4"
                    variant="outlined"
                    rounded="lg"
                  >
                    <v-card-item class="custom-title">
                      <v-card-title class="text-h5 font-weight-black">
                        查詢結果
                      </v-card-title>
                    </v-card-item>

                    <v-card-text>
                      <!-- 查詢結果內容卡片 -->
                      <v-card
                        class="table-card"
                        rounded="lg"
                        elevation="0"
                      >
                        <v-card-text class="pa-0">
                          <!-- 查詢結果標題 -->
                          <div
                            v-if="filteredLegacyResults.length > 0"
                            class="mb-4"
                          >
                            <div class="text-h6 font-weight-bold mb-2">
                              歸檔記錄查詢結果：{{ landLocationDescription }} {{ filteredLegacyResults[0].land_number }}
                            </div>

                            <div
                              v-if="searchResults.length > filteredLegacyResults.length"
                              class="text-caption text-warning mb-2"
                            >
                              ⚠️ 已過濾僅顯示與最新案件地段 ({{ filteredLegacyResults[0].land_section }}) 相關的 {{ filteredLegacyResults.length }} 筆記錄 (包含其它地段的記錄總共 {{ searchResults.length }} 筆)
                            </div>

                            <!-- 頂部統計資訊 - 橫向排列 -->
                            <div class="d-flex flex-wrap gap-4 pa-4 bg-grey-lighten-5 rounded mb-4">
                              <!-- 地籍登記面積 -->
                              <div class="text-center">
                                <div class="d-flex align-center mb-1">
                                  <v-icon
                                    color="blue"
                                    size="small"
                                    class="me-1"
                                  >
                                    mdi-chart-pie
                                  </v-icon>
                                  <span class="text-caption">地籍登記面積</span>
                                </div>
                                <div class="text-h5 font-weight-bold text-blue">
                                  {{ totalApprovedArea.toLocaleString() }}
                                </div>
                                <div class="text-caption">
                                  ㎡
                                </div>
                              </div>

                              <v-divider
                                class="mx-4"
                                vertical
                              />

                              <!-- 農田水利管轄區域資訊 -->
                              <div
                                v-if="allOfficeBoundaries && allOfficeBoundaries.length > 0"
                                class="flex-grow-1"
                              >
                                <div class="d-flex align-center mb-2">
                                  <v-icon
                                    color="teal"
                                    size="small"
                                    class="me-1"
                                  >
                                    mdi-domain
                                  </v-icon>
                                  <span class="text-caption font-weight-medium">農田水利管轄區域</span>
                                </div>
                                
                                <!-- 詳細管轄層級資訊 -->
                                <div class="d-flex flex-column gap-2">
                                  <div 
                                    v-for="boundary in allOfficeBoundaries.slice(0, 2)"
                                    :key="boundary.gid"
                                    class="text-body-2"
                                  >
                                    <span class="font-weight-bold text-teal">{{ boundary.ia_name || '未知' }}管理處</span>
                                    <template v-if="boundary.mng_name">
                                      <span class="mx-2 text-grey-darken-1">></span>
                                      <span>{{ boundary.mng_name }}分處</span>
                                    </template>
                                    <span class="mx-2 text-grey-darken-1">></span>
                                    <span>{{ boundary.stn_name || '未知工作站' }}</span>
                                    <span 
                                      v-if="boundary.grp_name"
                                      class="mx-2 text-grey-darken-1"
                                    >></span>
                                    <span 
                                      v-if="boundary.grp_name"
                                      class="text-blue-grey-darken-1"
                                    >{{ boundary.grp_name }}</span>
                                  </div>
                                  
                                  <div
                                    v-if="allOfficeBoundaries.length > 2"
                                    class="text-body-2 text-grey-darken-1 mt-1"
                                  >
                                    另有 {{ allOfficeBoundaries.length - 2 }} 個管轄區域
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>

                          <!-- 按年度分組的 Tab 展示 -->
                          <div v-if="groupedByYear.length > 0">
                            <v-tabs
                              v-model="selectedYearTab"
                              color="#3ea0a3"
                              bg-color="transparent"
                              slider-color="#3ea0a3"
                              show-arrows
                              class="mb-4"
                            >
                              <v-tab
                                v-for="yearGroup in groupedByYear"
                                :key="yearGroup.year"
                                :value="yearGroup.year"
                                class="text-none"
                              >
                                <v-chip
                                  :color="getYearChipColor(yearGroup.year)"
                                  size="small"
                                  variant="flat"
                                  class="me-2"
                                >
                                  {{ yearGroup.year }}年度
                                </v-chip>
                                <span class="text-caption">
                                  {{ yearGroup.cases.length }} 筆
                                </span>
                              </v-tab>
                            </v-tabs>

                            <v-tabs-window
                              v-model="selectedYearTab"
                              class="mt-4"
                            >
                              <v-tabs-window-item
                                v-for="yearGroup in groupedByYear"
                                :key="yearGroup.year"
                                :value="yearGroup.year"
                              >
                                <!-- 設施列表 - 緊湊布局 -->
                                <div class="facility-list">
                                  <div
                                    v-for="facilityGroup in yearGroup.facilities"
                                    :key="facilityGroup.type"
                                    class="facility-item d-flex align-center py-3 px-3 mb-2 rounded"
                                    :class="`border-s-4 border-${getFacilityIcon(facilityGroup.type).color}`"
                                    style="background-color: #fafafa;"
                                  >
                                    <!-- 左側：設施圖示和名稱 -->
                                    <div class="d-flex align-center flex-grow-1">
                                      <div
                                        class="facility-icon d-flex align-center justify-center me-3"
                                        :style="`background-color: ${getFacilityColorHex(facilityGroup.type)}; width: 36px; height: 36px; border-radius: 8px;`"
                                      >
                                        <v-icon
                                          :icon="getFacilityIcon(facilityGroup.type).icon"
                                          color="white"
                                          size="20"
                                        />
                                      </div>
                                      <div>
                                        <div class="text-body-1 font-weight-medium mb-1">
                                          {{ facilityGroup.type }}
                                        </div>
                                        <div class="text-caption text-grey-darken-1">
                                          案件 {{ facilityGroup.cases.length }} | {{ formatApplicantsInGroup(facilityGroup.cases) }}
                                        </div>
                                      </div>
                                    </div>

                                    <!-- 右側：面積和狀態 -->
                                    <div class="text-end">
                                      <div class="text-h6 font-weight-bold text-primary mb-1">
                                        {{ (facilityGroup.appliedArea || 0).toLocaleString() }}
                                        <span class="text-caption">㎡</span>
                                      </div>
                                      <v-chip
                                        :color="getStatusColor(facilityGroup.appliedArea || 0, facilityGroup.landRegisteredArea || 0)"
                                        size="small"
                                        variant="flat"
                                      >
                                        {{ facilityGroup.statusText }}
                                      </v-chip>
                                    </div>
                                  </div>
                                </div>
                              </v-tabs-window-item>
                            </v-tabs-window>
                          </div>
                        </v-card-text>
                      </v-card>
                    </v-card-text>
                  </v-card>
                </div>

                <!-- 無查詢結果提示 -->
                <v-alert
                  v-if="showNoResultMessage"
                  type="info"
                  variant="tonal"
                  icon="mdi-information"
                >
                  <div class="d-flex align-center justify-space-between">
                    <span>查詢無結果，此地號尚未有歷史補助申請紀錄。</span>
                    <v-btn
                      variant="text"
                      color="primary"
                      size="small"
                      to="/grants/new"
                    >
                      立即申請
                      <v-icon
                        end
                        size="small"
                      >
                        mdi-arrow-right
                      </v-icon>
                    </v-btn>
                  </div>
                </v-alert>
              </div>
            </v-expand-transition>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive, onMounted } from 'vue';
import { useQualificationStore } from '@/stores/qualification';
import { useDomicileStore } from '@/stores/domicile';
import type { QualificationSearchParams, IndigenousSearchParams, RecentSearch } from '@/types/qualification';

const qualificationStore = useQualificationStore();
const domicileStore = useDomicileStore();

const queryType = ref('general');

// API連線狀態
const apiStatus = ref({
  isOnline: false,
  lastChecked: null as Date | null
});

// 地段查詢參數
const searchParams = reactive<QualificationSearchParams>({
  county: '',
  town: '',
  section: '',
  landNumber: '',
  parentLandNumber: '',
  childLandNumber: ''
});

// 原民區域查詢參數
const indigenousParams = reactive<IndigenousSearchParams>({
  county: '',
  town: ''
});

// 山坡地查詢參數
const hillsideParams = reactive<QualificationSearchParams>({
  county: '',
  town: '',
  section: '',
  landNumber: '',
  parentLandNumber: '',
  childLandNumber: ''
});

// 年度選擇 - 不設置預設值代表查詢所有年度
const selectedYears = ref<string[]>([]);

// Tab 選擇的年度
const selectedYearTab = ref<number>();

// 可選年度範圍 (97年至114年)
const availableYears = Array.from({ length: 18 }, (_, i) => (114 - i).toString());

// 年度選擇相關方法
const clearYearSelection = () => {
  selectedYears.value = [];
};

const selectRecentYears = () => {
  selectedYears.value = ['114', '113', '112'];
};

// 使用 Store 的狀態
const isLoading = computed(() => qualificationStore.isLoading);
const isIndigenousLoading = computed(() => qualificationStore.isIndigenousLoading);
const showAlert = computed(() => qualificationStore.showAlert);
const error = computed(() => qualificationStore.error);
const searchResults = computed(() => qualificationStore.searchResults);
const recentSearches = computed(() => qualificationStore.recentSearches);
const showNoResultMessage = computed(() => qualificationStore.showNoResultMessage);
const isIndigenousArea = computed(() => qualificationStore.isIndigenousArea);
const isIndigenousAreaChecked = computed(() => qualificationStore.isIndigenousAreaChecked);


// 是否可以查詢 - 只要有母地號就可以查詢
const canSearch = computed(() => {
  return !!searchParams.parentLandNumber;
});

// 是否可以進行原民區域查詢
const canSearchIndigenous = computed(() => {
  return !!indigenousParams.county && !!indigenousParams.town;
});

// 是否可以進行山坡地查詢 - 只要有母地號就可以查詢
const canSearchHillside = computed(() => {
  return !!hillsideParams.parentLandNumber;
});

// 山坡地查詢狀態
const isHillsideLoading = ref(false);
const showHillsideAlert = computed(() => hillsideParams.landNumber && hillsideParams.landNumber.length > 0);

// 地區資料 - 使用 domicileStore 的動態資料
const counties = computed(() => {
  return domicileStore.countyOptions.map(county => ({
    title: county.title,
    value: county.title // 使用 title 作為 value 以配合現有的字串類型
  }));
});

// 動態獲取鄉鎮選項
const towns = computed(() => {
  if (!searchParams.county) return [];
  // 找到對應的縣市 ID
  const county = domicileStore.countyOptions.find(c => c.title === searchParams.county);
  if (!county) return [];

  return domicileStore.getTownsForCountyId(county.value).map(town => ({
    title: town.title,
    value: town.title
  }));
});

// 動態獲取地段選項
const sections = computed(() => {
  if (!searchParams.town) return [];
  // 找到對應的鄉鎮 ID
  const county = domicileStore.countyOptions.find(c => c.title === searchParams.county);
  if (!county) return [];

  const town = domicileStore.getTownsForCountyId(county.value).find(t => t.title === searchParams.town);
  if (!town) return [];

  return domicileStore.getLandSectionsForTownId(town.value).map(section => ({
    title: section.title,
    value: section.title
  }));
});

// 動態獲取原民區查詢的鄉鎮選項
const indigenousTowns = computed(() => {
  if (!indigenousParams.county) return [];
  const county = domicileStore.countyOptions.find(c => c.title === indigenousParams.county);
  if (!county) return [];

  return domicileStore.getTownsForCountyId(county.value).map(town => ({
    title: town.title,
    value: town.title
  }));
});

// 動態獲取山坡地查詢的鄉鎮選項
const hillsideTowns = computed(() => {
  if (!hillsideParams.county) return [];
  const county = domicileStore.countyOptions.find(c => c.title === hillsideParams.county);
  if (!county) return [];

  return domicileStore.getTownsForCountyId(county.value).map(town => ({
    title: town.title,
    value: town.title
  }));
});

// 動態獲取山坡地查詢的地段選項
const hillsideSections = computed(() => {
  if (!hillsideParams.town) return [];
  const county = domicileStore.countyOptions.find(c => c.title === hillsideParams.county);
  if (!county) return [];

  const town = domicileStore.getTownsForCountyId(county.value).find(t => t.title === hillsideParams.town);
  if (!town) return [];

  return domicileStore.getLandSectionsForTownId(town.value).map(section => ({
    title: section.title,
    value: section.title
  }));
});


// 格式化日期
const formatDate = (date: Date): string => {
  if (!date) return '';

  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${year}/${month}/${day} ${hours}:${minutes}`;
};

// 縣市變更事件處理
const onCountyChange = async (newCounty: string) => {
  searchParams.town = '';
  searchParams.section = '';

  // 載入該縣市的鄉鎮資料
  const county = domicileStore.countyOptions.find(c => c.title === newCounty);
  if (county) {
    await domicileStore.loadTownsByCountyId(county.value);
  }
};

// 鄉鎮變更事件處理
const onTownChange = async (newTown: string) => {
  searchParams.section = '';

  // 載入該鄉鎮的地段資料
  const county = domicileStore.countyOptions.find(c => c.title === searchParams.county);
  if (county) {
    const town = domicileStore.getTownsForCountyId(county.value).find(t => t.title === newTown);
    if (town) {
      await domicileStore.loadLandSectionsByTownId(town.value);
    }
  }
};

// 原民區縣市變更事件處理
const onIndigenousCountyChange = async (newCounty: string) => {
  indigenousParams.town = '';
  qualificationStore.clearIndigenousCheck();

  // 載入該縣市的鄉鎮資料
  const county = domicileStore.countyOptions.find(c => c.title === newCounty);
  if (county) {
    await domicileStore.loadTownsByCountyId(county.value);
  }
};

// 山坡地縣市變更事件處理
const onHillsideCountyChange = () => {
  hillsideParams.town = '';
  hillsideParams.section = '';
};

// 山坡地鄉鎮變更事件處理
const onHillsideTownChange = () => {
  hillsideParams.section = '';
};


// 格式化地號：將母子地號合併為完整地號
const formatLandNumber = (parentLandNumber: string, childLandNumber: string = '') => {
  if (!parentLandNumber) return '';

  const formattedParent = parentLandNumber.padStart(4, '0');
  const formattedChild = childLandNumber ? childLandNumber.padStart(4, '0') : '0000';

  return `${formattedParent}-${formattedChild}`;
};

// 格式化母地號：失去焦點時自動補正為四位數
const formatParentLandNumber = (paramsType: 'searchParams' | 'hillsideParams') => {
  const params = paramsType === 'searchParams' ? searchParams : hillsideParams;

  if (params.parentLandNumber && params.parentLandNumber.trim()) {
    // 只保留數字
    const cleanValue = params.parentLandNumber.replace(/\D/g, '');
    if (cleanValue) {
      // 補正為四位數
      params.parentLandNumber = cleanValue.padStart(4, '0');
    } else {
      // 如果清理後沒有數字，清空欄位
      params.parentLandNumber = '';
    }
  }
  // 如果為空，保持為空（讓用戶知道這是必填欄位）
};

// 格式化子地號：失去焦點時自動補正為四位數
const formatChildLandNumber = (paramsType: 'searchParams' | 'hillsideParams') => {
  const params = paramsType === 'searchParams' ? searchParams : hillsideParams;

  if (params.childLandNumber && params.childLandNumber.trim()) {
    // 只保留數字
    const cleanValue = params.childLandNumber.replace(/\D/g, '');
    if (cleanValue) {
      // 補正為四位數
      params.childLandNumber = cleanValue.padStart(4, '0');
    } else {
      // 如果清理後沒有數字，設為 '0000'（選填欄位的預設值）
      params.childLandNumber = '0000';
    }
  } else {
    // 如果為空，設置預設值 '0000'
    params.childLandNumber = '0000';
  }
};

// 地段查詢方法 - 使用真實的 API
const searchLand = async () => {
  // 檢查必填欄位
  if (!canSearch.value) {
    return;
  }

  try {
    // 格式化地號
    const formattedLandNumber = formatLandNumber(searchParams.parentLandNumber || '', searchParams.childLandNumber || '');

    // 創建查詢參數副本並設置格式化後的地號
    const queryParams = {
      ...searchParams,
      landNumber: formattedLandNumber
    };

    await qualificationStore.search('general', queryParams, selectedYears.value);
  } catch (error) {
    console.error('查詢失敗:', error);
    // 錯誤處理已在 store 中統一處理
  }
};

// 原民區域查詢方法 - 使用真實的 API
const searchIndigenous = async () => {
  // 檢查必填欄位
  if (!canSearchIndigenous.value) {
    return;
  }

  try {
    await qualificationStore.checkIndigenousArea(indigenousParams);
  } catch (error) {
    console.error('原民區域查詢失敗:', error);
    // 錯誤處理已在 store 中統一處理
  }
};

// 山坡地查詢方法 - 使用真實的 API
const searchHillside = async () => {
  // 檢查必填欄位
  if (!canSearchHillside.value) {
    return;
  }

  isHillsideLoading.value = true;

  try {
    // 格式化地號
    const formattedLandNumber = formatLandNumber(hillsideParams.parentLandNumber || '', hillsideParams.childLandNumber || '');

    // 創建查詢參數副本並設置格式化後的地號
    const queryParams = {
      ...hillsideParams,
      landNumber: formattedLandNumber
    };

    await qualificationStore.search('slope', queryParams, selectedYears.value);
  } catch (error) {
    console.error('山坡地查詢失敗:', error);
    // 錯誤處理已在 store 中統一處理
  } finally {
    isHillsideLoading.value = false;
  }
};

// 載入最近查詢記錄 - 整合 store 方法
const loadRecentSearch = (item: RecentSearch) => {
  const search = qualificationStore.loadFromHistory(item);

  if (search.section) {
    // 一般區域查詢
    queryType.value = 'general';
    searchParams.county = search.county;
    searchParams.town = search.town;
    searchParams.section = search.section || '';
    searchParams.landNumber = search.landNumber || '';
  } else if (search.landNumber) {
    // 判斷是否為山坡地查詢（這裡可以根據實際業務邏輯調整）
    if (search.queryType === 'slope') {
      queryType.value = 'hillside';
      hillsideParams.county = search.county;
      hillsideParams.town = search.town;
      hillsideParams.section = search.section || '';
      hillsideParams.landNumber = search.landNumber;
    } else {
      // 一般區域查詢，但沒有地段
      queryType.value = 'general';
      searchParams.county = search.county;
      searchParams.town = search.town;
      searchParams.landNumber = search.landNumber;
    }
  } else {
    // 原民區域查詢
    queryType.value = 'indigenous';
    indigenousParams.county = search.county;
    indigenousParams.town = search.town;
  }
};

// 新增：清除所有查詢結果
const clearAllResults = () => {
  qualificationStore.clearResults();
  qualificationStore.clearIndigenousCheck();
  qualificationStore.clearErrors();
};

// === 新增的計算屬性和方法 ===

// 土地位置描述（使用過濾後的結果）
const landLocationDescription = computed(() => {
  if (filteredLegacyResults.value.length === 0) return '';
  const first = filteredLegacyResults.value[0];
  const parts = [];
  if (first.land_section) parts.push(first.land_section);
  return parts.join(' ') || '查詢地號';
});

// 地籍登記總面積 - 取自最新案件的farmarea
const totalApprovedArea = computed(() => {
  if (searchResults.value.length === 0) return 0;

  // 只處理歸檔記錄 (source_system = "legacy_farmdata")
  const legacyRecords = searchResults.value.filter(item => item.source_system === "legacy_farmdata");

  if (legacyRecords.length === 0) {
    // 如果沒有歸檔記錄，使用一般記錄的第一筆
    const firstRecord = searchResults.value[0];
    return Number(firstRecord?.land_registered_area || firstRecord?.approved_area || '0');
  }

  // 找出最新案件：最新年度，該年度中最大的 source_id
  const latestYear = Math.max(...legacyRecords.map(item => item.application_year));
  const latestYearRecords = legacyRecords.filter(item => item.application_year === latestYear);

  // 將字串 source_id 轉換為數字進行比較
  const sourceIds = latestYearRecords.map(item => parseInt(String(item.source_id || 0), 10));
  const latestSourceId = Math.max(...sourceIds);

  // 找到具有最大 source_id 的記錄
  const latestRecord = latestYearRecords.find(item => parseInt(String(item.source_id || 0), 10) === latestSourceId);

  // 回傳最新案件的地籍登記面積
  return Number(latestRecord?.land_registered_area || latestRecord?.approved_area || '0');
});

// 動態查詢說明內容
const queryInstructions = computed(() => {
  switch (queryType.value) {
    case 'general':
      return {
        title: '歷史申請案件查詢說明',
        items: [
          {
            text: '目前只需輸入母地號即可查詢歷史歸檔記錄（縣市、鄉鎮、地段為選填項目）',
            icon: 'mdi-check-circle',
            color: '#3ea0a3'
          },
          {
            text: '若為確認地段是否為原民區域，請選擇原民區域查詢',
            icon: 'mdi-check-circle',
            color: '#3ea0a3'
          },
          {
            text: '查詢結果會顯示歷史申請案件與相關資料',
            icon: 'mdi-check-circle',
            color: '#3ea0a3'
          }
        ]
      };

    case 'indigenous':
      return {
        title: '原民區域查詢說明',
        items: [
          {
            text: '此功能用於確認指定縣市與鄉鎮是否屬於原民區域，並顯示相關訊息',
            icon: 'mdi-information',
            color: '#FF6B35'
          },
          {
            text: '山地鄉(30個)',
            icon: 'mdi-image-filter-hdr',
            color: '#FF6B35',
            isHeader: true
          },
          {
            text: '高雄市茂林區、高雄市桃源區、高雄市那瑪夏區、新北市烏來區、宜蘭縣大同鄉、宜蘭縣南澳鄉、桃園市復興區、新竹縣尖石鄉、新竹縣五峰鄉、苗栗縣泰安鄉、臺中市和平區、南投縣信義鄉、南投縣仁愛鄉、嘉義縣阿里山鄉、屏東縣三地門鄉、屏東縣霧臺鄉、屏東縣瑪家鄉、屏東縣泰武鄉、屏東縣來義鄉、屏東縣春日鄉、屏東縣獅子鄉、屏東縣牡丹鄉、花蓮縣秀林鄉、花蓮縣萬榮鄉、花蓮縣卓溪鄉、臺東縣延平鄉、臺東縣海端鄉、臺東縣達仁鄉、臺東縣金峰鄉、臺東縣蘭嶼鄉',
            icon: 'mdi-format-list-bulleted',
            color: '#757575',
            isContent: true
          },
          {
            text: '平地鄉(25個)',
            icon: 'mdi-home-group',
            color: '#FF6B35',
            isHeader: true
          },
          {
            text: '新竹縣關西鎮、苗栗縣南庄鄉、苗栗縣獅潭鄉、南投縣魚池鄉、屏東縣滿州鄉、花蓮縣花蓮市、花蓮縣光復鄉、花蓮縣玉里鎮、花蓮縣新城鄉、花蓮縣吉安鄉、花蓮縣壽豐鄉、花蓮縣鳳林鎮、花蓮縣豐濱鄉、花蓮縣瑞穗鄉、花蓮縣富里鄉、臺東縣台東市、臺東縣成功鎮、臺東縣關山鎮、臺東縣東河鄉、臺東縣太麻里鄉、臺東縣大武鄉、臺東縣卑南鄉、臺東縣長濱鄉、臺東縣鹿野鄉、臺東縣池上鄉',
            icon: 'mdi-format-list-bulleted',
            color: '#757575',
            isContent: true
          }
        ]
      };

    case 'slope':
      return {
        title: '山坡地查詢說明',
        items: [
          {
            text: '由於提供山坡地資料的API服務已停止更新，本系統無法在取得即時資料，請直接點選下方連結進行查詢：',
            icon: 'mdi-information',
            color: '#8BC34A'
          },
          {
            text: '直轄市政府山坡地查詢',
            icon: 'mdi-earth',
            color: '#8BC34A',
            url: 'https://serv.ardswc.gov.tw/B/#BLinkMain'
          },
          {
            text: '行動水保服務網',
            icon: 'mdi-earth',
            color: '#8BC34A',
            url: 'https://serv.ardswc.gov.tw/B/'
          }
        ]
      };

    default:
      return {
        title: '查詢說明',
        items: [
          {
            text: '請從左側選擇適當的查詢類型',
            icon: 'mdi-help-circle',
            color: '#757575'
          }
        ]
      };
  }
});

// 移除未使用的計算屬性以清理 ESLint 警告
// 這些計算屬性之前用於統計信息顯示，但目前已被註釋掉

// 歷史記錄過濾 - 只顯示與最新案件地段相關的資料
const filteredLegacyResults = computed(() => {
  if (searchResults.value.length === 0) return [];

  // 只處理歸檔記錄 (source_system = "legacy_farmdata")
  const legacyRecords = searchResults.value.filter(item => item.source_system === "legacy_farmdata");

  if (legacyRecords.length === 0) {
    return searchResults.value;
  }

  // 找出最新案件：最新年度，該年度中最大的 source_id
  const latestYear = Math.max(...legacyRecords.map(item => item.application_year));
  const latestYearRecords = legacyRecords.filter(item => item.application_year === latestYear);

  // 將字串 source_id 轉換為數字進行比較
  const sourceIds = latestYearRecords.map(item => parseInt(String(item.source_id || 0), 10));
  const latestSourceId = Math.max(...sourceIds);

  // 找到具有最大 source_id 的記錄
  const latestRecord = latestYearRecords.find(item => parseInt(String(item.source_id || 0), 10) === latestSourceId);

  if (!latestRecord?.land_section) {
    return legacyRecords;
  }

  // 使用最新記錄的地段號碼來過濾所有歸檔記錄
  const targetLandSection = latestRecord.land_section;
  const filteredResults = legacyRecords.filter(item => item.land_section === targetLandSection);

  return filteredResults;
});

// 按年度分組
const groupedByYear = computed(() => {
  if (filteredLegacyResults.value.length === 0) return [];

  const groups = new Map();
  // 固定的四個設施類型
  const fixedFacilityTypes = ['田間管路', '調蓄設施', '調控設施', '動力設備'];

  filteredLegacyResults.value.forEach(item => {
    const year = item.application_year;
    if (!groups.has(year)) {
      groups.set(year, {
        year,
        cases: [],
        totalArea: 0,
        facilities: new Map(),
        landRegisteredArea: Number(item.land_registered_area || item.approved_area || 0) // 地籍登記面積
      });
    }

    const yearGroup = groups.get(year);
    yearGroup.cases.push(item);
    yearGroup.totalArea += Number(item.approved_area);

    // 更新地籍登記面積（取最大值作為該年度的地籍登記面積）
    const currentLandArea = Number(item.land_registered_area || item.approved_area || 0);
    if (currentLandArea > yearGroup.landRegisteredArea) {
      yearGroup.landRegisteredArea = currentLandArea;
    }

    // 處理該記錄已申請的設施類型
    const appliedFacilityTypes = item.case_type ? item.case_type.split(', ').map(type => type.trim()) : [];

    appliedFacilityTypes.forEach(facilityType => {
      if (fixedFacilityTypes.includes(facilityType)) {
        if (!yearGroup.facilities.has(facilityType)) {
          yearGroup.facilities.set(facilityType, {
            type: facilityType,
            cases: [],
            appliedArea: 0,
            landRegisteredArea: yearGroup.landRegisteredArea,
            status: 'applied'
          });
        }

        const facilityGroup = yearGroup.facilities.get(facilityType);
        facilityGroup.cases.push(item);
        facilityGroup.appliedArea += Number(item.approved_area);
        facilityGroup.landRegisteredArea = yearGroup.landRegisteredArea;
      }
    });
  });

  // 為每個年度補充未申請的設施類型
  groups.forEach(yearGroup => {
    fixedFacilityTypes.forEach(facilityType => {
      if (!yearGroup.facilities.has(facilityType)) {
        yearGroup.facilities.set(facilityType, {
          type: facilityType,
          cases: [],
          appliedArea: 0,
          landRegisteredArea: yearGroup.landRegisteredArea,
          status: 'not_applied'
        });
      }
    });
  });

  // 轉換為陣列並排序
  return Array.from(groups.values())
    .sort((a, b) => (b as { year: number }).year - (a as { year: number }).year)
    .map(yearGroup => ({
      ...yearGroup,
      facilities: fixedFacilityTypes.map(facilityType => {
        const facility = (yearGroup as { facilities: Map<string, { type: string; cases: unknown[]; appliedArea: number; landRegisteredArea: number; status: string }> }).facilities.get(facilityType);
        return {
          ...facility,
          statusText: getFacilityStatusText(facility!.appliedArea || 0, facility!.landRegisteredArea || 0),
          remainingArea: Math.max(0, (facility!.landRegisteredArea || 0) - (facility!.appliedArea || 0))
        };
      })
    }));
});

// 年度標籤顏色
const getYearChipColor = (year: number) => {
  const currentYear = new Date().getFullYear() - 1911; // 轉換為民國年
  if (year >= currentYear - 1) return 'success'; // 近兩年
  if (year >= currentYear - 3) return 'info'; // 近三年
  return 'grey'; // 較舊年度
};

// 設施圖示
const getFacilityIcon = (facilityType: string) => {
  const iconMap: Record<string, { icon: string, color: string }> = {
    // '節水設備': { icon: 'mdi-water', color: 'blue' },
    '田間管路': { icon: 'mdi-pipe', color: 'green' },
    '調蓄設施': { icon: 'mdi-storage-tank', color: 'orange' },
    '調控設施': { icon: 'mdi-valve', color: 'purple' },
    '動力設備': { icon: 'mdi-engine', color: 'red' },
    // '一般設施': { icon: 'mdi-tools', color: 'grey' },
    // '歷史案件': { icon: 'mdi-history', color: 'brown' }
  };

  return iconMap[facilityType] || iconMap['一般設施'];
};

// 狀態顏色 - 基於狀態文字而非面積
const getStatusColor = (appliedArea: number, landRegisteredArea: number) => {
  const statusText = getFacilityStatusText(appliedArea, landRegisteredArea);

  if (statusText === '尚未申請') return 'info';
  if (statusText === '已全部申請') return 'grey';
  return 'teal'; // 尚有面積的情況 - 使用青色避免與調蓄設施橘色衝突
};

// 移除未使用的面積狀態格式化函數
// 此函數已被 getFacilityStatusText 和狀態文字邏輯取代

// 設施狀態文字計算
const getFacilityStatusText = (appliedArea: number, landRegisteredArea: number) => {
  const applied = appliedArea || 0;
  const registered = landRegisteredArea || 0;

  if (applied === 0) {
    return '尚未申請';
  } else if (applied >= registered) {
    return '已全部申請';
  } else {
    const remainingArea = registered - applied;
    return `尚有${remainingArea.toLocaleString()}㎡`;
  }
};

// 設施顏色十六進制值
const getFacilityColorHex = (facilityType: string) => {
  const colorMap: Record<string, string> = {
    // '節水設備': '#2196F3',  // blue
    '田間管路': '#4CAF50',  // green
    '調蓄設施': '#FF9800',  // orange
    '調控設施': '#9C27B0',  // purple
    '動力設備': '#F44336',  // red
    // '一般設施': '#757575',  // grey
    // '歷史案件': '#795548'   // brown
  };

  return colorMap[facilityType] || '#757575'; // 預設為灰色
};

// 格式化分組中的申請人
const formatApplicantsInGroup = (cases: Array<{ applicant: string }>) => {
  // 過濾掉空的或undefined的申請人
  const validApplicants = [...new Set(cases.map(c => c.applicant).filter(applicant => applicant && applicant.trim()))];

  if (validApplicants.length === 0) {
    return '無申請紀錄';
  } else if (validApplicants.length === 1) {
    return validApplicants[0];
  } else {
    return `${validApplicants[0]} 等 ${validApplicants.length} 人`;
  }
};

// 計算過濾後結果對應的 office_boundaries
const allOfficeBoundaries = computed(() => {
  // 只取與過濾後結果相同 land_section + land_number 組合的 office_boundaries
  if (filteredLegacyResults.value.length === 0) return [];

  // 取得過濾後結果的 land_section (所有記錄應該有相同的 land_section)
  const targetLandSection = filteredLegacyResults.value[0].land_section;
  const targetLandNumber = filteredLegacyResults.value[0].land_number;

  const boundaries = [];

  // 遍歷所有查詢結果，找到匹配的地段+地號組合
  for (const result of searchResults.value) {
    if (result.land_section === targetLandSection &&
        result.land_number === targetLandNumber &&
        result.office_boundaries &&
        result.office_boundaries.length > 0) {
      boundaries.push(...result.office_boundaries);
    }
  }

  // 去重複 (根據 gid)
  const seen = new Set();
  return boundaries.filter(boundary => {
    if (seen.has(boundary.gid)) {
      return false;
    }
    seen.add(boundary.gid);
    return true;
  });
});

// 移除 uniqueManagementOffices，直接在模板中顯示完整層級資訊

// 組件掛載時初始化
onMounted(async () => {
  console.log('Qualification page mounted');

  // 初始化 domicile store - 載入縣市資料
  try {
    await domicileStore.loadCounties();
    console.log('Counties loaded successfully');
  } catch (error) {
    console.error('Failed to load counties:', error);
  }
});

// 切換標籤頁時清除查詢結果
watch(queryType, () => {
  qualificationStore.clearResults();
  qualificationStore.clearIndigenousCheck();
});

// 當搜尻結果變化時，自動選擇第一個年度 tab
watch(groupedByYear, (newGroups) => {
  if (newGroups.length > 0) {
    selectedYearTab.value = newGroups[0].year;
  }
}, { immediate: true });
</script>

<style scoped>
/* 添加背景圖片樣式 */
.qualification-container {
  background-image: url('@/assets/bg_index.svg');
  background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

/* 區塊共通容器 */
.section-wrapper {
  padding: 8px 4px 0px 4px;
}

/* 卡片與標題樣式 */
.section-card {
  position: relative;
  margin: 24px 0;
  overflow: visible !important;
  border-top-left-radius: 0 !important;
  transition: all 0.3s ease;

  /* 毛玻璃效果 */
  background-color: rgba(255, 255, 255, 0.6) !important; /* 半透明白色背景 */
  backdrop-filter: blur(10px) !important; /* 背景模糊效果 */
  -webkit-backdrop-filter: blur(10px) !important; /* Safari 支持 */
  border: 1px solid rgba(255, 255, 255, 0.25) !important; /* 細微邊框增強玻璃感 */
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important; /* 柔和陰影增強玻璃感 */
}

.section-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  background-color: rgba(255, 255, 255, 0.85) !important; /* 懸停時略微增加不透明度 */
}

.section-card:hover .custom-title {
  background-color: #2d8c8f !important;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.08);
}

.custom-title {
  position: absolute;
  top: -50px;
  left: -1px;
  width: auto !important;
  min-width: 130px;
  height: 50px;
  background-color: #3ea0a3 !important;
  border-radius: 8px 8px 0 0;
  z-index: 1;
  transition: all 0.3s ease;
}

.v-card-title {
  color: white !important;
  display: flex;
  justify-content: flex-start;
  align-items: center;
  width: 100%;
  height: 100%;
}

/* 表格區域樣式 */
.table-card {
  border-radius: 12px;
  overflow: hidden;
  background-color: white !important;
}

/* 按鈕樣式 */
.action-btn {
  background-color: white !important;
  font-weight: 500;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: #3ea0a3 !important;
  color: white !important;
}

/* 篩選區域樣式 */
.filter-select {
  max-width: 200px;
}

@media (max-width: 600px) {
  .filter-select {
    min-width: 100%;
  }
}

/* 查詢結果樣式 */
.v-list .v-list-item .v-icon {
  color: #3ea0a3;
  font-size: 18px;
}

/* 最近查詢項目樣式 */
.v-list-item:hover {
  background-color: #f5f5f5;
  cursor: pointer;
}

/* 查詢類型按鈕組樣式 */
.v-btn-toggle {
  width: 100% !important;
  display: flex !important;
}

.v-btn-toggle .v-btn {
  flex: 1 !important;
  min-width: 0 !important;
}
</style>
