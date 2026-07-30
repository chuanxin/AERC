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

                  <!-- 年度選擇 - 僅在歷史申請案件查詢時顯示 -->
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

                          <!-- 只有非特殊城市才顯示鄉鎮市區選單 -->
                          <v-select
                            v-if="!['新竹市', '嘉義市'].includes(searchParams.county)"
                            v-model="searchParams.town"
                            :items="towns"
                            label="鄉鎮市區"
                            variant="outlined"
                            density="compact"
                            class="flex-grow-1 ml-3"
                            bg-color="white"
                            :disabled="!searchParams.county"
                            hide-details
                            clearable
                            @update:model-value="onTownChange"
                          />

                          <!-- 特殊城市顯示固定的地政分區資訊 -->
                          <v-text-field
                            v-else-if="searchParams.county"
                            :model-value="getSpecialCityDisplayText()"
                            class="flex-grow-1 ml-3"
                            bg-color="grey-lighten-4"
                            label="鄉政市區"
                            variant="outlined"
                            density="compact"
                            hide-details
                            disabled
                          />
                        </div>

                        <!-- 地段候選清單挑選器 - 第二排：只能選、不能打字，選定後自動帶入下方查詢欄位 -->
                        <div class="d-flex align-center mb-3">
                          <v-autocomplete
                            :key="sectionSelectKey"
                            v-model="selectedSectionCandidate"
                            :items="sections"
                            :item-title="item => item.displayName || item.name"
                            item-value="displayName"
                            :return-object="false"
                            label="從清單選擇地段"
                            variant="outlined"
                            density="compact"
                            hide-details
                            class="flex-grow-1"
                            bg-color="white"
                            clearable
                            autocomplete="off"
                            :placeholder="sections.length > 0 ? '從清單挑選...' : '請先選擇鄉鎮市區'"
                            :disabled="!searchParams.town && !['新竹市', '嘉義市'].includes(searchParams.county)"
                            :loading="loadingSections"
                            :no-data-text="'沒有找到相符的地段'"
                            :menu-props="{ closeOnContentClick: true }"
                            :auto-select-first="false"
                            aria-label="從清單選擇地段"
                            @update:model-value="onSectionCandidateSelected"
                          >
                            <template #item="{ props, item }">
                              <v-list-item v-bind="props">
                                <template #title>
                                  <div>
                                    {{ item.raw.displayName || item.raw.name }}
                                  </div>
                                </template>

                                <template #subtitle>
                                  <div class="d-flex align-center mt-1">
                                    <span class="text-caption text-grey-darken-1">
                                      段號: {{ item.raw.code || '無' }}
                                    </span>
                                  </div>
                                </template>
                              </v-list-item>
                            </template>
                          </v-autocomplete>

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

                        <!-- 查詢用地段名稱 - 第三排：可自行編輯，執行查詢時一律以此欄內容為準 -->
                        <div class="d-flex align-center">
                          <v-text-field
                            v-model="searchParams.section"
                            label="查詢用地段名稱"
                            variant="outlined"
                            density="compact"
                            hide-details
                            class="flex-grow-1"
                            bg-color="white"
                            clearable
                            autocomplete="off"
                            placeholder="或直接輸入地段名稱查詢"
                            aria-label="查詢用地段名稱"
                          />
                        </div>

                        <!-- 特殊城市提示 -->
                        <div
                          v-if="['新竹市', '嘉義市'].includes(searchParams.county)"
                          class="mt-2"
                        >
                          <v-alert
                            type="info"
                            variant="tonal"
                            density="compact"
                            icon="mdi-information"
                            class="text-caption"
                          >
                            {{ searchParams.county }}適用單一地政分區
                          </v-alert>
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
                            autocomplete="off"
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
                            autocomplete="off"
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
                      <!-- 山坡地服務離線警告 -->
                      <!-- <v-alert
                        type="warning"
                        variant="outlined"
                        class="mb-4"
                        density="compact"
                      >
                        <template #prepend>
                          <v-icon>mdi-alert-circle</v-icon>
                        </template>
                        <div class="text-body-2">
                          <strong>山坡地查詢服務目前離線</strong><br>
                          此功能暫時無法使用，請稍後再試或聯繫系統管理員。
                        </div>
                      </v-alert> -->

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
                            disabled
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
                            disabled
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
                            disabled
                            bg-color="white"
                          />

                          <!-- API連線狀態 -->
                          <div class="d-flex align-center ml-2">
                            <v-chip
                              color="error"
                              size="small"
                              variant="outlined"
                            >
                              <v-icon
                                icon="mdi-close-circle"
                                size="small"
                                class="me-1"
                              />
                              離線
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
                          disabled
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
                          <div class="mb-4">
                            <div
                              v-if="filteredLegacyResults.length > 0 && Object.keys(lastSearchParams).length > 0"
                              class="text-h6 font-weight-bold mb-2"
                            >
                              歸檔記錄查詢結果：{{ landLocationDescription }} {{ completeLandNumber }}
                            </div>
                            <div
                              v-else-if="filteredLegacyResults.length === 0 && Object.keys(lastSearchParams).length > 0"
                              class="text-h6 font-weight-bold mb-2"
                            >
                              歸檔記錄查詢結果：{{ landLocationDescription }} {{ completeLandNumber }}
                            </div>
                            <div
                              v-else
                              class="text-h6 font-weight-bold mb-2"
                            >
                              查詢結果
                            </div>

                            <!-- 地段過濾警告信息 - 已關閉地段過濾功能，故註解此警告 -->
                            <!--
                            <div
                              v-if="searchResults.length > filteredLegacyResults.length && filteredLegacyResults.length > 0"
                              class="text-caption text-warning mb-2"
                            >
                              ⚠️ 已過濾僅顯示與最新案件地段 ({{ filteredLegacyResults[0].land_section }}) 相關的 {{ filteredLegacyResults.length }} 筆記錄 (包含其它地段的記錄總共 {{ searchResults.length }} 筆)
                            </div>
                            -->

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
                                  <!-- {{ filteredLegacyResults.length > 0 ? selectedYearTotalApprovedArea.toLocaleString() : '-' }} -->
                                  {{ (filteredLegacyResults.length > 0 && selectedYearTotalApprovedArea > 0) ? selectedYearTotalApprovedArea.toLocaleString() : '--' }}
                                  
                                </div>
                                <div class="text-caption">
                                  ㎡
                                </div>
                              </div>

                              <v-divider
                                class="mx-4"
                                vertical
                              />

                              <!-- 農田水利事業區域資訊 -->
                              <div class="flex-grow-1">
                                <div class="d-flex align-center mb-2">
                                  <v-icon
                                    color="teal"
                                    size="small"
                                    class="me-1"
                                  >
                                    mdi-domain
                                  </v-icon>
                                  <span class="text-caption font-weight-medium">農田水利事業區域</span>
                                </div>

                                <!-- 詳細事業區層級資訊 -->
                                <div
                                  v-if="selectedYearOfficeBoundaries && selectedYearOfficeBoundaries.length > 0"
                                  class="d-flex flex-column gap-2"
                                >
                                  <div
                                    v-for="boundary in selectedYearOfficeBoundaries.slice(0, 2)"
                                    :key="boundary.gid"
                                    class="text-body-2"
                                  >
                                    <span class="font-weight-bold text-teal">{{ boundary.ia_name || '未知' }}管理處</span>
                                    <template v-if="boundary.mng_name">
                                      <span class="mx-2 text-grey-darken-1">></span>
                                      <span>{{ boundary.mng_name }}</span>
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
                                    v-if="selectedYearOfficeBoundaries.length > 2"
                                    class="text-body-2 text-grey-darken-1 mt-1"
                                  >
                                    另有 {{ selectedYearOfficeBoundaries.length - 2 }} 個事業區域
                                  </div>
                                </div>

                                <!-- 無事業區域資訊時的顯示 -->
                                <div
                                  v-else
                                  class="d-flex align-center justify-center pa-3 rounded"
                                  style="background-color: #f8f9fa; border: 1px dashed #dee2e6;"
                                >
                                  <v-icon
                                    color="grey-darken-1"
                                    size="small"
                                    class="me-2"
                                  >
                                    mdi-information-outline
                                  </v-icon>
                                  <span class="text-body-2 text-grey-darken-1 font-weight-medium">
                                    暫無事業區域資料
                                  </span>
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
                              <!-- Joya test -->
                              <div class="case-list mb-4">
                                <v-card
                                  v-for="(caseItem, index) in yearGroup.cases"
                                  :key="caseItem.id || index"
                                  class="mb-3 border-s-4"
                                  :class="getCaseStatusColorClass(caseItem)"
                                  elevation="1"
                                  rounded="lg"
                                  variant="flat"
                                  :style="caseItem.data_format_warning ? 'background-color: rgba(255, 152, 0, 0.10); border: 1px solid #e0e0e0;' : 'background-color: white; border: 1px solid #e0e0e0;'"
                                >
                                  <div class="d-flex align-center pa-3">
                                    <v-btn
                                      :icon="isCaseExpanded(caseItem, index) ? 'mdi-minus' : 'mdi-plus'"
                                      variant="text"
                                      density="comfortable"
                                      :color="isCaseExpanded(caseItem, index) ? 'grey-darken-3' : 'grey-darken-1'"
                                      class="me-2"
                                      @click.stop="toggleCaseExpansion(caseItem, index)"
                                    ></v-btn>

                                    <v-row 
                                      no-gutters 
                                      align="center" 
                                      style="cursor: pointer;"
                                      @click="toggleCaseExpansion(caseItem, index)"
                                    >
                                    <v-col cols="12" sm="2" class="d-flex align-center mb-2 mb-sm-0">
                                        <v-chip
                                          size="small"
                                          color="primary"
                                          variant="tonal"
                                          class="font-weight-bold me-2"
                                          label
                                        >
                                          {{ caseItem.office || '無管理處' }}
                                        </v-chip>
                                        <!-- 資料格式錯誤警告（逐案件；缺縣市/鄉鎮名稱時顯示，不阻擋其餘呈現） -->
                                        <v-tooltip
                                          v-if="caseItem.data_format_warning"
                                          location="top"
                                        >
                                          <template #activator="{ props }">
                                            <v-icon
                                              v-bind="props"
                                              icon="mdi-alert-circle"
                                              color="warning"
                                              size="18"
                                              class="ms-2"
                                            />
                                          </template>
                                          <span>{{ caseItem.data_format_warning }}</span>
                                        </v-tooltip>
                                      </v-col>
                                      
                                      <v-col cols="6" sm="2" class="mb-2 mb-sm-0">
                                        <div class="d-flex align-center">
                                          <v-icon size="small" color="indigo" class="me-1">mdi-file-document</v-icon>
                                          <span class="text-body-2 text-grey-darken-3">
                                            案號 : {{ caseItem.case_number || '無案號' }}
                                          </span>
                                        </div>
                                      </v-col>
                                      
                                      <v-col cols="6" sm="2" class="mb-2 mb-sm-0">
                                        <div class="d-flex align-center">
                                          <v-icon size="small" color="indigo" class="me-1">mdi-account</v-icon>
                                          <span class="text-body-2 text-grey-darken-3">
                                            申請人 : {{ caseItem.applicant || '未填寫' }}
                                          </span>
                                        </div>
                                      </v-col>

                                      <v-col cols="12" sm="3">
                                        <div class="d-flex align-center">
                                          <v-icon size="small" color="brown" class="me-1">mdi-map-marker</v-icon>
                                          <span class="text-body-2 text-grey-darken-3">
                                            土地 : {{ getLandSectionDisplay(caseItem) }} {{ caseItem.land_number }}
                                          </span>
                                        </div>
                                      </v-col>

                              

                                    </v-row>
                                  </div>
                                  <v-expand-transition>
                                  <div v-if="isCaseExpanded(caseItem, index)">
                                    <v-divider></v-divider>
                                    <div class="pa-3 bg-grey-lighten-5">
                                      <div class="text-caption text-grey-darken-1 mb-2">包含設施項目：</div>
                                      
                                      <div class="d-flex flex-wrap gap-2">
                                        <div
                                          v-for="facility in getFacilitiesForCase(caseItem)"
                                          :key="facility.type"
                                          class="d-flex align-center px-3 py-2 rounded bg-white border"
                                          style="min-width: 140px;"
                                        >
                                          <div
                                            class="d-flex align-center justify-center me-3 rounded"
                                            :style="`background-color: ${facility.colorHex}; width: 32px; height: 32px;`"
                                          >
                                            <v-icon :icon="facility.icon" color="white" size="18"></v-icon>
                                          </div>
                                          
                                          <div>
                                            <div class="text-body-2 font-weight-bold">
                                              {{ facility.type }}
                                              
                                              <span v-if="['田間管路', '水保署'].includes(facility.type)" class="ms-1">
                                                {{ formatIrrigationType(caseItem.irrigation_type) }}
                                            </span>
                                            </div>
                                            <div class="text-caption text-grey-darken-1">
                                              已申請
                                              </div>
                                          </div>
                                        </div>

                                        <div v-if="getFacilitiesForCase(caseItem).length === 0" class="text-body-2 text-grey">
                                          無詳細設施資料
                                        </div>
                                      </div>
                                     
                              <div class="facility-list">
                            </div>
                            

                                      <div class="d-flex justify-end align-center mt-3 pt-2 border-t">
                                        <span class="text-caption text-grey-darken-1 me-2">地籍面積：</span>
                                        <span class="text-body-1 font-weight-bold text-primary">
                                          <!-- {{ Number(caseItem.land_registered_area || 0).toLocaleString() }} -->
                                          {{ (caseItem.land_registered_area > 0) ? Number(caseItem.land_registered_area).toLocaleString() : '--' }}
                                        </span>
                                        <span class="text-caption ms-1">㎡</span>
                                        
                                        <span class="text-caption text-grey-darken-1 me-2 ms-4">施設面積：</span>
                                        <span class="text-body-1 font-weight-bold text-primary">
                                          <!-- {{ Number(caseItem.approved_area || 0).toLocaleString() }} -->
                                          {{ (caseItem.approved_area > 0) ? Number(caseItem.approved_area).toLocaleString() : '--' }}
                                        </span>
                                        <span class="text-caption ms-1">㎡</span>

                                        <span class="text-caption text-grey-darken-1 me-2 ms-4">剩餘面積：</span>
                                        <span class="text-body-1 font-weight-bold text-red">
                                          {{ (caseItem.land_registered_area > 0 || caseItem.approved_area > 0) 
                                            ? Number((caseItem.land_registered_area || 0) - (caseItem.approved_area || 0)).toLocaleString() 
                                            : '--' }}
                                        </span>
                                        <span class="text-caption ms-1">㎡</span>

                                      </div>
                                    </div>
                                  </div>
                                  </v-expand-transition>
                                  </v-card>
                              </div>
                        <!-- Joya test end -->
                               
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
                    <span>無查詢結果，此地號尚未有歷史補助申請紀錄。</span>
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
import { ref, computed, watch, reactive, onMounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { useQualificationStore } from '@/stores/qualification';
import { useDomicileStore } from '@/stores/domicile';
import { checkNlscApiHealth, type LandSection } from '@/services/landSectionNlscService';
import type { QualificationSearchParams, IndigenousSearchParams, RecentSearch, GrantCaseItem } from '@/types/qualification';

const qualificationStore = useQualificationStore();
const domicileStore = useDomicileStore();
const route = useRoute();

const queryType = ref('general');

// API連線狀態
const apiStatus = ref({
  isOnline: false,
  lastChecked: null as Date | null
});

// NLSC 地段資料
const nlscSections = ref<LandSection[]>([]);
const loadingSections = ref(false);

// 用於強制重新渲染地段選單的 key
const sectionSelectKey = ref(0);

// 地段候選清單挑選器目前的選取值（僅供快速帶入，不直接作為查詢值）
const selectedSectionCandidate = ref<string | null>(null);

// 從候選清單挑選地段後，帶入查詢用的文字輸入框；查詢送出時一律以文字輸入框內容為準
const onSectionCandidateSelected = (value: string | null) => {
  if (value) {
    searchParams.section = value;
  }
};

// 地段查詢參數
const searchParams = reactive<QualificationSearchParams>({
  county: '',
  town: null,
  section: null,
  landNumber: '',
  parentLandNumber: '',
  childLandNumber: ''
});

// 查詢用地段名稱只要不再與上方清單挑選的值一致（清空或手動改成別的內容），
// 上方的清單挑選狀態就一併清空，避免畫面顯示「已選取」卻與實際查詢值不同步
watch(() => searchParams.section, (newValue) => {
  if (newValue !== selectedSectionCandidate.value) {
    selectedSectionCandidate.value = null;
  }
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

// 保存實際執行查詢時的條件
const lastSearchParams = ref<{
  county?: string;
  town?: string | null;
  section?: string | null;
  parentLandNumber?: string;
  childLandNumber?: string;
}>({});

// 可選年度範圍 (97年至115年)
const availableYears = Array.from({ length: 18 }, (_, i) => (115 - i).toString());

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

//Joya test
// 取得案件的管理處名稱
const getCaseOfficeName = (item: any) => {
  if (item.office_boundaries && item.office_boundaries.length > 0) {
    // 優先顯示第一個管理處名稱
    const office = item.office_boundaries[0];
    return `${office.ia_name || ''} ${office.stn_name || ''}`;
  }
  // 如果沒有 boundary 資料，嘗試回傳 office 欄位或預設值
  return item.office || item.management_office || '未知管理處';
};

// 根據案件狀態決定卡片左側邊框顏色 (裝飾用)
const getCaseStatusColorClass = (item: any) => {
  // 這裡可以根據 item.status 做判斷，目前先隨機或固定
  return 'border-primary'; // 需在 <style> 定義或使用 Vuetify 顏色類別
};

// 灌溉型式名稱對照表 (簡化顯示用)
const formatIrrigationType = (type: string) => {
  if (!type) return '未設定';
  const map: Record<string, string> = {
    '穿孔管系統': '穿孔管',
    '噴頭式系統': '噴灌',
    '微噴系統': '微噴',
    '滴灌系統': '滴灌',
    '其它': '其它',
    '水保署': '水保署'
  };
  return map[type] || type;
};

// === 新增：展開/收合狀態管理 ===
const expandedCaseIds = ref(new Set<string | number>());

const toggleCaseExpansion = (caseItem: any, index: number) => {
  // 使用 id 作為 key，若無 id 則使用 index 組合年份當作臨時 key
  const key = caseItem.id || `${caseItem.application_year}_${index}`;
  
  if (expandedCaseIds.value.has(key)) {
    expandedCaseIds.value.delete(key);
  } else {
    expandedCaseIds.value.add(key);
  }
};

const isCaseExpanded = (caseItem: any, index: number) => {
  const key = caseItem.id || `${caseItem.application_year}_${index}`;
  return expandedCaseIds.value.has(key);
};

// === 新增：解析單一案件的設施列表 ===
// 這會將 case_type 字串 (例如 "田間管路, 調蓄設施") 轉換為陣列物件，方便 v-for 渲染
const getFacilitiesForCase = (caseItem: any) => {
  if (!caseItem.case_type) return [];
  
  const types = caseItem.case_type.split(',').map((t: string) => t.trim());
  const fixedTypes = ['田間管路', '調蓄設施', '調控設施', '動力設備', '水保署'];
  
  // 過濾出我們關注的 4 大類，並回傳渲染需要的設定
  return types
    .filter((type: string) => fixedTypes.includes(type))
    .map((type: string) => ({
      type,
      ...getFacilityIcon(type), // 複用原本的圖示設定
      colorHex: getFacilityColorHex(type) // 複用原本的顏色設定
    }));
};

//Joya test end
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
  // 後端已排序，直接使用
  return domicileStore.countyOptions
    .map(county => ({
      title: county.title,
      value: county.title, // 使用 title 作為 value 以配合現有的字串類型
      code: county.code,
      land_code: county.land_code
    }));
});

// 動態獲取鄉鎮選項（僅非特殊城市使用）
const towns = computed(() => {
  if (!searchParams.county || ['新竹市', '嘉義市'].includes(searchParams.county)) return [];

  // 找到對應的縣市 ID
  const county = domicileStore.countyOptions.find(c => c.title === searchParams.county);
  if (!county) return [];

  // 後端已排序，直接使用
  return domicileStore.getTownsForCountyId(county.value)
    .map(town => ({
      title: town.title,
      value: town.title,
      code: town.code,
      land_code: town.land_code
    }));
});

// 動態獲取地段選項 - 使用 NLSC API，優化搜尋支援
const sections = computed(() => {
  const result = nlscSections.value
    .map(section => ({
      displayName: section.name,  // 純地段名稱，供顯示使用
      value: section.code,        // 實際存儲的值，使用 API 原始格式
      code: section.code,         // 保持 API 原始格式（如 "0446"）
      name: section.name,         // 保留名稱
      office: section.office
    }))
    .sort((a, b) => {
      // 優先按地段代碼排序，如果沒有代碼則按名稱排序
      if (a.code && b.code) {
        return a.code.localeCompare(b.code);
      }
      return a.name.localeCompare(b.name);
    });

  // Debug: 檢查資料結構
  // if (result.length > 0) {
  //   console.log('🔍 [Qualification] sections 資料結構範例:', result[0]);
  //   console.log('🔍 [Qualification] 預設搜尋將搜尋 title 欄位:', result[0].title);
  // }

  return result;
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
  // 重置地段選擇和資料
  searchParams.section = null;
  selectedSectionCandidate.value = null;
  nlscSections.value = [];

  // 強制重新渲染地段選單
  sectionSelectKey.value++;

  // 使用 nextTick 確保重置生效
  await nextTick();

  // 載入該縣市的鄉鎮資料
  const county = domicileStore.countyOptions.find(c => c.title === newCounty);
  if (county) {
    await domicileStore.loadTownsByCountyId(county.value);

    // 如果是特殊城市，設定虛擬town並自動載入地段資料
    if (specialCities[newCounty] && county.land_code) {
      // 為特殊城市設定一個虛擬的town值，確保API請求正常運作
      searchParams.town = 'SPECIAL_CITY_AUTO';

      const specialCode = specialCities[newCounty].code;
      loadingSections.value = true;
      try {
        await domicileStore.loadLandSectionsByLandCodes(county.land_code, specialCode);
        nlscSections.value = domicileStore.landSections.filter(s =>
          s.county_land_code === county.land_code && s.town_land_code === specialCode
        );
        console.log(`已自動載入 ${newCounty} 的地段資料 (${specialCode}):`, nlscSections.value.length);
      } catch (error) {
        console.error('Failed to load land sections for special city:', error);
        nlscSections.value = [];
      } finally {
        loadingSections.value = false;
      }
    } else {
      // 一般縣市清空town選擇
      searchParams.town = null;
    }
  }
};

// 鄉鎮變更事件處理
// 特殊城市配置
const specialCities: Record<string, { code: string; name: string }> = {
  '新竹市': { code: 'O01', name: '新竹市' },
  '嘉義市': { code: 'I01', name: '嘉義市' }
};

// 取得特殊城市的顯示文字
const getSpecialCityDisplayText = (): string => {
  if (!searchParams.county) return '';
  const cityInfo = specialCities[searchParams.county];
  return cityInfo ? `${cityInfo.name}` : '';
};

// 地政代碼對應表 - 處理戶政/地政資料不一致的問題
const getLandCodeForNlsc = (countyName: string, townLandCode: string | null | undefined): string | null => {
  // 如果是特殊城市，統一使用固定的地政代碼
  if (specialCities[countyName]) {
    return specialCities[countyName].code;
  }

  // 其他縣市使用原始的 land_code
  return townLandCode || null;
};

const onTownChange = async (newTown: string) => {
  // 重置地段選擇和資料
  searchParams.section = null;
  selectedSectionCandidate.value = null;
  nlscSections.value = [];

  // 強制重新渲染地段選單
  sectionSelectKey.value++;

  // 使用 nextTick 確保重置生效
  await nextTick();

  // 如果是特殊城市的虛擬town值，跳過處理（地段資料已在縣市變更時載入）
  if (newTown === 'SPECIAL_CITY_AUTO') {
    return;
  }

  // 載入該鄉鎮的地段資料 - 使用 NLSC API
  const county = domicileStore.countyOptions.find(c => c.title === searchParams.county);
  if (county && county.land_code) {
    const town = domicileStore.getTownsForCountyId(county.value).find(t => t.title === newTown);
    if (town) {
      // 獲取適用於 NLSC API 的地政代碼
      const nlscLandCode = getLandCodeForNlsc(searchParams.county, town.land_code);

      if (nlscLandCode) {
        loadingSections.value = true;
        try {
          await domicileStore.loadLandSectionsByLandCodes(county.land_code, nlscLandCode);
          nlscSections.value = domicileStore.landSections.filter(s =>
            s.county_land_code === county.land_code && s.town_land_code === nlscLandCode
          );
          console.log(`載入 ${searchParams.county} ${newTown} 的地段資料 (${nlscLandCode}):`, nlscSections.value.length);
        } catch (error) {
          console.error('Failed to load land sections:', error);
          nlscSections.value = [];
        } finally {
          loadingSections.value = false;
        }
      } else {
        console.warn('No valid land_code found for', searchParams.county, newTown);
      }
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
    // 保存執行查詢時的條件
    lastSearchParams.value = {
      county: searchParams.county,
      town: searchParams.town,
      section: searchParams.section,
      parentLandNumber: searchParams.parentLandNumber,
      childLandNumber: searchParams.childLandNumber
    };

    // 格式化地號
    const formattedLandNumber = formatLandNumber(searchParams.parentLandNumber || '', searchParams.childLandNumber || '');

    // 創建查詢參數副本並設置格式化後的地號
    const queryParams = {
      ...searchParams,
      landNumber: formattedLandNumber
    };

    // 如果是特殊城市，使用實際的通用town名稱而不是虛擬值
    if (specialCities[searchParams.county] && searchParams.town === 'SPECIAL_CITY_AUTO') {
      // 對於特殊城市，在API請求中使用統一的代表性鄉鎮名稱
      // 這樣後端API可以正確處理並使用對應的通用land_code
      const representativeTown = specialCities[searchParams.county].name; // 例如：'新竹市' 或 '嘉義市'
      queryParams.town = representativeTown;

      console.log(`特殊城市查詢：${searchParams.county} 使用代表性鄉鎮名稱: ${representativeTown}`);
    }

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
    searchParams.section = search.section || null;
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

// 完整查詢條件描述 - 使用實際執行查詢時的條件
const landLocationDescription = computed(() => {
  const parts = [];

  // 縣市名稱
  if (lastSearchParams.value.county) {
    parts.push(lastSearchParams.value.county);
  }

  // 鄉鎮市區名稱
  if (lastSearchParams.value.town && lastSearchParams.value.town !== 'SPECIAL_CITY_AUTO') {
    parts.push(lastSearchParams.value.town);
  }

  // 地段名稱（需要從段號轉換為地段名稱）
  if (lastSearchParams.value.section) {
    // 從 sections 中找到對應的地段名稱
    const selectedSection = sections.value.find(section => section.code === lastSearchParams.value.section);
    if (selectedSection) {
      parts.push(selectedSection.name || selectedSection.title);
    } else {
      // 如果找不到，可能是舊資料或直接輸入的段號，嘗試從結果中取得地段名稱
      // 缺名稱時省略地段一段，不退回顯示代碼——否則會出現「標題顯示代碼、卡片顯示名稱」的矛盾畫面
      if (filteredLegacyResults.value.length > 0) {
        const first = filteredLegacyResults.value[0];
        if (first.land_section_name) {
          parts.push(first.land_section_name);
        }
      }
    }
  }

  return parts.join(' ') || '查詢條件';
});

// 完整地號格式 - 使用實際執行查詢時的條件
const completeLandNumber = computed(() => {
  return formatLandNumber(lastSearchParams.value.parentLandNumber || '', lastSearchParams.value.childLandNumber || '');
});

// 地籍登記總面積 - 取自最新案件的farmarea
const totalApprovedArea = computed(() => {
  if (searchResults.value.length === 0) return 0;

  // 只處理歸檔記錄 (統一處理所有舊系統資料來源)
  const legacyRecords = searchResults.value.filter(item =>
    item.source_system === "legacy_farmdata" || item.source_system === "mssql_legacy"
  );

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

// 根據選中年度計算地籍登記面積
const selectedYearTotalApprovedArea = computed(() => {
  if (filteredLegacyResults.value.length === 0 || selectedYearTab.value === undefined) {
    return totalApprovedArea.value; // fallback 到原邏輯
  }

  // 找到選中年度的案件
  const selectedYearRecords = filteredLegacyResults.value.filter(
    item => item.application_year === selectedYearTab.value
  );

  if (selectedYearRecords.length === 0) {
    return 0;
  }

  // 找到該年度中最大的 source_id 記錄
  const sourceIds = selectedYearRecords.map(item => parseInt(String(item.source_id || 0), 10));
  const latestSourceId = Math.max(...sourceIds);
  const latestRecord = selectedYearRecords.find(item => parseInt(String(item.source_id || 0), 10) === latestSourceId);

  return Number(latestRecord?.land_registered_area || latestRecord?.approved_area || '0');
});

// 根據選中年度計算農田水利事業區域
const selectedYearOfficeBoundaries = computed(() => {
  if (filteredLegacyResults.value.length === 0 || selectedYearTab.value === undefined) {
    return allOfficeBoundaries.value; // fallback 到原邏輯
  }

  // 找到選中年度的案件
  const selectedYearRecords = filteredLegacyResults.value.filter(
    item => item.application_year === selectedYearTab.value
  );

  if (selectedYearRecords.length === 0) {
    return [];
  }

  // 取得該年度案件的地段名稱和 land_number
  const targetLandSectionName = selectedYearRecords[0].land_section_name;
  const targetLandNumber = selectedYearRecords[0].land_number;

  // 缺地段名稱的土地不參與比對：名稱為空時兩端相等判斷會成立（null === null），
  // 導致不相干的地段被判定為同一個。實測地號 0878-0000 有 2 筆缺名稱紀錄分屬
  // 南投縣集集鎮與高雄市燕巢區，無此守衛會合併出橫跨兩縣市的錯誤區域清單。
  // 該案件的資料異常已由卡片的 data_format_warning 說明，此處回空即為正確結果。
  if (!targetLandSectionName) {
    return [];
  }

  const boundaries = [];

  // 遍歷所有查詢結果，找到匹配的地段+地號組合且為選中年度的記錄
  for (const result of searchResults.value) {
    if (result.land_section_name === targetLandSectionName &&
        result.land_number === targetLandNumber &&
        result.application_year === selectedYearTab.value &&
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

// 動態查詢說明內容
const queryInstructions = computed(() => {
  switch (queryType.value) {
    case 'general':
      return {
        title: '歷史申請案件查詢說明',
        items: [
          {
            text: '目前只需輸入母地號即可查詢歷史歸檔記錄（地段為選填項目）',
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
            text: '由於提供山坡地資料的API服務已停止更新，本系統無法再取得即時資料，請直接點選下方連結進行查詢：',
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

// 歷史記錄處理 - 已關閉最新案件地段過濾
const filteredLegacyResults = computed(() => {
  if (searchResults.value.length === 0) return [];

  // === 以下是原有的地段過濾邏輯，已註解關閉 ===
  // // 只處理歸檔記錄 (統一處理所有舊系統資料來源)
  // const legacyRecords = searchResults.value.filter(item => item.source_system === "legacy_farmdata" || item.source_system === "mssql_legacy");

  // if (legacyRecords.length === 0) {
  //   return searchResults.value;
  // }

  // // 找出最新案件：最新年度，該年度中最大的 source_id
  // const latestYear = Math.max(...legacyRecords.map(item => item.application_year));
  // const latestYearRecords = legacyRecords.filter(item => item.application_year === latestYear);

  // // 將字串 source_id 轉換為數字進行比較
  // const sourceIds = latestYearRecords.map(item => parseInt(String(item.source_id || 0), 10));
  // const latestSourceId = Math.max(...sourceIds);

  // // 找到具有最大 source_id 的記錄
  // const latestRecord = latestYearRecords.find(item => parseInt(String(item.source_id || 0), 10) === latestSourceId);

  // if (!latestRecord?.land_section) {
  //   return legacyRecords;
  // }

  // // 使用最新記錄的地段號碼來過濾所有歸檔記錄
  // const targetLandSection = latestRecord.land_section;
  // const filteredResults = legacyRecords.filter(item => item.land_section === targetLandSection);

  // return filteredResults;
  // === 地段過濾邏輯結束 ===

  // 直接返回所有搜尋結果，不進行地段過濾
  return searchResults.value;
});

// 按年度分組
const groupedByYear = computed(() => {
  if (filteredLegacyResults.value.length === 0) return [];
  console.log('check第一筆案件的所有欄位:', filteredLegacyResults.value[0]);
  const groups = new Map();
  // 固定的四個設施類型
  const fixedFacilityTypes = ['田間管路', '調蓄設施', '調控設施', '動力設備', '水保署'];

  filteredLegacyResults.value.forEach(item => {
    const year = item.application_year;
    if (!groups.has(year)) {
      groups.set(year, {
        year,
        cases: [],
        totalArea: 0,
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
  });

  // 轉換為陣列並排序（依年度新到舊）；035 起結果以逐案件卡片呈現，不再聚合設施
  return Array.from(groups.values())
    .sort((a, b) => (b as { year: number }).year - (a as { year: number }).year);
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
    '水保署': { icon: 'mdi-office-building', color: 'blue-grey' },
    // '一般設施': { icon: 'mdi-tools', color: 'grey' },
    // '歷史案件': { icon: 'mdi-history', color: 'brown' }
  };

  // 預設值：case_type 可能為「一般設施」或多設施逗號串（非單一固定類型），需回傳有效物件避免 undefined.color
  return iconMap[facilityType] || { icon: 'mdi-tools', color: 'grey' };
};

// 案件狀態中文標籤（對應後端 GrantStatus enum；035 逐案件卡片使用）
const CASE_STATUS_LABELS: Record<string, string> = {
  draft: '草稿',
  submitted: '已結案',
  under_review: '審查中',
  approved: '核准',
  rejected: '駁回',
  withdrawn: '撤回',
  cross_year: '跨年度',
  completed: '線上結案',
  deleted: '已刪除',
  inactive: '歷史案件',
};
const getCaseStatusLabel = (status: string): string => CASE_STATUS_LABELS[status] || status || '—';

// 地段顯示值：一律用中文名稱，缺名稱時顯示佔位符號
// 刻意不退回顯示 land_section（代碼）——缺名稱屬錯誤資料，顯示代碼會讓錯誤資料看起來正常；
// 該案件會由後端的 data_format_warning 亮起警告說明原因
const getLandSectionDisplay = (caseItem: GrantCaseItem): string => caseItem.land_section_name || '—';

// 案件狀態顏色（Vuetify color）
const getCaseStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    approved: 'success',
    under_review: 'info',
    submitted: 'teal',
    completed: 'teal',
    cross_year: 'purple',
    draft: 'grey',
    inactive: 'grey',
    rejected: 'error',
    withdrawn: 'grey',
    deleted: 'grey',
  };
  return colorMap[status] || 'grey';
};

// 設施顏色十六進制值
const getFacilityColorHex = (facilityType: string) => {
  const colorMap: Record<string, string> = {
    '田間管路': '#4CAF50',  // green
    '調蓄設施': '#FF9800',  // orange
    '調控設施': '#9C27B0',  // purple
    '動力設備': '#F44336',  // red
    '水保署': '#607D8B'     // blue-grey
  };

  return colorMap[facilityType] || '#757575'; // 預設為灰色
};

// 計算過濾後結果對應的 office_boundaries
const allOfficeBoundaries = computed(() => {
  // 只取與過濾後結果相同 地段名稱 + land_number 組合的 office_boundaries
  if (filteredLegacyResults.value.length === 0) return [];

  // 取得過濾後結果的地段名稱 (所有記錄應該有相同的地段)
  const targetLandSectionName = filteredLegacyResults.value[0].land_section_name;
  const targetLandNumber = filteredLegacyResults.value[0].land_number;

  // 缺地段名稱的土地不參與比對，理由同 selectedYearOfficeBoundaries（空值兩端相等會誤配）
  if (!targetLandSectionName) {
    return [];
  }

  const boundaries = [];

  // 遍歷所有查詢結果，找到匹配的地段+地號組合
  for (const result of searchResults.value) {
    if (result.land_section_name === targetLandSectionName &&
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

  // 檢查 NLSC API 健康狀態
  try {
    const healthStatus = await checkNlscApiHealth();
    apiStatus.value.isOnline = healthStatus.nlsc_api_status === 'online';
    apiStatus.value.lastChecked = new Date();
    console.log('NLSC API health status:', healthStatus);
  } catch (error) {
    console.error('Failed to check NLSC API health:', error);
    apiStatus.value.isOnline = false;
    apiStatus.value.lastChecked = new Date();
  }

  // 處理來自 step2.vue 的 URL 參數並預填表單
  const urlParams = route.query;
  if (urlParams.county || urlParams.town || urlParams.section || urlParams.parentLandNumber) {
    console.log('Processing URL parameters:', urlParams);

    // 設定查詢類型為一般區域查詢
    queryType.value = 'general';

    // 預填縣市
    if (urlParams.county) {
      const countyName = urlParams.county as string;
      const county = domicileStore.countyOptions.find(c => c.title === countyName);
      if (county) {
        searchParams.county = county.title;
        // 載入鄉鎮資料
        await domicileStore.loadTownsByCountyId(county.value);
      }
    }

    // 預填鄉鎮
    if (urlParams.town && searchParams.county) {
      const townName = urlParams.town as string;
      const county = domicileStore.countyOptions.find(c => c.title === searchParams.county);
      if (county) {
        const towns = domicileStore.getTownsForCountyId(county.value);
        const town = towns.find(t => t.title === townName);
        if (town) {
          searchParams.town = town.title;
          // 載入地段資料
          // await domicileStore.loadLandSectionsByTownId(town.value);
        }
      }
    }

    // 處理特殊縣市：如果有 section 但沒有 town，檢查是否為特殊縣市
    if (urlParams.section && !urlParams.town && searchParams.county) {
      if (specialCities[searchParams.county]) {
        // 為特殊縣市設定虛擬 town 值，以便後續地段載入邏輯正常執行
        searchParams.town = 'SPECIAL_CITY_AUTO';
        console.log(`檢測到特殊縣市 ${searchParams.county}，設定虛擬鄉鎮值`);
      }
    }

    // 預填地段 - 觸發候選清單載入（供 v-combobox 下拉使用），並直接以名稱賦值
    if (urlParams.section && (searchParams.town || specialCities[searchParams.county])) {
      try {
        if (specialCities[searchParams.county] && searchParams.town === 'SPECIAL_CITY_AUTO') {
          // 特殊縣市：觸發縣市變更來載入地段資料
          await onCountyChange(searchParams.county);
        } else if (searchParams.town) {
          // 一般縣市：觸發鄉鎮變更來載入地段資料
          await onTownChange(searchParams.town);
        }

        searchParams.section = urlParams.section as string;
      } catch (error) {
        console.error('❌ 載入地段資料失敗:', error);
      }
    }

    // 預填地號
    if (urlParams.parentLandNumber) {
      searchParams.parentLandNumber = urlParams.parentLandNumber as string;
    }

    if (urlParams.childLandNumber) {
      searchParams.childLandNumber = urlParams.childLandNumber as string;
    }

    console.log('URL parameters processed, form pre-filled:', searchParams);

    // 如果有母地號，自動執行查詢
    if (searchParams.parentLandNumber) {
      console.log('Auto-executing search with pre-filled data...');
      // 使用 nextTick 確保 DOM 更新完成後再執行查詢
      await new Promise(resolve => setTimeout(resolve, 100)); // 短暫延遲確保表單渲染完成
      try {
        await searchLand();
        console.log('Auto-search completed successfully');
      } catch (error) {
        console.error('Auto-search failed:', error);
      }
    }
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

.border-s-4 {
  border-left-width: 4px !important;
  border-left-style: solid !important;
}

.border-primary {
  border-left-color: #3ea0a3 !important; /* 與主題色一致 */
}
</style>
