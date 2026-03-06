<template>
  <v-container
    fluid
    class="material-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <v-row justify="center">
      <v-col cols="12">
        <div class="section-wrapper">
          <!-- 統計報表主卡片 -->
          <v-card class="section-card statistics-main-card">
            <v-card-text class="pa-0">
              <v-row no-gutters>
                <!-- 左側導航區 -->
                <v-col cols="12" md="2" class="navigation-col">
                  <div class="navigation-header">
                    <div class="text-grey-darken-2 font-weight-bold px-3 pt-4 pb-2">
                      統計報表類別
                    </div>
                  </div>

                  <v-list density="compact" class="pa-3" nav>
                    <v-list-item
                      v-for="(section, index) in reportSections"
                      :key="index"
                      :value="section.id"
                      :active="activeSection === section.id"
                      color="#3ea0a3"
                      class="mb-2 nav-section-item"
                      rounded="lg"
                      @click="navigateToSection(section.id)"
                    >
                      <template #prepend>
                        <v-avatar color="#3ea0a3" size="30" rounded="lg">
                          <span class="text-body-2 font-weight-bold">{{ section.badge }}</span>
                        </v-avatar>
                      </template>
                      <v-list-item-title class="section-title">
                        {{ section.title }}
                      </v-list-item-title>
                      <template #append>
                        <v-chip size="x-small" color="grey-lighten-3" class="count-chip">
                          {{ section.count }}
                        </v-chip>
                      </template>
                    </v-list-item>
                  </v-list>
                </v-col>

                <!-- 右側內容區 -->
                <v-col cols="12" md="10" class="content-col pa-6">
                  <!-- A. 執行進度相關報表 -->
                  <div v-show="activeSection === 'progress'" class="report-section">
                    <div class="section-header mb-4">
                      <div class="d-flex align-items-center mb-3">
                        <v-avatar color="#3ea0a3" size="44" rounded="lg" class="mr-4">
                          <span class="text-h6 font-weight-bold">A</span>
                        </v-avatar>
                        <h2
                          class="d-flex align-center text-h6 font-weight-bold"
                          style="color: #2d8c8f"
                        >
                          執行進度相關報表
                        </h2>
                      </div>
                      <v-divider class="border-opacity-50" />
                    </div>

                    <!-- A01 各管理處執行進度 -->
                    <v-card
                      class="report-item-card mb-3"
                      flat
                      rounded="lg"
                    >
                      <v-card-text class="pa-4">
                        <v-row align="center">
                          <v-col
                            cols="12"
                            md="4"
                          >
                            <div class="d-flex align-items-start">
                              <v-avatar
                                color="#3ea0a3"
                                size="52"
                                rounded="lg"
                              >
                                <span class="text-body-1 font-weight-bold">A01</span>
                              </v-avatar>
                              <div class="ms-3">
                                <div class="report-title-text">
                                  各管理處執行進度
                                </div>
                                <div class="report-category-tags mt-1">
                                  <v-chip
                                    size="x-small"
                                    color="teal"
                                    variant="tonal"
                                    class="me-1"
                                  >
                                    年報
                                  </v-chip>
                                  <v-chip
                                    size="x-small"
                                    color="blue-grey"
                                    variant="tonal"
                                  >
                                    執行進度
                                  </v-chip>
                                </div>
                              </div>
                            </div>
                          </v-col>

                          <v-col
                            cols="12"
                            md="3"
                          >
                            <v-select
                              v-model="a01Filters.office"
                              :items="officeOptions"
                              label="管理處"
                              variant="outlined"
                              density="compact"
                              hide-details
                              color="#3ea0a3"
                            />
                          </v-col>

                          <v-col
                            cols="12"
                            md="3"
                          >
                            <div class="d-flex align-center">
                              <v-select
                                v-model="a01Filters.year"
                                :items="yearOptions"
                                label="統計年度"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="flex-grow-1"
                                :disabled="a01Filters.currentYear"
                                color="#3ea0a3"
                              />
                              <v-checkbox
                                v-model="a01Filters.currentYear"
                                label="本年度"
                                density="compact"
                                hide-details
                                class="ml-2 flex-shrink-0"
                                color="#3ea0a3"
                              />
                            </div>
                          </v-col>

                          <v-col
                            cols="12"
                            md="2"
                            class="text-right pr-6"
                          >
                            <v-btn
                              color="#3ea0a3"
                              variant="flat"
                              prepend-icon="mdi-file-download-outline"
                              size="small"
                              block
                              rounded="lg"
                              @click="downloadReport('A01')"
                            >
                              下載
                            </v-btn>
                          </v-col>
                        </v-row>
                      </v-card-text>
                    </v-card>

                    <!-- A02 各縣市鄉鎮區統計表 -->
                    <v-card
                      class="report-item-card mb-3"
                      flat
                      rounded="lg"
                    >
                      <v-card-text class="pa-4">
                        <v-row align="center">
                          <v-col
                            cols="12"
                            md="4"
                          >
                            <div class="d-flex align-items-start">
                              <v-avatar
                                color="#3ea0a3"
                                size="52"
                                rounded="lg"
                              >
                                <span class="text-body-1 font-weight-bold">A02</span>
                              </v-avatar>
                              <div class="ms-3">
                                <div class="report-title-text">
                                  各縣市鄉鎮區統計
                                </div>
                                <div class="report-category-tags mt-1">
                                  <v-chip
                                    size="x-small"
                                    color="teal"
                                    variant="tonal"
                                    class="me-1"
                                  >
                                    年報
                                  </v-chip>
                                  <v-chip
                                    size="x-small"
                                    color="blue-grey"
                                    variant="tonal"
                                  >
                                    縣市鄉鎮
                                  </v-chip>
                                </div>
                              </div>
                            </div>
                          </v-col>

                          <v-col
                            cols="12"
                            md="3"
                          >
                            <v-select
                              v-model="a02Filters.office"
                              :items="officeOptions"
                              label="管理處"
                              variant="outlined"
                              density="compact"
                              hide-details
                              color="#3ea0a3"
                            />
                          </v-col>

                          <v-col
                            cols="12"
                            md="3"
                          >
                            <div class="d-flex align-center">
                              <v-select
                                v-model="a02Filters.year"
                                :items="yearOptions"
                                label="統計年度"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="flex-grow-1"
                                :disabled="a02Filters.currentYear"
                                color="#3ea0a3"
                              />
                              <v-checkbox
                                v-model="a02Filters.currentYear"
                                label="本年度"
                                density="compact"
                                hide-details
                                class="ml-2 flex-shrink-0"
                                color="#3ea0a3"
                              />
                            </div>
                          </v-col>

                          <v-col
                            cols="12"
                            md="2"
                            class="text-right pr-6"
                          >
                            <v-btn
                              color="#3ea0a3"
                              variant="flat"
                              prepend-icon="mdi-file-download-outline"
                              size="small"
                              block
                              rounded="lg"
                              @click="downloadReport('A02')"
                            >
                              下載
                            </v-btn>
                          </v-col>
                        </v-row>
                      </v-card-text>
                    </v-card>

                    <!-- A03 各管理處統計表 -->
                    <v-card
                      class="report-item-card mb-3"
                      flat
                      rounded="lg"
                    >
                      <v-card-text class="pa-4">
                        <v-row align="center">
                          <v-col
                            cols="12"
                            md="4"
                          >
                            <div class="d-flex align-items-start">
                              <v-avatar
                                color="#3ea0a3"
                                size="52"
                                rounded="lg"
                              >
                                <span class="text-body-1 font-weight-bold">A03</span>
                              </v-avatar>
                              <div class="ms-3">
                                <div class="report-title-text">
                                  各管理處統計
                                </div>
                                <div class="report-category-tags mt-1">
                                  <v-chip
                                    size="x-small"
                                    color="teal"
                                    variant="tonal"
                                    class="me-1"
                                  >
                                    年報
                                  </v-chip>
                                  <v-chip
                                    size="x-small"
                                    color="blue-grey"
                                    variant="tonal"
                                  >
                                    管理處
                                  </v-chip>
                                </div>
                              </div>
                            </div>
                          </v-col>

                          <v-col
                            cols="12"
                            md="3"
                          >
                            <v-select
                              v-model="a03Filters.office"
                              :items="officeOptions"
                              label="管理處"
                              variant="outlined"
                              density="compact"
                              hide-details
                              color="#3ea0a3"
                            />
                          </v-col>

                          <v-col
                            cols="12"
                            md="3"
                          >
                            <div class="d-flex align-center">
                              <v-select
                                v-model="a03Filters.year"
                                :items="yearOptions"
                                label="統計年度"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="flex-grow-1"
                                :disabled="a03Filters.currentYear"
                                color="#3ea0a3"
                              />
                              <v-checkbox
                                v-model="a03Filters.currentYear"
                                label="本年度"
                                density="compact"
                                hide-details
                                class="ml-2 flex-shrink-0"
                                color="#3ea0a3"
                              />
                            </div>
                          </v-col>

                          <v-col
                            cols="12"
                            md="2"
                            class="text-right pr-6"
                          >
                            <v-btn
                              color="#3ea0a3"
                              variant="flat"
                              prepend-icon="mdi-file-download-outline"
                              size="small"
                              block
                              rounded="lg"
                              @click="downloadReport('A03')"
                            >
                              下載
                            </v-btn>
                          </v-col>
                        </v-row>
                      </v-card-text>
                    </v-card>

                    <!-- A04 歷年各縣市鄉鎮區統計 -->
                    <v-card
                      class="report-item-card mb-3"
                      flat
                      rounded="lg"
                    >
                      <v-card-text class="pa-4">
                        <v-row align="center">
                          <v-col
                            cols="12"
                            md="4"
                          >
                            <div class="d-flex align-items-start">
                              <v-avatar
                                color="#3ea0a3"
                                size="52"
                                rounded="lg"
                              >
                                <span class="text-body-1 font-weight-bold">A04</span>
                              </v-avatar>
                              <div class="ms-3">
                                <div class="report-title-text">
                                  歷年各縣市鄉鎮區統計
                                </div>
                                <div class="report-category-tags mt-1">
                                  <v-chip
                                    size="x-small"
                                    color="indigo"
                                    variant="tonal"
                                    class="me-1"
                                  >
                                    歷年趨勢
                                  </v-chip>
                                  <v-chip
                                    size="x-small"
                                    color="blue-grey"
                                    variant="tonal"
                                  >
                                    縣市鄉鎮
                                  </v-chip>
                                </div>
                              </div>
                            </div>
                          </v-col>

                          <v-col
                            cols="12"
                            md="2"
                          >
                            <v-select
                              v-model="a04Filters.office"
                              :items="officeOptions"
                              label="管理處"
                              variant="outlined"
                              density="compact"
                              hide-details
                              color="#3ea0a3"
                            />
                          </v-col>

                          <v-col
                            cols="12"
                            md="4"
                          >
                            <div class="d-flex align-center">
                              <v-select
                                v-model="a04Filters.startYear"
                                :items="yearOptions"
                                label="起始年度"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="flex-grow-1 me-2"
                                color="#3ea0a3"
                              />
                              <v-select
                                v-model="a04Filters.year"
                                :items="yearOptions"
                                label="結束年度"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="flex-grow-1"
                                :disabled="a04Filters.currentYear"
                                color="#3ea0a3"
                              />
                              <v-checkbox
                                v-model="a04Filters.currentYear"
                                label="本年度"
                                density="compact"
                                hide-details
                                class="ml-2 flex-shrink-0"
                                color="#3ea0a3"
                              />
                            </div>
                          </v-col>

                          <v-col
                            cols="12"
                            md="2"
                            class="text-right pr-6"
                          >
                            <v-btn
                              color="#3ea0a3"
                              variant="flat"
                              prepend-icon="mdi-file-download-outline"
                              size="small"
                              block
                              rounded="lg"
                              @click="downloadReport('A04')"
                            >
                              下載
                            </v-btn>
                          </v-col>
                        </v-row>
                      </v-card-text>
                    </v-card>

                    <!-- A05 歷年各管理處統計 -->
                    <v-card
                      class="report-item-card mb-3"
                      flat
                      rounded="lg"
                    >
                      <v-card-text class="pa-4">
                        <v-row align="center">
                          <v-col
                            cols="12"
                            md="4"
                          >
                            <div class="d-flex align-items-start">
                              <v-avatar
                                color="#3ea0a3"
                                size="52"
                                rounded="lg"
                              >
                                <span class="text-body-1 font-weight-bold">A05</span>
                              </v-avatar>
                              <div class="ms-3">
                                <div class="report-title-text">
                                  歷年各管理處統計
                                </div>
                                <div class="report-category-tags mt-1">
                                  <v-chip
                                    size="x-small"
                                    color="indigo"
                                    variant="tonal"
                                    class="me-1"
                                  >
                                    歷年趨勢
                                  </v-chip>
                                  <v-chip
                                    size="x-small"
                                    color="blue-grey"
                                    variant="tonal"
                                  >
                                    管理處
                                  </v-chip>
                                </div>
                              </div>
                            </div>
                          </v-col>

                          <v-col
                            cols="12"
                            md="2"
                          >
                            <v-select
                              v-model="a05Filters.office"
                              :items="officeOptions"
                              label="管理處"
                              variant="outlined"
                              density="compact"
                              hide-details
                              color="#3ea0a3"
                            />
                          </v-col>

                          <v-col
                            cols="12"
                            md="4"
                          >
                            <div class="d-flex align-center">
                              <v-select
                                v-model="a05Filters.startYear"
                                :items="yearOptions"
                                label="起始年度"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="flex-grow-1 me-2"
                                color="#3ea0a3"
                              />
                              <v-select
                                v-model="a05Filters.year"
                                :items="yearOptions"
                                label="結束年度"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="flex-grow-1"
                                :disabled="a05Filters.currentYear"
                                color="#3ea0a3"
                              />
                              <v-checkbox
                                v-model="a05Filters.currentYear"
                                label="本年度"
                                density="compact"
                                hide-details
                                class="ml-2 flex-shrink-0"
                                color="#3ea0a3"
                              />
                            </div>
                          </v-col>

                          <v-col
                            cols="12"
                            md="2"
                            class="text-right pr-6"
                          >
                            <v-btn
                              color="#3ea0a3"
                              variant="flat"
                              prepend-icon="mdi-file-download-outline"
                              size="small"
                              block
                              rounded="lg"
                              @click="downloadReport('A05')"
                            >
                              下載
                            </v-btn>
                          </v-col>
                        </v-row>
                      </v-card-text>
                    </v-card>

                    <!-- A06 各管理處經費統計表 -->
                    <v-card class="report-item-card mb-3" flat rounded="lg">
                      <v-card-text class="pa-4">
                        <v-row align="center">
                          <v-col cols="12" md="4">
                            <div class="d-flex align-items-start">
                              <v-avatar color="#3ea0a3" size="52" rounded="lg">
                                <span class="text-body-1 font-weight-bold">A06</span>
                              </v-avatar>
                              <div class="ms-3">
                                <div class="report-title-text">
                                  各管理處經費統計
                                </div>
                                <div class="report-category-tags mt-1">
                                  <v-chip size="x-small" color="teal" variant="tonal" class="me-1">
                                    年報
                                  </v-chip>
                                  <v-chip size="x-small" color="green" variant="tonal">
                                    補助經費
                                  </v-chip>
                                </div>
                              </div>
                            </div>
                          </v-col>

                          <v-col cols="12" md="3">
                            <v-select
                              v-model="a06Filters.office"
                              :items="officeOptions"
                              label="管理處"
                              variant="outlined"
                              density="compact"
                              hide-details
                              color="#3ea0a3"
                            />
                          </v-col>

                          <v-col cols="12" md="3">
                            <div class="d-flex align-center">
                              <v-select
                                v-model="a06Filters.year"
                                :items="yearOptions"
                                label="統計年度"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="flex-grow-1"
                                :disabled="a06Filters.currentYear"
                                color="#3ea0a3"
                              />
                              <v-checkbox
                                v-model="a06Filters.currentYear"
                                label="本年度"
                                density="compact"
                                hide-details
                                class="ml-2 flex-shrink-0"
                                color="#3ea0a3"
                              />
                            </div>
                          </v-col>

                          <v-col cols="12" md="2" class="text-right">
                            <v-btn
                              color="#3ea0a3"
                              variant="flat"
                              prepend-icon="mdi-file-download-outline"
                              size="small"
                              block
                              rounded="lg"
                              @click="downloadReport('A06')"
                            >
                              下載
                            </v-btn>
                          </v-col>
                        </v-row>
                      </v-card-text>
                    </v-card>

                    <!-- A07 原民區域統計 -->
                    <v-card class="report-item-card mb-3" flat rounded="lg">
                      <v-card-text class="pa-4">
                        <v-row align="center">
                          <v-col cols="12" md="4">
                            <div class="d-flex align-items-start">
                              <v-avatar color="#3ea0a3" size="52" rounded="lg">
                                <span class="text-body-1 font-weight-bold">A07</span>
                              </v-avatar>
                              <div class="ms-3">
                                <div class="report-title-text">
                                  原民區域統計
                                </div>
                                <div class="report-category-tags mt-1">
                                  <v-chip size="x-small" color="teal" variant="tonal" class="me-1">
                                    年報
                                  </v-chip>
                                  <v-chip size="x-small" color="orange" variant="tonal">
                                    原民區域
                                  </v-chip>
                                </div>
                              </div>
                            </div>
                          </v-col>

                          <v-spacer />

                          <v-col cols="12" md="3">
                            <div class="d-flex align-center">
                              <v-select
                                v-model="a07Filters.year"
                                :items="yearOptions"
                                label="統計年度"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="flex-grow-1"
                                :disabled="a07Filters.currentYear"
                                color="#3ea0a3"
                              />
                              <v-checkbox
                                v-model="a07Filters.currentYear"
                                label="本年度"
                                density="compact"
                                hide-details
                                class="ml-2 flex-shrink-0"
                                color="#3ea0a3"
                              />
                            </div>
                          </v-col>

                          <v-col cols="12" md="2" class="text-right">
                            <v-btn
                              color="#3ea0a3"
                              variant="flat"
                              prepend-icon="mdi-file-download-outline"
                              size="small"
                              block
                              rounded="lg"
                              @click="downloadReport('A07')"
                            >
                              下載
                            </v-btn>
                          </v-col>
                        </v-row>
                      </v-card-text>
                    </v-card>
                    <!-- A08 歷年原民區域統計 -->
                    <v-card class="report-item-card mb-3" flat rounded="lg">
                      <v-card-text class="pa-4">
                        <v-row align="center">
                          <v-col cols="12" md="4">
                            <div class="d-flex align-items-start">
                              <v-avatar color="#3ea0a3" size="52" rounded="lg">
                                <span class="text-body-1 font-weight-bold">A08</span>
                              </v-avatar>
                              <div class="ms-3">
                                <div class="report-title-text">
                                  歷年原民區域統計
                                </div>
                                <div class="report-category-tags mt-1">
                                  <v-chip size="x-small" color="indigo" variant="tonal" class="me-1">
                                    歷年趨勢
                                  </v-chip>
                                  <v-chip size="x-small" color="orange" variant="tonal">
                                    原民區域
                                  </v-chip>
                                </div>
                              </div>
                            </div>
                          </v-col>

                          <v-col cols="12" md="4">
                            <div class="d-flex align-center">
                              <v-select
                                v-model="a08Filters.startYear"
                                :items="yearOptions"
                                label="起始年度"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="flex-grow-1 me-2"
                                color="#3ea0a3"
                              />
                              <v-select
                                v-model="a08Filters.year"
                                :items="yearOptions"
                                label="結束年度"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="flex-grow-1"
                                :disabled="a08Filters.currentYear"
                                color="#3ea0a3"
                              />
                              <v-checkbox
                                v-model="a08Filters.currentYear"
                                label="本年度"
                                density="compact"
                                hide-details
                                class="ml-2 flex-shrink-0"
                                color="#3ea0a3"
                              />
                            </div>
                          </v-col>

                          <v-col cols="12" md="2" class="text-right pr-6">
                            <v-btn
                              color="#3ea0a3"
                              variant="flat"
                              prepend-icon="mdi-file-download-outline"
                              size="small"
                              block
                              rounded="lg"
                              @click="downloadReport('A08')"
                            >
                              下載
                            </v-btn>
                          </v-col>
                        </v-row>
                      </v-card-text>
                    </v-card>

                    <!-- A09 各縣市事業區域內外推動成果統計 -->
                    <v-card class="report-item-card mb-3" flat rounded="lg">
                      <v-card-text class="pa-4">
                        <v-row align="center">
                          <v-col cols="12" md="4">
                            <div class="d-flex align-items-start">
                              <v-avatar color="#3ea0a3" size="52" rounded="lg">
                                <span class="text-body-1 font-weight-bold">A09</span>
                              </v-avatar>
                              <div class="ms-3">
                                <div class="report-title-text">
                                  各縣市事業區域內外統計
                                </div>
                                <div class="report-category-tags mt-1">
                                  <v-chip size="x-small" color="teal" variant="tonal" class="me-1">
                                    年報
                                  </v-chip>
                                  <v-chip size="x-small" color="blue-grey" variant="tonal">
                                    事業區域
                                  </v-chip>
                                </div>
                              </div>
                            </div>
                          </v-col>

                          <v-spacer />

                          <v-col cols="12" md="3">
                            <div class="d-flex align-center">
                              <v-select
                                v-model="a09Filters.year"
                                :items="yearOptions"
                                label="統計年度"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="flex-grow-1"
                                :disabled="a09Filters.currentYear"
                                color="#3ea0a3"
                              />
                              <v-checkbox
                                v-model="a09Filters.currentYear"
                                label="本年度"
                                density="compact"
                                hide-details
                                class="ml-2 flex-shrink-0"
                                color="#3ea0a3"
                              />
                            </div>
                          </v-col>

                          <v-col cols="12" md="2" class="text-right">
                            <v-btn
                              color="#3ea0a3"
                              variant="flat"
                              prepend-icon="mdi-file-download-outline"
                              size="small"
                              block
                              rounded="lg"
                              @click="downloadReport('A09')"
                            >
                              下載
                            </v-btn>
                          </v-col>
                        </v-row>
                      </v-card-text>
                    </v-card>

                    <!-- A10 各管理處事業區域內外推動成果統計 -->
                    <v-card class="report-item-card mb-3" flat rounded="lg">
                      <v-card-text class="pa-4">
                        <v-row align="center">
                          <v-col cols="12" md="4">
                            <div class="d-flex align-items-start">
                              <v-avatar color="#3ea0a3" size="52" rounded="lg">
                                <span class="text-body-1 font-weight-bold">A10</span>
                              </v-avatar>
                              <div class="ms-3">
                                <div class="report-title-text">
                                  各管理處事業區域內外統計
                                </div>
                                <div class="report-category-tags mt-1">
                                  <v-chip size="x-small" color="teal" variant="tonal" class="me-1">
                                    年報
                                  </v-chip>
                                  <v-chip size="x-small" color="blue-grey" variant="tonal">
                                    事業區域
                                  </v-chip>
                                </div>
                              </div>
                            </div>
                          </v-col>

                          <v-spacer />

                          <v-col cols="12" md="3">
                            <div class="d-flex align-center">
                              <v-select
                                v-model="a10Filters.year"
                                :items="yearOptions"
                                label="統計年度"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="flex-grow-1"
                                :disabled="a10Filters.currentYear"
                                color="#3ea0a3"
                              />
                              <v-checkbox
                                v-model="a10Filters.currentYear"
                                label="本年度"
                                density="compact"
                                hide-details
                                class="ml-2 flex-shrink-0"
                                color="#3ea0a3"
                              />
                            </div>
                          </v-col>

                          <v-col cols="12" md="2" class="text-right">
                            <v-btn
                              color="#3ea0a3"
                              variant="flat"
                              prepend-icon="mdi-file-download-outline"
                              size="small"
                              block
                              rounded="lg"
                              @click="downloadReport('A10')"
                            >
                              下載
                            </v-btn>
                          </v-col>
                        </v-row>
                      </v-card-text>
                    </v-card>
                  </div>

                  <!-- B. 推動成果統計表 -->
                  <div v-show="activeSection === 'achievement'" class="report-section">
                    <div class="section-header mb-4">
                      <div class="d-flex align-items-center mb-3">
                        <v-avatar color="#3ea0a3" size="44" rounded="lg" class="mr-4">
                          <span class="text-h6 font-weight-bold">B</span>
                        </v-avatar>
                        <h2 class="d-flex align-center text-h6 font-weight-bold mb-0" style="color: #2d8c8f">
                          推動成果統計報表
                        </h2>
                      </div>
                      <v-divider class="border-opacity-50" />
                    </div>

                    <!-- B03 各縣市鄉鎮區各類補助項目統計 -->
                    <v-card
                      class="report-item-card mb-3"
                      flat
                      rounded="lg"
                    >
                      <v-card-text class="pa-4">
                        <v-row align="center">
                          <v-col
                            cols="12"
                            md="4"
                          >
                            <div class="d-flex align-items-start">
                              <v-avatar
                                color="#3ea0a3"
                                size="52"
                                rounded="lg"
                              >
                                <span class="text-body-1 font-weight-bold">B03</span>
                              </v-avatar>
                              <div class="ms-3">
                                <div class="report-title-text">
                                  各縣市鄉鎮區各類補助項目統計
                                </div>
                                <div class="report-category-tags mt-1">
                                  <v-chip
                                    size="x-small"
                                    color="teal"
                                    variant="tonal"
                                    class="me-1"
                                  >
                                    年報
                                  </v-chip>
                                  <v-chip
                                    size="x-small"
                                    color="blue-grey"
                                    variant="tonal"
                                  >
                                    補助項目
                                  </v-chip>
                                </div>
                              </div>
                            </div>
                          </v-col>

                          <v-col
                            cols="12"
                            md="3"
                          >
                            <v-select
                              v-model="b03Filters.office"
                              :items="officeOptions"
                              label="管理處"
                              variant="outlined"
                              density="compact"
                              hide-details
                              color="#3ea0a3"
                            />
                          </v-col>

                          <v-col
                            cols="12"
                            md="3"
                          >
                            <div class="d-flex align-center">
                              <v-select
                                v-model="b03Filters.year"
                                :items="yearOptions"
                                label="統計年度"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="flex-grow-1"
                                :disabled="b03Filters.currentYear"
                                color="#3ea0a3"
                              />
                              <v-checkbox
                                v-model="b03Filters.currentYear"
                                label="本年度"
                                density="compact"
                                hide-details
                                class="ml-2 flex-shrink-0"
                                color="#3ea0a3"
                              />
                            </div>
                          </v-col>

                          <v-col
                            cols="12"
                            md="2"
                            class="text-right pr-6"
                          >
                            <v-btn
                              color="#3ea0a3"
                              variant="flat"
                              prepend-icon="mdi-file-download-outline"
                              size="small"
                              block
                              rounded="lg"
                              @click="downloadReport('B03')"
                            >
                              下載
                            </v-btn>
                          </v-col>
                        </v-row>
                      </v-card-text>
                    </v-card>
                  </div>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>

    <!-- 下載進度對話框 -->
    <v-dialog
      v-model="downloadDialog"
      max-width="500px"
      :persistent="downloading"
    >
      <v-card rounded="lg">
        <v-card-title class="text-h6 pa-6 pb-2">
          <v-icon
            :icon="downloading ? 'mdi-download' : (downloadProgress === 100 ? 'mdi-check-circle' : 'mdi-alert-circle')"
            :color="downloading ? '#3ea0a3' : (downloadProgress === 100 ? 'success' : 'error')"
            class="mr-2"
          />
          {{ downloading ? '報表下載中' : (downloadProgress === 100 ? '下載完成' : '下載失敗') }}
        </v-card-title>

        <v-card-text class="pa-6">
          <div class="text-center">
            <v-progress-circular
              v-if="downloading || downloadProgress === 100"
              :model-value="downloadProgress"
              size="64"
              width="4"
              :color="downloadProgress === 100 ? 'success' : '#3ea0a3'"
              class="mb-4"
            >
              {{ Math.round(downloadProgress) }}%
            </v-progress-circular>

            <v-icon
              v-else
              icon="mdi-alert-circle-outline"
              color="error"
              size="64"
              class="mb-4"
            />

            <div class="text-body-1 mb-2">
              {{ downloadStatus }}
            </div>

            <div
              v-if="downloading && currentReportCode"
              class="text-caption text-medium-emphasis"
            >
              正在準備 {{ currentReportCode }} 報表檔案...
            </div>
          </div>
        </v-card-text>

        <!-- 操作按鈕 -->
        <v-card-actions
          v-if="!downloading"
          class="pa-6 pt-0"
        >
          <v-spacer />
          <v-btn
            v-if="downloadProgress !== 100"
            color="#3ea0a3"
            variant="flat"
            @click="retryDownload"
          >
            重新下載
          </v-btn>
          <v-btn
            color="grey-darken-1"
            variant="text"
            @click="downloadDialog = false"
          >
            關閉
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { officeService, type Office } from '@/services/officelistService'
import { statisticsService } from '@/services/statisticsService'

const route = useRoute()
const router = useRouter()

// ==================== 導航區段定義 ====================
const reportSections = [
  {
    id: 'progress',
    badge: 'A',
    title: '執行進度相關報表',
    icon: 'mdi-chart-line',
    count: 8
  },
  {
    id: 'achievement',
    badge: 'B',
    title: '推動成果統計報表',
    icon: 'mdi-chart-bar',
    count: 1
  }
]

// 當前活動區段 (從 URL query 讀取或預設為 progress)
const activeSection = ref<string>('progress')

// ==================== 篩選條件定義 ====================

// A01 篩選條件
const a01Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true
})

// A02 / A03 篩選條件（單一年度）
const a02Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true
})
const a03Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true
})

// A04 / A05 篩選條件（年度區間）
const a04Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true,
  startYear: 97
})
const a05Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true,
  startYear: 97
})

// A06 篩選條件
const a06Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true
})

// A07 篩選條件
const a07Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true
})

// A08 篩選條件（年度區間）
const a08Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true,
  startYear: 97
})

// A09 篩選條件
const a09Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true
})

// A10 篩選條件
const a10Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true
})

// B01-1 篩選條件
const b01_1Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true
})

// B01-2 (現為 B01-2) 篩選條件
const b01_2Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true
})

// B01-3 (現為 B01-3) 篩選條件
const b01_3Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true
})

// B01-4 (現為 B01-4) 篩選條件
const b01_4Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true
})

// B03 篩選條件
const b03Filters = ref({
  office: null as number | null,
  year: new Date().getFullYear() - 1911,
  currentYear: true
})

// ==================== 下拉選單選項 ====================

// 允許的管理處 ID 清單 (1-19 和 23)
const ALLOWED_OFFICE_IDS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 23]

// 管理處資料
const offices = ref<Office[]>([])
const isLoadingOffices = ref(false)

// 管理處選項（從 API 載入並過濾）
const officeOptions = computed(() => {
  const filteredOffices = offices.value
    .filter(office => ALLOWED_OFFICE_IDS.includes(office.id))
    .map(office => ({
      title: office.name,
      value: office.id
    }))

  return [
    { title: '全部', value: null },
    ...filteredOffices
  ]
})

// 年度選項 (民國年)
const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear() - 1911
  const years = []
  for (let i = currentYear; i >= 97; i--) {
    years.push(i)
  }
  return years
})

// ==================== Watch 監聽 ====================

// 監聽「本年度」checkbox，自動更新年度
watch(() => a01Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) {
    a01Filters.value.year = new Date().getFullYear() - 1911
  }
})

watch(() => a02Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) a02Filters.value.year = new Date().getFullYear() - 1911
})
watch(() => a03Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) a03Filters.value.year = new Date().getFullYear() - 1911
})
watch(() => a04Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) a04Filters.value.year = new Date().getFullYear() - 1911
})
watch(() => a05Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) a05Filters.value.year = new Date().getFullYear() - 1911
})

watch(() => a06Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) {
    a06Filters.value.year = new Date().getFullYear() - 1911
  }
})

watch(() => a07Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) {
    a07Filters.value.year = new Date().getFullYear() - 1911
  }
})

watch(() => a08Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) {
    a08Filters.value.year = new Date().getFullYear() - 1911
  }
})

watch(() => a09Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) {
    a09Filters.value.year = new Date().getFullYear() - 1911
  }
})

watch(() => a10Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) {
    a10Filters.value.year = new Date().getFullYear() - 1911
  }
})

watch(() => b01_1Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) {
    b01_1Filters.value.year = new Date().getFullYear() - 1911
  }
})

watch(() => b01_2Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) {
    b01_2Filters.value.year = new Date().getFullYear() - 1911
  }
})

watch(() => b01_3Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) {
    b01_3Filters.value.year = new Date().getFullYear() - 1911
  }
})

watch(() => b01_4Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) {
    b01_4Filters.value.year = new Date().getFullYear() - 1911
  }
})

watch(() => b03Filters.value.currentYear, (isCurrentYear) => {
  if (isCurrentYear) {
    b03Filters.value.year = new Date().getFullYear() - 1911
  }
})

// 監聽 URL query 參數變化
watch(() => route.query.section, (newSection) => {
  if (newSection && typeof newSection === 'string') {
    activeSection.value = newSection
  }
}, { immediate: true })

// ==================== 方法 ====================

/**
 * 切換區段並更新 URL
 */
const navigateToSection = (sectionId: string) => {
  activeSection.value = sectionId
  router.push({ query: { section: sectionId } })
}

// 下載狀態
const isDownloading = ref(false)
const downloadError = ref<string | null>(null)

// 下載進度對話框相關變數
const downloading = ref(false)
const downloadDialog = ref(false)
const downloadProgress = ref(0)
const downloadStatus = ref('')
const currentReportCode = ref<string | null>(null)

/**
 * 下載報表
 * @param reportCode 報表代碼 (A01, A03, B01-1, etc.)
 */
const downloadReport = async (reportCode: string) => {
  const filters = getFiltersForReport(reportCode)

  // 設定當前下載報表和開啟對話框
  currentReportCode.value = reportCode
  downloading.value = true
  downloadDialog.value = true
  downloadProgress.value = 0
  downloadStatus.value = '準備下載...'

  isDownloading.value = true
  downloadError.value = null

  try {
    // 第一階段：準備工作
    downloadProgress.value = 20
    downloadStatus.value = '正在驗證篩選條件...'
    await new Promise(resolve => setTimeout(resolve, 300))

    downloadProgress.value = 40
    downloadStatus.value = '正在產生報表...'
    await new Promise(resolve => setTimeout(resolve, 300))

    downloadProgress.value = 60
    downloadStatus.value = `正在下載 ${reportCode} 報表...`

    switch (reportCode) {
      case 'A01':
        // A01 各管理處執行進度報表
        await statisticsService.downloadExecutionProgressExcel(
          filters.year,
          filters.office
        )
        break

      case 'A02':
        await statisticsService.downloadCountyTownExcel(
          filters.year, filters.office
        )
        break
      case 'A03':
        await statisticsService.downloadOfficeSummaryExcel(
          filters.year, filters.office
        )
        break
      case 'A04': {
        const f4 = a04Filters.value
        if (f4.startYear > f4.year) {
          throw new Error('起始年度不得大於結束年度')
        }
        await statisticsService.downloadCountyTownYearlyExcel(
          f4.startYear, f4.year, f4.office
        )
        break
      }
      case 'A05': {
        const f5 = a05Filters.value
        if (f5.startYear > f5.year) {
          throw new Error('起始年度不得大於結束年度')
        }
        await statisticsService.downloadOfficeSummaryYearlyExcel(
          f5.startYear, f5.year, f5.office
        )
        break
      }
      case 'A06':
        // A06 各管理處經費統計報表
        await statisticsService.downloadBudgetAnalysisExcel(
          filters.year,
          filters.office
        )
        break
      case 'A07':
        // A07 原民區域統計報表
        await statisticsService.downloadAboriginalStatsExcel(
          filters.year
        )
        break
      case 'A08': {
        const f8 = a08Filters.value
        if (f8.startYear > f8.year) {
          throw new Error('起始年度不得大於結束年度')
        }
        await statisticsService.downloadAboriginalYearlyExcel(
          f8.startYear, f8.year
        )
        break
      }
      case 'A09':
        await statisticsService.downloadA09Excel(a09Filters.value.year)
        break
      case 'A10':
        await statisticsService.downloadA10Excel(a10Filters.value.year)
        break
      case 'B01-1':
        await statisticsService.downloadB01_1Excel(
          filters.year, filters.office
        )
        break
      case 'B01-2':
        await statisticsService.downloadB01_2Excel(
          filters.year, filters.office
        )
        break
      case 'B01-3': {
        const b01_3 = getFiltersForReport('B01-3')
        const startYear = b01_3.startYear || 97
        const endYear = b01_3.currentYear ? new Date().getFullYear() - 1911 : b01_3.year
        if (startYear > endYear) {
          throw new Error('起始年度不得大於結束年度')
        }
        await statisticsService.downloadB01_3Excel(
          startYear, endYear, b01_3.office
        )
        break
      }
      case 'B01-4': {
        const b01_4 = getFiltersForReport('B01-4')
        const startYear = b01_4.startYear || 97
        const endYear = b01_4.currentYear ? new Date().getFullYear() - 1911 : b01_4.year
        if (startYear > endYear) {
          throw new Error('起始年度不得大於結束年度')
        }
        await statisticsService.downloadB01_4Excel(
          startYear, endYear, b01_4.office
        )
        break
      }

      case 'B03':
        await statisticsService.downloadB03Excel(filters.year, filters.office)
        break

      default:
        throw new Error(`未知的報表代碼: ${reportCode}`)
    }

    // 下載完成
    downloadProgress.value = 90
    downloadStatus.value = '檔案已生成，正在啟動下載...'
    await new Promise(resolve => setTimeout(resolve, 500))

    downloadProgress.value = 100
    downloadStatus.value = '檔案已送出，請查看瀏覽器的下載紀錄'
    console.log(`下載報表 ${reportCode} 成功`)

  } catch (error) {
    console.error(`下載報表 ${reportCode} 失敗:`, error)
    downloadError.value = error instanceof Error ? error.message : '下載失敗，請稍後再試'
    downloadStatus.value = error instanceof Error ? error.message : '下載失敗，請稍後再試'
    downloadProgress.value = 0
  } finally {
    downloading.value = false
    isDownloading.value = false
  }
}

// 重新下載功能
const retryDownload = async () => {
  if (currentReportCode.value) {
    await downloadReport(currentReportCode.value)
  }
}

// 報表篩選條件類型
interface ReportFilters {
  office: number | null
  year: number
  currentYear: boolean
  startYear?: number
}

/**
 * 根據報表代碼取得篩選條件
 */
const getFiltersForReport = (reportCode: string): ReportFilters => {
  const filterMap: Record<string, ReportFilters> = {
    'A01': a01Filters.value,
    'A02': a02Filters.value,
    'A03': a03Filters.value,
    'A04': a04Filters.value,
    'A05': a05Filters.value,
    'A06': a06Filters.value,
    'A07': a07Filters.value,
    'A08': a08Filters.value,
    'A09': a09Filters.value,
    'A10': a10Filters.value,
    'B01-1': b01_1Filters.value,
    'B01-2': b01_2Filters.value,
    'B01-3': b01_3Filters.value,
    'B01-4': b01_4Filters.value,
    'B03': b03Filters.value
  }
  return filterMap[reportCode] || { office: null, year: new Date().getFullYear() - 1911, currentYear: true }
}

// ==================== 生命週期 ====================

/**
 * 載入管理處資料
 */
const loadOffices = async () => {
  isLoadingOffices.value = true
  try {
    const response = await officeService.getAll()
    // API 可能返回 { items: [...] } 或直接返回陣列
    offices.value = Array.isArray(response) ? response : response.items
  } catch (error) {
    console.error('載入管理處資料失敗:', error)
  } finally {
    isLoadingOffices.value = false
  }
}

onMounted(async () => {
  // 初始化：從 URL 讀取區段
  const sectionQuery = route.query.section
  if (sectionQuery && typeof sectionQuery === 'string') {
    activeSection.value = sectionQuery
  }

  // 載入管理處資料
  await loadOffices()
})
</script>

<style scoped>
/* 添加背景圖片樣式 */
.material-container {
  background-image: url('@/assets/bg_index.svg');
  background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  background-attachment: fixed;
}

/* 卡片與標題樣式 */
.section-card {
  /* position: relative; */
  /* margin: 24px 0; */
  overflow: visible !important;
  /* border-top-left-radius: 0 !important; */
  transition: all 0.3s ease;

  /* 毛玻璃效果 */
  background-color: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important;
}

.section-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
  background-color: rgba(255, 255, 255, 0.85) !important;
}

.section-card:hover .custom-title {
  background-color: #2d8c8f !important;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.08);
}

.custom-title {
  position: absolute;
  top: -50px;
  left: -1px;
  width: 100% !important;
  height: 50px;
  background-color: #3ea0a3 !important;
  border-radius: 8px 8px 0 0;
  z-index: 1;
  transition: all 0.3s ease;
  color: white !important;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

/* ==================== 左側導航樣式 ==================== */

.navigation-col {
  border-right: 1px solid rgba(0, 0, 0, 0.06);
  background: linear-gradient(to bottom, #fafafa 0%, #f8f8f8 100%);
  min-height: 600px;
}

.navigation-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background-color: rgba(255, 255, 255, 0.5);
}

/* 左側導航項目 */
.nav-section-item {
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.nav-section-item:hover {
  background-color: rgba(62, 160, 163, 0.04);
}

.nav-section-item.v-list-item--active {
  background-color: rgba(62, 160, 163, 0.08) !important;
  border-color: rgba(62, 160, 163, 0.2);
}

/* Active 狀態下的 Avatar 顏色 */
.v-list-item--active :deep(.v-avatar) {
  background-color: #2d8c8f !important;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: #424242;
}

.v-list-item--active .section-title {
  font-weight: 600;
  color: #2d8c8f;
}

.count-chip {
  font-weight: 600;
  font-size: 0.7rem;
}

/* ==================== 右側內容區樣式 ==================== */

.content-col {
  background-color: white;
}

/* 區段標題 */
.section-header {
  padding-bottom: 0.5rem;
}

/* 報表項目卡片 */
.report-item-card {
  /* background-color: #e3f4f4; */
  transition: all 0.2s ease;
}

.report-item-card:hover {
  background-color: #d6f0f0;
}

.report-title-text {
  font-size: 1rem;
  font-weight: 600;
  color: #2d8c8f;
  line-height: 1.4;
}

.report-category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.report-category-tags .v-chip {
  font-size: 0.7rem;
  font-weight: 500;
  height: 20px;
  padding: 0 8px;
}

/* 展開面板內容 */
.expansion-content {
  background-color: white;
  border-radius: 8px;
  padding: 12px;
}

/* 子報表項目 */
.sub-report-item {
  padding: 12px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.sub-report-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #2d8c8f;
  line-height: 1.3;
}

/* Expansion panel 樣式覆寫 */
:deep(.v-expansion-panel-title) {
  padding: 16px;
  min-height: auto;
}

:deep(.v-expansion-panel-text__wrapper) {
  padding: 0;
}

:deep(.v-expansion-panel) {
  background-color: transparent;
}

:deep(.v-expansion-panel-title:hover) {
  background-color: rgba(62, 160, 163, 0.02);
}

/* 響應式調整 */
@media (max-width: 960px) {
  .navigation-col {
    border-right: none;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    min-height: auto;
  }
}
</style>
