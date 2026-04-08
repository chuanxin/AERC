<template>
  <div
    ref="stepContent"
    class="step-content"
  >
    <v-card
      class="mt-4 mb-0 pa-0"
      flat
    >
      <v-card-text class="pb-0 pt-0">
        <!-- 🆕 唯讀模式提示（硬鎖定） -->
        <v-alert
          v-if="props.readonly && grantsStore.currentGrant?.status !== 'rejected'"
          type="warning"
          variant="tonal"
          density="compact"
          class="mb-4"
          rounded="lg"
        >
          <div class="d-flex align-center">
            <span class="text-body-2">
              {{ grantsStore.currentGrant?.status === 'submitted'
                ? '已完成結案申報，此步驟已鎖定，無法編輯。'
                : '已完成申報並送審，此步驟已鎖定，無法編輯。' }}
            </span>
          </div>
        </v-alert>

        <!-- ⚠️ 軟鎖定警告 -->
        <v-alert
          v-if="props.softLocked && !props.readonly"
          color="warning"
          variant="tonal"
          density="compact"
          class="mb-4"
          rounded="lg"
        >
          <div class="d-flex align-center">
            <v-icon
              class="me-2"
              size="small"
            >
              mdi-alert
            </v-icon>
            <span class="text-body-2">
              已完成現場勘查，修改此步驟資料可能導致勘查結果無效，請謹慎編輯。
            </span>
          </div>
        </v-alert>

        <v-form
          ref="form"
          v-model="localValid"
          @submit.prevent
        >
          <!-- STEP 1: 設計人姓名 -->
          <v-card
            v-if="!props.readonly"
            flat
            class="mb-4 pa-4"
            color="#e3f4f4"
            rounded="lg"
          >
            <v-card-title
              class="text-subtitle-1 font-weight-bold pa-0 pb-4 d-flex align-center flex-wrap"
              style="color: #2d8c8f"
            >
              <v-icon
                color="#3ea0a3"
                class="me-2 pb-1"
                size="small"
              >
                mdi-cog
              </v-icon>
              田間管路系統設計

              <!-- 設計人姓名 chip (僅在有值且非編輯模式時顯示) -->
              <template v-if="localFormData.designerName && !isEditingDesigner">
                <v-chip
                  class="ms-4"
                  size="small"
                  variant="flat"
                  color="#3ea0a3"
                >
                  <v-icon
                    size="x-small"
                    class="me-1"
                  >
                    mdi-account-edit
                  </v-icon>
                  設計人：{{ localFormData.designerName }}
                </v-chip>
                <v-btn
                  icon
                  size="x-small"
                  variant="text"
                  color="#3ea0a3"
                  class="ms-2"
                  @click="isEditingDesigner = true"
                >
                  <v-icon size="small">
                    mdi-pencil
                  </v-icon>
                  <!-- <v-tooltip
                    activator="parent"
                    location="top"
                  >
                    編輯設計人姓名
                  </v-tooltip> -->
                </v-btn>
              </template>
            </v-card-title>

            <!-- 初始輸入區塊 (當設計人姓名為空或在編輯模式時顯示) -->
            <v-sheet
              v-if="!localFormData.designerName || isEditingDesigner"
              class="mb-3 pa-4 rounded"
              color="#fff3e0"
            >
              <div
                v-if="!localFormData.designerName"
                class="d-flex align-center mb-3"
              >
                <v-icon
                  size="small"
                  color="#f57c00"
                  class="me-2"
                >
                  mdi-alert-circle
                </v-icon>
                <span
                  class="text-body-2 font-weight-bold"
                  style="color: #e65100;"
                >
                  請先輸入設計人姓名以完成設計
                </span>
              </div>
              <div class="d-flex align-center">
                <v-text-field
                  v-model="localFormData.designerName"
                  label="設計人姓名"
                  variant="outlined"
                  density="comfortable"
                  color="#f57c00"
                  bg-color="white"
                  class="me-3"
                  style="max-width: 300px;"
                  hide-details
                  @blur="updateFormData"
                />
                <v-btn
                  color="#f57c00"
                  variant="flat"
                  class="flex-grow-2"
                  rounded="lg"
                  size="large"
                  :disabled="!localFormData.designerName"
                  @click="isEditingDesigner = false"
                >
                  <v-icon class="me-1">
                    mdi-check
                  </v-icon>
                  確認
                </v-btn>
                <v-btn
                  v-if="!localFormData.designerName"
                  color="grey-darken-1"
                  variant="outlined"
                  rounded="lg"
                  size="large"
                  class="ms-2"
                  @click="skipStep"
                >
                  <v-icon class="me-1">
                    mdi-skip-next
                  </v-icon>
                  不需申請田間管路補助
                </v-btn>
              </div>
            </v-sheet>

            <!-- 主要配置區塊 (僅在有設計人姓名且非編輯模式時顯示) -->
            <template v-if="localFormData.designerName && !isEditingDesigner">
              <!-- STEP 2: 設施基地長寬長度調整 -->
              <v-sheet
                class="mb-3 pa-3 rounded"
                color="white"
              >
                <div class="d-flex align-center mb-2">
                  <v-icon
                    size="small"
                    class="me-2"
                  >
                    mdi-land-fields
                  </v-icon>
                  <span class="text-body-2 font-weight-medium">田間坵塊</span>
                </div>
                <div class="d-flex flex-wrap align-center">
                  <div class="d-flex align-center flex-wrap me-4 mb-2">
                    <div class="text-body-2 me-2">
                      設施基地長寬:
                    </div>
                    <v-text-field
                      v-model.number="localFormData.fieldLength"
                      label="長(m)"
                      type="number"
                      variant="outlined"
                      density="comfortable"
                      color="#3ea0a3"
                      bg-color="white"
                      style="width: 100px"
                      class="me-1"
                      @update:model-value="calculateWidth"
                    />
                    <span class="mx-1">x</span>
                    <v-text-field
                      v-model.number="localFormData.fieldWidth"
                      label="寬(m)"
                      type="number"
                      variant="outlined"
                      density="comfortable"
                      style="width: 100px"
                      class="me-1"
                      readonly
                      bg-color="grey-lighten-4"
                    />
                  </div>

                  <div class="d-flex align-center me-4 mb-2">
                    <div class="text-body-2 me-2">
                      施設面積:
                    </div>
                    <v-text-field
                      :value="facilityAreaFromStep2"
                      type="number"
                      variant="outlined"
                      density="comfortable"
                      style="max-width: 100px"
                      class="me-1"
                      readonly
                    />
                    <span>m²</span>
                  </div>
                </div>
              </v-sheet>

              <!-- STEP 3: 田間主管資訊 -->
              <v-sheet
                class="mb-3 pa-3 rounded"
                color="white"
              >
                <div class="d-flex align-center mb-2">
                  <v-icon
                    size="small"
                    class="me-2"
                  >
                    mdi-pipe
                  </v-icon>
                  <span class="text-body-2 font-weight-medium">田間主管配置</span>
                </div>
                <!-- 主管1 -->
                <div class="text-subtitle-2 mb-1">
                  主管 1（L1）
                </div>
                <div class="d-flex align-center flex-wrap">
                  <v-text-field
                    v-model.number="localFormData.mainPipeLength"
                    label="長度(M)"
                    type="number"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    color="#3ea0a3"
                    style="width: 120px"
                    :rules="[v => (v !== null && v !== '') || '請輸入長度']"
                    @update:model-value="calculateMainPipeQuantity"
                  />
                  <v-select
                    v-model="localFormData.mainPipeDiameterId"
                    :items="pipe1DiameterOptions"
                    item-title="name"
                    item-value="id"
                    label="管徑(吋)"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    color="#3ea0a3"
                    style="width: 120px"
                    :rules="[v => !!v || '請選擇管徑']"
                    @update:model-value="() => fetchPipePrice(1)"
                  >
                    <template #item="{ props, item }">
                      <v-list-item
                        v-bind="props"
                        :title="item.raw.name"
                        :class="{'text-light-blue-accent-3': item.raw.isFiltered}"
                      />
                    </template>
                  </v-select>
                  <v-select
                    v-model="localFormData.mainPipeMaterialId"
                    :items="pipe1MaterialOptions"
                    item-title="name"
                    item-value="id"
                    label="材質"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    color="#3ea0a3"
                    style="width: 120px"
                    :rules="[v => !!v || '請選擇材質']"
                    @update:model-value="() => fetchPipePrice(1)"
                  >
                    <template #item="{ props, item }">
                      <v-list-item
                        v-bind="props"
                        :title="item.raw.name"
                        :class="{'text-light-blue-accent-3': item.raw.isFiltered}"
                      />
                    </template>
                  </v-select>
                  <v-text-field
                    v-model.number="localFormData.mainPipeUnitPrice"
                    label="單價"
                    type="number"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 100px"
                    readonly
                    bg-color="grey-lighten-4"
                    persistent-hint
                  />
                  <v-text-field
                    v-model.number="localFormData.mainPipeQuantity"
                    label="數量"
                    type="number"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 80px"
                    readonly
                    bg-color="grey-lighten-4"
                    persistent-hint
                  />
                  <v-text-field
                    v-model="mainPipeTotalPrice"
                    label="總價"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    readonly
                    bg-color="grey-lighten-4"
                  />
                </div>

                <v-divider class="my-3" />

                <!-- 主管2 -->
                <div class="d-flex align-center mb-1">
                  <v-checkbox-btn
                    v-model="localFormData.mainPipe2Enabled"
                    label="啟用主管2（L2）"
                    density="compact"
                    @update:model-value="toggleMainPipe2"
                  />
                </div>
                <div
                  v-if="localFormData.mainPipe2Enabled"
                  class="d-flex align-center flex-wrap mt-1"
                >
                  <v-text-field
                    v-model.number="localFormData.mainPipe2Length"
                    label="主管2 長度(M)"
                    type="number"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    color="#3ea0a3"
                    style="width: 120px"
                    :rules="[localFormData.mainPipe2Enabled ? (v => (v !== null && v !== '') || '請輸入長度') : true]"
                    @update:model-value="calculateMainPipe2Quantity"
                  />
                  <v-select
                    v-model="localFormData.mainPipe2DiameterId"
                    :items="pipe2DiameterOptions"
                    item-title="name"
                    item-value="id"
                    label="主管2 管徑(吋)"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    color="#3ea0a3"
                    style="width: 120px"
                    :rules="[localFormData.mainPipe2Enabled ? (v => !!v || '請選擇管徑') : true]"
                    @update:model-value="() => fetchPipePrice(2)"
                  >
                    <template #item="{ props, item }">
                      <v-list-item
                        v-bind="props"
                        :title="item.raw.name"
                        :class="{'text-light-blue-accent-3': item.raw.isFiltered}"
                      />
                    </template>
                  </v-select>
                  <v-select
                    v-model="localFormData.mainPipe2MaterialId"
                    :items="pipe2MaterialOptions"
                    item-title="name"
                    item-value="id"
                    label="主管2 材質"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    color="#3ea0a3"
                    style="width: 120px"
                    :rules="[localFormData.mainPipe2Enabled ? (v => !!v || '請選擇材質') : true]"
                    @update:model-value="() => fetchPipePrice(2)"
                  >
                    <template #item="{ props, item }">
                      <v-list-item
                        v-bind="props"
                        :title="item.raw.name"
                        :class="{'text-light-blue-accent-3': item.raw.isFiltered}"
                      />
                    </template>
                  </v-select>
                  <v-text-field
                    v-model.number="localFormData.mainPipe2UnitPrice"
                    label="主管2 單價"
                    type="number"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 100px"
                    readonly
                    bg-color="grey-lighten-4"
                    persistent-hint
                  />
                  <v-text-field
                    v-model.number="localFormData.mainPipe2Quantity"
                    label="主管2 數量"
                    type="number"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 80px"
                    readonly
                    bg-color="grey-lighten-4"
                    persistent-hint
                  />
                  <v-text-field
                    v-model="mainPipe2TotalPrice"
                    label="主管2 總價"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 120px"
                    readonly
                    bg-color="grey-lighten-4"
                  />
                </div>
              </v-sheet>

              <!-- STEP 4: 灌溉型式與相關管路配置 -->
              <v-sheet
                class="mb-3 pa-3 rounded"
                color="white"
              >
                <div class="d-flex align-center mb-2">
                  <v-icon
                    size="small"
                    class="me-2"
                  >
                    mdi-sprinkler
                  </v-icon>
                  <span class="text-body-2 font-weight-medium">灌溉管路配置</span>
                </div>
                <!-- 補助額度狀態提示 -->
                <v-alert
                  v-if="localFormData.irrigationTypeId && facilityAreaFromStep2 > 0"
                  type="info"
                  variant="tonal"
                  density="compact"
                  class="mb-3"
                >
                  <template #prepend>
                    <v-icon size="small">
                      mdi-information-outline
                    </v-icon>
                  </template>
                  <div class="text-caption">
                    <strong>補助額度狀態（{{ irrigationSystemDisplayName }}）：</strong>
                    <!-- 判斷限制類型並顯示對應說明 -->
                    <template v-if="grantsStore.hasSubsidySummary && effectivePipelineSubsidyLimit < pipelineSubsidyLimit">
                      面積 {{ facilityAreaHaFromStep2 }} 公頃 → 有效額度 ${{ effectivePipelineSubsidyLimit.toLocaleString() }}
                      <span class="text-warning font-weight-bold">（原補助上限 ${{ pipelineSubsidyLimit.toLocaleString() }} 超過個人年度補助限額）</span>
                    </template>
                    <template v-else>
                      面積 {{ facilityAreaHaFromStep2 }} 公頃 → 補助上限 ${{ effectivePipelineSubsidyLimit.toLocaleString() }}
                    </template>
                    |
                    本次申請 ${{ currentPipelineSubsidy.toLocaleString() }} |
                    剩餘額度 ${{ availablePipelineSubsidy.toLocaleString() }}
                    <span
                      v-if="pipelineSubsidyRatio > 0"
                      class="ms-2"
                    >
                      (補助比例: {{ (pipelineSubsidyRatio * 100).toFixed(1) }}%)
                    </span>
                  </div>
                </v-alert>

                <v-alert
                  v-if="!localFormData.irrigationTypeId"
                  type="warning"
                  variant="tonal"
                  density="compact"
                  class="mb-3"
                >
                  <template #prepend>
                    <v-icon size="small">
                      mdi-alert-circle-outline
                    </v-icon>
                  </template>
                  <div class="text-caption">
                    請先選擇<strong>灌溉型式</strong>以查看補助額度資訊
                  </div>
                </v-alert>

                <v-alert
                  v-if="localFormData.irrigationTypeId && facilityAreaFromStep2 <= 0"
                  type="warning"
                  variant="tonal"
                  density="compact"
                  class="mb-3"
                >
                  <template #prepend>
                    <v-icon size="small">
                      mdi-alert-circle-outline
                    </v-icon>
                  </template>
                  <div class="text-caption">
                    請先在 <strong>Step2 土地資料</strong> 中填寫施作面積，以計算補助額度
                  </div>
                </v-alert>
                <div class="d-flex align-center flex-wrap">
                  <!-- 灌溉型式選擇 -->
                  <v-select
                    v-model="localFormData.irrigationTypeId"
                    :items="irrigationTypeOptions"
                    item-title="description"
                    item-value="id"
                    label="灌溉型式"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    color="#3ea0a3"
                    style="width: 180px"
                    hide-details
                    @update:model-value="onIrrigationTypeChange"
                  />
                  <!-- 水源選擇 (適用於所有灌溉類型) -->
                  <v-select
                    v-model="localFormData.waterSourceId"
                    :items="waterSourceOptions"
                    item-title="name"
                    item-value="id"
                    label="灌溉水源"
                    variant="outlined"
                    density="comfortable"
                    class="mb-2"
                    color="#3ea0a3"
                    style="width: 160px"
                    hide-details
                    @update:model-value="updateFormData"
                  />
                </div>

                <!-- 穿孔管系统相关配置 -->
                <div
                  v-if="localFormData.irrigationTypeId === 1"
                  class="irrigation-type-config"
                >
                  <div class="text-subtitle-2 mb-3">
                    穿孔管系統配置
                  </div>

                  <div class="d-flex flex-wrap perforated-pipe-config">
                    <!-- 穿孔管出水方向 -->
                    <v-select
                      v-model="localFormData.perforatedPipeDirection"
                      :items="perforatedPipeTypeOptions"
                      item-title="title"
                      item-value="value"
                      label="穿孔管出水方向"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 100px"
                    />

                    <!-- 支管行距(SL) -->
                    <div class="me-3 mb-2">
                      <div class="text-body-2 mb-1">
                        行距(SL)
                      </div>
                      <div class="d-flex align-center">
                        <v-text-field
                          v-model.number="localFormData.branchPipeSpacing_SL"
                          variant="outlined"
                          density="comfortable"
                          type="number"
                          color="#3ea0a3"
                          style="width: 100px"
                          class="me-1"
                          @update:model-value="updateFormData"
                        />
                        <span>m</span>
                      </div>
                    </div>

                    <!-- 設施型式 -->
                    <v-select
                      v-model="localFormData.installationType"
                      :items="installationTypeOptions"
                      item-title="name"
                      item-value="id"
                      label="設施型式"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 160px"
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2">
                    <!-- 末端設施規格和名稱 -->
                    <v-select
                      v-model="localFormData.endFacilitySpecId"
                      :items="endFacilityDiameterOptions"
                      item-title="name"
                      item-value="id"
                      label="管徑（吋）"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 150px"
                      @update:model-value="onEndFacilitySpecChange"
                    />

                    <v-autocomplete
                      v-model="localFormData.endFacilityPomno"
                      :items="filteredEndFacilityPipeFittings"
                      item-title="displayName"
                      item-value="pomno"
                      label="管材名稱"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 250px"
                      clearable
                      autocomplete="off"
                      @update:model-value="onSelectedEndFacilityChange"
                    >
                      <template #item="{ props, item }">
                        <v-list-item
                          v-bind="props"
                          :title="item.raw.displayName"
                          :subtitle="`材質: ${item.raw.materialName}`"
                        />
                      </template>
                    </v-autocomplete>
                  </div>
                </div>

                <!-- 噴頭式系統相關配置 -->
                <div
                  v-else-if="localFormData.irrigationTypeId === 2"
                  class="irrigation-type-config"
                >
                  <div class="text-subtitle-2 mb-3">
                    噴頭式系統配置
                  </div>

                  <div class="d-flex flex-wrap">
                    <!-- 噴頭子系統選擇 -->
                    <v-select
                      v-model="localFormData.sprinklerSubtypeId"
                      :items="sprinklerTypeOptions"
                      item-title="name"
                      item-value="id"
                      label="噴頭類型"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 180px"
                      @update:model-value="onEndFacilityParamsChange"
                    />

                    <!-- 設施型式 -->
                    <v-select
                      v-model="localFormData.installationType"
                      :items="installationTypeOptions"
                      item-title="name"
                      item-value="id"
                      label="設施型式"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 160px"
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2 sprinkler-system-config align-center">
                    <!-- 支管行距與間距 -->
                    <div class="me-3 mb-2">
                      <div class="text-body-2 mb-1">
                        支管行距(SL)
                      </div>
                      <div class="d-flex align-center">
                        <v-text-field
                          v-model.number="localFormData.branchPipeSpacing_SL"
                          variant="outlined"
                          density="comfortable"
                          type="number"
                          style="width: 80px"
                          class="me-1"
                          color="#3ea0a3"
                          @update:model-value="updateFormData"
                        />
                        <span>m</span>
                      </div>
                    </div>

                    <div class="me-3 mb-2">
                      <div class="text-body-2 mb-1">
                        噴頭間距(SS)
                      </div>
                      <div class="d-flex align-center">
                        <v-text-field
                          v-model.number="localFormData.sprinklerSpacing_SS"
                          variant="outlined"
                          type="number"
                          density="comfortable"
                          style="width: 80px"
                          class="me-1"
                          color="#3ea0a3"
                          @update:model-value="updateFormData"
                        />
                        <span>m</span>
                      </div>
                    </div>

                    <!-- 支管材質和規格 -->
                    <v-select
                      v-model="localFormData.branchPipeMaterialId"
                      :items="pipeMaterialOptions"
                      item-title="name"
                      item-value="id"
                      label="支管材質"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 150px"
                      hide-details
                      @update:model-value="updateFormData"
                    />

                    <v-select
                      v-model="localFormData.branchPipeDiameterId"
                      :items="pipeDiameterOptions"
                      item-title="name"
                      item-value="id"
                      label="支管規格"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 150px"
                      hide-details
                      @update:model-value="updateFormData"
                    />

                    <!-- 變徑 checkbox -->
                    <v-checkbox
                      v-model="localFormData.enableBranchDiameterChange"
                      label="變徑"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      hide-details
                      @update:model-value="(val) => { if (!val) localFormData.changeBranchSpecId = null; }"
                    />

                    <!-- 支管變徑規格（條件顯示） -->
                    <v-select
                      v-if="localFormData.enableBranchDiameterChange"
                      v-model="localFormData.changeBranchSpecId"
                      :items="pipeDiameterOptions"
                      item-title="name"
                      item-value="id"
                      label="變徑規格"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 150px"
                      hide-details
                      variant="outlined"
                      density="comfortable"
                      clearable
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2 mb-0 align-center">
                    <!-- 豎管高度 -->
                    <div class="me-3 mb-2">
                      <div class="text-body-2 mb-1">
                        豎管高度(H)
                      </div>
                      <div class="d-flex align-center">
                        <v-text-field
                          v-model.number="localFormData.riserHeight_H"
                          variant="outlined"
                          type="number"
                          density="comfortable"
                          style="width: 80px"
                          class="me-1"
                          color="#3ea0a3"
                        />
                        <span>m</span>
                      </div>
                    </div>

                    <!-- 末端設施規格和名稱 -->
                    <v-select
                      v-model="localFormData.endFacilitySpecId"
                      :items="endFacilityDiameterOptions"
                      item-title="name"
                      item-value="id"
                      label="末端設施規格"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 150px"
                      hide-details
                      @update:model-value="onEndFacilitySpecChange"
                    />

                    <v-autocomplete
                      v-model="localFormData.endFacilityPomno"
                      :items="filteredEndFacilityPipeFittings"
                      item-title="displayName"
                      item-value="pomno"
                      label="末端設施名稱"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 250px"
                      clearable
                      hide-details
                      autocomplete="off"
                      @update:model-value="onSelectedEndFacilityChange"
                    >
                      <template #item="{ props, item }">
                        <v-list-item
                          v-bind="props"
                          :title="item.raw.displayName"
                          :subtitle="`材質: ${item.raw.materialName}`"
                        />
                      </template>
                    </v-autocomplete>
                  </div>

                  <!-- 豎管材質和規格欄位已隱藏，自動與末端設施同步 -->
                  <v-select
                    v-show="false"
                    v-model="localFormData.riserPipeMaterialId"
                    :items="pipeMaterialOptions"
                    item-title="name"
                    item-value="id"
                    label="豎管材質"
                    variant="outlined"
                    density="comfortable"
                  />

                  <v-select
                    v-show="false"
                    v-model="localFormData.riserPipeSpecId"
                    :items="pipeDiameterOptions"
                    item-title="name"
                    item-value="id"
                    label="豎管規格"
                    variant="outlined"
                    density="comfortable"
                  />
                </div>

                <!-- 微噴系統相關配置 -->
                <div
                  v-else-if="localFormData.irrigationTypeId === 3"
                  class="irrigation-type-config"
                >
                  <div class="text-subtitle-2 mb-3">
                    微噴系統配置
                  </div>

                  <div class="d-flex flex-wrap">
                    <!-- 設施型式 -->
                    <v-select
                      v-model="localFormData.installationType"
                      :items="installationTypeOptions"
                      item-title="name"
                      item-value="id"
                      label="設施型式"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 160px"
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2 align-center">
                    <!-- 支管行距和間距 -->
                    <div class="me-3 mb-2">
                      <div class="text-body-2 mb-1">
                        支管行距(SL)
                      </div>
                      <div class="d-flex align-center">
                        <v-text-field
                          v-model.number="localFormData.branchPipeSpacing_SL"
                          variant="outlined"
                          density="comfortable"
                          type="number"
                          style="width: 80px"
                          class="me-1"
                          color="#3ea0a3"
                          @update:model-value="updateFormData"
                        />
                        <span>m</span>
                      </div>
                    </div>

                    <div class="me-3 mb-2">
                      <div class="text-body-2 mb-1">
                        噴頭間距(SS)
                      </div>
                      <div class="d-flex align-center">
                        <v-text-field
                          v-model.number="localFormData.sprinklerSpacing_SS"
                          variant="outlined"
                          type="number"
                          density="comfortable"
                          style="width: 80px"
                          class="me-1"
                          color="#3ea0a3"
                          @update:model-value="updateFormData"
                        />
                        <span>m</span>
                      </div>
                    </div>

                    <!-- 支管材質和規格 -->
                    <v-select
                      v-model="localFormData.branchPipeMaterialId"
                      :items="pipeMaterialOptions"
                      item-title="name"
                      item-value="id"
                      label="支管材質"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 150px"
                      hide-details
                      @update:model-value="updateFormData"
                    />

                    <v-select
                      v-model="localFormData.branchPipeDiameterId"
                      :items="pipeDiameterOptions"
                      item-title="name"
                      item-value="id"
                      label="支管規格"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 150px"
                      hide-details
                      @update:model-value="updateFormData"
                    />

                    <!-- 變徑 checkbox -->
                    <v-checkbox
                      v-model="localFormData.enableBranchDiameterChange"
                      label="變徑"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      hide-details
                      @update:model-value="(val) => { if (!val) localFormData.changeBranchSpecId = null; }"
                    />

                    <!-- 支管變徑規格（條件顯示） -->
                    <v-select
                      v-if="localFormData.enableBranchDiameterChange"
                      v-model="localFormData.changeBranchSpecId"
                      :items="pipeDiameterOptions"
                      item-title="name"
                      item-value="id"
                      label="變徑規格"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 150px"
                      hide-details
                      clearable
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2 mb-0 pb-0 align-center">
                    <!-- 豎管高度 -->
                    <div class="me-3 mb-2">
                      <div class="text-body-2 mb-1">
                        豎管高度(H)
                      </div>
                      <div class="d-flex align-center">
                        <v-text-field
                          v-model.number="localFormData.riserHeight_H"
                          variant="outlined"
                          type="number"
                          density="comfortable"
                          style="width: 80px"
                          class="me-1"
                          color="#3ea0a3"
                        />
                        <span>m</span>
                      </div>
                    </div>

                    <!-- 末端設施規格和名稱 -->
                    <v-select
                      v-model="localFormData.endFacilitySpecId"
                      :items="endFacilityDiameterOptions"
                      item-title="name"
                      item-value="id"
                      label="末端設施規格"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 150px"
                      hide-details
                      @update:model-value="onEndFacilitySpecChange"
                    />

                    <v-autocomplete
                      v-model="localFormData.endFacilityPomno"
                      :items="filteredEndFacilityPipeFittings"
                      item-title="displayName"
                      item-value="pomno"
                      label="末端設施名稱"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 250px"
                      clearable
                      hide-details
                      autocomplete="off"
                      @update:model-value="onSelectedEndFacilityChange"
                    >
                      <template #item="{ props, item }">
                        <v-list-item
                          v-bind="props"
                          :title="item.raw.displayName"
                          :subtitle="`材質: ${item.raw.materialName}`"
                        />
                      </template>
                    </v-autocomplete>
                  </div>

                  <!-- 豎管材質和規格欄位已隱藏，自動與末端設施同步 -->
                  <v-select
                    v-show="false"
                    v-model="localFormData.riserPipeMaterialId"
                    :items="pipeMaterialOptions"
                    item-title="name"
                    item-value="id"
                    label="豎管材質"
                    variant="outlined"
                    density="comfortable"
                  />

                  <v-select
                    v-show="false"
                    v-model="localFormData.riserPipeSpecId"
                    :items="pipeDiameterOptions"
                    item-title="name"
                    item-value="id"
                    label="豎管規格"
                    variant="outlined"
                    density="comfortable"
                  />
                </div>

                <!-- 滴灌系統相關配置 -->
                <div
                  v-else-if="localFormData.irrigationTypeId === 4"
                  class="irrigation-type-config"
                >
                  <div class="text-subtitle-2 mb-3">
                    滴灌系統配置
                  </div>

                  <div class="d-flex flex-wrap">
                    <!-- 滴灌子系統選擇 -->
                    <v-select
                      v-model="localFormData.dripperSubtypeId"
                      :items="dripperTypeOptions"
                      item-title="name"
                      item-value="id"
                      label="滴頭類型"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 180px"
                      @update:model-value="onEndFacilityParamsChange"
                    />

                    <!-- 設施型式 -->
                    <v-select
                      v-model="localFormData.installationType"
                      :items="installationTypeOptions"
                      item-title="name"
                      item-value="id"
                      label="設施型式"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      color="#3ea0a3"
                      style="width: 160px"
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2 drip-system-config">
                    <!-- ID=7滴嘴滴灌系統的特殊配置：使用與ID=8相同的資料來源 -->
                    <template v-if="localFormData.dripperSubtypeId === 7">
                      <!-- 滴灌管行距(SL) - 移至滴水管規格前方 -->
                      <div class="me-3 mb-2">
                        <div class="text-body-2 mb-1">
                          滴灌管行距(SL)
                        </div>
                        <div class="d-flex align-center">
                          <v-text-field
                            v-model.number="localFormData.branchPipeSpacing_SL"
                            variant="outlined"
                            density="comfortable"
                            type="number"
                            style="width: 80px"
                            class="me-1"
                            color="#3ea0a3"
                            @update:model-value="updateFormData"
                          />
                          <span>m</span>
                        </div>
                      </div>

                      <!-- 滴水管規格 - 使用與ID=8相同的pipeDrip資料來源 -->
                      <v-select
                        v-model="localFormData.branchPipeDiameterId"
                        :items="branchPipeSpecOptionsForId7"
                        item-title="name"
                        item-value="id"
                        label="滴灌管規格"
                        variant="outlined"
                        density="comfortable"
                        class="me-3 mb-2"
                        color="#3ea0a3"
                        style="width: 150px"
                        @update:model-value="onBranchPipeSpecChangeForId7"
                      />

                      <!-- 滴水管名稱 - 替換原本的滴水管材質，使用與ID=8相同的pipeDrip資料來源 -->
                      <v-autocomplete
                        :key="`branch-pipe-name-${localFormData.branchPipeDiameterId}`"
                        v-model="localFormData.branchPipePomno"
                        :items="filteredBranchPipeFittings"
                        item-title="displayName"
                        item-value="pomno"
                        label="滴灌管名稱"
                        variant="outlined"
                        density="comfortable"
                        class="me-3 mb-2"
                        color="#3ea0a3"
                        style="width: 250px"
                        clearable
                        autocomplete="off"
                        @update:model-value="onSelectedBranchPipeChangeForId7"
                      >
                        <template #item="{ props: itemProps, item }">
                          <v-list-item
                            v-bind="itemProps"
                            :title="item.raw.displayName"
                            :subtitle="`材質: ${item.raw.materialName}`"
                          />
                        </template>
                      </v-autocomplete>
                    </template>

                    <!-- 其他滴灌系統(ID=8等)：不再需要滴水管材質+滴水管規格 -->
                    <!-- ID=8時，滴灌管行距(SL)已移至末端管徑同一列，此處不顯示任何欄位 -->
                    <!-- 其他ID時保持原有邏輯 -->
                    <template v-else-if="localFormData.dripperSubtypeId !== 8">
                      <v-select
                        v-model="localFormData.branchPipeMaterialId"
                        :items="pipeMaterialOptions"
                        item-title="name"
                        item-value="id"
                        label="滴水管材質"
                        variant="outlined"
                        density="comfortable"
                        class="me-3 mb-2"
                        color="#3ea0a3"
                        style="width: 150px"
                        @update:model-value="updateFormData"
                      />

                      <v-select
                        v-model="localFormData.branchPipeDiameterId"
                        :items="pipeDiameterOptions"
                        item-title="name"
                        item-value="id"
                        label="滴水管規格"
                        variant="outlined"
                        density="comfortable"
                        class="me-3 mb-2"
                        color="#3ea0a3"
                        style="width: 150px"
                        @update:model-value="updateFormData"
                      />

                      <!-- 滴灌管行距(SL) - 其他ID時保持在原位 -->
                      <div class="me-3 mb-2">
                        <div class="text-body-2 mb-1">
                          滴灌管行距(SL)
                        </div>
                        <div class="d-flex align-center">
                          <v-text-field
                            v-model.number="localFormData.branchPipeSpacing_SL"
                            variant="outlined"
                            density="comfortable"
                            type="number"
                            style="width: 80px"
                            class="me-1"
                            color="#3ea0a3"
                            @update:model-value="updateFormData"
                          />
                          <span>m</span>
                        </div>
                      </div>
                    </template>
                  </div>

                  <div class="d-flex flex-wrap mt-2 drip-system-config">
                    <!-- 噴頭間距、末端管徑和末端管材 -->

                    <!-- 噴頭間距：只有滴嘴滴灌系統(ID=7)才需要顯示 -->
                    <div
                      v-if="localFormData.dripperSubtypeId === 7"
                      class="me-3 mb-2"
                    >
                      <div class="text-body-2 mb-1">
                        噴頭間距(SS)
                      </div>
                      <div class="d-flex align-center">
                        <v-text-field
                          v-model.number="localFormData.sprinklerSpacing_SS"
                          variant="outlined"
                          type="number"
                          density="comfortable"
                          style="width: 80px"
                          class="me-1"
                          color="#3ea0a3"
                          @update:model-value="updateFormData"
                        />
                        <span>m</span>
                      </div>
                    </div>

                    <!-- ID=8時：滴灌管行距(SL) + 末端管徑 + 末端管材名稱 在同一列 -->
                    <template v-if="localFormData.dripperSubtypeId === 8">
                      <!-- 滴灌管行距(SL) -->
                      <div class="me-3 mb-2">
                        <div class="text-body-2 mb-1">
                          滴灌管行距(SL)
                        </div>
                        <div class="d-flex align-center">
                          <v-text-field
                            v-model.number="localFormData.branchPipeSpacing_SL"
                            variant="outlined"
                            density="comfortable"
                            type="number"
                            style="width: 80px"
                            class="me-1"
                            color="#3ea0a3"
                            @update:model-value="updateFormData"
                          />
                          <span>m</span>
                        </div>
                      </div>

                      <!-- 末端管徑 -->
                      <v-select
                        :key="`end-facility-spec-${localFormData.dripperSubtypeId}`"
                        v-model="localFormData.endFacilitySpecId"
                        :items="endFacilityDiameterOptions"
                        item-title="name"
                        item-value="id"
                        label="管徑（吋）"
                        variant="outlined"
                        density="comfortable"
                        class="me-3 mb-2"
                        color="#3ea0a3"
                        style="width: 150px"
                        @update:model-value="onEndFacilitySpecChange"
                      />

                      <!-- 末端管材名稱 -->
                      <v-autocomplete
                        :key="`end-facility-pomno-${localFormData.dripperSubtypeId}`"
                        v-model="localFormData.endFacilityPomno"
                        :items="filteredEndFacilityPipeFittings"
                        item-title="displayName"
                        item-value="pomno"
                        label="管材名稱"
                        variant="outlined"
                        density="comfortable"
                        class="me-3 mb-2"
                        color="#3ea0a3"
                        style="width: 250px"
                        clearable
                        autocomplete="off"
                        @update:model-value="onSelectedEndFacilityChange"
                      >
                        <template #item="{ props: itemProps, item }">
                          <v-list-item
                            v-bind="itemProps"
                            :title="item.raw.displayName"
                            :subtitle="`材質: ${item.raw.materialName}`"
                          />
                        </template>
                      </v-autocomplete>
                    </template>

                    <!-- 其他ID時：保持原有的末端管徑+末端管材名稱佈局 -->
                    <template v-else>
                      <!-- 末端管徑 -->
                      <v-select
                        :key="`end-facility-spec-${localFormData.dripperSubtypeId}`"
                        v-model="localFormData.endFacilitySpecId"
                        :items="endFacilityDiameterOptions"
                        item-title="name"
                        item-value="id"
                        label="末端管徑（吋）"
                        variant="outlined"
                        density="comfortable"
                        class="me-3 mb-2"
                        color="#3ea0a3"
                        style="width: 150px"
                        @update:model-value="onEndFacilitySpecChange"
                      />

                      <!-- 末端管材名稱 -->
                      <v-autocomplete
                        :key="`end-facility-pomno-${localFormData.dripperSubtypeId}`"
                        v-model="localFormData.endFacilityPomno"
                        :items="filteredEndFacilityPipeFittings"
                        item-title="displayName"
                        item-value="pomno"
                        label="末端管材名稱"
                        variant="outlined"
                        density="comfortable"
                        class="me-3 mb-2"
                        color="#3ea0a3"
                        style="width: 250px"
                        clearable
                        autocomplete="off"
                        @update:model-value="onSelectedEndFacilityChange"
                      >
                        <template #item="{ props: itemProps2, item }">
                          <v-list-item
                            v-bind="itemProps2"
                            :title="item.raw.displayName"
                            :subtitle="`材質: ${item.raw.materialName}`"
                          />
                        </template>
                      </v-autocomplete>
                    </template>
                  </div>
                </div>

                <div class="text-body-2 mb-2 text-grey-darken-1">
                  點擊下方按鈕可根據您選擇的灌溉型式和設施配置，自動帶入相應的材料清單。
                </div>

                <!-- 版本選擇控制項 -->
                <div>
                  <v-chip-group
                    v-model="materialGenerationVersion"
                    mandatory
                    selected-class="text-primary"
                    class="mb-2"
                  >
                    <v-chip
                      value="v1"
                      size="small"
                      variant="outlined"
                      class="me-2"
                    >
                      v1 - 包含所有材料
                    </v-chip>
                    <v-chip
                      value="v2"
                      size="small"
                      variant="outlined"
                    >
                      v2 - 只帶入有單價的材料
                    </v-chip>
                  </v-chip-group>
                  <div class="text-caption text-grey-darken-1">
                    {{ materialGenerationVersion === 'v1' ? '帶入所有材料項目（含無單價項目）' : '只帶入資料庫中具有單價的材料項目' }}
                  </div>
                </div>
              </v-sheet>
              <div class="d-flex gap-3">
                <v-btn
                  color="success"
                  class="flex-grow-1"
                  block
                  variant="flat"
                  rounded="lg"
                  size="large"
                  :loading="isLoadingMaterials"
                  :disabled="!canAutoFillMaterials"
                  @click="autoFillMaterials"
                >
                  <v-icon
                    start
                    size="small"
                  >
                    mdi-autorenew
                  </v-icon>
                  自動帶入材料 ({{ materialGenerationVersion.toUpperCase() }})
                </v-btn>
              </div>
              <div
                v-if="!canAutoFillMaterials"
                class="text-caption text-red pb-0 mt-4 border-t border-grey-lighten-2"
              >
                請先完成上方配置中的必填欄位，才能自動帶入材料
                <v-btn
                  variant="text"
                  size="small"
                  color="info"
                  class="ml-2 mt-n1"
                  @click="showMissingFieldsInfo"
                >
                  查看缺少欄位
                </v-btn>
              </div>
            </template>
          </v-card>

          <!-- STEP 5: 已新增管路設施列表 -->
          <v-card-title
            class="text-subtitle-1 font-weight-bold pa-0 pb-2"
            style="color: #2d8c8f"
          >
            <v-icon
              color="#3ea0a3"
              class="me-2 mb-0 pb-0"
              size="small"
            >
              mdi-format-list-bulleted
            </v-icon>
            管路設施列表
          </v-card-title>

          <!-- 💰 個人年度補助額度資訊 -->
          <v-alert
            v-if="grantsStore.hasSubsidySummary && localFormData.pipes.length > 0"
            type="info"
            variant="tonal"
            density="compact"
            class="mb-3"
            prominent
            border="start"
          >
            <template #prepend>
              <v-icon size="small">
                mdi-calculator
              </v-icon>
            </template>
            <div class="text-body-2">
              <div class="font-weight-bold mb-2">
                個人年度補助額度使用狀況
              </div>
              <v-row dense>
                <v-col
                  cols="12"
                  sm="6"
                  md="3"
                >
                  <div class="text-caption text-grey-darken-1">
                    個人年度上限
                  </div>
                  <div class="text-subtitle-2 font-weight-bold">
                    NT$ {{ grantsStore.subsidyLimit.toLocaleString() }}
                  </div>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="3"
                >
                  <div class="text-caption text-grey-darken-1">
                    個人其他案件已用
                  </div>
                  <div class="text-subtitle-2 font-weight-bold">
                    NT$ {{ grantsStore.totalSubsidyAmount.toLocaleString() }}
                  </div>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="3"
                >
                  <div class="text-caption text-grey-darken-1">
                    本案件規劃補助（含灌溉調控設施）
                  </div>
                  <div class="text-subtitle-2 font-weight-bold text-primary">
                    NT$ {{ currentGrantTotalSubsidy.toLocaleString() }}
                  </div>
                </v-col>
                <v-col
                  cols="12"
                  sm="6"
                  md="3"
                >
                  <div class="text-caption text-grey-darken-1">
                    剩餘可用額度
                  </div>
                  <div class="text-subtitle-2 font-weight-bold">
                    NT$ {{ remainingSubsidyQuota.toLocaleString() }}
                  </div>
                </v-col>
              </v-row>
              <v-divider class="my-2" />
              <div class="text-caption">
                灌溉調控設施補助：NT$ {{ step3SubsidyAmount.toLocaleString() }} |
                田間管路補助：NT$ {{ (localFormData.subsidyAmount || 0).toLocaleString() }} |
                使用率：{{ quotaUsageRate }}%
              </div>
            </div>
          </v-alert>

          <v-sheet
            class="mt-2 pb-4 rounded"
            color="white"
          >
            <v-row>
              <v-col
                cols="12"
              >
                <v-table
                  class="rounded border"
                  density="compact"
                >
                  <thead class="bg-grey-lighten-3">
                    <tr>
                      <th
                        class="text-center px-2"
                        style="width: 100px; min-width: 40px;"
                      >
                        項目
                      </th>
                      <th
                        class="px-2"
                        style="width: auto; min-width: 70px;"
                      >
                        名稱
                      </th>
                      <th
                        class="text-center px-2"
                        style="width: 80px; min-width: 70px;"
                      >
                        類別
                      </th>
                      <th
                        class="text-center px-2"
                        style="width: 80px; min-width: 70px;"
                      >
                        規格
                      </th>
                      <th
                        class="text-center px-2"
                        style="width: 80px; min-width: 30px;"
                      >
                        單位
                      </th>
                      <th
                        class="px-2"
                        style="width: auto; min-width: 120px;"
                      >
                        說明
                      </th>
                      <th
                        class="text-center px-2"
                        style="width: 100px; min-width: 100px;"
                      >
                        數量
                      </th>
                      <th
                        class="text-center px-2"
                        style="width: 100px; min-width: 80px;"
                      >
                        單價
                      </th>
                      <th
                        class="text-center px-2"
                        style="width: 120px; min-width: 100px;"
                      >
                        總價
                      </th>
                      <th
                        class="text-center px-2"
                        style="width: 80px; min-width: 30px;"
                      >
                        刪除
                      </th>
                      <th
                        class="text-center px-2"
                        style="width: 80px; min-width: 30px;"
                      >
                        排序
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <template
                      v-for="(group, groupIndex) in groupedPipes"
                      :key="`group-${group.groupNo}`"
                    >
                      <tr class="bg-grey-lighten-5">
                        <td
                          colspan="11"
                          class="py-2 px-3 font-weight-bold text-body-2"
                        >
                          {{ groupIndex + 1 }}. {{ group.groupName }}
                          <v-btn
                            variant="text"
                            size="small"
                            color="primary"
                            class="text-caption"
                            @click="openManualAddDialog(group.groupNo)"
                          >
                            <v-icon
                              start
                              size="x-small"
                            >
                              mdi-plus
                            </v-icon>
                            新增材料
                          </v-btn>
                        </td>
                      </tr>
                      <tr
                        v-for="(pipe, pipeIndex) in group.items"
                        :key="`pipe-${group.groupNo}-${pipe.pomno}-${pipeIndex}`"
                      >
                        <td class="text-center px-2">
                          <div class="d-flex align-center justify-center">
                            <span class="text-body-2">{{ groupIndex + 1 }}-{{ pipe.order }}</span>
                          </div>
                        </td>
                        <td class="px-2">
                          <div
                            class="text-body-2"
                            style="word-break: break-word;"
                          >
                            {{ pipe.matname }}
                          </div>
                        </td>
                        <td class="text-center px-2">
                          <div class="text-body-2">
                            {{ pipe.module }}
                          </div>
                        </td>
                        <td class="text-center px-2">
                          <div class="text-body-2">
                            {{ pipe.specification }}
                          </div>
                        </td>
                        <td class="text-center px-2">
                          <div class="text-body-2">
                            {{ pipe.itemunit }}
                          </div>
                        </td>
                        <td class="px-2">
                          <div
                            class="text-body-2"
                            style="word-break: break-word;"
                          >
                            {{ pipe.description }}
                          </div>
                        </td>
                        <td class="text-center px-1">
                          <v-text-field
                            v-model.number="pipe.matamount"
                            type="number"
                            min="0"
                            density="compact"
                            variant="outlined"
                            hide-details="auto"
                            class="material-input"
                            style="min-width: 80px;"
                            :rules="[
                              v => v >= 0 || '數量不能為負數'
                            ]"
                            @update:model-value="(value) => updatePipeQuantity(group.groupNo, pipeIndex, Number(value) || 0)"
                          />
                        </td>
                        <td class="text-center px-1">
                          <v-text-field
                            v-model.number="pipe.matprice"
                            type="number"
                            min="0"
                            step="1"
                            density="compact"
                            variant="outlined"
                            hide-details="auto"
                            class="material-input"
                            style="min-width: 80px;"
                            :rules="[
                              v => v >= 0 || '單價不能為負數'
                            ]"
                            @update:model-value="(value) => updatePipePrice(group.groupNo, pipeIndex, Number(value) || 0)"
                          />
                        </td>
                        <td class="text-center px-1">
                          <div class="text-body-2 font-weight-medium">
                            {{ pipe.totalPrice?.toLocaleString() }}
                          </div>
                        </td>
                        <td class="text-center px-1">
                          <v-btn
                            icon
                            size="x-small"
                            color="error"
                            variant="text"
                            @click="removePipe(group.groupNo, pipeIndex)"
                          >
                            <v-icon size="small">
                              mdi-close
                            </v-icon>
                          </v-btn>
                        </td>
                        <td class="text-center px-0">
                          <div class="d-flex flex-column align-center ga-1">
                            <v-btn
                              icon
                              size="x-small"
                              color="primary"
                              variant="text"
                              :disabled="pipeIndex === 0"
                              @click="movePipeUp(group.groupNo, pipeIndex)"
                            >
                              <v-icon size="small">
                                mdi-chevron-up
                              </v-icon>
                            </v-btn>
                            <v-btn
                              icon
                              size="x-small"
                              color="primary"
                              variant="text"
                              :disabled="pipeIndex === group.items.length - 1"
                              @click="movePipeDown(group.groupNo, pipeIndex)"
                            >
                              <v-icon size="small">
                                mdi-chevron-down
                              </v-icon>
                            </v-btn>
                          </div>
                        </td>
                      </tr>
                    </template>

                    <tr v-if="localFormData.pipes.length === 0">
                      <td
                        colspan="11"
                        class="text-center py-4 text-grey"
                      >
                        點擊「自動帶入材料」或手動新增管路設施
                      </td>
                    </tr>
                    <tr
                      v-if="localFormData.pipes.length !== 0"
                      class="bg-grey-lighten-4"
                    >
                      <td
                        colspan="8"
                        class="text-right font-weight-bold px-2 py-2"
                      >
                        合計
                      </td>
                      <td class="text-center font-weight-bold px-2 py-2">
                        <div class="text-body-1 font-weight-bold text-primary">
                          {{ (localFormData.totalAmount || 0).toLocaleString() }}
                        </div>
                        <div class="text-caption text-grey-darken-1 mt-1">
                          <template v-if="isLegacyData">
                            歷史案件格式，設計費 ${{ (localFormData.designFee || 0).toLocaleString() }} 另計
                          </template>
                          <template v-else>
                            （設計費 ${{ (localFormData.designFee || 0).toLocaleString() }}）
                          </template>
                        </div>
                      </td>
                      <td colspan="2" />
                    </tr>
                  </tbody>
                </v-table>
              </v-col>
            </v-row>
          </v-sheet>

          <!-- 💰 金額統計區塊 -->
          <div
            v-if="localFormData.pipes.length > 0"
            class="mb-4"
          >
            <v-row>
              <v-col
                cols="12"
                md="6"
              >
                <v-card
                  class="pa-4 text-center"
                  color="green-lighten-5"
                  variant="outlined"
                >
                  <v-icon
                    class="mb-2"
                    color="green-darken-2"
                    size="large"
                  >
                    mdi-hand-coin
                  </v-icon>
                  <div class="text-h6 text-green-darken-2 font-weight-bold">
                    補助款總額
                  </div>
                  <div class="text-h4 text-green-darken-3 font-weight-bold mt-2">
                    ${{ (localFormData.subsidyAmount || 0).toLocaleString() }}
                  </div>
                  <div class="text-caption text-green-darken-1 mt-1">
                    共 {{ localFormData.pipes.length }} 項管路設施
                  </div>
                </v-card>
              </v-col>
              <v-col
                cols="12"
                md="6"
              >
                <v-card
                  class="pa-4 text-center"
                  color="orange-lighten-5"
                  variant="outlined"
                >
                  <v-icon
                    class="mb-2"
                    color="orange-darken-2"
                    size="large"
                  >
                    mdi-wallet
                  </v-icon>
                  <div class="text-h6 text-orange-darken-2 font-weight-bold">
                    自備款總額
                  </div>
                  <div class="text-h4 text-orange-darken-3 font-weight-bold mt-2">
                    ${{ (localFormData.selfPaidAmount || 0).toLocaleString() }}
                  </div>
                  <div class="text-caption text-orange-darken-1 mt-1">
                    {{ localFormData.selfPaidAmount > 0 ? '田間管路設計超過補助限額，增加相應之自備款' : '無需自備款' }}
                  </div>
                </v-card>
              </v-col>
            </v-row>

            <!-- ⚠️ 年度餘額限制警告 -->
            <v-alert
              v-if="isSubsidyLimitedByQuota"
              type="warning"
              variant="tonal"
              class="mt-3"
              density="compact"
            >
              <template #prepend>
                <v-icon>mdi-alert-circle</v-icon>
              </template>
              <div class="text-body-2">
                <strong>補助金額受個人年度補助餘額限制</strong>
              </div>
              <div class="text-caption mt-1">
                本案件補助金額已依據您的個人年度補助餘額調整。
                扣除「灌溉調控設施」(step3) 已使用的 NT$ {{ step3SubsidyAmount.toLocaleString() }} 後，
                剩餘可用額度不足以支付完整的灌溉系統補助上限，因此自備款金額相應增加。
              </div>
            </v-alert>
          </div>
        </v-form>
      </v-card-text>
    </v-card>
  </div>

  <!-- 除錯資訊對話框 -->
  <v-dialog
    v-model="debugDialog"
    max-width="800px"
    scrollable
  >
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon
          class="me-2"
          color="info"
        >
          mdi-bug
        </v-icon>
        <span>材料比對除錯資訊</span>
        <v-spacer />
        <v-btn
          icon
          variant="text"
          @click="debugDialog = false"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text v-if="selectedMaterialDebugInfo">
        <v-row>
          <!-- 生成的材料資訊 -->
          <v-col
            cols="12"
            md="6"
          >
            <v-card
              variant="outlined"
              class="mb-4"
            >
              <v-card-title class="bg-blue-lighten-5 py-2">
                <v-icon
                  class="me-2"
                  size="small"
                >
                  mdi-wrench
                </v-icon>
                生成的材料資訊
              </v-card-title>
              <v-card-text class="pa-3">
                <v-table density="compact">
                  <tbody>
                    <tr>
                      <td class="font-weight-bold">
                        POMNO
                      </td>
                      <td>{{ selectedMaterialDebugInfo.generated.pomno }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        模組
                      </td>
                      <td>{{ selectedMaterialDebugInfo.generated.module }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        模組ID
                      </td>
                      <td>{{ selectedMaterialDebugInfo.generated.module_id }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        材料名稱
                      </td>
                      <td>{{ selectedMaterialDebugInfo.generated.matname }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        材質
                      </td>
                      <td>{{ selectedMaterialDebugInfo.generated.mattype || 'N/A' }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        規格1
                      </td>
                      <td>{{ selectedMaterialDebugInfo.generated.spec1 || 'N/A' }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        規格2
                      </td>
                      <td>{{ selectedMaterialDebugInfo.generated.spec2 || 'N/A' }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        規格3
                      </td>
                      <td>{{ selectedMaterialDebugInfo.generated.spec3 || 'N/A' }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        單價
                      </td>
                      <td>{{ selectedMaterialDebugInfo.generated.matprice }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        數量
                      </td>
                      <td>{{ selectedMaterialDebugInfo.generated.matamount }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- 比對狀態與條件 -->
          <v-col
            cols="12"
            md="6"
          >
            <v-card
              variant="outlined"
              class="mb-4"
            >
              <v-card-title
                class="py-2"
                :class="selectedMaterialDebugInfo.matchStatus === 'success' ? 'bg-green-lighten-5' : 'bg-red-lighten-5'"
              >
                <v-icon
                  class="me-2"
                  size="small"
                  :color="selectedMaterialDebugInfo.matchStatus === 'success' ? 'success' : 'error'"
                >
                  {{ selectedMaterialDebugInfo.matchStatus === 'success' ? 'mdi-check-circle' : 'mdi-alert-circle' }}
                </v-icon>
                比對狀態: {{ selectedMaterialDebugInfo.matchStatus === 'success' ? '成功' : '失敗' }}
              </v-card-title>
              <v-card-text class="pa-3">
                <div class="mb-3">
                  <div class="font-weight-bold mb-2">
                    比對條件:
                  </div>
                  <v-chip-group column>
                    <v-chip
                      size="small"
                      color="primary"
                    >
                      模組ID: {{ selectedMaterialDebugInfo.matchCriteria.module_id }}
                    </v-chip>
                    <v-chip
                      size="small"
                      color="secondary"
                    >
                      規格: {{ selectedMaterialDebugInfo.matchCriteria.spec1 }}
                    </v-chip>
                    <v-chip
                      v-if="selectedMaterialDebugInfo.matchCriteria.mattype"
                      size="small"
                      color="accent"
                    >
                      材質: {{ selectedMaterialDebugInfo.matchCriteria.mattype }}
                    </v-chip>
                  </v-chip-group>
                </div>
              </v-card-text>
            </v-card>

            <!-- 比對的 pipeFittingsStore 資料 -->
            <v-card
              v-if="selectedMaterialDebugInfo.matched"
              variant="outlined"
            >
              <v-card-title class="bg-green-lighten-5 py-2">
                <v-icon
                  class="me-2"
                  size="small"
                  color="success"
                >
                  mdi-database-check
                </v-icon>
                比對的 Store 資料
              </v-card-title>
              <v-card-text class="pa-3">
                <v-table density="compact">
                  <tbody>
                    <tr>
                      <td class="font-weight-bold">
                        POMNO
                      </td>
                      <td>{{ selectedMaterialDebugInfo.matched.pomno }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        名稱
                      </td>
                      <td>{{ selectedMaterialDebugInfo.matched.name }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        模組ID
                      </td>
                      <td>{{ selectedMaterialDebugInfo.matched.module_id }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        材質ID
                      </td>
                      <td>{{ selectedMaterialDebugInfo.matched.material_id }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        材質名稱
                      </td>
                      <td>{{ selectedMaterialDebugInfo.matched.material?.name || 'N/A' }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        規格1 ID
                      </td>
                      <td>{{ selectedMaterialDebugInfo.matched.diameter1_id || 'N/A' }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        規格1 值
                      </td>
                      <td>{{ selectedMaterialDebugInfo.matched.diameter1?.value || 'N/A' }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        規格1 名稱
                      </td>
                      <td>{{ selectedMaterialDebugInfo.matched.diameter1?.name || 'N/A' }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        目前價格
                      </td>
                      <td class="text-success font-weight-bold">
                        {{ selectedMaterialDebugInfo.matched.current_price || 'N/A' }}
                      </td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        單位
                      </td>
                      <td>{{ selectedMaterialDebugInfo.matched.unit || 'N/A' }}</td>
                    </tr>
                    <tr>
                      <td class="font-weight-bold">
                        說明
                      </td>
                      <td>{{ selectedMaterialDebugInfo.matched.description || 'N/A' }}</td>
                    </tr>
                  </tbody>
                </v-table>
              </v-card-text>
            </v-card>

            <!-- 未比對提示 -->
            <v-card
              v-else
              variant="outlined"
            >
              <v-card-title class="bg-red-lighten-5 py-2">
                <v-icon
                  class="me-2"
                  size="small"
                  color="error"
                >
                  mdi-database-remove
                </v-icon>
                未找到比對資料
              </v-card-title>
              <v-card-text class="pa-3">
                <v-alert
                  type="warning"
                  variant="tonal"
                  class="mb-0"
                >
                  在 pipeFittingsStore 中未找到符合條件的材料。使用預設的 POMNO 和價格。
                </v-alert>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn
          color="primary"
          variant="text"
          @click="debugDialog = false"
        >
          關閉
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- 手動新增材料對話框 -->
  <v-dialog
    v-model="showManualAddDialog"
    max-width="650"
    persistent
    scrollable
  >
    <v-card>
      <v-card-title
        class="text-h6 d-flex align-center pa-4"
        style="color: #2d8c8f; background-color: #f8f9fa;"
      >
        <v-icon
          color="#3ea0a3"
          class="me-3"
          size="large"
        >
          mdi-plus-circle
        </v-icon>
        <span>手動新增材料</span>
        <v-spacer />
        <v-btn
          icon
          variant="text"
          size="small"
          @click="closeManualAddDialog"
        >
          <v-icon color="#666">
            mdi-close
          </v-icon>
        </v-btn>
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-0">
        <v-container
          fluid
          class="pa-6"
        >
          <v-form
            ref="manualAddForm"
            v-model="manualAddFormValid"
          >
            <!-- 材料搜尋與選擇區塊 -->
            <v-card
              variant="outlined"
              class="mb-4"
              rounded="lg"
            >
              <v-card-title
                class="d-flex align-center py-3 px-4"
                style="background-color: #f8f9fa; color: #2d8c8f;"
              >
                <v-icon
                  color="#3ea0a3"
                  class="me-2"
                  size="small"
                >
                  mdi-magnify
                </v-icon>
                <span class="text-subtitle-1 font-weight-medium">材料搜尋</span>
              </v-card-title>

              <v-card-text class="pa-4">
                <v-autocomplete
                  v-model="selectedMaterialPomno"
                  :items="filteredMaterialOptions"
                  :item-title="item => item.searchText || item.name"
                  item-value="pomno"
                  label="搜尋並選擇材料"
                  placeholder="可搜尋材料名稱、規格管徑(如:1、1吋、3/4)、材質或型號..."
                  variant="outlined"
                  density="comfortable"
                  clearable
                  hide-details="auto"
                  autocomplete="off"
                  :loading="isLoadingMaterialOptions"
                  :no-data-text="materialSearchQuery ? '沒有找到相符的材料，請嘗試其他關鍵字或規格(如:1、1吋、3/4等)' : '請輸入關鍵字開始搜尋'"
                  :rules="[v => !!v || '請選擇材料']"
                  :search="materialSearchQuery"
                  @update:search="onMaterialSearch"
                  @update:model-value="onMaterialSelectionChange"
                >
                  <template #prepend-inner>
                    <v-icon
                      color="grey-darken-1"
                      size="small"
                    >
                      mdi-database-search
                    </v-icon>
                  </template>

                  <template #item="{ props, item }">
                    <v-list-item
                      v-bind="props"
                      class="px-4 py-3"
                    >
                      <template #title>
                        <div class="text-body-1 font-weight-medium text-grey-darken-3">
                          {{ item.raw.name }}
                        </div>
                      </template>

                      <template #subtitle>
                        <div class="d-flex flex-column mt-1">
                          <div class="text-caption text-grey-darken-1 mb-1">
                            <v-icon
                              size="x-small"
                              class="me-1"
                              color="grey-darken-1"
                            >
                              mdi-identifier
                            </v-icon>
                            POMNO: {{ item.raw.pomno }}
                          </div>

                          <div class="d-flex flex-wrap ga-1">
                            <v-chip
                              v-if="item.raw.material?.name"
                              size="x-small"
                              color="#3ea0a3"
                              variant="tonal"
                            >
                              {{ item.raw.material.name }}
                            </v-chip>

                            <v-chip
                              v-if="item.raw.module?.name"
                              size="x-small"
                              color="blue-grey"
                              variant="tonal"
                            >
                              {{ item.raw.module.name }}
                            </v-chip>

                            <v-chip
                              v-if="getDiameterDisplay(item.raw)"
                              size="x-small"
                              color="indigo"
                              variant="tonal"
                            >
                              {{ getDiameterDisplay(item.raw) }}
                            </v-chip>

                            <v-chip
                              v-if="item.raw.current_price"
                              size="x-small"
                              color="green"
                              variant="tonal"
                              class="font-weight-medium"
                            >
                              ${{ item.raw.current_price.toLocaleString() }}
                            </v-chip>

                            <v-chip
                              v-else
                              size="x-small"
                              color="orange"
                              variant="tonal"
                            >
                              無單價
                            </v-chip>
                          </div>
                        </div>
                      </template>
                    </v-list-item>
                  </template>

                  <template #no-data>
                    <v-list-item class="text-center py-4">
                      <template #title>
                        <div class="text-grey-darken-1">
                          <v-icon
                            size="large"
                            color="grey-darken-1"
                            class="mb-2"
                          >
                            {{ materialSearchQuery ? 'mdi-magnify-close' : 'mdi-magnify' }}
                          </v-icon>
                          <div>{{ materialSearchQuery ? '沒有找到相符的材料' : '請輸入關鍵字開始搜尋' }}</div>
                        </div>
                      </template>
                    </v-list-item>
                  </template>
                </v-autocomplete>
              </v-card-text>
            </v-card>

            <!-- 選中材料的詳細資訊 -->
            <v-card
              v-if="selectedMaterial"
              variant="outlined"
              class="mb-4"
              rounded="lg"
            >
              <v-card-title
                class="d-flex align-center py-3 px-4"
                style="background-color: #f0f8f8; color: #2d8c8f;"
              >
                <v-icon
                  color="#3ea0a3"
                  class="me-2"
                  size="small"
                >
                  mdi-check-circle
                </v-icon>
                <span class="text-subtitle-1 font-weight-medium">選中的材料</span>
              </v-card-title>

              <v-card-text class="pa-4">
                <div class="d-flex align-center">
                  <div class="flex-grow-1">
                    <div class="text-body-1 font-weight-medium text-grey-darken-3">
                      {{ selectedMaterial.name }}
                    </div>
                    <div class="text-caption text-grey-darken-1 mt-1">
                      <v-icon
                        size="x-small"
                        class="me-1"
                        color="grey-darken-1"
                      >
                        mdi-identifier
                      </v-icon>
                      POMNO: {{ selectedMaterial.pomno }}
                    </div>

                    <div class="d-flex flex-wrap mt-2 ga-1">
                      <v-chip
                        v-if="selectedMaterial.material?.name"
                        size="small"
                        color="#3ea0a3"
                        variant="tonal"
                      >
                        {{ selectedMaterial.material.name }}
                      </v-chip>

                      <v-chip
                        v-if="selectedMaterial.module?.name"
                        size="small"
                        color="blue-grey"
                        variant="tonal"
                      >
                        {{ selectedMaterial.module.name }}
                      </v-chip>

                      <v-chip
                        v-if="getDiameterDisplay(selectedMaterial)"
                        size="small"
                        color="indigo"
                        variant="tonal"
                      >
                        {{ getDiameterDisplay(selectedMaterial) }}
                      </v-chip>

                      <v-chip
                        v-if="selectedMaterial.current_price"
                        size="small"
                        color="green"
                        variant="tonal"
                        class="font-weight-medium"
                      >
                        單價: ${{ selectedMaterial.current_price.toLocaleString() }}
                      </v-chip>

                      <v-chip
                        v-else
                        size="small"
                        color="orange"
                        variant="tonal"
                      >
                        無單價資訊
                      </v-chip>
                    </div>
                  </div>

                  <v-chip
                    size="small"
                    color="#3ea0a3"
                    variant="outlined"
                    class="font-weight-medium"
                  >
                    {{ selectedMaterial.unit || '個' }}
                  </v-chip>
                </div>
              </v-card-text>
            </v-card>

            <!-- 表單輸入區域 -->
            <v-row>
              <!-- 選擇組別 -->
              <v-col
                cols="12"
                md="6"
              >
                <v-select
                  v-model="selectedGroup"
                  :items="materialGroupOptions"
                  item-title="name"
                  item-value="id"
                  label="選擇材料組別"
                  variant="outlined"
                  required
                  hide-details="auto"
                  :rules="[v => !!v || '請選擇材料組別']"
                >
                  <template #prepend-inner>
                    <v-icon
                      color="grey-darken-1"
                      size="small"
                    >
                      mdi-group
                    </v-icon>
                  </template>
                </v-select>
              </v-col>

              <!-- 數量輸入 -->
              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model.number="materialQuantity"
                  type="number"
                  label="數量"
                  variant="outlined"
                  min="1"
                  step="1"
                  required
                  hide-details="auto"
                  :rules="[
                    v => !!v || '請輸入數量',
                    v => v > 0 || '數量必須大於0'
                  ]"
                >
                  <template #prepend-inner>
                    <v-icon
                      color="grey-darken-1"
                      size="small"
                    >
                      mdi-numeric
                    </v-icon>
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-container>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          variant="outlined"
          size="large"
          @click="closeManualAddDialog"
        >
          <v-icon
            size="small"
            class="me-1"
          >
            mdi-close
          </v-icon>
          取消
        </v-btn>
        <v-btn
          color="#3ea0a3"
          variant="flat"
          size="large"
          :disabled="!canAddMaterial"
          :loading="isAddingMaterial"
          @click="addMaterialToList"
        >
          <v-icon
            size="small"
            class="me-1"
          >
            mdi-plus
          </v-icon>
          新增材料
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import Big from 'big.js';
import { nextTick } from 'vue'
import { useGrantsStore } from '@/stores/grants';
import { useOfficesStore } from '@/stores/offices'
import { usePipeFittingsStore } from '@/stores/pipeFittingsStore'
import { usePFDiametersStore } from '@/stores/pfDiametersStore'
import { usePFMaterialsStore } from '@/stores/pfMaterialsStore'
import { useIrrigationTypesStore } from '@/stores/irrigationTypesStore'
import type { PipeFitting } from '@/types/pipeFittings'
import type { MaterialItem, MaterialGroup } from '@/types/step4Materials'
import {
  calculatePipelineSubsidyAllocation,
  determineRegionType,
  getPipelineSubsidyLimit,
  type PipelineSubsidyResult
} from '@/utils/subsidyStandards'


// Type definitions for material generation
interface MaterialData {
  pomno: number;
  groupId: number;
  groupName?: string;
  module: string;
  moduleType?: string;
  matname: string;
  mattype?: string;
  specification: string;
  spec1?: string;
  spec2?: string;
  spec3?: string;
  itemunit: string;
  description: string;
  matprice: number;
  matamount: number;
  totalPrice: number;
  order?: number;
  GroupNo?: number;
  GroupName?: string;
  List?: Array<{
    pomno: number;
    groupId: number;
    groupName?: string;
    module: string;
    matname: string;
    mattype?: string;
    specification: string;
    spec1?: string;
    spec2?: string;
    spec3?: string;
    itemunit: string;
    description: string;
    matprice: number;
    matamount: number;
    totalPrice: number;
    order?: number;
  }>;
  // Legacy properties
  Length?: string | number;
  width?: string | number;
  L1Len?: number;
  L1Material?: number;
  L1Spec?: number;
  L1Price?: number;
  L1MatAmt?: number;
  L1Bend?: number;
  L1Receptacle?: number;
  L2Len?: number;
  L2Material?: number;
  L2Spec?: number;
  L2Price?: number;
  L2MatAmt?: number;
  L2Bend?: number;
  ddl_EndType?: number;
  ddl_Sprinkler?: number;
  ddl_Drop?: number;
  ddl_FacType?: number;
  ddl_WtaerSrc?: number;
  SL?: number;
  SS?: number;
  BranchMaterial?: number;
  BranchSpec?: number;
  BranchLength?: string | number;
  StdpipeMat?: number;
  StdpipeSpec?: number;
  NozzleMaterial?: number;
  NozzleSpec?: number;
  H?: number;
  PerforatedPipe?: number;
  SpecChange?: number;
  BranchAmt?: number;
  NozzleAmt?: number;
}

interface FormInputs {
  Length?: number | null;
  width?: number | null;
  L1Len?: number | null;
  L1Material?: number | null;
  L1Spec?: number | null;
  L1Price?: number;
  L1MatAmt?: number;
  L2Len?: number | null;
  L2Material?: number | null;
  L2Spec?: number | null;
  L2Price?: number;
  L2MatAmt?: number;
  ddl_EndType?: number;
  ddl_Sprinkler?: number;
  ddl_Drop?: number;
  ddl_FacType?: number;
  ddl_WtaerSrc?: number;
  SL?: number;
  SS?: number;
  BranchMaterial?: number;
  BranchSpec?: number;
  StdpipeMat?: number;
  StdpipeSpec?: number;
  NozzleMaterial?: number;
  NozzleSpec?: number;
  H?: number;
  PerforatedPipe?: number;
  SpecChange?: number;
  [key: string]: string | number | boolean | null | undefined;
}

interface MaterialData {
  pomno: number;
  groupId: number;
  groupName?: string;
  module: string;
  module_id?: number;
  matname: string;
  mattype?: string;
  specification: string;
  spec1?: string;
  spec2?: string;
  spec3?: string;
  itemunit: string;
  description: string;
  matprice: number;
  matamount: number;
  totalPrice: number;
  order?: number;
  moduleType?: string;
  // Add missing properties that are referenced in the code
  List?: MaterialData[];
  GroupNo?: number;
  GroupName?: string;
}

interface PipeOption {
  id: number | string;
  name: string;
  standardLength?: number;
}

interface EndFacilityPipeFitting {
    pomno: number;
    displayName: string; // 例如: "PVC噴頭 1/2吋"
    materialName: string;
    materialId?: number; // 材質ID (material_id) - 用於自動同步到豎管材質
    specName: string; // 主要規格描述
    specId?: number; // 主要規格ID (diameter1_id)
    // 其他 pipe_fittings 表的相關欄位
}

// Props and emits
const props = defineProps({
  formData: {
    type: Object as PropType<any>, // 應定義更精確的類型
    required: true,
    default: () => ({})
  },
  currentStep: {
    type: Number,
    required: true
  },
  readonly: {
    type: Boolean,
    required: false,
    default: false
  },
  softLocked: {
    type: Boolean,
    required: false,
    default: false
  }
});

const emit = defineEmits(['update:formData', 'validated', 'go-back', 'show-snackbar']);

// Access the store
const grantsStore = useGrantsStore();
const officesStore = useOfficesStore();
const pipeFittingsStore = usePipeFittingsStore();
const pfDiametersStore = usePFDiametersStore();
const pfMaterialsStore = usePFMaterialsStore();
const irrigationTypesStore = useIrrigationTypesStore()
const route = useRoute();


// Store the filtered pipe fittings
// const filteredPipeFittings = ref([]);

// Form validation references
const form = ref<HTMLFormElement | null>(null); // 顯式類型
const localValid = ref(true);
const stepContent = ref<HTMLElement | null>(null); // 顯式類型

// 設計人姓名編輯狀態控制
// 初始值會在 onMounted 中根據 props.formData.designerName 設置
const isEditingDesigner = ref(false);

// 載入與計算狀態
const isLoadingMaterials = ref(false);
const isLoadingMaterialOptions = ref(false);
// 材料生成版本控制
const materialGenerationVersion = ref<'v1' | 'v2'>('v1');

// 手動新增材料相關狀態
const showManualAddDialog = ref(false);
const manualAddFormValid = ref(false);
const selectedMaterialPomno = ref<number | null>(null);
const selectedGroup = ref<number | null>(null);
const materialQuantity = ref<number>(1);
const materialRemark = ref<string>('');
const materialSearchQuery = ref('');
const isAddingMaterial = ref(false);
const isCalculatingSubsidy = ref(false);
const isUpdating = ref(false);
const isClearingEndFacility = ref(false);


// 除錯資訊相關
const debugDialog = ref(false);
const selectedMaterialDebugInfo = ref<any>(null);

// 本地表單數據
const localFormData = reactive({
  // 栅塊形狀和面積
  fieldLength: null as number | null,
  fieldWidth: null as number | null,
  // 🔧 facilityArea 不再是獨立欄位，改為從 Step2 計算得出
  // facilityArea: null as number | null,

  // 補助來源
  fundingSourceId: 0, // 存儲ID
  // 設計人姓名
  designerName: '' as string,

  // 主管
  mainPipeLength: null as number | null,
  mainPipeDiameterId: null as number | null, // 管徑ID
  mainPipeMaterialId: 1, // 主管主要材質ID，默認為 PVC
  mainPipeUnitPrice: null as number | null,
  mainPipeQuantity: null as number | null,
  mainPipeStandardLength: 4, // 主管1的標準長度，應動態獲取

  //主管2
  mainPipe2Enabled: false,
  mainPipe2Length: null as number | null,
  mainPipe2DiameterId: null as number | null,
  mainPipe2MaterialId: 1, // 主管2主要材質ID，默認為 PVC
  mainPipe2UnitPrice: null as number | null,
  mainPipe2Quantity: null as number | null,
  mainPipe2StandardLength: 4, // 主管2的標準長度，應動態獲取

  // 支管
  branchPipeSpacing_SL: null as number | null, // SL
  sprinklerSpacing_SS: null as number | null,  // SS
  riserHeight_H: null as number | null,        // H
  enableBranchDiameterChange: false, // 是否啟用支管變徑功能
  changeBranchSpecId: null as number | null, // 變徑規格ID (原 variantType/Adjustable)
  branchPipeMaterialId: null as number | null, // 支管主要材質ID
  branchPipeDiameterId: null as number | null, // 支管主要管徑ID
  branchPipePomno: null as number | null, // 滴水管件POMNO (ID=7時使用)

  // Legacy properties for backward compatibility
  variantType: '',
  branchPipeLength: '',
  branchPipeDiameter: '',
  branchPipeMaterial: '',
  branchPipeUnitPrice: '',
  branchPipeQuantity: '',

  // Missing properties referenced in the code
  branchPipeSpacing: null as number | null,
  sprinklerSpacing: null as number | null,
  riserHeight: null as number | null,
  mainPipeMaterial: '',
  mainPipeDiameter: '',
  fundingSource: '',
  irrigationType: '',
  waterSource: '',
  perforatedPipeType: null as number | null,
  sprinklerType: null as number | null,
  dripperType: null as number | null,
  endFacilityType: '',
  endFacilityDiameter: '',
  endFacilityMaterial: '',
  endFacilityUnitPrice: '',
  endFacilityQuantity: '',

  // 末端設施
  irrigationTypeId: null as number | null,       // 灌溉型式ID
  sprinklerSubtypeId: null as number | null,   // 噴頭子類型ID (原 ddl_Sprinkler)
  dripperSubtypeId: null as number | null,     // 滴灌子類型ID (原 ddl_Drop)
  perforatedPipeDirection: 1,                // 穿孔管出水方向 (原 ddl_Perforated)
  installationType: null as number | null,       // 設施型式ID (原 ddl_FacType)
  waterSourceId: null as number | null,        // 灌溉水源ID (原 ddl_WtaerSrc)

  endFacilityPomno: null as number | null,     // 末端設施POMNo (原 NozzleMaterial)
  endFacilitySpecId: null as number | null,    // 末端設施主要規格ID (原 NozzleSpec)
  // 豎管材質與規格，如果獨立於末端設施選擇
  riserPipeMaterialId: null as number | null, // 豎管材質ID (原 StdpipeMat)
  riserPipeSpecId: null as number | null,     // 豎管規格ID (原 StdpipeSpec)

  // 管路列表 (結構將由API響應決定，這裡的初始值不重要)
  pipes: [] as Array<{
    pomno: number; // 新增: 材料的POMNo
    groupId: number;
    groupName?: string; // 新增: 組名
    module: string;    // 原 moduleType
    matname: string;   // 原 name
    mattype?: string;  // 新增: 材質類型名稱
    specification: string;
    spec1?: string; spec2?: string; spec3?: string; // 新增: 分解規格
    itemunit: string;  // 原 unit
    description: string;
    matprice: number;  // 原 unitPrice
    matamount: number; // 原 quantity
    totalPrice: number;
    order?: number;    // 新增: 組內排序
  }>,

  // 補助計算結果
  totalAmount: 0,
  subsidyAmount: 0,
  selfPaidAmount: 0,
  designFee: 0,

  // Always valid for seamless navigation
  valid: true
});

const getStepDataSafely = (step: number) => {
  const currentCaseNumber = route.query.id as string;

  // 確保只處理當前案件的資料
  if (!currentCaseNumber || grantsStore.caseNumber !== currentCaseNumber) {
    return null;
  }

  const formData = grantsStore.formData[step];
  const allStepsData = (grantsStore.currentGrant?.active_version as any)?.all_steps_data?.steps?.[step.toString()];

  // 檢查 formData 是否屬於當前案件（透過 _caseNumber 欄位比對）
  const formDataCaseNumber = formData?._caseNumber;
  const isFormDataValid = formDataCaseNumber === currentCaseNumber;

  if (isFormDataValid && formData && Object.keys(formData).length > 1) { // >1 因為至少有 _caseNumber
    console.log(`✅ Step3: Using formData for step ${step} (case: ${formDataCaseNumber})`);
    return formData; // 使用 formData（即時同步）
  }

  // 使用 all_steps_data 作為備用資料源
  return (allStepsData && Object.keys(allStepsData).length > 0) ? allStepsData : null;
};

// --- 選項列表 (應從API獲取) ---
const perforatedPipeTypeOptions = ref([ { value: 1, title: '單向' }, { value: 2, title: '雙向' } ]); // 這個選項較固定
const installationTypeOptions = ref<PipeOption[]>([]);   // 設施型式
const waterSourceOptions = ref<PipeOption[]>([]);    // 灌溉水源


const irrigationTypeOptions = computed(() => {
  return irrigationTypesStore.getIrrigationTypeSelectOptions
})

const sprinklerTypeOptions = computed(() => {
  return irrigationTypesStore.getSprinklerTypeOptions
})

const dripperTypeOptions = computed(() => {
  return irrigationTypesStore.getDripperTypeOptions
})
// 末端設施的選項列表 (動態載入)
const filteredEndFacilityPipeFittings = ref<EndFacilityPipeFitting[]>([]);

// ID=7滴水管件的選項列表 (使用與ID=8相同的資料來源)
const filteredBranchPipeFittings = ref<EndFacilityPipeFitting[]>([]);

// --- 模擬API獲取下拉選單數據 ---
const loadDropdownOptions = async () => {
  await officesStore.fetchOffices();
  await pfDiametersStore.fetchDiameters();
  await pfMaterialsStore.fetchMaterials();
  await irrigationTypesStore.fetchIrrigationTypeOptions()
  await fetchPipeFittings();

  // 模擬設施型式和水源選項
  installationTypeOptions.value = [ {id: 1, name: '埋設固定式'}, {id: 2, name: '地表定置式'}, {id: 3, name: '附掛棚架式'}];
  waterSourceOptions.value = [ {id:1, name: '灌溉渠道'}, {id:2, name: '山溪溝'}, {id:3, name: '埤(池)塘'}, {id:4, name: '地下水'}, {id:5, name: '其他'} /* ... */];
};

const pipeDiameterOptions = computed(() => {
  // 使用主管模塊的管件來提取管徑選項
  const mainPipeFittings = filteredPipeFittingsByModule.value.mainPipe || [];

  // 根據當前選擇的材質ID過濾管徑
  const materialDiameterFiltered = mainPipeFittings
    .filter(fitting =>
      !localFormData.mainPipeMaterialId || // 如果没有选择材质则不过滤
      fitting.material_id === localFormData.mainPipeMaterialId
    )
    .map(fitting => fitting.diameter1_id)
    .filter(id => id != null);

  // 獲取唯一的管徑ID列表
  const uniqueDiameterIds = [...new Set([
    ...materialDiameterFiltered,
    // 加入當前已選擇的管徑ID（如果有值）
    ...(localFormData.mainPipeDiameterId ? [localFormData.mainPipeDiameterId] : []),
    ...(localFormData.mainPipe2Enabled && localFormData.mainPipe2DiameterId ? [localFormData.mainPipe2DiameterId] : [])
  ])];

  // 獲取完整的管徑列表
  const allDiameters = pfDiametersStore.diameters.map(diameter => {
    // 檢查此管徑對於當前選擇的材質是否有有效組合
    const isFilteredByMaterial = materialDiameterFiltered.includes(diameter.id);

    return {
      id: diameter.id,
      name: diameter.name,
      value: diameter.value,
      // 如有管徑篩選或當前選擇則標記
      isFiltered: isFilteredByMaterial,
      // 獲取此管徑的標準長度
      standardLength: mainPipeFittings.find(f => f.diameter1_id === diameter.id)?.length || 4
    };
  });

  // 確保所有篩選的管徑都已包含在列表中
  uniqueDiameterIds.forEach(id => {
    if (!allDiameters.some(d => d.id === id)) {
      const fitting = mainPipeFittings.find(f => f.diameter1_id === id);
      const diameterInfo = pfDiametersStore.diameters.find(d => d.id === id);
      allDiameters.push({
        id,
        name: diameterInfo?.name || `直徑ID: ${id}`,
        value: diameterInfo?.value ?? 0,
        isFiltered: materialDiameterFiltered.includes(id) ||
                    id === localFormData.mainPipeDiameterId ||
                    (localFormData.mainPipe2Enabled && id === localFormData.mainPipe2DiameterId),
        standardLength: fitting?.length || 4
      });
    }
  });


  return allDiameters.sort((a, b) => {
    // 優先按數字排序，如果無法轉換為數字則按字母排序
    const numA = parseFloat(a.name);
    const numB = parseFloat(b.name);
    if (!isNaN(numA) && !isNaN(numB)) {
      return numA - numB;
    }
    return a.name.localeCompare(b.name);
  });
});

// 根據灌溉型式提供不同來源的末端設施規格選項
const endFacilityDiameterOptions = computed(() => {
  // 依據灌溉型式選擇不同的來源
  if (localFormData.irrigationTypeId === 1) {
    // 穿孔管系統 - 使用穿孔管管件
    return convertToSelectOptions(filteredPipeFittingsByModule.value.perforatedPipe || []);
  }
  else if (localFormData.irrigationTypeId === 2 || localFormData.sprinklerSubtypeId === 6) {
    // 噴頭式系統或高壓大型噴頭系統 - 使用噴頭管件
    return convertToSelectOptions(filteredPipeFittingsByModule.value.sprinkler || []);
  }
  else if (localFormData.irrigationTypeId === 3) {
    // 微噴系統 - 使用微噴管件
    return convertToSelectOptions(filteredPipeFittingsByModule.value.microSprinkler || []);
  }
  else if (localFormData.irrigationTypeId === 4) { // 滴灌系統
    if (localFormData.dripperSubtypeId === 8) {
      // 滴灌系統 - 使用滴水管件
      return convertToSelectOptions(filteredPipeFittingsByModule.value.pipeDrip || []);
    } else {
      // 滴灌系統 - 使用滴頭管件 (默認 dripperSubtypeId === 7 或未設置)
      return convertToSelectOptions(filteredPipeFittingsByModule.value.nozzleDrip || []);
    }
  }

  // 默認返回所有管徑選項
  return pipeDiameterOptions.value;
});

// ID=7滴灌管規格選項
// 💡 修正：當滴頭類型為滴嘴滴灌系統(ID=7)時，使用 module_id=1 (輸水管) 的管材
// 當滴頭類型為滴水管滴灌系統(ID=8)時，使用 module_id=12 (滴水滴灌管) 的管材
const branchPipeSpecOptionsForId7 = computed(() => {
  if (localFormData.dripperSubtypeId === 7) {
    // 滴嘴滴灌系統 - 使用輸水管 (module_id=1)
    return convertToSelectOptions(filteredPipeFittingsByModule.value.mainPipe || []);
  } else {
    // 滴水管滴灌系統 (ID=8) 或未設置 - 使用滴水滴灌管 (module_id=12)
    return convertToSelectOptions(filteredPipeFittingsByModule.value.pipeDrip || []);
  }
});

// 輔助函數：將管件數據轉換為下拉選項格式
const convertToSelectOptions = (fittings: PipeFitting[]) => {
  if (!fittings || fittings.length === 0) return pipeDiameterOptions.value;

  // 提取唯一的管徑 ID
  const diameterIds = [...new Set(fittings.map(f => f.diameter1_id).filter(id => id != null))];

  // 獲取這些 ID 對應的完整管徑資訊
  const diameters = diameterIds.map(id => {
    const fitting = fittings.find(f => f.diameter1_id === id);
    const diameterInfo = pfDiametersStore.diameters.find(d => d.id === id);

    return {
      id: id,
      name: diameterInfo?.name || `規格ID: ${id}`,
      value: diameterInfo?.value || 0,
      standardLength: fitting?.length || 4
    };
  });

  // 確保有選項，若沒有則回退到所有管徑
  return diameters.length > 0 ? diameters : pipeDiameterOptions.value;
};



const pipeMaterialOptions = computed(() => {
  // 使用主管模塊的管件來提取材質選項
  const mainPipeFittings = filteredPipeFittingsByModule.value.mainPipe || [];

  // 根據當前選擇的管徑ID過濾材質
  const diameterMaterialFiltered = mainPipeFittings
    .filter(fitting =>
      !localFormData.mainPipeDiameterId || // 如果没有选择管径则不过滤
      fitting.diameter1_id === localFormData.mainPipeDiameterId
    )
    .map(fitting => fitting.material_id)
    .filter(id => id != null);

  // 獲取唯一的材質ID列表
  const uniqueMaterialIds = [...new Set([
    ...diameterMaterialFiltered,
    // 加入當前已選擇的材質ID（如果有值）
    ...(localFormData.mainPipeMaterialId ? [localFormData.mainPipeMaterialId] : []),
    ...(localFormData.mainPipe2Enabled && localFormData.mainPipe2MaterialId ? [localFormData.mainPipe2MaterialId] : [])
  ])];

  // 獲取完整的材質列表
  const allMaterials = pfMaterialsStore.materials.map(material => {
    // 檢查此材質對於當前選擇的管徑是否有有效組合
    const isFilteredByDiameter = diameterMaterialFiltered.includes(material.id);

    return {
      id: material.id,
      name: material.name,
      // 如有材質篩選或當前選擇則標記
      isFiltered: isFilteredByDiameter
    };
  });

  // 確保所有篩選的材質都已包含在列表中
  uniqueMaterialIds.forEach(id => {
    if (!allMaterials.some(m => m.id === id)) {
      const materialInfo = pfMaterialsStore.materials.find(m => m.id === id);
      allMaterials.push({
        id,
        name: materialInfo?.name || `材質ID: ${id}`,
        isFiltered: diameterMaterialFiltered.includes(id) ||
                    id === localFormData.mainPipeMaterialId ||
                    (localFormData.mainPipe2Enabled && id === localFormData.mainPipe2MaterialId)
      });
    }
  });

  return allMaterials.sort((a, b) => a.name.localeCompare(b.name));
});

const getFilteredDiameterOptions = (currentMaterialId: number | null) => {
  const mainPipeFittings = filteredPipeFittingsByModule.value.mainPipe || [];

  // 根據當前選擇的材質ID過濾管徑
  const materialDiameterFiltered = mainPipeFittings
    .filter(fitting =>
      !currentMaterialId || // 如果沒有選擇材質則不過濾
      fitting.material_id === currentMaterialId
    )
    .map(fitting => fitting.diameter1_id)
    .filter(id => id != null);

  // 构建并返回过滤后的选项列表
  const allDiameters = pfDiametersStore.diameters.map(diameter => ({
    id: diameter.id,
    name: diameter.name,
    value: diameter.value,
    isFiltered: materialDiameterFiltered.includes(diameter.id),
    standardLength: mainPipeFittings.find(f => f.diameter1_id === diameter.id)?.length || 4
  }));

  // 确保所有筛选的ID都在列表中
  materialDiameterFiltered.forEach(id => {
    if (!allDiameters.some(d => d.id === id)) {
      const fitting = mainPipeFittings.find(f => f.diameter1_id === id);
      const diameterInfo = pfDiametersStore.diameters.find(d => d.id === id);
      allDiameters.push({
        id,
        name: diameterInfo?.name || `管徑ID: ${id}`,
        value: diameterInfo?.value ?? 0,
        isFiltered: true,
        standardLength: fitting?.length || 4
      });
    }
  });

  return allDiameters.sort((a, b) => {
    const numA = parseFloat(a.name);
    const numB = parseFloat(b.name);
    if (!isNaN(numA) && !isNaN(numB)) return numA - numB;
    return a.name.localeCompare(b.name);
  });
};

const getFilteredMaterialOptions = (currentDiameterId: number | null) => {
  const mainPipeFittings = filteredPipeFittingsByModule.value.mainPipe || [];

  // 根据传入的管径ID过滤材质
  const diameterMaterialFiltered = mainPipeFittings
    .filter(fitting =>
      !currentDiameterId || // 如果没有选择管径则不过滤
      fitting.diameter1_id === currentDiameterId
    )
    .map(fitting => fitting.material_id)
    .filter(id => id != null);

  // 构建并返回过滤后的选项列表
  const allMaterials = pfMaterialsStore.materials.map(material => ({
    id: material.id,
    name: material.name,
    isFiltered: diameterMaterialFiltered.includes(material.id)
  }));

  // 确保所有筛选的ID都在列表中
  diameterMaterialFiltered.forEach(id => {
    if (!allMaterials.some(m => m.id === id)) {
      const materialInfo = pfMaterialsStore.materials.find(m => m.id === id);
      allMaterials.push({
        id,
        name: materialInfo?.name || `材質ID: ${id}`,
        isFiltered: true
      });
    }
  });

  return allMaterials.sort((a, b) => a.name.localeCompare(b.name));
};

const pipe1DiameterOptions = computed(() => getFilteredDiameterOptions(localFormData.mainPipeMaterialId));
const pipe1MaterialOptions = computed(() => getFilteredMaterialOptions(localFormData.mainPipeDiameterId));

const pipe2DiameterOptions = computed(() => getFilteredDiameterOptions(localFormData.mainPipe2MaterialId));
const pipe2MaterialOptions = computed(() => getFilteredMaterialOptions(localFormData.mainPipe2DiameterId));

// Step4 的設施面積應該直接從 Step2 的總施作面積計算得出
// 🔥 Good Taste: 單一資料來源，直接使用 step2 持久化的 totalFacilityArea
const facilityAreaFromStep2 = computed(() => {
  const step2Data = getStepDataSafely(2);

  if (!step2Data) {
    return 0;
  }

  // 直接使用 totalFacilityArea（Step2 重構後的持久化欄位）
  return step2Data.totalFacilityArea || 0;
})

// 直接取 step2 已截斷至第 6 位小數的公頃值，避免 / 10000 浮點誤差
const facilityAreaHaFromStep2 = computed(() => {
  const step2Data = getStepDataSafely(2);
  if (!step2Data) return 0;
  return step2Data.totalFacilityAreaHa || 0;
})

const filteredPipeFittingsByModule = computed(() => {
  const moduleFilters = {
    mainPipe: 1, // 輸水管模組 ID
    branchPipe: 2, // 支管模組 ID
    endFacility: 3, // 末端設施模組 ID
    valves: 10, // 制水閥模組 ID
    sprinkler: 5, // 噴頭模組 ID
    perforatedPipe: 6, // 穿孔管模組 ID
    riser: 4, // 豎管模組 ID
    microSprinkler: 8, // 微噴模組 ID
    nozzleDrip: 9, // 滴嘴滴灌模組 ID
    pipeDrip: 12 // 滴水滴灌模組  ID
  };

  const result: Record<string, any[]> = {};

  // 針對每種模塊類型創建過濾後的列表
  Object.entries(moduleFilters).forEach(([key, moduleId]) => {
    result[key] = pipeFittingsStore.pipeFittings.filter(
      fitting => fitting.module_id === moduleId
    );
  });

  return result;
});

// Computed Properties
// 檢測是否為 legacy 資料格式
const isLegacyData = computed(() => {
  const activeVersion = grantsStore.currentGrant?.active_version as any;
  const dataSchemaVersion = activeVersion?.data_schema_version || null;
  return dataSchemaVersion === 'legacy';
});

const mainPipeTotalPrice = computed(() => {
  if (!localFormData.mainPipeQuantity || !localFormData.mainPipeUnitPrice) return '0';
  return Math.floor(localFormData.mainPipeQuantity * localFormData.mainPipeUnitPrice).toLocaleString();
});
const mainPipe2TotalPrice = computed(() => {
  if (!localFormData.mainPipe2Enabled || !localFormData.mainPipe2Quantity || !localFormData.mainPipe2UnitPrice) return '0';
  return Math.floor(localFormData.mainPipe2Quantity * localFormData.mainPipe2UnitPrice).toLocaleString();
});

// 支管總價等原有的 computed properties 保持不變或按需調整
// const branchPipeTotalPrice = computed(() => {
//   // 支管的價格通常由後端自動帶入材料列表時一併給出，此處計算可能僅為UI示意
//   const unitPrice = parseFloat(localFormData.branchPipeUnitPrice?.toString() || '0');
//   const quantity = parseFloat(localFormData.branchPipeQuantity?.toString() || '0');
//   return Math.round(unitPrice * quantity).toLocaleString();
// });


// const endFacilityTotalPrice = computed(() => {
//   return '0'; // 暫時，因為末端設施通常是POMNo選擇
// });

// 將管路按群組分類
const groupedPipes = computed(() => {
  const groups: Record<number, { groupNo: number; groupName: string; items: any[] }> = {};

  // 定義群組名稱映射
  const groupNameMapping: Record<number, string> = {
    1: '主管組',
    2: '支管組',
    3: '穿孔管組', // 穿孔管末端
    4: '滴灌系統組',   // 滴灌末端
    5: '豎管組',
    6: '固定設施組',
    7: '消耗性材料',
    8: '末端設施' // 噴頭/微噴/滴嘴組各類末端頭
  };

  // 為每個管路項目建立群組
  localFormData.pipes.forEach(pipe => {
    if (!groups[pipe.groupId]) {
      groups[pipe.groupId] = {
        groupNo: pipe.groupId,
        groupName: pipe.groupName || groupNameMapping[pipe.groupId] || `群組 ${pipe.groupId}`,
        items: []
      };
    }
    groups[pipe.groupId].items.push(pipe);
  });

  // 按 GroupNo 排序，並且每個群組內的項目按 order 排序
  return Object.values(groups)
    .sort((a, b) => a.groupNo - b.groupNo)
    .map(group => ({
      ...group,
      items: group.items.sort((a, b) => (a.order || 0) - (b.order || 0))
    }));
});

const totalPipesPrice = computed(() => {
  const total = localFormData.pipes.reduce((sum, pipe) => sum + (pipe.totalPrice || 0), 0);
  return total.toLocaleString();
});

// 補助結果
// const totalAmountAmount = computed(() => {
//   return localFormData.totalAmount.toLocaleString();
// });

// const subsidyAmount = computed(() => {
//   return localFormData.subsidyAmount.toLocaleString();
// });

// const selfPaidAmount = computed(() => {
//   return localFormData.selfPaidAmount.toLocaleString();
// });

// 個人年度補助額度計算
// 獲取 step3 的補助金額
// 🔥 統一架構 (2025-11-04): step3.vue (UI step 4) 現在儲存在 formData[4]
const step3SubsidyAmount = computed(() => {
  const step3Data = getStepDataSafely(4);  // step3.vue → formData[4]
  const facilities = step3Data.facilities || [];
  return facilities.reduce((total: number, facility: any) => {
    return total + (facility.subsidyAmount || 0);
  }, 0);
});

// 本案件總補助（step3 + step4）
const currentGrantTotalSubsidy = computed(() => {
  return step3SubsidyAmount.value + (localFormData.subsidyAmount || 0);
});

// 剩餘可用額度
const remainingSubsidyQuota = computed(() => {
  if (!grantsStore.hasSubsidySummary) return 0;
  const estimatedTotal = grantsStore.totalSubsidyAmount + currentGrantTotalSubsidy.value;
  return grantsStore.subsidyLimit - estimatedTotal;
});

// 使用率
const quotaUsageRate = computed(() => {
  if (!grantsStore.hasSubsidySummary || grantsStore.subsidyLimit === 0) return '0.0';
  const estimatedTotal = grantsStore.totalSubsidyAmount + currentGrantTotalSubsidy.value;
  const rate = (estimatedTotal / grantsStore.subsidyLimit) * 100;
  return rate.toFixed(1);
});

// 💡 檢查補助是否受到個人年度餘額限制
const isSubsidyLimitedByQuota = computed(() => {
  if (!grantsStore.hasSubsidySummary || !localFormData.subsidyAmount) return false;

  // 計算 step4 可用的個人年度餘額
  const step3Subsidy = step3SubsidyAmount.value;
  const otherCasesTotal = grantsStore.totalSubsidyAmount;
  const availableQuota = grantsStore.subsidyLimit - otherCasesTotal - step3Subsidy;

  // 如果可用餘額小於補助金額，表示受到年度餘額限制
  return availableQuota < localFormData.subsidyAmount && availableQuota >= 0;
});

// 💰 田間管路補助額度狀態（參考 step3 的實現）
// 根據灌溉型式和面積計算補助上限
const pipelineSubsidyLimit = computed(() => {
  const irrigationTypeId = localFormData.irrigationTypeId;
  if (!irrigationTypeId) return 0;

  const facilityAreaInHectares = facilityAreaHaFromStep2.value;
  if (facilityAreaInHectares <= 0) return 0;

  // 獲取地區類型
  const step2Data = getStepDataSafely(2);
  let isAboriginalArea = false;
  if (step2Data?.lands && Array.isArray(step2Data.lands) && step2Data.lands.length > 0) {
    isAboriginalArea = step2Data.lands.some((land: any) => {
      return land.isIndigenous || land.is_indigenous ||
             land.isAboriginalArea || land.is_aboriginal_area ||
             land.indigenousType || land.indigenous_type;
    });
  }
  const region = determineRegionType(isAboriginalArea);

  // 映射灌溉系統名稱
  const irrigationSystemNameMap: Record<number, string> = {
    1: '穿孔管系統',
    2: '噴頭系統',
    3: '微噴系統',
    4: '滴灌系統'
  };
  const irrigationSystemName = irrigationSystemNameMap[irrigationTypeId] || '';

  // 計算補助上限
  return getPipelineSubsidyLimit(irrigationSystemName, facilityAreaInHectares, region);
});

// 有效補助上限（考慮個人年度補助限額）
const effectivePipelineSubsidyLimit = computed(() => {
  const areaBasedLimit = pipelineSubsidyLimit.value;

  if (grantsStore.hasSubsidySummary) {
    const step3Subsidy = step3SubsidyAmount.value;
    const otherCasesTotal = grantsStore.totalSubsidyAmount;
    const availableQuota = grantsStore.subsidyLimit - otherCasesTotal - step3Subsidy;

    return Math.min(areaBasedLimit, Math.max(0, availableQuota));
  }

  return areaBasedLimit;
});

// 當前田間管路補助金額
const currentPipelineSubsidy = computed(() => {
  return localFormData.subsidyAmount || 0;
});

// 剩餘可用田間管路補助額度
const availablePipelineSubsidy = computed(() => {
  return Math.max(0, effectivePipelineSubsidyLimit.value - currentPipelineSubsidy.value);
});

// 田間管路補助比例
const pipelineSubsidyRatio = computed(() => {
  const totalCost = localFormData.totalAmount || 0;
  const subsidyAmount = currentPipelineSubsidy.value;
  if (totalCost === 0) return 0;
  return subsidyAmount / totalCost;
});

// 灌溉型式名稱（用於顯示）
const irrigationSystemDisplayName = computed(() => {
  const irrigationTypeId = localFormData.irrigationTypeId;
  const nameMap: Record<number, string> = {
    1: '穿孔管系統',
    2: '噴頭系統',
    3: '微噴系統',
    4: '滴灌系統'
  };
  return nameMap[irrigationTypeId] || '未選擇';
});

// 驗證條件 - 依照不同灌溉型式驗證自動帶入材料所需欄位
const canAutoFillMaterials = computed(() => {
  // console.log("檢查自動帶入材料條件", JSON.parse(JSON.stringify(localFormData)));

  // 基本必要條件 (對所有灌溉型式都需要)
  const basicConditions =
    !!localFormData.fieldLength &&
    !!localFormData.fieldWidth &&
    (localFormData.fundingSourceId !== null) &&
    !!localFormData.irrigationTypeId &&
    !!localFormData.waterSourceId &&
    (localFormData.mainPipeLength !== null) &&
    !!localFormData.mainPipeMaterialId &&
    !!localFormData.mainPipeDiameterId;

  // 如果主管2已啟用，則需要檢查主管2的相關欄位
  const mainPipe2Conditions = !localFormData.mainPipe2Enabled || (
    !!localFormData.mainPipe2Length &&
    !!localFormData.mainPipe2MaterialId &&
    !!localFormData.mainPipe2DiameterId
  );

  // 根據不同灌溉型式的特定條件
  let irrigationTypeSpecificConditions = true;

  // 穿孔管系統 (irrigationTypeId === 1)
  if (localFormData.irrigationTypeId === 1) {
    // 注意：穿孔管系統的判斷條件最簡單，根據原始專案邏輯
    irrigationTypeSpecificConditions =
      // 穿孔管出水方向 (1=單向 或 2=雙向)
      [1, 2].includes(localFormData.perforatedPipeDirection) &&
      // 支管行距必須有值
      (localFormData.branchPipeSpacing_SL !== null && localFormData.branchPipeSpacing_SL > 0) &&
      // 末端設施規格必須選擇 (但不需要選擇末端設施名稱)
      !!localFormData.endFacilitySpecId;

    // 重要：穿孔管系統不需要支管材質和規格作為必填欄位
    // 原始專案中這些欄位在選擇穿孔管系統時會被隱藏
  }
  // 噴頭式系統 (irrigationTypeId === 2)
  else if (localFormData.irrigationTypeId === 2) {
    irrigationTypeSpecificConditions =
      !!localFormData.sprinklerSubtypeId &&
      (localFormData.branchPipeSpacing_SL !== null && localFormData.branchPipeSpacing_SL > 0) &&
      (localFormData.sprinklerSpacing_SS !== null && localFormData.sprinklerSpacing_SS > 0) &&
      !!localFormData.branchPipeMaterialId &&
      !!localFormData.branchPipeDiameterId &&
      (localFormData.riserHeight_H !== null && localFormData.riserHeight_H > 0) &&
      !!localFormData.riserPipeMaterialId &&
      !!localFormData.riserPipeSpecId &&
      !!localFormData.endFacilitySpecId &&
      !!localFormData.endFacilityPomno;
  }
  // 微噴系統 (irrigationTypeId === 3)
  else if (localFormData.irrigationTypeId === 3) {
    irrigationTypeSpecificConditions =
      !!localFormData.installationType &&
      (localFormData.branchPipeSpacing_SL !== null && localFormData.branchPipeSpacing_SL > 0) &&
      (localFormData.sprinklerSpacing_SS !== null && localFormData.sprinklerSpacing_SS > 0) &&
      !!localFormData.branchPipeMaterialId &&
      !!localFormData.branchPipeDiameterId &&
      (localFormData.riserHeight_H !== null && localFormData.riserHeight_H >= 0) && // 🔥 允許豎管高度為 0
      !!localFormData.endFacilitySpecId &&
      !!localFormData.endFacilityPomno;
  }
  // 滴灌系統 (irrigationTypeId === 4)
  else if (localFormData.irrigationTypeId === 4) {
    // 滴嘴滴灌系統(7)需要噴頭間距，滴水管滴灌系統(8)不需要
    const needsSprinklerSpacing = localFormData.dripperSubtypeId === 7;
    const sprinklerSpacingCondition = needsSprinklerSpacing ?
      (localFormData.sprinklerSpacing_SS !== null && localFormData.sprinklerSpacing_SS > 0) : true;

    // ID=7 (滴嘴滴灌系統) 需要檢查滴水管規格和名稱
    // ID=8 (滴水管滴灌系統) 不再需要檢查支管材質和規格，因為已移除這些欄位
    let branchPipeConditions = true;
    if (localFormData.dripperSubtypeId === 7) {
      // ID=7：檢查滴水管規格和名稱
      branchPipeConditions = !!localFormData.branchPipeDiameterId && !!localFormData.branchPipePomno;
    } else if (localFormData.dripperSubtypeId === 8) {
      // ID=8：不需要檢查支管材質和規格，因為這些欄位已移除
      branchPipeConditions = true;
    } else {
      // 其他滴灌系統類型：保持原有邏輯
      branchPipeConditions = !!localFormData.branchPipeMaterialId && !!localFormData.branchPipeDiameterId;
    }

    irrigationTypeSpecificConditions =
      !!localFormData.dripperSubtypeId &&
      !!localFormData.installationType &&
      (localFormData.branchPipeSpacing_SL !== null && localFormData.branchPipeSpacing_SL > 0) &&
      sprinklerSpacingCondition &&
      branchPipeConditions &&
      !!localFormData.endFacilitySpecId &&
      !!localFormData.endFacilityPomno;
  }

  const result = basicConditions && mainPipe2Conditions && irrigationTypeSpecificConditions;

  // 輸出判斷結果供除錯用
  // console.log("自動帶入材料判斷結果:", {
  //   basicConditions,
  //   mainPipe2Conditions,
  //   irrigationTypeSpecificConditions,
  //   finalResult: result
  // });

  return result;
});

// 手動新增材料相關計算屬性
const filteredMaterialOptions = computed(() => {
  // 建立唯一的材料選項，避免重複
  const uniqueFittings = pipeFittingsStore.pipeFittings.reduce((acc, fitting) => {
    // 使用 pomno 作為唯一鍵，確保沒有重複材料
    if (!acc.has(fitting.pomno)) {
      // 建構完整的搜尋文字，包含規格（管徑）資訊 - 不去重，顯示所有口徑
      const diameters = [
        fitting.diameter1?.name,
        fitting.diameter1?.value,
        fitting.diameter2?.name,
        fitting.diameter2?.value,
        fitting.diameter3?.name,
        fitting.diameter3?.value
      ].filter(d => d !== null && d !== undefined && d !== '').join(' ');

      const searchText = [
        fitting.name,
        fitting.material?.name,
        fitting.module?.name,
        diameters,
        fitting.description,
        fitting.pomno?.toString()
      ].filter(text => text && text.toString().trim() !== '').join(' ');

      acc.set(fitting.pomno, {
        ...fitting,
        searchText: searchText
      });
    }
    return acc;
  }, new Map());

  // 轉換為陣列
  const allMaterials = Array.from(uniqueFittings.values());

  // 如果沒有搜尋查詢，返回所有材料
  if (!materialSearchQuery.value) {
    return allMaterials;
  }

  // 有搜尋查詢時進行智慧過濾
  const query = materialSearchQuery.value.toLowerCase().trim();
  return allMaterials.filter(fitting => {
    // 基本搜尋文字匹配
    const searchText = fitting.searchText.toLowerCase();
    if (searchText.includes(query)) {
      return true;
    }

    // 額外的規格搜尋邏輯
    // 支援直接搜尋管徑數值（如：搜尋 "1" 可以找到 "1\"" 的材料）
    const diameterValues = [
      fitting.diameter1?.value,
      fitting.diameter2?.value,
      fitting.diameter3?.value
    ].filter(v => v !== null && v !== undefined);

    // 檢查是否為數值搜尋
    const numericQuery = parseFloat(query);
    if (!isNaN(numericQuery)) {
      // 數值匹配：支援精確匹配和模糊匹配
      const hasNumericMatch = diameterValues.some(value => {
        return Math.abs(value - numericQuery) < 0.001; // 精確匹配
      });
      if (hasNumericMatch) return true;
    }

    // 支援分數格式搜尋（如：搜尋 "3/4" 可以找到 0.75 的材料）
    if (query.includes('/')) {
      const [numerator, denominator] = query.split('/').map(n => parseFloat(n));
      if (!isNaN(numerator) && !isNaN(denominator) && denominator !== 0) {
        const fractionValue = numerator / denominator;
        const hasFractionMatch = diameterValues.some(value => {
          return Math.abs(value - fractionValue) < 0.001;
        });
        if (hasFractionMatch) return true;
      }
    }

    // 支援英寸符號搜尋（如：搜尋 "1\"" 或 "1吋"）
    if (query.includes('"') || query.includes('吋')) {
      const cleanQuery = query.replace(/["\s吋]/g, '');
      const inchValue = parseFloat(cleanQuery);
      if (!isNaN(inchValue)) {
        const hasInchMatch = diameterValues.some(value => {
          return Math.abs(value - inchValue) < 0.001;
        });
        if (hasInchMatch) return true;
      }
    }

    return false;
  });
});

const selectedMaterial = computed(() => {
  if (!selectedMaterialPomno.value) return null;
  return pipeFittingsStore.pipeFittings.find(
    fitting => fitting.pomno === selectedMaterialPomno.value
  );
});

const materialGroupOptions = computed(() => [
  { id: 1, name: '主管組' },
  { id: 2, name: '支管組' },
  { id: 3, name: '穿孔管組' },
  { id: 4, name: '滴灌系統組' },
  { id: 5, name: '豎管組' },
  { id: 6, name: '固定設施組' },
  { id: 7, name: '消耗性材料' },
  { id: 8, name: '末端設施' }
]);

const canAddMaterial = computed(() => {
  return !!(selectedMaterialPomno.value && selectedGroup.value && materialQuantity.value > 0);
});

// 確保主管材質有預設值的輔助函數
const ensureDefaultMaterials = () => {
  // 確保主管1材質預設為 PVC (ID=1)
  if (!localFormData.mainPipeMaterialId || localFormData.mainPipeMaterialId === 0) {
    localFormData.mainPipeMaterialId = 1;
    console.log('🔧 Setting default material for mainPipe1: 1 (PVC)');
  }

  // 確保主管2材質預設為 PVC (ID=1)，但只在啟用時檢查
  if (localFormData.mainPipe2Enabled && (!localFormData.mainPipe2MaterialId || localFormData.mainPipe2MaterialId === 0)) {
    localFormData.mainPipe2MaterialId = 1;
    console.log('🔧 Setting default material for mainPipe2: 1 (PVC)');
  }
};

const calculateWidth = () => {
  const length = localFormData.fieldLength || 0;
  const area = facilityAreaFromStep2.value || 0;
  // 2026_01更新：寬度計算改為無條件捨去
  if (length > 0 && area > 0) {
    localFormData.fieldWidth = new Big(area).div(length).round(0, Big.roundDown).toNumber();
  }
  // updateFormData();
};

// 🔧 Linus式修正：監聽 Step2 面積變化，自動重新計算 fieldWidth
watch(facilityAreaFromStep2, (newArea, oldArea) => {
  if (newArea !== oldArea) {
    calculateWidth();
  }
}, { immediate: false });

// 也監聽 fieldLength 變化
watch(() => localFormData.fieldLength, (newLength, oldLength) => {
  if (newLength !== oldLength && newLength > 0) {
    calculateWidth();
  }
}, { immediate: false });

// 管路設施列表 → 田間主管配置 單向同步（pipes[] 有主管項目時才覆寫）
// 當 pipes[] 為空或無主管項目時，外層欄位由 fetchPipePrice / calculateMainPipeQuantity 維護，
// 作為 autoFillMaterials() 的 L1Price / L1MatAmt 輸入，不應被 watch 覆寫為 0
watch(
  () => localFormData.pipes,
  (pipes) => {
    const mainPipes = (pipes ?? []).filter(
      (p: any) => p.groupId === 1 && p.module === '主管'
    );

    // 無主管項目：不覆寫，保留 fetchPipePrice / calculateMainPipeQuantity 的中間值
    if (mainPipes.length === 0) return;

    const p1 = mainPipes[0];
    const p2 = mainPipes[1] ?? null;

    if (p1.matamount == null) console.warn('[step4 watch] 主管1 matamount 缺失');
    if (p1.matprice  == null) console.warn('[step4 watch] 主管1 matprice 缺失');
    if (p2 && p2.matamount == null) console.warn('[step4 watch] 主管2 matamount 缺失');
    if (p2 && p2.matprice  == null) console.warn('[step4 watch] 主管2 matprice 缺失');

    localFormData.mainPipeQuantity  = p1.matamount  ?? 0;
    localFormData.mainPipeUnitPrice = p1.matprice   ?? 0;
    localFormData.mainPipe2Quantity  = p2?.matamount ?? 0;
    localFormData.mainPipe2UnitPrice = p2?.matprice  ?? 0;
  },
  { deep: true }
);

const fetchPipeFittings = async () => {
  try {
    // Get the current grant's office_id
    const officeId = grantsStore.currentGrant?.office_id;

    if (!officeId) {
      console.warn('No office_id available for the current grant');
      return;
    }

    await pipeFittingsStore.fetchPipeFittingsByOfficeId(officeId, {
      skip: 0,
      limit: 1000, // Fetch all pipe fittings for the office
      append: false,  // 🔧 清空舊資料並重新載入，確保價格是最新的
      include_inactive: false,  // 🔧 只載入啟用的管件（用戶介面）
    });
    // console.log(`Fetched all pipe fittings for office_id: ${officeId}`);
    // Store the filtered pipe fittings
    // filteredPipeFittings.value = pipeFittingsStore.pipeFittings;
    // console.log(`Fetched ${filteredPipeFittings.value.length} pipe fittings for office_id: ${officeId}`);
  } catch (error) {
    console.error('Error fetching pipe fittings:', error);
  }
};

const getStandardPipeLength = async (materialId: number | null, diameterId: number | null, moduleId: number = 1): Promise<number> => {
  if (!materialId || !diameterId) return 4; // 預設長度
  // 從 pipeFittingsStore 中尋找比對的管件
  const matchingPipe = pipeFittingsStore.pipeFittings.find(pipe =>
      pipe.material_id === materialId &&
      pipe.diameter1_id === diameterId &&
      pipe.module_id === moduleId
  );

  // 如果找到比對的管件且有 length 屬性，返回該長度值
  if (matchingPipe && matchingPipe.length) {
      // console.log(`Found matching pipe with length: ${matchingPipe.length} for materialId=${materialId}, diameterId=${diameterId}, moduleId=${moduleId}`);
      return matchingPipe.length;
  }

  // 未找到比對的管件，返回預設長度
  console.warn(`No matching pipe found for materialId=${materialId}, diameterId=${diameterId}, moduleId=${moduleId}, using default length: 4`);
  return 4;
};

// 計算主管數量（根據長度） - 管材使用無條件進位
const calculateMainPipeQuantity = async () => {
  const length = localFormData.mainPipeLength || 0;
  if (length > 0) {
    const standardLength = await getStandardPipeLength(
        localFormData.mainPipeMaterialId,
        localFormData.mainPipeDiameterId,
        1 // module_id=1 for main pipe
    );
    localFormData.mainPipeStandardLength = standardLength;
    localFormData.mainPipeQuantity = new Big(length).div(standardLength).round(0, Big.roundUp).toNumber(); // 無條件進位
  }
  updateFormData();
};

const calculateMainPipe2Quantity = async () => {
  if (!localFormData.mainPipe2Enabled) return;
  const length = localFormData.mainPipe2Length || 0;
  if (length > 0) {
     const standardLength = await getStandardPipeLength(
        localFormData.mainPipe2MaterialId,
        localFormData.mainPipe2DiameterId,
        1 // module_id=1 for main pipe
    );
    localFormData.mainPipe2StandardLength = standardLength;
    localFormData.mainPipe2Quantity = new Big(length).div(standardLength).round(0, Big.roundUp).toNumber(); // 無條件進位
  }
  updateFormData();
};

const toggleMainPipe2 = () => {
  if (!localFormData.mainPipe2Enabled) {
    // 禁用主管2時，清空所有相關欄位
    localFormData.mainPipe2Length = null;
    localFormData.mainPipe2DiameterId = null;
    localFormData.mainPipe2MaterialId = 1; // 默認材質為 PVC
    localFormData.mainPipe2UnitPrice = null;
    localFormData.mainPipe2Quantity = null;
  } else {
    // 啟用主管2時，確保材質有預設值
    if (!localFormData.mainPipe2MaterialId || localFormData.mainPipe2MaterialId === 0) {
      localFormData.mainPipe2MaterialId = 1; // 預設為 PVC
      console.log('🔧 Setting default material for mainPipe2: 1 (PVC)');
    }
  }
  updateFormData();
};

// 灌溉類型變更
const onIrrigationTypeChange = async () => {
  // 根據選取的 irrigationTypeId 對應 irrigationTypeOptions 中的 id，將 description 值同步更新至 localFormData.irrigationType
  if (localFormData.irrigationTypeId) {
    const selectedOption = irrigationTypeOptions.value.find(option => option.id === localFormData.irrigationTypeId);
    if (selectedOption) {
      localFormData.irrigationType = selectedOption.description;
      console.log(`🔄 Updated irrigationType to: ${localFormData.irrigationType} (ID: ${localFormData.irrigationTypeId})`);
    } else {
      console.warn(`⚠️ Could not find irrigation type option for ID: ${localFormData.irrigationTypeId}`);
      localFormData.irrigationType = '';
    }
  } else {
    localFormData.irrigationType = '';
  }

  localFormData.sprinklerSubtypeId = null;
  localFormData.perforatedPipeDirection = 1; // Default for perforated
  localFormData.endFacilityPomno = null;
  localFormData.endFacilitySpecId = null;

  if (localFormData.irrigationTypeId === 2) { // 噴頭系統
    localFormData.sprinklerSubtypeId = 2; // 默認為一般噴頭系統
  } else {
    localFormData.sprinklerSubtypeId = null;
  }

  // 為滴灌系統設置默認子類型，確保能夠正確加載對應的末端設施
  if (localFormData.irrigationTypeId === 4) { // 滴灌系統
    // 默認選擇滴嘴滴灌系統(7)，除非用戶已經明確選擇了另一個子類型
    localFormData.dripperSubtypeId = 7; // 默認為滴嘴滴灌系統
  } else {
    localFormData.dripperSubtypeId = null;
  }

  await loadEndFacilityOptions(); // 動態載入末端設施選項
  updateFormData();
};

const onEndFacilityParamsChange = async () => {
  localFormData.endFacilityPomno = null; // 清除之前選擇的末端設施
  await loadEndFacilityOptions();

  // 💡 當滴頭類型改變時，也需要更新滴灌管選項（ID=7專用）
  if (localFormData.irrigationTypeId === 4 && localFormData.dripperSubtypeId === 7) {
    // 清除之前選擇的滴灌管規格和名稱
    localFormData.branchPipeDiameterId = null;
    localFormData.branchPipePomno = null;
    // 更新滴灌管選項
    updateBranchPipeFittingsForId7();
  }

  updateFormData();
};

const onEndFacilitySpecChange = async () => {
  localFormData.endFacilityPomno = null; // 清除之前選擇的末端設施
  await loadEndFacilityOptions(); // 重新載入與當前規格比對的末端設施選項
};

const loadEndFacilityOptions = async () => {
  // TODO: API Call to fetch end facility options (pipe_fittings)
  // based on irrigationTypeId, sprinklerSubtypeId, dripperSubtypeId, installationType, operating_unit_id
  // This API should return a list of objects like EndFacilityPipeFitting interface
  // Example: filteredEndFacilityPipeFittings.value = await pipeFittingsService.getTerminalFittings({ type: localFormData.irrigationTypeId, ... });
  // 保存當前選擇的項目
  // const currentSelection = localFormData.endFacilityPomno;

  // 根據灌溉類型和末端設施規格篩選末端設施選項
  const irrigationTypeId = localFormData.irrigationTypeId;
  const dripperSubtypeId = localFormData.dripperSubtypeId;
  const endFacilitySpecId = localFormData.endFacilitySpecId;

  let fittings = [];

  // console.log(`loadEndFacilityOptions: irrigationTypeId=${irrigationTypeId}, dripperSubtypeId=${dripperSubtypeId}`);

  if (irrigationTypeId === 1) {
    // 穿孔管系統
    fittings = filteredPipeFittingsByModule.value.perforatedPipe || [];
    // console.log(`Using perforatedPipe fittings, count: ${fittings.length}`);
  }
  else if (irrigationTypeId === 2 || localFormData.sprinklerSubtypeId === 6) {
    // 噴頭式系統
    fittings = filteredPipeFittingsByModule.value.sprinkler || [];
    // console.log(`Using sprinkler fittings, count: ${fittings.length}`);
  }
  else if (irrigationTypeId === 3) {
    // 微噴系統
    fittings = filteredPipeFittingsByModule.value.microSprinkler || [];
    // console.log(`Using microSprinkler fittings, count: ${fittings.length}`);
  }
  else if (irrigationTypeId === 4) { // 滴灌系統
    if (dripperSubtypeId === 8) {
      // 滴水管滴灌系統
      fittings = filteredPipeFittingsByModule.value.pipeDrip || [];
      // console.log(`Using pipeDrip fittings for drip pipe system, count: ${fittings.length}`);
    } else {
      // 默認使用滴嘴系統 (dripperSubtypeId === 7 或未設置)
      fittings = filteredPipeFittingsByModule.value.nozzleDrip || [];
      // console.log(`Using nozzleDrip fittings for drip nozzle system, count: ${fittings.length}`);
    }
  }

  // 根據選擇的規格進一步篩選
  if (endFacilitySpecId) {
    fittings = fittings.filter(f => f.diameter1_id === endFacilitySpecId);
  }

  // 轉換為末端設施選項格式
  const newFittings = fittings.map(fitting => ({
    pomno: fitting.pomno,
    displayName: fitting.name || `${fitting.material_name || ''} ${fitting.diameter1_name || ''}`.trim(),
    materialName: fitting.material?.name || '',
    materialId: fitting.material_id, // 添加材質ID用於自動同步到豎管材質
    specName: fitting.diameter1?.name || '',
    specId: fitting.diameter1_id
  }));

  // 去重複
  const uniqueFittings = newFittings.reduce((acc, current) => {
    const exists = acc.find(item => item.pomno === current.pomno);
    if (!exists) {
      acc.push(current);
    }
    return acc;
  }, [] as EndFacilityPipeFitting[]);

  console.log(`📋 末端設施選項已載入，共 ${uniqueFittings.length} 項`, uniqueFittings.slice(0, 3));
  filteredEndFacilityPipeFittings.value = uniqueFittings;
};

const onSelectedEndFacilityChange = (selectedPomno: number | null) => {
    if (selectedPomno) {
        const selectedFitting = filteredEndFacilityPipeFittings.value.find(f => f.pomno === selectedPomno);
        if (selectedFitting) {
            localFormData.endFacilitySpecId = selectedFitting.specId || null;

            // 自動同步到豎管欄位（僅限噴頭式和微噴系統）
            if (localFormData.irrigationTypeId === 2 || localFormData.irrigationTypeId === 3) {
                localFormData.riserPipeSpecId = selectedFitting.specId || null;
                localFormData.riserPipeMaterialId = selectedFitting.materialId || null;
                console.log(`✅ 自動同步豎管欄位：材質ID=${selectedFitting.materialId}, 規格ID=${selectedFitting.specId}`);
            }
            // 單價等也應從此 fitting 物件或後續API獲取
        }
    } else {
        localFormData.endFacilitySpecId = null;

        // 清空時也清空豎管欄位
        if (localFormData.irrigationTypeId === 2 || localFormData.irrigationTypeId === 3) {
            localFormData.riserPipeSpecId = null;
            localFormData.riserPipeMaterialId = null;
        }
    }
    updateFormData();
};

// ID=7滴水管規格變更處理
const onBranchPipeSpecChangeForId7 = () => {
  // 清空滴灌管名稱選擇（參考末端設施規格的觸發邏輯）
  localFormData.branchPipePomno = null;
  updateBranchPipeFittingsForId7();
};

// 更新ID=7滴灌管件選項
// 💡 修正：根據滴頭類型選擇不同的資料來源
const updateBranchPipeFittingsForId7 = () => {
  const branchPipeSpec = localFormData.branchPipeDiameterId;

  // 根據滴頭類型選擇資料來源
  let fittings;
  if (localFormData.dripperSubtypeId === 7) {
    // 滴嘴滴灌系統 - 使用輸水管 (module_id=1)
    fittings = filteredPipeFittingsByModule.value.mainPipe || [];
  } else {
    // 滴水管滴灌系統 (ID=8) 或未設置 - 使用滴水滴灌管 (module_id=12)
    fittings = filteredPipeFittingsByModule.value.pipeDrip || [];
  }

  // 根據選擇的規格進一步篩選
  if (branchPipeSpec) {
    fittings = fittings.filter(f => f.diameter1_id === branchPipeSpec);
  }

  // 轉換為滴灌管件選項格式
  const newFittings = fittings.map(fitting => ({
    pomno: fitting.pomno,
    displayName: fitting.name || `${fitting.material_name || ''} ${fitting.diameter1_name || ''}`.trim(),
    materialName: fitting.material?.name || '',
    specName: fitting.diameter1_name || '',
    specId: fitting.diameter1_id
  }));

  // 去重複
  const uniqueFittings = newFittings.reduce((acc, current) => {
    const exists = acc.find(item => item.pomno === current.pomno);
    if (!exists) {
      acc.push(current);
    }
    return acc;
  }, [] as EndFacilityPipeFitting[]);

  filteredBranchPipeFittings.value = uniqueFittings;
};

// ID=7滴水管件名稱變更處理
const onSelectedBranchPipeChangeForId7 = (selectedPomno: number | null) => {
  if (selectedPomno) {
    const selectedFitting = filteredBranchPipeFittings.value.find(f => f.pomno === selectedPomno);
    if (selectedFitting) {
      // 將規格同步回主要欄位
      localFormData.branchPipeDiameterId = selectedFitting.specId || null;
      // 可以從POMNO獲取對應的材質資訊
    }
  } else {
    // 清空時同時清除滴灌管規格和POMNO，與末端管材名稱的清除邏輯保持一致
    localFormData.branchPipePomno = null;
    localFormData.branchPipeDiameterId = null;
    // 清空管件選項
    filteredBranchPipeFittings.value = [];
  }
  updateFormData();
};

// 設施類型變更
// const onInstallationTypeChange = () => {
//   updateFormData();
// };

// 獲取管路價格
const fetchPipePrice = async (pipeNumber: 1 | 2) => {
  let materialId: number | null, diameterId: number | null;
  if (pipeNumber === 1) {
    materialId = localFormData.mainPipeMaterialId;
    diameterId = localFormData.mainPipeDiameterId;
  } else {
    materialId = localFormData.mainPipe2MaterialId;
    diameterId = localFormData.mainPipe2DiameterId;
  }

  if (!materialId || !diameterId) return;

  try {
    // console.log(`Workspaceing pipe ${pipeNumber} price for: materialId=${materialId}, diameterId=${diameterId}`);
     // 從 filteredPipeFittingsByModule 中篩選出主管類型的管件
    const mainPipeFittings = filteredPipeFittingsByModule.value.mainPipe || [];

    // 進一步篩選符合 materialId 和 diameterId 的管件
    const matchingPipe = mainPipeFittings.find(pipe =>
      pipe.material_id === materialId &&
      pipe.diameter1_id === diameterId
    );

    if (matchingPipe) {
      // console.log(`Found matching pipe: ${matchingPipe.name}, price: ${matchingPipe.current_price}, length: ${matchingPipe.length}`);

      const price = matchingPipe.current_price;
      const standardLength = matchingPipe.length || 4; // 如果沒有長度資訊，預設為 4

      if (pipeNumber === 1) {
        localFormData.mainPipeUnitPrice = price;
        localFormData.mainPipeStandardLength = standardLength;
        await calculateMainPipeQuantity(); // 根據新的標準長度重新計算數量
      } else {
        localFormData.mainPipe2UnitPrice = price;
        localFormData.mainPipe2StandardLength = standardLength;
        await calculateMainPipe2Quantity();
      }
    } else {
      console.warn(`No matching pipe found for materialId=${materialId}, diameterId=${diameterId}`);

      if (pipeNumber === 1) {
        localFormData.mainPipeUnitPrice = 0;
        // localFormData.mainPipeStandardLength = standardLength;
        await calculateMainPipeQuantity();
      } else {
        localFormData.mainPipe2UnitPrice = 0;
        // localFormData.mainPipe2StandardLength = standardLength;
        await calculateMainPipe2Quantity();
      }
    }
  } catch (error) {
    console.error(`Error fetching pipe ${pipeNumber} price:`, error);
  }
  updateFormData();
};


// 更新管路數量
const updatePipeQuantity = (groupNo: number, pipeIndex: number, newQuantity: number) => {
  // 確保數量不為負數
  if (newQuantity < 0) {
    newQuantity = 0;
  }

  // 找到對應的管路項目
  const group = groupedPipes.value.find(g => g.groupNo === groupNo);
  if (!group || !group.items[pipeIndex]) return;

  const pipe = group.items[pipeIndex];

  // 更新數量
  pipe.matamount = newQuantity;

  // 重新計算總價
  pipe.totalPrice = Math.floor(pipe.matprice * newQuantity);

  // 在原始數組中找到對應項目並更新
  const originalIndex = localFormData.pipes.findIndex(p =>
    p.pomno === pipe.pomno &&
    p.groupId === pipe.groupId &&
    p.matname === pipe.matname &&
    p.description === pipe.description
  );

  if (originalIndex !== -1) {
    localFormData.pipes[originalIndex].matamount = newQuantity;
    localFormData.pipes[originalIndex].totalPrice = pipe.totalPrice;
  }

  // 更新父組件數據
  updateFormData();

  // 自動重新計算補助
  calculateSubsidy();
};

// 更新管路單價
const updatePipePrice = (groupNo: number, pipeIndex: number, newPrice: number) => {
  // 確保單價不為負數
  if (newPrice < 0) {
    newPrice = 0;
  }

  // 找到對應的管路項目
  const group = groupedPipes.value.find(g => g.groupNo === groupNo);
  if (!group || !group.items[pipeIndex]) return;

  const pipe = group.items[pipeIndex];

  // 更新單價
  pipe.matprice = newPrice;

  // 重新計算總價
  pipe.totalPrice = Math.floor(pipe.matprice * pipe.matamount);

  // 在原始數組中找到對應項目並更新
  const originalIndex = localFormData.pipes.findIndex(p =>
    p.pomno === pipe.pomno &&
    p.groupId === pipe.groupId &&
    p.matname === pipe.matname &&
    p.description === pipe.description
  );

  if (originalIndex !== -1) {
    localFormData.pipes[originalIndex].matprice = newPrice;
    localFormData.pipes[originalIndex].totalPrice = pipe.totalPrice;
  }

  // 更新父組件數據
  updateFormData();

  // 自動重新計算補助
  calculateSubsidy();
};

// 移除管路
const removePipe = (groupNo: number, pipeIndexInGroup: number) => {
  const group = groupedPipes.value.find(g => g.groupNo === groupNo);
  if (!group) return;

  const pipeToRemove = group.items[pipeIndexInGroup];
  if (!pipeToRemove) return;

  localFormData.pipes = localFormData.pipes.filter(p =>
    !(p.pomno === pipeToRemove.pomno &&
      p.groupId === pipeToRemove.groupId &&
      p.order === pipeToRemove.order) // 更精確的移除條件
  );
  // 移除後需要重新計算訂單和總價
  updatePipeOrderWithinGroups();
  calculateSubsidy(); // 可選：移除材料後是否立即重算補助
  updateFormData();
};

// 上移管路順序
const movePipeUp = (groupNo: number, pipeIndexInGroup: number) => {
  if (pipeIndexInGroup <= 0) return;

  // 獲取同群組的所有項目，按 order 排序
  const groupItems = localFormData.pipes.filter(p => p.groupId === groupNo).sort((a,b) => (a.order || 0) - (b.order || 0));

  // 找到要交換的兩個項目在原數組中的索引
  const currentItem = groupItems[pipeIndexInGroup];
  const previousItem = groupItems[pipeIndexInGroup - 1];

  const currentIndex = localFormData.pipes.findIndex(p =>
    p.pomno === currentItem.pomno &&
    p.order === currentItem.order &&
    p.groupId === currentItem.groupId &&
    p.matname === currentItem.matname &&
    p.description === currentItem.description
  );
  const previousIndex = localFormData.pipes.findIndex(p =>
    p.pomno === previousItem.pomno &&
    p.order === previousItem.order &&
    p.groupId === previousItem.groupId &&
    p.matname === previousItem.matname &&
    p.description === previousItem.description
  );

  if (currentIndex !== -1 && previousIndex !== -1) {
    // 交換兩個項目的完整數據
    const temp = { ...localFormData.pipes[currentIndex] };
    localFormData.pipes[currentIndex] = { ...localFormData.pipes[previousIndex] };
    localFormData.pipes[previousIndex] = temp;

    // 重新編號該群組的所有項目
    reorderGroupItems(groupNo);
  }
  updateFormData();
};

// 下移管路順序
const movePipeDown = (groupNo: number, pipeIndexInGroup: number) => {
  // 獲取同群組的所有項目，按 order 排序
  const groupItems = localFormData.pipes.filter(p => p.groupId === groupNo).sort((a,b) => (a.order || 0) - (b.order || 0));

  if (pipeIndexInGroup >= groupItems.length - 1) return;

  // 找到要交換的兩個項目在原數組中的索引
  const currentItem = groupItems[pipeIndexInGroup];
  const nextItem = groupItems[pipeIndexInGroup + 1];

  const currentIndex = localFormData.pipes.findIndex(p =>
    p.pomno === currentItem.pomno &&
    p.order === currentItem.order &&
    p.groupId === currentItem.groupId &&
    p.matname === currentItem.matname &&
    p.description === currentItem.description
  );
  const nextIndex = localFormData.pipes.findIndex(p =>
    p.pomno === nextItem.pomno &&
    p.order === nextItem.order &&
    p.groupId === nextItem.groupId &&
    p.matname === nextItem.matname &&
    p.description === nextItem.description
  );

  if (currentIndex !== -1 && nextIndex !== -1) {
    // 交換兩個項目的完整數據
    const temp = { ...localFormData.pipes[currentIndex] };
    localFormData.pipes[currentIndex] = { ...localFormData.pipes[nextIndex] };
    localFormData.pipes[nextIndex] = temp;

    // 重新編號該群組的所有項目
    reorderGroupItems(groupNo);
  }
  updateFormData();
};

// 重新編號群組內項目的順序
const reorderGroupItems = (groupNo: number) => {
  const groupItems = localFormData.pipes.filter(p => p.groupId === groupNo);
  groupItems.forEach((item, index) => {
    // 使用更精確的匹配條件，包括當前的 order 值來確保找到正確的項目
    const actualIndex = localFormData.pipes.findIndex(p =>
      p.pomno === item.pomno &&
      p.groupId === item.groupId &&
      p.matname === item.matname &&
      p.order === item.order &&
      p.description === item.description
    );
    if (actualIndex !== -1) {
      localFormData.pipes[actualIndex].order = index + 1;
    }
  });
};

const autoFillMaterials = async () => {
  if (!form.value?.validate()) {
     console.error('Form validation failed for auto-filling materials');
     return;
  }
  if (!canAutoFillMaterials.value) {
    console.error('Not all required fields for auto-filling materials are filled or valid.');

    // 根據不同灌溉型式提供相應的提示訊息
    let errorMessage = '請填寫以下必填欄位：\n';

    // 基本必要欄位檢查
    if (!localFormData.fieldLength || !localFormData.fieldWidth) {
      errorMessage += '- 田間坵塊的長度與寬度\n';
    }
    if (localFormData.fundingSourceId === null) {
      errorMessage += '- 補助單位\n';
    }
    if (!localFormData.irrigationTypeId) {
      errorMessage += '- 灌溉型式\n';
    }
    if (!localFormData.waterSourceId) {
      errorMessage += '- 灌溉水源\n';
    }
    if (localFormData.mainPipeLength === null || !localFormData.mainPipeMaterialId || !localFormData.mainPipeDiameterId) {
      errorMessage += '- 田間主管1的長度、材質和管徑\n';
    }

    // 如果主管2已啟用但欄位未填寫完整
    if (localFormData.mainPipe2Enabled &&
        (!localFormData.mainPipe2Length || !localFormData.mainPipe2MaterialId || !localFormData.mainPipe2DiameterId)) {
      errorMessage += '- 田間主管2的長度、材質和管徑\n';
    }

    // 根據灌溉型式檢查特定欄位
    if (localFormData.irrigationTypeId === 1) { // 穿孔管系統
      if (localFormData.perforatedPipeDirection === null) {
        errorMessage += '- 穿孔管出水方向\n';
      }
      if (localFormData.branchPipeSpacing_SL === null) {
        errorMessage += '- 支管行距(SL)\n';
      }
      // 穿孔管系統不需要支管材質和規格作為必填欄位
      if (!localFormData.endFacilitySpecId) {
        errorMessage += '- 末端設施規格\n';
      }
    }
    else if (localFormData.irrigationTypeId === 2) { // 噴頭式系統
      if (!localFormData.sprinklerSubtypeId) {
        errorMessage += '- 噴頭類型\n';
      }
      if (localFormData.branchPipeSpacing_SL === null || localFormData.sprinklerSpacing_SS === null) {
        errorMessage += '- 支管行距(SL)和噴頭間距(SS)\n';
      }
      if (!localFormData.branchPipeMaterialId || !localFormData.branchPipeDiameterId) {
        errorMessage += '- 支管材質和規格\n';
      }
      if (!localFormData.riserHeight_H || !localFormData.riserPipeMaterialId || !localFormData.riserPipeSpecId) {
        errorMessage += '- 豎管高度、材質和規格\n';
      }
      if (!localFormData.endFacilitySpecId || !localFormData.endFacilityPomno) {
        errorMessage += '- 末端設施規格和名稱\n';
      }
    }
    else if (localFormData.irrigationTypeId === 3) { // 微噴系統
      if (!localFormData.installationType) {
        errorMessage += '- 設施型式\n';
      }
      if (localFormData.branchPipeSpacing_SL === null || localFormData.sprinklerSpacing_SS === null) {
        errorMessage += '- 支管行距(SL)和噴頭間距(SS)\n';
      }
      if (!localFormData.branchPipeMaterialId || !localFormData.branchPipeDiameterId) {
        errorMessage += '- 支管材質和規格\n';
      }
      // 允許豎管高度為 0，但不能是 null 或 undefined
      if (localFormData.riserHeight_H === null || localFormData.riserHeight_H === undefined) {
        errorMessage += '- 豎管高度\n';
      }
      if (!localFormData.endFacilitySpecId || !localFormData.endFacilityPomno) {
        errorMessage += '- 末端設施規格和名稱\n';
      }
    }
    else if (localFormData.irrigationTypeId === 4) { // 滴灌系統
      if (!localFormData.dripperSubtypeId) {
        errorMessage += '- 滴灌類型\n';
      }
      if (!localFormData.installationType) {
        errorMessage += '- 設施型式\n';
      }

      // 條件性檢查行距和間距
      const needsSprinklerSpacing = localFormData.dripperSubtypeId === 7;
      const missingFields: string[] = [];

      if (localFormData.branchPipeSpacing_SL === null) {
        missingFields.push('滴水管行距(SL)');
      }
      if (needsSprinklerSpacing && localFormData.sprinklerSpacing_SS === null) {
        missingFields.push('噴頭間距(SS)');
      }

      if (missingFields.length > 0) {
        errorMessage += `- ${missingFields.join('和')}\n`;
      }

      if (!localFormData.branchPipeMaterialId || !localFormData.branchPipeDiameterId) {
        errorMessage += '- 支管材質和規格\n';
      }
      if (!localFormData.endFacilitySpecId || !localFormData.endFacilityPomno) {
        errorMessage += '- 末端設施規格和名稱\n';
      }
    }

    // 使用Vuetify的提示元件顯示錯誤訊息
    emit('show-snackbar', {
      text: errorMessage,
      color: 'error',
      timeout: 7000  // 顯示7秒
    });

    return;
  }

  isLoadingMaterials.value = true;

  try {
    // 準備請求數據 (應嚴格對應後端 FastAPI 的 Pydantic 模型)
    const requestPayload = {
      map_no: props.mapNo,
      operating_unit_id: props.operatingUnitId,
      form_inputs: { // 這部分對應原 C# StdMaterialStruct
        Length: localFormData.fieldLength,
        width: localFormData.fieldWidth,

        L1Len: localFormData.mainPipeLength,
        L1Material: localFormData.mainPipeMaterialId,
        L1Spec: localFormData.mainPipeDiameterId,
        L1Price: localFormData.mainPipeUnitPrice || 0, // 單價應已獲取
        L1MatAmt: localFormData.mainPipeQuantity || 0, // 數量應已計算

        L2Len: localFormData.mainPipe2Enabled ? localFormData.mainPipe2Length : 0,
        L2Material: localFormData.mainPipe2Enabled ? localFormData.mainPipe2MaterialId : 0,
        L2Spec: localFormData.mainPipe2Enabled ? localFormData.mainPipe2DiameterId : 0,
        L2Price: localFormData.mainPipe2Enabled ? (localFormData.mainPipe2UnitPrice || 0) : 0,
        L2MatAmt: localFormData.mainPipe2Enabled ? (localFormData.mainPipe2Quantity || 0) : 0,

        ddl_EndType: localFormData.irrigationTypeId,
        ddl_Sprinkler: localFormData.irrigationTypeId === 2 ? localFormData.sprinklerSubtypeId : null,
        ddl_Drop: localFormData.irrigationTypeId === 4 ? localFormData.dripperSubtypeId : null,
        ddl_FacType: localFormData.installationType,
        ddl_WtaerSrc: localFormData.waterSourceId,

        SL: localFormData.branchPipeSpacing_SL,
        SS: localFormData.sprinklerSpacing_SS,

        BranchMaterial: localFormData.branchPipeMaterialId,
        BranchSpec: localFormData.branchPipeDiameterId,
        ChangeBranchSpec: localFormData.changeBranchSpecId || 0, // 0 表示不變徑

        StdpipeHei: localFormData.riserHeight_H,
        StdpipeMat: localFormData.riserPipeMaterialId,  // 豎管材質
        StdpipeSpec: localFormData.riserPipeSpecId,   // 豎管規格

        NozzleMaterial: localFormData.endFacilityPomno, // 末端設施POMNo
        NozzleSpec: localFormData.endFacilitySpecId,     // 末端設施主要規格ID

        PerforatedPipe: localFormData.irrigationTypeId === 1 ? localFormData.perforatedPipeDirection : 1, // 假設 1 是穿孔管ID
      }
    };

    // 直接使用前端數據進行材料計算
    const materialGroupsFromApi = getMockMaterialData(requestPayload.form_inputs, {
      excludeNoPriceMaterials: materialGenerationVersion.value === 'v2',
      version: materialGenerationVersion.value
    });

    localFormData.pipes = []; // 清空現有
    materialGroupsFromApi.forEach(group => {
      group.List.forEach((material: MaterialItem) => {
        localFormData.pipes.push({
          pomno: material.pomno,
          groupId: group.GroupNo,
          groupName: group.GroupName,
          module: material.module,
          matname: material.matname,
          module_id: material.module_id, // 加入缺少的 module_id
          mattype: material.mattype,
          specification: `${material.spec1 || ''} ${material.spec2 || ''} ${material.spec3 || ''}`.trim(),
          spec1: material.spec1,
          spec2: material.spec2,
          spec3: material.spec3,
          itemunit: material.itemunit,
          description: material.description,
          matprice: material.matprice,
          matamount: material.matamount,
          totalPrice: Math.floor(material.matprice * material.matamount),
          order: material.order,
          // debugMatchData: material.debugMatchData // 加入除錯比對資料
        });
      });
    });

    // 🔥 在計算補助之前，先檢查是否為 legacy 資料並設定標記
    // 這樣 calculateSubsidy() 才能正確檢測到標記並允許重新計算
    if (isLegacyData.value) {
      console.log('🔄 [自動帶入材料] 檢測到 legacy 資料已重新生成材料清單，標記需要更新 data_schema_version');
      // 標記需要更新 schema version（在保存時執行）
      localFormData._needsSchemaVersionUpdate = true;
    }

    await calculateSubsidy(); // 自動帶入材料後觸發補助計算（此時標記已設定）

    // 🔥 如果是 legacy 資料重新生成，自動儲存以觸發 schema version 更新
    if (isLegacyData.value) {
      console.log('💾 [自動帶入材料] 自動儲存資料以更新 schema version');
      try {
        await grantsStore.saveStepData(4, localFormData);
        console.log('✅ [自動帶入材料] 資料儲存成功，schema version 已更新');
      } catch (saveError) {
        console.error('❌ [自動帶入材料] 資料儲存失敗:', saveError);
      }
    }
  } catch (error) {
    console.error('Error auto-filling materials:', error);
    // 可以在此處設定錯誤提示訊息
  } finally {
    isLoadingMaterials.value = false;
  }
};

// 計算補助金額
const calculateSubsidy = async () => {
  if (localFormData.pipes.length === 0) {
    // alert('請先自動帶入或新增管路設施!');
    // 使用統一的清除函數
    await clearPipelineData(true);
    return;
  }

  // � 檢查是否為剛重新生成材料的 legacy 資料
  const isRegeneratedLegacy = isLegacyData.value && localFormData._needsSchemaVersionUpdate === true;

  // Legacy 資料不重新計算，但剛重新生成材料的 legacy 資料允許計算（因為已使用新邏輯）
  if (isLegacyData.value && !isRegeneratedLegacy) {
    console.log('⚠️ [田間管路補助] 檢測到 legacy 資料，跳過重新計算以保持原有金額結構');
    console.log('💾 [田間管路補助] Legacy 資料:', {
      totalAmount: localFormData.totalAmount,
      subsidyAmount: localFormData.subsidyAmount,
      selfPaidAmount: localFormData.selfPaidAmount,
      designFee: localFormData.designFee
    });
    return;
  }

  if (isRegeneratedLegacy) {
    console.log('🔄 [田間管路補助] 檢測到已重新生成材料的 legacy 資料，允許重新計算金額');
  }

  isCalculatingSubsidy.value = true;
  try {
    // 根據灌溉型式和原民區域狀態計算補助金額
    const currentTotalPipesPrice = parseFloat(totalPipesPrice.value.replace(/,/g, ''));
    const facilityAreaInHectares = facilityAreaHaFromStep2.value;

    // 從 step2 數據中獲取原民區域狀態
    const step2Data = getStepDataSafely(2);

    // 優先從 lands 陣列中檢查實際土地的原住民地區狀態
    // 檢查邏輯：只要有任一筆土地位於原住民地區，就套用原住民地區補助標準
    let isAboriginalArea = false;

    if (step2Data?.lands && Array.isArray(step2Data.lands) && step2Data.lands.length > 0) {
      // 檢查 lands 陣列中是否有土地位於原住民地區
      isAboriginalArea = step2Data.lands.some((land: any) => {
        // 可能的欄位名稱：isIndigenous, is_indigenous, isAboriginalArea, is_aboriginal_area
        return land.isIndigenous || land.is_indigenous ||
               land.isAboriginalArea || land.is_aboriginal_area ||
               land.indigenousType || land.indigenous_type;
      });
    }

    // 如果 lands 沒有資料，回退到使用 step2 的 isAboriginalArea
    if (!step2Data?.lands || step2Data.lands.length === 0) {
      isAboriginalArea = step2Data?.isAboriginalArea || false;
    }

    const region = determineRegionType(isAboriginalArea);

    // 根據灌溉型式ID獲取系統名稱並映射到補助標準中的名稱
    const irrigationTypeId = localFormData.irrigationTypeId;
    // const irrigationType = irrigationTypesStore.getIrrigationTypeById(irrigationTypeId);

    // 映射灌溉系統名稱到補助標準格式
    const irrigationSystemNameMap: Record<number, string> = {
      1: '穿孔管系統',
      2: '噴頭系統',
      3: '微噴系統',
      4: '滴灌系統'
    };

    const irrigationSystemName = irrigationSystemNameMap[irrigationTypeId] || '';

    // 使用統一的補助分配計算（不應包含設計費）
    const subsidyResult: PipelineSubsidyResult = calculatePipelineSubsidyAllocation(
      irrigationSystemName,
      facilityAreaInHectares,
      region,
      currentTotalPipesPrice // 管路材料成本（不含設計費）
    );

    // 💰 計算個人年度補助餘額限制
    // 剩餘可用額度 = 年度上限 - 已申請總額 - step3 補助
    const step3Subsidy = step3SubsidyAmount.value;
    let availableQuota = 0;

    if (grantsStore.hasSubsidySummary) {
      // 年度補助餘額（扣除其他案件但不含本案）
      const otherCasesTotal = grantsStore.totalSubsidyAmount;
      // 本案 step4 可用額度 = 年度上限 - 其他案件 - 本案 step3
      availableQuota = grantsStore.subsidyLimit - otherCasesTotal - step3Subsidy;
    }

    // 🎯 雙重限制：取「灌溉系統補助上限」與「個人年度餘額」兩者較小值
    let finalSubsidy = subsidyResult.subsidyAmount;
    let finalSelfPaid = subsidyResult.selfPaidAmount;
    const finalTotalCost = subsidyResult.totalCost;
    let limitType = '灌溉系統補助上限';

    if (grantsStore.hasSubsidySummary && availableQuota < subsidyResult.subsidyAmount) {
      // 個人年度餘額不足，需調整
      finalSubsidy = Math.max(0, availableQuota); // 不能為負數
      finalSelfPaid = finalTotalCost - finalSubsidy;
      limitType = '個人年度補助餘額';
    }

    // 更新表單數據
    localFormData.subsidyAmount = Math.floor(finalSubsidy);
    localFormData.selfPaidAmount = Math.floor(finalSelfPaid);
    localFormData.designFee = subsidyResult.designFee;
    localFormData.totalAmount = finalTotalCost;

    // 關鍵日誌：補助計算結果
    console.log(
      `💰 [田間管路補助] 系統:${irrigationSystemName}, 面積:${facilityAreaInHectares.toFixed(4)}公頃, ` +
      `管路材料:${currentTotalPipesPrice.toLocaleString()}, 設計費:${subsidyResult.designFee.toLocaleString()}, ` +
      `總成本:${finalTotalCost.toLocaleString()}, 補助:${Math.round(finalSubsidy).toLocaleString()}, ` +
      `自備:${Math.round(finalSelfPaid).toLocaleString()}, 限制類型:${limitType}`
    );

  } catch (error) {
    console.error('Error calculating subsidy:', error);
  } finally {
    isCalculatingSubsidy.value = false;
  }
  updateFormData();
};

// 更新組內排序 (當材料增刪時)
const updatePipeOrderWithinGroups = () => {
    const grouped = localFormData.pipes.reduce((acc, pipe) => {
        (acc[pipe.groupId] = acc[pipe.groupId] || []).push(pipe);
        return acc;
    }, {} as Record<number, any[]>);

    for (const groupId in grouped) {
        grouped[groupId].sort((a, b) => (a.originalIndex ?? Infinity) - (b.originalIndex ?? Infinity)) // 假設有個 originalIndex 或按加入順序
                       .forEach((pipe, index) => {
                           pipe.order = index + 1;
                       });
    }
    // This re-flattens and re-assigns to trigger reactivity if needed, or just ensure orders are updated.
    localFormData.pipes = Object.values(grouped).flat();
};


// 更新父組件數據
const updateFormData = () => {

  if (isUpdating.value) {
    return;
  }

  // 在此處進行任何必要的驗證
  const dataToEmit = {
    ...props.formData, // 保留父組件的其他步驟數據
    ...localFormData, // 將此步驟的數據嵌套
    // 🔧 Linus式修正：facilityArea 現在是 computed，確保使用正確的值
    facilityArea: facilityAreaFromStep2.value,
    valid: localValid.value // 或總是true，取決於您的導航邏輯
  };

  emit('update:formData', dataToEmit);
};

/**
 * 清除管路設施相關數據的統一函數
 * @param updateParent - 是否更新父組件（預設 true）
 * @returns Promise<void>
 */
const clearPipelineData = async (updateParent = true): Promise<void> => {
  // 清空管路列表
  localFormData.pipes = [];

  // 使用 nextTick 確保 Vue 響應式系統能夠正確更新 UI
  await nextTick();

  // 清空金額相關欄位
  localFormData.subsidyAmount = 0;
  localFormData.selfPaidAmount = 0;
  localFormData.totalAmount = 0;
  localFormData.designFee = 0;

  // 根據需要更新父組件
  if (updateParent) {
    await nextTick();
    updateFormData();
  }
};

// 跳過田間管路步驟功能
const skipStep = async () => {
  console.log('⏭️ [step4] Skipping step (田間管路) - using unified clearStepData');

  try {
    // 🔥 使用統一的原子性清除方法（與 step2 觸發的清除邏輯一致）
    // 這會清除：API + Store (formData/previousFormData/changedFields) + localStorage
    const success = await grantsStore.clearStepData(props.currentStep);

    if (!success) {
      console.error('❌ [step4] clearStepData failed');
      alert('清除資料失敗，請稍後再試');
      return;
    }

    console.log('✅ [step4] clearStepData succeeded (API + Store + localStorage cleared)');

    // 🔥 清除本地 UI 狀態（確保即時響應）
    Object.assign(localFormData, {
      // 基本欄位
      designerName: '',
      fieldLength: null,
      fieldWidth: null,
      fundingSourceId: 0,

      // 主管相關
      mainPipeLength: null,
      mainPipeDiameterId: null,
      mainPipeMaterialId: 1,
      mainPipeUnitPrice: null,
      mainPipeQuantity: null,
      mainPipeStandardLength: 4,

      // 主管2相關
      mainPipe2Enabled: false,
      mainPipe2Length: null,
      mainPipe2DiameterId: null,
      mainPipe2MaterialId: 1,
      mainPipe2UnitPrice: null,
      mainPipe2Quantity: null,
      mainPipe2StandardLength: 4,

      // 支管相關
      branchPipeSpacing_SL: null,
      sprinklerSpacing_SS: null,
      riserHeight_H: null,
      enableBranchDiameterChange: false,
      changeBranchSpecId: null,
      branchPipeMaterialId: null,
      branchPipeDiameterId: null,
      branchPipePomno: null,

      // 末端設施相關
      irrigationTypeId: null,
      sprinklerSubtypeId: null,
      dripperSubtypeId: null,
      perforatedPipeDirection: 1,
      installationType: null,
      waterSourceId: null,
      endFacilityPomno: null,
      endFacilitySpecId: null,
      riserPipeMaterialId: null,
      riserPipeSpecId: null,

      // 管路列表和補助
      pipes: [],
      totalAmount: 0,
      subsidyAmount: 0,
      selfPaidAmount: 0,
      designFee: 0,
    });

    // 使用 nextTick 確保響應式更新完成
    await nextTick();

    // 設置為有效狀態，允許跳過
    localValid.value = true;

    // 觸發 validated 事件，進入下一步
    emit('validated', {
      valid: true,
      step: props.currentStep
    });

    console.log('✅ [step4] Step skipped successfully');
  } catch (error) {
    console.error('❌ [step4] Skip step failed:', error);
    alert('操作失敗，請稍後再試');
  }
};

// 顯示缺少的必填欄位詳細信息
const showMissingFieldsInfo = () => {
  // 準備診斷信息
  const basicFieldStatus = {
    'fieldLength': !!localFormData.fieldLength ? '✓' : '✗',
    'fieldWidth': !!localFormData.fieldWidth ? '✓' : '✗',
    'fundingSourceId': (localFormData.fundingSourceId !== null) ? '✓' : '✗',
    'irrigationTypeId': !!localFormData.irrigationTypeId ? '✓' : '✗',
    'waterSourceId': !!localFormData.waterSourceId ? '✓' : '✗',
    'mainPipeLength': (localFormData.mainPipeLength !== null) ? '✓' : '✗',
    'mainPipeMaterialId': !!localFormData.mainPipeMaterialId ? '✓' : '✗',
    'mainPipeDiameterId': !!localFormData.mainPipeDiameterId ? '✓' : '✗'
  };

  // 主管2狀態 (如果啟用)
  const mainPipe2Status = localFormData.mainPipe2Enabled ? {
    'mainPipe2Length': !!localFormData.mainPipe2Length ? '✓' : '✗',
    'mainPipe2MaterialId': !!localFormData.mainPipe2MaterialId ? '✓' : '✗',
    'mainPipe2DiameterId': !!localFormData.mainPipe2DiameterId ? '✓' : '✗'
  } : { '主管2': '未啟用' };

  // 依灌溉型式建立不同的檢查項目
  let typeSpecificStatus = {};
  const irrigationType = localFormData.irrigationTypeId;

  if (irrigationType === 1) { // 穿孔管系統
    typeSpecificStatus = {
      'perforatedPipeDirection': (localFormData.perforatedPipeDirection !== null) ? '✓' : '✗',
      'branchPipeSpacing_SL': (localFormData.branchPipeSpacing_SL !== null) ? '✓' : '✗',
      'endFacilitySpecId': !!localFormData.endFacilitySpecId ? '✓' : '✗',
      // 支管材質和規格在穿孔管系統中不是必填欄位
      'branchPipeMaterialId (非必填)': !!localFormData.branchPipeMaterialId ? '✓' : '✗',
      'branchPipeDiameterId (非必填)': !!localFormData.branchPipeDiameterId ? '✓' : '✗'
    };
  } else if (irrigationType === 2) { // 噴頭式系統
    typeSpecificStatus = {
      'sprinklerSubtypeId': !!localFormData.sprinklerSubtypeId ? '✓' : '✗',
      'branchPipeSpacing_SL': (localFormData.branchPipeSpacing_SL !== null) ? '✓' : '✗',
      'sprinklerSpacing_SS': (localFormData.sprinklerSpacing_SS !== null) ? '✓' : '✗',
      'branchPipeMaterialId': !!localFormData.branchPipeMaterialId ? '✓' : '✗',
      'branchPipeDiameterId': !!localFormData.branchPipeDiameterId ? '✓' : '✗',
      'riserHeight_H': !!localFormData.riserHeight_H ? '✓' : '✗',
      'riserPipeMaterialId': !!localFormData.riserPipeMaterialId ? '✓' : '✗',
      'riserPipeSpecId': !!localFormData.riserPipeSpecId ? '✓' : '✗',
      'endFacilitySpecId': !!localFormData.endFacilitySpecId ? '✓' : '✗',
      'endFacilityPomno': !!localFormData.endFacilityPomno ? '✓' : '✗'
    };
  } else if (irrigationType === 3) { // 微噴系統
    typeSpecificStatus = {
      'installationType': !!localFormData.installationType ? '✓' : '✗',
      'branchPipeSpacing_SL': (localFormData.branchPipeSpacing_SL !== null) ? '✓' : '✗',
      'sprinklerSpacing_SS': (localFormData.sprinklerSpacing_SS !== null) ? '✓' : '✗',
      'branchPipeMaterialId': !!localFormData.branchPipeMaterialId ? '✓' : '✗',
      'branchPipeDiameterId': !!localFormData.branchPipeDiameterId ? '✓' : '✗',
      'riserHeight_H': !!localFormData.riserHeight_H ? '✓' : '✗',
      'endFacilitySpecId': !!localFormData.endFacilitySpecId ? '✓' : '✗',
      'endFacilityPomno': !!localFormData.endFacilityPomno ? '✓' : '✗'
    };
  } else if (irrigationType === 4) { // 滴灌系統
    // 只有滴嘴滴灌系統 (ID=7) 才需要檢查噴頭間距
    const needsSprinklerSpacing = localFormData.dripperSubtypeId === 7;

    typeSpecificStatus = {
      'dripperSubtypeId': !!localFormData.dripperSubtypeId ? '✓' : '✗',
      'installationType': !!localFormData.installationType ? '✓' : '✗',
      'branchPipeSpacing_SL': (localFormData.branchPipeSpacing_SL !== null) ? '✓' : '✗',
      'branchPipeMaterialId': !!localFormData.branchPipeMaterialId ? '✓' : '✗',
      'branchPipeDiameterId': !!localFormData.branchPipeDiameterId ? '✓' : '✗',
      'endFacilitySpecId': !!localFormData.endFacilitySpecId ? '✓' : '✗',
      'endFacilityPomno': !!localFormData.endFacilityPomno ? '✓' : '✗'
    };

    // 條件性地添加 sprinklerSpacing_SS 檢查
    if (needsSprinklerSpacing) {
      typeSpecificStatus['sprinklerSpacing_SS'] = (localFormData.sprinklerSpacing_SS !== null) ? '✓' : '✗';
    }
  } else {
    typeSpecificStatus = { '灌溉型式': '未選擇或不支援的類型' };
  }

  // 組合所有狀態資訊
  const allStatus = {
    '基本資料': basicFieldStatus,
    '主管2': mainPipe2Status,
    '灌溉型式特定欄位': typeSpecificStatus,
    '目前選擇的灌溉型式': irrigationType
  };

  // 顯示給使用者的診斷訊息
  const missingFields = [];

  // 檢查基本欄位
  Object.entries(basicFieldStatus).forEach(([field, status]) => {
    if (status === '✗') {
      const fieldName = getFieldDisplayName(field);
      missingFields.push(fieldName);
    }
  });

  // 檢查主管2欄位 (如果啟用)
  if (localFormData.mainPipe2Enabled) {
    Object.entries(mainPipe2Status).forEach(([field, status]) => {
      if (status === '✗') {
        const fieldName = getFieldDisplayName(field);
        missingFields.push(fieldName);
      }
    });
  }

  // 檢查特定灌溉型式欄位
  Object.entries(typeSpecificStatus).forEach(([field, status]) => {
    if (status === '✗') {
      const fieldName = getFieldDisplayName(field);
      missingFields.push(fieldName);
    }
  });

  // 準備訊息
  let message = '';
  if (missingFields.length > 0) {
    message = `缺少以下必填欄位:\n${missingFields.map(f => `• ${f}`).join('\n')}`;
  } else {
    message = '所有必填欄位皆已填寫，但可能有其他條件未滿足。請檢查控制台以獲取更多訊息。';
  }

  // 使用 alert 顯示訊息 (或可以改用其他 UI 元件)
  alert(message);
};

// 欄位名稱對照表，轉換為更友善的顯示名稱
const getFieldDisplayName = (fieldName: string) => {
  const fieldNameMap = {
    'fieldLength': '田間坵塊長度',
    'fieldWidth': '田間坵塊寬度',
    'fundingSourceId': '補助單位',
    'irrigationTypeId': '灌溉型式',
    'waterSourceId': '灌溉水源',
    'mainPipeLength': '主管1長度',
    'mainPipeMaterialId': '主管1材質',
    'mainPipeDiameterId': '主管1管徑',
    'mainPipe2Length': '主管2長度',
    'mainPipe2MaterialId': '主管2材質',
    'mainPipe2DiameterId': '主管2管徑',
    'perforatedPipeDirection': '穿孔管出水方向',
    'branchPipeSpacing_SL': '支管行距(SL)',
    'sprinklerSpacing_SS': '噴頭間距(SS)',
    'branchPipeMaterialId': '支管材質',
    'branchPipeDiameterId': '支管規格',
    'installationType': '設施型式',
    'sprinklerSubtypeId': '噴頭類型',
    'dripperSubtypeId': '滴灌類型',
    'riserHeight_H': '豎管高度',
    'riserPipeMaterialId': '豎管材質',
    'riserPipeSpecId': '豎管規格',
    'endFacilitySpecId': '末端設施規格',
    'endFacilityPomno': '末端設施名稱'
  };

  return fieldNameMap[fieldName] || fieldName;
};

// 獲取材料數據 - 實現14種公式條件的動態材料計算
// 材料生成版本控制參數
interface MaterialGenerationOptions {
  excludeNoPriceMaterials?: boolean; // 是否排除沒有單價的材料
  version?: 'v1' | 'v2'; // 版本控制：v1=包含所有材料，v2=排除無單價材料
}

const getMockMaterialData = (formInputs: FormInputs, options: MaterialGenerationOptions = {}) => {
  // 預設版本設定
  const { excludeNoPriceMaterials = false, version = 'v1' } = options;

  console.log(`[getMockMaterialData] 使用版本: ${version}, 排除無單價材料: ${excludeNoPriceMaterials}`);

  // 映射前端欄位到legacy欄位名稱
  const legacyData = mapToLegacyFields(formInputs);

  // 決定使用哪個公式
  const formulaNumber = determineFormula(legacyData);
  console.log(`[getMockMaterialData] 使用公式 ${formulaNumber} 進行材料計算 (版本: ${version})`);

  // 根據公式生成材料列表
  const materialGroups = generateMaterialsByFormula(formulaNumber, legacyData);

  // 🔥 Linus式修復：版本 v2 過濾邏輯
  if (version === 'v2' || excludeNoPriceMaterials) {
    return filterMaterialGroupsByPrice(materialGroups);
  }

  return materialGroups;
};

// 過濾沒有單價的材料（版本 v2 專用）
const filterMaterialGroupsByPrice = (materialGroups: MaterialGroup[]) => {
  const filteredGroups = materialGroups.map(group => {
    const filteredList = group.List.filter((material: MaterialItem) => {
      // 過濾條件：材料必須有有效的單價
      const hasValidPrice = material.matprice !== null &&
                           material.matprice !== undefined &&
                           material.matprice > 0;

      if (!hasValidPrice) {
        console.log(`[filterMaterialGroupsByPrice] 排除無單價材料: ${material.matname} (${material.description})`);
      }

      return hasValidPrice;
    });

    return {
      ...group,
      List: filteredList
    };
  }).filter(group => group.List.length > 0); // 移除空的群組

  const originalCount = materialGroups.reduce((sum, group) => sum + group.List.length, 0);
  const filteredCount = filteredGroups.reduce((sum, group) => sum + group.List.length, 0);

  console.log(`[filterMaterialGroupsByPrice] 過濾結果: ${originalCount} -> ${filteredCount} 項材料 (移除 ${originalCount - filteredCount} 項無單價材料)`);

  return filteredGroups;
};

// 映射前端欄位到Legacy系統欄位
const mapToLegacyFields = (formInputs: FormInputs) => {
  const fieldLength = localFormData.fieldLength || formInputs.Length || 0;
  const fieldWidth = localFormData.fieldWidth || formInputs.width || 0;
  const branchPipeSpacing = localFormData.branchPipeSpacing_SL || formInputs.SL || 0;
  const sprinklerSpacing = localFormData.sprinklerSpacing_SS || formInputs.SS || 0;

  // 計算支管數量和末端設施數量
  // 穿孔管配件計算使用 Math.floor (無條件捨去)
  const branchAmt = branchPipeSpacing > 0 ? new Big(fieldLength).div(branchPipeSpacing).round(0, Big.roundDown).toNumber() : 0;
  const branchLength = fieldWidth; // 支管長度通常等於田區寬度
  const nozzlePerBranch = sprinklerSpacing > 0 ? new Big(fieldWidth).div(sprinklerSpacing).round(0, Big.roundDown).toNumber() : 0;
  const totalNozzles = branchAmt * nozzlePerBranch;

  return {
    // 基本參數
    Length: fieldLength,
    width: fieldWidth,
    SL: branchPipeSpacing,
    SS: sprinklerSpacing,

    // 主管相關
    L1Len: formInputs.L1Len || localFormData.mainPipeLength || 0,
    L1Material: formInputs.L1Material || localFormData.mainPipeMaterialId || 1,
    L1Spec: formInputs.L1Spec || localFormData.mainPipeDiameterId || 1,
    L1Price: formInputs.L1Price || localFormData.mainPipeUnitPrice || 0,
    L1MatAmt: formInputs.L1MatAmt || localFormData.mainPipeQuantity || 0,
    L1Bend: 3, // 預設彎頭數量
    // L1Receptacle logic: 當主管1和主管2都配置且口徑相同時，塞口數量為2；否則為1
    L1Receptacle: (localFormData.mainPipe2Enabled &&
                   localFormData.mainPipeDiameterId &&
                   localFormData.mainPipe2DiameterId &&
                   localFormData.mainPipeDiameterId === localFormData.mainPipe2DiameterId) ? 2 : 1,

    // 主管2相關
    L2Len: localFormData.mainPipe2Enabled ? (localFormData.mainPipe2Length || 0) : 0,
    L2Material: localFormData.mainPipe2Enabled ? (localFormData.mainPipe2MaterialId || 0) : 0,
    L2Spec: localFormData.mainPipe2Enabled ? (localFormData.mainPipe2DiameterId || 0) : 0,
    L2Price: localFormData.mainPipe2Enabled ? (localFormData.mainPipe2UnitPrice || 0) : 0,
    L2MatAmt: localFormData.mainPipe2Enabled ? (localFormData.mainPipe2Quantity || 0) : 0,
    // L2Bend: localFormData.mainPipe2Enabled ? 2 : 0,
    L2Bend: localFormData.mainPipe2Enabled ? 3 : 0,

    // 灌溉系統類型
    ddl_EndType: formInputs.ddl_EndType || localFormData.irrigationTypeId || 1,
    ddl_Sprinkler: localFormData.sprinklerSubtypeId || 2,
    ddl_Drop: localFormData.dripperSubtypeId || 7,
    PerforatedPipe: localFormData.perforatedPipeDirection || 1,

    // 支管相關
    BranchAmt: branchAmt,
    BranchLength: branchLength,
    BranchSpec: localFormData.branchPipeDiameterId || formInputs.BranchSpec || 3,
    BranchMaterial: localFormData.branchPipeMaterialId || formInputs.BranchMaterial || 1,

    // 末端設施相關
    NozzleAmt: totalNozzles,
    NozzleMaterial: localFormData.endFacilitySpecId || formInputs.NozzleMaterial || 1,
    EndFacilityPomno: localFormData.endFacilityPomno, // 添加末端設施的 pomno

    // 豎管相關
    StandPipeSpec: localFormData.riserPipeSpecId || 2,
    StandPipeLength: localFormData.riserHeight_H,
    StdpipeMat: localFormData.riserPipeMaterialId || 1,

    // 變更相關
    ChangeBranchSpec: localFormData.changeBranchSpecId || 0, // 支管變徑規格ID
    NewBranchSpec: null,

    // 設施類型
    ddl_FacType: localFormData.installationType || 1,
    ddl_WtaerSrc: localFormData.waterSourceId || 1
  };
};

// 決定使用哪個公式
const determineFormula = (data: MaterialData): number => {
  const endType = data.ddl_EndType;
  const hasL2 = data.L2MatAmt > 0;
  // 規格變更條件：changeBranchSpecId不為0且與原支管規格不同
  const hasSpecChange = data.ChangeBranchSpec !== 0 && data.ChangeBranchSpec !== data.BranchSpec;
  const dropType = data.ddl_Drop;

  console.log(`[determineFormula] endType: ${endType}, hasL2: ${hasL2}, hasSpecChange: ${hasSpecChange}`);
  console.log(`[determineFormula] ChangeBranchSpec: ${data.ChangeBranchSpec}, BranchSpec: ${data.BranchSpec}`);

  if (endType === 1) { // 穿孔管系統
    if (!hasL2) return 1;
    return 2;
  }

  if (endType === 2) { // 噴頭式系統
    if (!hasSpecChange && !hasL2) return 3;
    if (!hasSpecChange && hasL2) return 4;
    if (hasSpecChange && !hasL2) return 5;
    if (hasSpecChange && hasL2) return 6;
  }

  if (endType === 3) { // 微噴系統
    if (!hasSpecChange && !hasL2) return 7;
    if (!hasSpecChange && hasL2) return 8;
    if (hasSpecChange && !hasL2) return 9;
    if (hasSpecChange && hasL2) return 10;
  }

  if (endType === 4) { // 滴灌系統
    if (dropType === 7) { // 滴嘴
      if (!hasL2) return 11;
      return 12;
    }
    if (dropType === 8) { // 滴水管
      if (!hasL2) return 13;
      return 14;
    }
  }

  return 1; // 預設公式
};

// 材料數量取整
// const calculateMaterialAmount = (amount: number, itemType: string): number => {
//   // 管材類型：無條件進位取整數
//   const pipeTypes = ['主管', '支管', '穿孔管', '滴灌管', '滴水帶', '豎管'];
//   if (pipeTypes.includes(itemType)) {
//     return Math.ceil(amount);
//   }

//   // 配件類型：無條件捨去取整數
//   const fittingTypes = ['主管配件', '支管配件', '穿孔管配件', '滴灌配件', '滴水帶配件', '豎管配件', '固定設施', '噴頭', '微噴頭', '滴嘴'];
//   if (fittingTypes.includes(itemType)) {
//     return Math.floor(amount);
//   }

//   // 預設使用無條件進位
//   return Math.ceil(amount);
// };

// 直接根據 pomno 比對材料 - 用於用戶已明確選擇的材料
const matchMaterialByPomno = (pomno: string | number): { pomno: number | null, matprice: number | null, matchedData: any | null } => {
  if (!pipeFittingsStore.pipeFittings || pipeFittingsStore.pipeFittings.length === 0) {
    return { pomno: null, matprice: null, matchedData: null };
  }

  const matchedMaterial = pipeFittingsStore.pipeFittings.find(fitting => fitting.pomno === pomno);

  if (matchedMaterial) {
    return {
      pomno: matchedMaterial.pomno,
      matprice: matchedMaterial.current_price || null,
      matchedData: matchedMaterial
    };
  }

  return { pomno: null, matprice: null, matchedData: null };
};

// 材料比對函數 - 根據 module_id 和 spec1 比對 pipeFittingsStore 中的材料
const matchMaterialFromStore = (moduleId: number, spec1: string, spec2?: string, spec3?: string, mattype?: string, matname?: string): { pomno: number | null, matprice: number | null, matchedData: any | null } => {
  if (!pipeFittingsStore.pipeFittings || pipeFittingsStore.pipeFittings.length === 0) {
    return { pomno: null, matprice: null, matchedData: null };
  }

  // 解析 spec1 中的數值 (例如: "1\"" -> 1, "2\"" -> 2, "3/4\"" -> 0.75)
  const parseSpecValue = (spec: string): number => {
    if (!spec) return 0;
    // 移除雙引號和單位
    const cleanSpec = spec.replace(/["\s]/g, '');
    // 處理分數格式 (如 3/4)
    if (cleanSpec.includes('/')) {
      const [numerator, denominator] = cleanSpec.split('/').map(Number);
      return numerator / denominator;
    }
    return parseFloat(cleanSpec) || 0;
  };

  // 文字模糊比對函數
  const fuzzyTextMatch = (searchText: string, targetText: string): boolean => {
    if (!searchText || !targetText) {
      return false;
    }

    const search = searchText.toLowerCase().trim();
    const target = targetText.toLowerCase().trim();

    // 完全比對
    if (target.includes(search)) {
      return true;
    }

    // 反向比對 - 檢查搜尋詞是否包含目標詞
    if (search.includes(target)) {
      return true;
    }

    // 關鍵字比對 - 將搜尋文字拆分成關鍵字進行比對
    const searchKeywords = search.split(/[\s\-_、，,]+/).filter(keyword => keyword.length > 0);
    const targetKeywords = target.split(/[\s\-_、，,]+/).filter(keyword => keyword.length > 0);

    // 檢查搜尋關鍵字是否在目標文字中
    const matchedFromSearch = searchKeywords.filter(keyword => target.includes(keyword));

    // 檢查目標關鍵字是否在搜尋文字中
    const matchedFromTarget = targetKeywords.filter(keyword => search.includes(keyword));

    // 如果搜尋關鍵字中有超過一半比對，或者目標關鍵字中有任一比對
    const searchMatchRatio = matchedFromSearch.length / searchKeywords.length;
    const targetMatchRatio = matchedFromTarget.length / targetKeywords.length;

    const isMatch = searchMatchRatio >= 0.5 || targetMatchRatio >= 0.5 || matchedFromTarget.length > 0;

    return isMatch;
  };

  // 輔助函數：檢查規格相容性
  // 對於多規格配件（如三通），spec1 對應 diameter1，spec2 對應 diameter2
  const checkSpecCompatibility = (fitting: any, spec1: string, spec2?: string, spec3?: string): boolean => {

    // 如果沒有提供規格要求，則認為相容
    if (!spec1 || spec1.trim() === '') {
      return true;
    }

    // 沒有設定規格的配件，直接相容
    if (!fitting.diameter1_id && !fitting.diameter2_id && !fitting.diameter3_id) {
      return true;
    }

    const spec1Value = parseSpecValue(spec1);
    const spec2Value = spec2 ? parseSpecValue(spec2) : null;
    const spec3Value = spec3 ? parseSpecValue(spec3) : null;

    // 檢查 spec1 是否匹配 diameter1
    const spec1MatchesDiameter1 =
      fitting.diameter1?.value === spec1Value ||
      fitting.diameter1?.name === spec1;

    // 如果有提供 spec2，檢查是否匹配 diameter2
    // 如果沒有提供 spec2，則不需要檢查 diameter2
    const spec2MatchesDiameter2 =
      !spec2Value ||
      !fitting.diameter2_id ||
      fitting.diameter2?.value === spec2Value ||
      fitting.diameter2?.name === spec2;

    // 如果有提供 spec3，檢查是否匹配 diameter3
    const spec3MatchesDiameter3 =
      !spec3Value ||
      !fitting.diameter3_id ||
      fitting.diameter3?.value === spec3Value ||
      fitting.diameter3?.name === spec3;

    // 多規格配件：所有提供的規格都必須匹配對應的 diameter
    if (spec2Value || spec3Value) {
      const isMatch = spec1MatchesDiameter1 && spec2MatchesDiameter2 && spec3MatchesDiameter3;
      // console.log(`[checkSpecCompatibility] Multi-spec match:`, { spec1MatchesDiameter1, spec2MatchesDiameter2, spec3MatchesDiameter3, isMatch });
      return isMatch;
    }

    // 單規格配件：spec1 可以匹配任何一個 diameter
    const singleSpecMatch =
      spec1MatchesDiameter1 ||
      fitting.diameter2?.value === spec1Value ||
      fitting.diameter2?.name === spec1 ||
      fitting.diameter3?.value === spec1Value ||
      fitting.diameter3?.name === spec1;

    // console.log(`[checkSpecCompatibility] Single-spec match: ${singleSpecMatch}`);
    return singleSpecMatch;
  };

  const spec1Value = parseSpecValue(spec1);
  // const spec2Value = spec2 ? parseSpecValue(spec2) : 0;
  // const spec3Value = spec3 ? parseSpecValue(spec3) : 0;

  // 在 pipeFittingsStore 中查找比對的材料
  const matchedMaterial = pipeFittingsStore.pipeFittings.find(fitting => {
    // 檢查 module_id 是否比對
    if (fitting.module_id !== moduleId) return false;

    // 當 module_id 為 1（管材類）時，需要額外比對材質名稱
    if (moduleId === 1 && mattype) {
      // 比對 material.name 中是否包含 mattype
      const materialNameMatch = fitting.material?.name?.includes(mattype) ||
                               fitting.name?.includes(mattype);
      if (!materialNameMatch) return false;
    }

    // 當 module_id 為 2(配件類) 或 3(其他特殊模組) 時，必須通過名稱模糊比對
    if ((moduleId === 2 || moduleId === 3) && matname) {
      // console.log(`[matchMaterialFromStore] Trying fuzzy match for module_id=${moduleId}, matname="${matname}", fitting.name="${fitting.name}"`);

      const nameMatch = fuzzyTextMatch(matname, fitting.name || '');
      if (nameMatch) {
        // console.log(`[matchMaterialFromStore] Name match found! Checking spec compatibility...`);
        // 如果名稱比對成功，還需要檢查規格是否相容
        const hasSpecMatch = checkSpecCompatibility(fitting, spec1, spec2, spec3);
        // console.log(`[matchMaterialFromStore] Spec compatibility: ${hasSpecMatch}`);
        if (hasSpecMatch) {
          // console.log(`[matchMaterialFromStore] FUZZY MATCH SUCCESS for "${matname}" -> "${fitting.name}"`);
          return true;
        }
      }
      // 對於 module_id = 2 或 3，如果提供了 matname 但名稱比對失敗，直接返回 false
      // 不允許僅通過規格比對成功而忽略名稱比對失敗的情況
      // console.log(`[matchMaterialFromStore] Name match failed for module_id=${moduleId}, matname="${matname}", fitting.name="${fitting.name}"`);
      return false;
    }

    // 當 module_id 為 2 或 3 但沒有提供 matname 時，或者 module_id 為 1 時
    // 執行規格比對邏輯

    // 檢查規格是否比對 - 比對 diameter1, diameter2, diameter3 的 id 或 value
    const diameterMatches = [
      fitting.diameter1_id,
      fitting.diameter2_id,
      fitting.diameter3_id
    ].some(diameterId => {
      if (!diameterId) return false;

      // 如果有 diameter 物件，比對 value
      const diameter1Match = fitting.diameter1?.value === spec1Value;
      const diameter2Match = fitting.diameter2?.value === spec1Value;
      const diameter3Match = fitting.diameter3?.value === spec1Value;

      return diameter1Match || diameter2Match || diameter3Match;
    });

    // 或者比對 diameter_id 直接比對
    const diameterIdMatches = [
      fitting.diameter1_id === pipeDiameterOptions.value.find(d => d.name === spec1)?.id,
      fitting.diameter2_id === pipeDiameterOptions.value.find(d => d.name === spec1)?.id,
      fitting.diameter3_id === pipeDiameterOptions.value.find(d => d.name === spec1)?.id
    ].some(Boolean);

    return diameterMatches || diameterIdMatches;
  });

  if (matchedMaterial) {
    return {
      pomno: matchedMaterial.pomno,
      matprice: matchedMaterial.current_price || null,
      matchedData: matchedMaterial
    };
  }

  return { pomno: null, matprice: null, matchedData: null };
};

// 輔助函數：添加材料 - 支援模糊比對和直接 pomno 比對
const addMaterial = (
  materials: MaterialItem[],
  moduleIdOrPomno: number | string,
  spec1: string = '',
  mattype: string = '',
  matname: string = '',
  materialConfig: Omit<MaterialItem, 'pomno' | 'matprice'>
): boolean => {
  let match;

  // 判斷是否為直接 pomno 比對
  if (typeof moduleIdOrPomno === 'string' || (typeof moduleIdOrPomno === 'number' && moduleIdOrPomno.toString().length > 3)) {
    // 直接使用 pomno 比對
    match = matchMaterialByPomno(moduleIdOrPomno);
    // console.log(`[addMaterial] 使用直接 pomno 比對: ${moduleIdOrPomno}`);
  } else {
    // 使用模糊比對
    const moduleId = moduleIdOrPomno as number;
    match = matchMaterialFromStore(moduleId, spec1, materialConfig.spec2 || '', materialConfig.spec3 || '', mattype, matname);
    // console.log(`[addMaterial] 使用模糊比對: moduleId=${moduleId}, spec1=${spec1}`);
  }

  if (match.pomno !== null && match.matprice !== null) {
    // 比對成功：使用真實的 pomno、matprice 和 matname
    materials.push({
      ...materialConfig,
      pomno: match.pomno,
      matprice: match.matprice,
      matname: match.matchedData?.name || materialConfig.matname, // 使用真實名稱
      mattype: match.matchedData?.material?.name || materialConfig.mattype, // 使用真實材質
      spec1: match.matchedData?.diameter1?.name || materialConfig.spec1, // 使用真實規格
      // debugMatchData: match.matchedData
    });

    // console.log(`[addMaterial] Successfully matched: ${materialConfig.matname} -> ${match.matchedData?.name} (${materialConfig.description})`);
    return true;
  } else {
    // 比對失敗：使用原始材料配置，但 pomno 和 matprice 設為空值
    materials.push({
      ...materialConfig,
      pomno: null,
      matprice: null,
      // debugMatchData: null
    });

    console.warn(`[addMaterial] No match found, using default values: ${materialConfig.matname}`, {
      moduleIdOrPomno,
      spec1,
      mattype,
      matname,
      description: materialConfig.description
    });
    return false;
  }
};

// 根據公式生成材料列表
const generateMaterialsByFormula = (formulaNumber: number, data: MaterialData): MaterialGroup[] => {
  const materialGroups: (MaterialGroup | undefined)[] = [];

  // 所有公式都包含主管1材料
  materialGroups.push(generateL1MainPipeLine(data));

  // 當主管材質為鍍鋅鋼時，添加制水閥到滴水管組
  materialGroups.push(generateGalvanizedSteelValveGroup(data));

  // 根據公式添加特定材料組
  switch (formulaNumber) {
    case 1:
      materialGroups.push(generatePerforatedPipe(data, data.L1Spec));
      break;
    case 2:
      materialGroups.push(generatePerforatedPipe(data, data.L1Spec));
      materialGroups.push(generateL2MainPipeLine(data));
      break;
    case 3:
      // 噴頭式系統 - 分別添加各個組件以保持正確分組
      materialGroups.push(generateBranchPipeGroup(data, data.L1Spec));
      materialGroups.push(generateStandPipeGroup(data));
      // materialGroups.push(generateFixedFacilitiesGroup(data));
      materialGroups.push(generateSprinklerHeadsGroup(data));
      break;
    case 4:
      // 噴頭式系統加L2主管 - 分別添加各個組件以保持正確分組
      materialGroups.push(generateBranchPipeGroup(data, data.L1Spec));
      materialGroups.push(generateStandPipeGroup(data));
      // materialGroups.push(generateFixedFacilitiesGroup(data));
      materialGroups.push(generateSprinklerHeadsGroup(data));
      materialGroups.push(generateL2MainPipeLine(data));
      break;
    case 5:
      // 噴頭式系統 + 支管變徑 - 分別添加各個組件以保持正確分組
      materialGroups.push(generateBranchPipeGroupWithSpecChange(data, data.L1Spec));
      materialGroups.push(generateStandPipeGroupWithSpecChange(data));
      // materialGroups.push(generateFixedFacilitiesGroup(data));
      materialGroups.push(generateSprinklerHeadsGroup(data));
      break;
    case 6:
      // 噴頭式系統 + 支管變徑 + 主管2 - 分別添加各個組件以保持正確分組
      materialGroups.push(generateBranchPipeGroupWithSpecChange(data, data.L1Spec));
      materialGroups.push(generateStandPipeGroupWithSpecChange(data));
      // materialGroups.push(generateFixedFacilitiesGroup(data));
      materialGroups.push(generateSprinklerHeadsGroup(data));
      materialGroups.push(generateL2MainPipeLine(data));
      break;
    case 7:
      // 微噴系統 - 分別添加各個組件以保持正確分組
      materialGroups.push(generateBranchPipeGroup(data, data.L1Spec));
      materialGroups.push(generateStandPipeGroup(data));
      // materialGroups.push(generateFixedFacilitiesGroup(data));
      materialGroups.push(generateMicroSprinklerHeadsGroup(data));
      break;
    case 8:
      // 微噴系統加L2主管 - 分別添加各個組件以保持正確分組
      materialGroups.push(generateBranchPipeGroup(data, data.L1Spec));
      materialGroups.push(generateStandPipeGroup(data));
      // materialGroups.push(generateFixedFacilitiesGroup(data));
      materialGroups.push(generateMicroSprinklerHeadsGroup(data));
      materialGroups.push(generateL2MainPipeLine(data));
      break;
    case 9:
      // 微噴系統 + 支管變徑 - 分別添加各個組件以保持正確分組
      materialGroups.push(generateBranchPipeGroupWithSpecChange(data, data.L1Spec));
      materialGroups.push(generateStandPipeGroupWithSpecChange(data));
      // materialGroups.push(generateFixedFacilitiesGroup(data));
      materialGroups.push(generateMicroSprinklerHeadsGroup(data));
      break;
    case 10:
      // 微噴系統 + 支管變徑 + 主管2 - 分別添加各個組件以保持正確分組
      materialGroups.push(generateBranchPipeGroupWithSpecChange(data, data.L1Spec));
      materialGroups.push(generateStandPipeGroupWithSpecChange(data));
      // materialGroups.push(generateFixedFacilitiesGroup(data));
      materialGroups.push(generateMicroSprinklerHeadsGroup(data));
      materialGroups.push(generateL2MainPipeLine(data));
      break;
    case 11:
      materialGroups.push(generateDripIrrigationSystem(data, data.L1Spec));
      materialGroups.push(generateDripperHeads(data)); // 單獨的滴嘴組
      break;
    case 12:
      materialGroups.push(generateDripIrrigationSystem(data, data.L1Spec));
      materialGroups.push(generateDripperHeads(data)); // 單獨的滴嘴組
      materialGroups.push(generateL2MainPipeLine(data));
      break;
    case 13:
      materialGroups.push(generateDripPipeIrrigationSystem(data, data.L1Spec));
      break;
    case 14:
      materialGroups.push(generateDripPipeIrrigationSystem(data, data.L1Spec));
      materialGroups.push(generateL2MainPipeLine(data));
      break;
  }

  return materialGroups.filter((group): group is MaterialGroup => !!(group && group.List && group.List.length > 0));
};

// 添加主管材料的專用函數，使用自定義單價
const addMainPipeMaterial = (
  materials: MaterialItem[],
  materialConfig: Omit<MaterialItem, 'pomno' | 'matprice'>,
  customPrice: number
) => {
  // 嘗試比對材料
  const match = matchMaterialFromStore(
    materialConfig.module_id,
    materialConfig.spec1,
    materialConfig.spec2 || '',
    materialConfig.spec3 || '',
    materialConfig.mattype,
    ''
  );

  // 使用自定義單價，但保留比對到的 pomno 和名稱
  materials.push({
    ...materialConfig,
    pomno: match.pomno,
    matprice: customPrice, // 使用田間主管配置的自定義單價
    matname: match.matchedData?.name || materialConfig.matname,
    mattype: match.matchedData?.material?.name || materialConfig.mattype,
    // debugMatchData: match.matchedData,
    isMainPipeMaterial: true, // 標記為主管材料
    customPrice: customPrice // 保存自定義價格
  });

  console.log(`[addMainPipeMaterial] 使用自定義單價: ${materialConfig.matname} -> ${customPrice}元`);
  return true;
};

// 生成主管1材料 (L1MainPipeLine)
const generateL1MainPipeLine = (data: any) => {
  const materials: MaterialItem[] = [];
  const L1MaterialName = pipeMaterialOptions.value.find(m => m.id === data.L1Material)?.name || '';
  const L1SpecName = pipeDiameterOptions.value.find(d => d.id === data.L1Spec)?.name || '';

  // 主管材料 - 使用田間主管配置的單價
  addMainPipeMaterial(materials, {
    module: '主管',
    matname: `${L1MaterialName} ${L1SpecName}`,
    module_id: 1,
    mattype: L1MaterialName,
    spec1: L1SpecName,
    spec2: '',
    spec3: '',
    itemunit: '支',
    matamount: Math.ceil(data.L1MatAmt || new Big(data.L1Len).div(4).round(0, Big.roundUp).toNumber()),
    description: '主管管材(L1)',
    order: 1,
    group: 1
  }, data.L1Price || 0);

  // 彎頭 (2025/06/06 更新：不需要顯示彎頭管材的計算結果)
  // addMaterial(materials, 2, L1SpecName, '', '彎頭', {
  //   module: '主管配件',
  //   matname: '彎頭',
  //   module_id: 2,
  //   mattype: L1MaterialName,
  //   spec1: L1SpecName,
  //   spec2: '',
  //   spec3: '',
  //   itemunit: '個',
  //   matamount: Math.floor(data.L1Bend || 3),
  //   description: '90度彎頭',
  //   order: 2,
  //   group: 1
  // });

  // 塞口
  addMaterial(materials, 2, L1SpecName, '', '塞口', {
    module: '主管配件',
    matname: '塞口',
    module_id: 2,
    mattype: L1MaterialName,
    spec1: L1SpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.L1Receptacle || 1),
    description: '塞口',
    order: 2,
    group: 1
  });

  return {
    GroupNo: 1,
    GroupName: '主管組',
    List: materials
  };
};

// 生成鍍鋅鋼制水閥材料組 (當主管使用鍍鋅鋼材質時)
const generateGalvanizedSteelValveGroup = (data: any) => {
  if (data.L1Material !== 20) { // 非鍍鋅鋼材質則返回空組
    return { GroupNo: 4, GroupName: '滴水管組', List: [] };
  }

  const L1MaterialName = pipeMaterialOptions.value.find(m => m.id === data.L1Material)?.name || 'PVC管';
  const L1SpecName = pipeDiameterOptions.value.find(d => d.id === data.L1Spec)?.name || '1"';

  // 比對制水閥材料
  const valveMatch = matchMaterialFromStore(10, L1SpecName, '', '', '', '制水閥');
  const materials = [{
    pomno: valveMatch.pomno,
    module: '主管配件',
    matname: '制水閥',
    module_id: 10,
    mattype: L1MaterialName,
    spec1: L1SpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matprice: valveMatch.matprice,
    matamount: Math.floor(1),
    description: '鍍鋅鋼主管制水閥',
    order: 1,
    group: 4,
    // debugMatchData: valveMatch.matchedData // 除錯用資料
  }];

  return {
    GroupNo: 4,
    GroupName: '滴水管組',
    List: materials
  };
};

// 生成主管2材料 (L2MainPipeLine)
const generateL2MainPipeLine = (data: any) => {
  if (data.L2MatAmt <= 0) {
    return { GroupNo: 1, GroupName: '主管路', List: [] };
  }

  const materials: MaterialItem[] = [];
  const L2MaterialName = pipeMaterialOptions.value.find(m => m.id === data.L2Material)?.name || 'PVC管';
  const L2SpecName = pipeDiameterOptions.value.find(d => d.id === data.L2Spec)?.name || '1"';

  // 主管2材料 - 使用田間主管配置的單價
  addMainPipeMaterial(materials, {
    module: '主管',
    matname: `${L2MaterialName} ${L2SpecName}`,
    module_id: 1,
    mattype: L2MaterialName,
    spec1: L2SpecName,
    spec2: '',
    spec3: '',
    itemunit: '支',
    matamount: Math.ceil(data.L2MatAmt || new Big(data.L2Len).div(4).round(0, Big.roundUp).toNumber()),
    description: '主管管材(L2)',
    order: 3,
    group: 1
  }, data.L2Price || 0);


  // 主管2彎頭
  // addMaterial(materials, 2, L2SpecName, '', '彎頭', {
  //   module: '主管配件',
  //   matname: '彎頭',
  //   module_id: 2,
  //   mattype: L2MaterialName,
  //   spec1: L2SpecName,
  //   spec2: '',
  //   spec3: '',
  //   itemunit: '個',
  //   matamount: Math.floor(data.L2Bend || 2),
  //   description: '90度彎頭',
  //   order: 2,
  //   group: 1
  // });

  return {
    GroupNo: 1,
    GroupName: '主管組',
    List: materials
  };
};

// 生成穿孔管系統材料
const generatePerforatedPipe = (data: any, mainPipeSpec: any) => {
  const materials: MaterialItem[] = [];
  // 新的穿孔管管材計算方式:
  // 1. 行數 = Math.floor(fieldLength / branchPipeSpacing_SL) (已在BranchAmt中實現)
  // 2. 穿孔管長度 = 行數 * fieldWidth
  // 3. 穿孔管數量 = Math.ceil(穿孔管長度 / 100) (以100m為單位計價)
  // 注意：雙向出水時穿孔管管材長度不變，只有配件數量會加倍
  // 2026_01上線更新：雙向出水不影響支管數量
  const perforatedTotalLength = data.BranchAmt * data.BranchLength; // 總穿孔管長度
  const isDoubleDirection = data.PerforatedPipe === 2;
  const multiplier = isDoubleDirection ? 2 : 1; // 僅用於配件計算

  // 計算以100m為單位的穿孔管數量（不受雙向影響）
  const perforatedQuantityPer100m = new Big(perforatedTotalLength).div(100).round(0, Big.roundUp).toNumber();

  // 從用戶選擇的末端設施中獲取正確的規格和材質資訊
  const selectedEndFacility = pipeFittingsStore.pipeFittings.find(
    fitting => fitting.pomno === localFormData.endFacilityPomno
  );

  // 如果找到用戶選擇的末端設施，使用其規格和材質；否則使用預設值
  let nozzleSpecName: string = '';
  let endFacilityMaterial: string = '';
  if (selectedEndFacility) {
    // 使用末端設施的第一個管徑作為穿孔管規格
    nozzleSpecName = selectedEndFacility.diameter1?.name ||
                     selectedEndFacility.diameter2?.name ||
                     selectedEndFacility.diameter3?.name || '';
    endFacilityMaterial = selectedEndFacility.material?.name || '';
    // console.log(`[generatePerforatedPipe] 使用末端設施規格: ${nozzleSpecName}, 材質: ${endFacilityMaterial}`);
  } else {
    // 回退到舊邏輯
    // nozzleSpecName = pipeDiameterOptions.value.find(d => d.id === data.NozzleMaterial)?.name || '3/4"';
    // endFacilityMaterial = 'PE';
    // console.warn(`[generatePerforatedPipe] 未找到末端設施 pomno=${localFormData.endFacilityPomno}，使用預設規格: ${nozzleSpecName}`);
  }

  const mainSpecName = pipeDiameterOptions.value.find(d => d.id === mainPipeSpec)?.name || '';

  // 穿孔管 - 直接使用用戶選擇的末端設施 pomno 進行精確比對
  const perforatedPipeMatch = matchMaterialByPomno(localFormData.endFacilityPomno);

  // 取得實際的標準長度，若無資料則預設為100
  const standardLength = perforatedPipeMatch.matchedData?.length || 100;

  // 計算穿孔管數量 = Math.ceil(總長度 / 標準長度)
  const perforatedQuantity = new Big(perforatedTotalLength).div(standardLength).round(0, Big.roundUp).toNumber();

  // 穿孔管
  addMaterial(materials, localFormData.endFacilityPomno, nozzleSpecName, endFacilityMaterial, '', {
    module: '穿孔管',
    matname: perforatedPipeMatch.matchedData?.name || '穿孔管',
    module_id: 6,
    mattype: endFacilityMaterial,
    spec1: nozzleSpecName,
    spec2: '',
    spec3: '',
    itemunit: standardLength === 100 ? '100m' : `${standardLength}m`,
    // matamount: perforatedQuantity * multiplier, // 雙向出水不影響管材數量
    matamount: perforatedQuantity,
    description: `穿孔管材(${standardLength}m計價)`,
    order: 1,
    group: 3
  });

  // 三通或四通
  const fittingName = data.PerforatedPipe === 1 ? '三通' : '四通';
  addMaterial(materials, 2, mainSpecName, '', fittingName, {
    module: '穿孔管配件',
    matname: fittingName,
    module_id: 2,
    mattype: 'PVC',
    spec1: mainSpecName,
    spec2: nozzleSpecName,
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt),
    description: `主管轉穿孔管${fittingName}`,
    order: 2,
    group: 3
  });

  // 制水閥
  addMaterial(materials, 10, nozzleSpecName, '', '制水閥', {
    module: '穿孔管配件',
    matname: '制水閥',
    module_id: 10,
    mattype: 'PVC',
    spec1: nozzleSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt * multiplier),
    description: '穿孔管制水閥',
    order: 3,
    group: 3
  });

  // 穿孔管接頭
  addMaterial(materials, 2, nozzleSpecName, '', '穿孔管接頭', {
    module: '穿孔管配件',
    matname: '穿孔管接頭',
    module_id: 2,
    mattype: 'PE',
    spec1: nozzleSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt * multiplier),
    description: '穿孔管首端配件',
    order: 4,
    group: 3
  });

  // 穿孔管尾夾
  addMaterial(materials, 2, nozzleSpecName, '', '穿孔管尾夾', {
    module: '穿孔管配件',
    matname: '穿孔管尾夾',
    module_id: 2,
    mattype: 'PE',
    spec1: nozzleSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt * multiplier),
    description: '穿孔管末端固定',
    order: 5,
    group: 3
  });

  return {
    GroupNo: 3,
    GroupName: '穿孔管組',
    List: materials
  };
};

// 生成支管組材料 (獨立分組)
const generateBranchPipeGroup = (data: any, mainPipeSpec: any) => {
  const materials = generateBranchPipeMaterials(data, mainPipeSpec, 2);
  return {
    GroupNo: 2,
    GroupName: '支管組',
    List: materials
  };
};

// 生成支管組材料 (含變徑規格) - 公式5專用
const generateBranchPipeGroupWithSpecChange = (data: any, mainPipeSpec: any) => {
  const materials = generateBranchPipeMaterialsWithSpecChange(data, mainPipeSpec, 2);
  return {
    GroupNo: 2,
    GroupName: '支管組',
    List: materials
  };
};

// 生成支管材料的通用函數
const generateBranchPipeMaterials = (data: any, mainPipeSpec: any, groupId: number) => {
  const materials: MaterialItem[] = [];
  const branchMaterialName = pipeMaterialOptions.value.find(m => m.id === data.BranchMaterial)?.name || '';
  const branchSpecName = pipeDiameterOptions.value.find(d => d.id === data.BranchSpec)?.name || '';
  const mainSpecName = pipeDiameterOptions.value.find(d => d.id === mainPipeSpec)?.name || '';

  // 先比對支管材料以取得實際的標準長度
  const branchPipeMatch = matchMaterialFromStore(1, branchSpecName, '', '', branchMaterialName, '');
  // 取得實際的標準長度，若無資料則預設為 4m
  const standardLength = branchPipeMatch.matchedData?.length || 4;
  // 計算支管總長度
  const totalBranchLength = data.BranchAmt * data.BranchLength;
  // 計算支管數量
  const branchQuantity = new Big(totalBranchLength).div(standardLength).round(0, Big.roundUp).toNumber();

  // 支管
  addMaterial(materials, 1, branchSpecName, branchMaterialName, '', {
    module: '支管',
    matname: `${branchMaterialName} ${branchSpecName}`,
    module_id: 1,
    mattype: branchMaterialName,
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: `${standardLength}m`,
    matamount: branchQuantity,
    description: `支管管材(${standardLength}m計價)`,
    order: 1,
    group: groupId
  });

  // 三通
  addMaterial(materials, 2, mainSpecName, '', '三通', {
    module: '支管配件',
    matname: '三通',
    module_id: 2,
    mattype: 'PVC',
    spec1: mainSpecName,
    spec2: branchSpecName,
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt),
    description: '主管轉支管三通',
    order: 2,
    group: groupId
  });

  // 制水閥
  addMaterial(materials, 10, branchSpecName, '', '制水閥', {
    module: '支管配件',
    matname: '制水閥',
    module_id: 10,
    mattype: 'PVC',
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt),
    description: '支管制水閥',
    order: 3,
    group: groupId
  });

  // 閥接頭
  // addMaterial(materials, 2, branchSpecName, '', '閥接頭', {
  //   module: '支管配件',
  //   matname: '閥接頭',
  //   module_id: 2,
  //   mattype: 'PVC',
  //   spec1: branchSpecName,
  //   spec2: '',
  //   spec3: '',
  //   itemunit: '個',
  //   matamount: Math.floor(data.BranchAmt * 2),
  //   description: '制水閥接頭',
  //   order: 4,
  //   group: groupId
  // });

  // 塞口
  addMaterial(materials, 2, branchSpecName, '', '塞口', {
    module: '支管配件',
    matname: '塞口',
    module_id: 2,
    mattype: 'PVC',
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt),
    description: '支管末端塞口',
    order: 4,
    group: groupId
  });

  return materials;
};

// 生成支管材料 (含規格變更邏輯) - 公式5專用
const generateBranchPipeMaterialsWithSpecChange = (data: any, mainPipeSpec: any, groupId: number) => {
  const materials: MaterialItem[] = [];
  const branchMaterialName = pipeMaterialOptions.value.find(m => m.id === data.BranchMaterial)?.name ?? '';
  const branchSpecName = pipeDiameterOptions.value.find(d => d.id === data.BranchSpec)?.name ?? '';
  const changeBranchSpecName = pipeDiameterOptions.value.find(d => d.id === data.ChangeBranchSpec)?.name ?? '';
  const mainSpecName = pipeDiameterOptions.value.find(d => d.id === mainPipeSpec)?.name ?? '';

  // 比對原規格支管材料以取得標準長度
  const branchPipeMatch = matchMaterialFromStore(1, branchSpecName, '', '', branchMaterialName, '');
  const branchStandardLength = branchPipeMatch.matchedData?.length || 4;

  // 比對變徑規格支管材料以取得標準長度
  const changeBranchPipeMatch = matchMaterialFromStore(1, changeBranchSpecName, '', '', branchMaterialName, '');
  const changeBranchStandardLength = changeBranchPipeMatch.matchedData?.length || 4;

  // 計算支管總長度
  const totalBranchLength = data.BranchAmt * data.BranchLength;

  // 1. 原規格支管 (2/3 數量)
  const originalBranchQuantity = new Big(totalBranchLength).times(2).div(3).div(branchStandardLength).round(0, Big.roundUp).toNumber();
  addMaterial(materials, 1, branchSpecName, branchMaterialName, '', {
    module: '支管',
    matname: `${branchMaterialName} ${branchSpecName}`,
    module_id: 1,
    mattype: branchMaterialName,
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: `${branchStandardLength}m`,
    matamount: originalBranchQuantity,
    description: `支管管材(支管規格, ${branchStandardLength}m計價)`,
    order: 1,
    group: groupId
  });

  // 2. 變徑規格支管 (1/3 數量)
  const changeBranchQuantity = new Big(totalBranchLength).div(3).div(changeBranchStandardLength).round(0, Big.roundUp).toNumber();
  addMaterial(materials, 1, changeBranchSpecName, branchMaterialName, '', {
    module: '支管',
    matname: `${branchMaterialName} ${changeBranchSpecName}`,
    module_id: 1,
    mattype: branchMaterialName,
    spec1: changeBranchSpecName,
    spec2: '',
    spec3: '',
    itemunit: `${changeBranchStandardLength}m`,
    matamount: changeBranchQuantity,
    description: `支管管材(變徑規格, ${changeBranchStandardLength}m計價)`,
    order: 2,
    group: groupId
  });

  // 3. 異徑接頭 (支管×變徑規格) - 連接兩種不同規格的支管
  addMaterial(materials, 2, branchSpecName, changeBranchSpecName, '異徑接頭', {
    module: '支管配件',
    matname: '異徑接頭',
    module_id: 2,
    mattype: 'PVC',
    spec1: branchSpecName,
    spec2: changeBranchSpecName,
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt), // 與三通數量相同
    description: `支管異徑接頭 (${branchSpecName}×${changeBranchSpecName})`,
    order: 3,
    group: groupId
  });

  // 4. 三通 (主管×支管) - 與公式3相同
  addMaterial(materials, 2, mainSpecName, '', '三通', {
    module: '支管配件',
    matname: '三通',
    module_id: 2,
    mattype: 'PVC',
    spec1: mainSpecName,
    spec2: branchSpecName,
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt), // 與公式3相同的三通數量
    description: '主管轉支管三通',
    order: 4,
    group: groupId
  });

  // 5. 制水閥 (與公式3相同)
  addMaterial(materials, 10, branchSpecName, '', '制水閥', {
    module: '支管配件',
    matname: '制水閥',
    module_id: 10,
    mattype: 'PVC',
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt),
    description: '支管制水閥',
    order: 5,
    group: groupId
  });

  // 6. 塞口 (與公式3相同)
  addMaterial(materials, 2, branchSpecName, '', '塞口', {
    module: '支管配件',
    matname: '塞口',
    module_id: 2,
    mattype: 'PVC',
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt),
    description: '支管末端塞口',
    order: 6,
    group: groupId
  });

  return materials;
};

// 生成豎管組材料 (獨立分組)
const generateStandPipeGroup = (data: any) => {
  // 當豎管高度為 0 時，不生成豎管組
  if (data.StandPipeLength > 0) {
    const materials = generateStandPipeMaterials(data, 5);
    return {
      GroupNo: 5,
      GroupName: '豎管組',
      List: materials
    };
  }
};

// 生成豎管組材料 (含變徑規格) - 公式5專用
const generateStandPipeGroupWithSpecChange = (data: any) => {
  // 當豎管高度為 0 時，不生成豎管組
  if (data.StandPipeLength > 0) {
    const materials = generateStandPipeMaterialsWithSpecChange(data, 5);
    return {
      GroupNo: 5,
      GroupName: '豎管組',
      List: materials
    };
  }
};

// 生成豎管材料
const generateStandPipeMaterials = (data: any, groupId: number) => {
  const materials: MaterialItem[] = [];
  const standPipeMaterialName = pipeMaterialOptions.value.find(m => m.id === data.StdpipeMat)?.name || '';
  const standPipeSpecName = pipeDiameterOptions.value.find(d => d.id === data.StandPipeSpec)?.name || '';
  const branchSpecName = pipeDiameterOptions.value.find(d => d.id === data.BranchSpec)?.name || '';

  // 比對豎管材料以取得實際的標準長度
  const standPipeMatch = matchMaterialFromStore(4, standPipeSpecName, '', '', standPipeMaterialName, '');
  // 取得實際的標準長度，若無資料則預設為 4m
  const standardLength = standPipeMatch.matchedData?.length || 4;
  // 計算豎管總長度
  const totalStandPipeLength = data.NozzleAmt * data.StandPipeLength;
  // 計算豎管數量
  const standPipeQuantity = new Big(totalStandPipeLength).div(standardLength).round(0, Big.roundUp).toNumber();

  // 豎管
  addMaterial(materials, 4, standPipeSpecName, standPipeMaterialName, '', {
    module: '豎管',
    matname: `${standPipeSpecName} ${standPipeMaterialName} 豎管`,
    module_id: 4,
    mattype: standPipeMaterialName,
    spec1: standPipeSpecName,
    spec2: '',
    spec3: '',
    itemunit: `${standardLength}m`,
    matamount: standPipeQuantity,
    description: `豎管材料(${standardLength}m計價)`,
    order: 1,
    group: groupId
  });

  // 豎管三通
  addMaterial(materials, 2, branchSpecName, '', '三通', {
    module: '豎管配件',
    matname: '三通',
    module_id: 2,
    mattype: 'PVC',
    spec1: branchSpecName,
    spec2: standPipeSpecName,
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.NozzleAmt),
    description: '支管轉豎管三通',
    order: 2,
    group: groupId
  });

  // 豎管制水閥
  addMaterial(materials, 10, standPipeSpecName, '', '制水閥', {
    module: '豎管配件',
    matname: '制水閥',
    module_id: 10,
    mattype: 'PVC',
    spec1: standPipeSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.NozzleAmt),
    description: '豎管制水閥',
    order: 3,
    group: groupId
  });

  addMaterial(materials, 2, standPipeSpecName, '', '直龍口', {
    module: '豎管配件',
    matname: '直龍口',
    module_id: 2,
    mattype: 'PVC',
    spec1: standPipeSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.NozzleAmt),
    description: '豎管直龍口',
    order: 4,
    group: groupId
  });

  // 豎管閥接頭
  // addMaterial(materials, 2, standPipeSpecName, '', '閥接頭', {
  //   module: '豎管配件',
  //   matname: '閥接頭',
  //   module_id: 2,
  //   mattype: 'PVC',
  //   spec1: standPipeSpecName,
  //   spec2: '',
  //   spec3: '',
  //   itemunit: '個',
  //   matamount: Math.floor(data.NozzleAmt * 2),
  //   description: '豎管制水閥接頭',
  //   order: 4,
  //   group: groupId
  // });

  return materials;
};

// 生成豎管材料 (含變徑規格) - 公式5專用
const generateStandPipeMaterialsWithSpecChange = (data: any, groupId: number) => {
  const materials: MaterialItem[] = [];
  const standPipeMaterialName = pipeMaterialOptions.value.find(m => m.id === data.StdpipeMat)?.name || '';
  const standPipeSpecName = pipeDiameterOptions.value.find(d => d.id === data.StandPipeSpec)?.name || '';
  const branchSpecName = pipeDiameterOptions.value.find(d => d.id === data.BranchSpec)?.name || '';
  const changeBranchSpecName = pipeDiameterOptions.value.find(d => d.id === data.ChangeBranchSpec)?.name || '';

  // 比對豎管材料以取得實際的標準長度
  const standPipeMatch = matchMaterialFromStore(4, standPipeSpecName, '', '', standPipeMaterialName, '');
  const standardLength = standPipeMatch.matchedData?.length || 4;
  // 計算豎管總長度
  const totalStandPipeLength = data.NozzleAmt * data.StandPipeLength;
  // 計算豎管數量
  const standPipeQuantity = new Big(totalStandPipeLength).div(standardLength).round(0, Big.roundUp).toNumber();

  // 1. 豎管 (與公式3相同)
  addMaterial(materials, 4, standPipeSpecName, standPipeMaterialName, '', {
    module: '豎管',
    matname: `${standPipeSpecName} ${standPipeMaterialName} 豎管`,
    module_id: 4,
    mattype: standPipeMaterialName,
    spec1: standPipeSpecName,
    spec2: '',
    spec3: '',
    itemunit: `${standardLength}m`,
    matamount: standPipeQuantity,
    description: `豎管材料(${standardLength}m計價)`,
    order: 1,
    group: groupId
  });

  // 2. 三通 (支管規格×豎管規格) - 數量為公式3三通的2/3
  addMaterial(materials, 2, branchSpecName, '', '三通', {
    module: '豎管配件',
    matname: '三通',
    module_id: 2,
    mattype: 'PVC',
    spec1: branchSpecName,
    spec2: standPipeSpecName,
    spec3: '',
    itemunit: '只',
    matamount: new Big(data.NozzleAmt).times(2).div(3).round(0, Big.roundDown).toNumber(),
    description: '支管轉豎管三通 (支管規格)',
    order: 2,
    group: groupId
  });

  // 3. 三通 (變徑規格×豎管規格) - 數量為公式3三通的1/3
  addMaterial(materials, 2, changeBranchSpecName, '', '三通', {
    module: '豎管配件',
    matname: '三通',
    module_id: 2,
    mattype: 'PVC',
    spec1: changeBranchSpecName,
    spec2: standPipeSpecName,
    spec3: '',
    itemunit: '只',
    matamount: new Big(data.NozzleAmt).div(3).round(0, Big.roundDown).toNumber(),
    description: '支管轉豎管三通 (變徑規格)',
    order: 3,
    group: groupId
  });

  // 4. 豎管制水閥 (與公式3相同)
  addMaterial(materials, 10, standPipeSpecName, '', '制水閥', {
    module: '豎管配件',
    matname: '制水閥',
    module_id: 10,
    mattype: 'PVC',
    spec1: standPipeSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.NozzleAmt),
    description: '豎管制水閥',
    order: 4,
    group: groupId
  });

  // 5. 直龍口 (與公式3相同)
  addMaterial(materials, 2, standPipeSpecName, '', '直龍口', {
    module: '豎管配件',
    matname: '直龍口',
    module_id: 2,
    mattype: 'PVC',
    spec1: standPipeSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.NozzleAmt),
    description: '豎管直龍口',
    order: 5,
    group: groupId
  });

  return materials;
};

// 生成固定設施組材料 (獨立分組)
// const generateFixedFacilitiesGroup = (data: any) => {
//   const materials = generateFixedFacilities(data, 6);
//   return {
//     GroupNo: 6,
//     GroupName: '固定設施組',
//     List: materials
//   };
// };

// 生成固定設施材料
const generateFixedFacilities = (data: any, groupId: number) => {
  const materials: MaterialItem[] = [];

  addMaterial(materials, 11, '支架用', '', '鍍鋅鋼管', {
    module: '固定設施',
    matname: '鍍鋅鋼管',
    module_id: 11,
    mattype: '鋼管',
    spec1: '支架用',
    spec2: '',
    spec3: '',
    itemunit: '條',
    matamount: Math.floor(data.NozzleAmt), // 配件用無條件捨去
    description: '噴頭固定支架',
    order: 1,
    group: groupId
  });

  return materials;
};

// 生成噴頭組材料 (獨立分組)
const generateSprinklerHeadsGroup = (data: any) => {
  const materials = generateSprinklerHeads(data, 8);
  return {
    GroupNo: 8,
    GroupName: '末端設施',
    List: materials
  };
};

// 生成噴頭材料
const generateSprinklerHeads = (data: any, groupId: number) => {
  const materials: MaterialItem[] = [];

  // 噴頭 - 直接使用用戶選擇的末端設施 pomno 進行精確比對
  const sprinklerMatch = matchMaterialByPomno(localFormData.endFacilityPomno);
  materials.push({
    pomno: sprinklerMatch.pomno,
    module: '噴頭',
    matname: sprinklerMatch.matchedData?.name || '可調式噴頭',
    module_id: 5,
    mattype: sprinklerMatch.matchedData?.material?.name || '塑膠',
    spec1: sprinklerMatch.matchedData?.diameter1?.name || '1/2"',
    spec2: '',
    spec3: '',
    itemunit: '只',
    matprice: sprinklerMatch.matprice,
    matamount: Math.floor(data.NozzleAmt), // 配件用無條件捨去
    description: '末端噴灑裝置',
    order: 1,
    group: groupId,
    // debugMatchData: sprinklerMatch.matchedData
  });

  return materials;
};


// 生成微噴系統材料
const generateMicroSprinklerSystem = (data: any, mainPipeSpec: any) => {
  const materials: MaterialItem[] = [];

  // 支管材料 (與噴頭系統類似)
  materials.push(...generateBranchPipeMaterials(data, mainPipeSpec, 2));

  // 豎管/懸吊管材料
  materials.push(...generateStandPipeMaterials(data, 5));

  // 固定設施
  materials.push(...generateFixedFacilities(data, 6));

  // 微噴頭
  materials.push(...generateMicroSprinklerHeads(data, 8));

  return {
    GroupNo: 2,
    GroupName: '微噴系統組',
    List: materials
  };
};

// 生成微噴頭組材料 (獨立分組)
const generateMicroSprinklerHeadsGroup = (data: any) => {
  const materials = generateMicroSprinklerHeads(data, 8);
  return {
    GroupNo: 8,
    GroupName: '末端設施',
    List: materials
  };
};

// 生成微噴頭材料
const generateMicroSprinklerHeads = (data: any, groupId: number) => {
  const materials: MaterialItem[] = [];

  // 微噴頭 - 直接使用用戶選擇的末端設施 pomno 進行精確比對
  const microSprinklerMatch = matchMaterialByPomno(localFormData.endFacilityPomno);
  materials.push({
    pomno: microSprinklerMatch.pomno,
    module: '微噴頭',
    matname: microSprinklerMatch.matchedData?.name || '微噴頭',
    module_id: 8,
    mattype: microSprinklerMatch.matchedData?.material?.name || '塑膠',
    spec1: microSprinklerMatch.matchedData?.diameter1?.name || '1/4"',
    spec2: '',
    spec3: '',
    itemunit: '只',
    matprice: microSprinklerMatch.matprice,
    matamount: Math.floor(data.NozzleAmt), // 配件用無條件捨去
    description: '微噴頭裝置',
    order: 1,
    group: groupId,
    // debugMatchData: microSprinklerMatch.matchedData
  });

  return materials;
};

// 生成微噴變更系統材料
// const generateMicroSprinklerChangeSystem = (data: any, mainPipeSpec: any) => {
//   // 與generateMicroSprinklerSystem相同，但處理規格變更
//   return generateMicroSprinklerSystem(data, mainPipeSpec);
// };

// 生成滴灌系統材料 (滴嘴)
const generateDripIrrigationSystem = (data: any, mainPipeSpec: any) => {
  const materials: MaterialItem[] = [];
  const branchMaterialName = pipeMaterialOptions.value.find(m => m.id === data.BranchMaterial)?.name || 'PE管';
  const branchSpecName = pipeDiameterOptions.value.find(d => d.id === data.BranchSpec)?.name || '16mm';
  const mainSpecName = pipeDiameterOptions.value.find(d => d.id === mainPipeSpec)?.name || '1"';

  // 滴灌管 - 當ID=7時，使用選擇的滴水管名稱和規格
  if (localFormData.dripperSubtypeId === 7 && localFormData.branchPipePomno) {
    // ID=7：使用選擇的滴水管件（來源與ID=8相同）
    const branchPipeMatch = matchMaterialByPomno(localFormData.branchPipePomno);
    const selectedBranchPipe = filteredBranchPipeFittings.value.find(
      fitting => fitting.pomno === localFormData.branchPipePomno
    );

    if (branchPipeMatch.matchedData || selectedBranchPipe) {
      const branchPipeName = branchPipeMatch.matchedData?.name || selectedBranchPipe?.displayName || '滴灌管';
      const branchPipeMaterial = branchPipeMatch.matchedData?.material?.name || selectedBranchPipe?.materialName || 'PE';
      const branchPipeSpec = branchPipeMatch.matchedData?.diameter1?.name || selectedBranchPipe?.specName || branchSpecName;

      // 計算管材數量：總長度除以標準長度，當length欄位為空值時固定除4
      const materialLength = branchPipeMatch.matchedData?.length || 4;
      const totalLength = data.BranchAmt * data.width;
      const materialQuantity = new Big(totalLength).div(materialLength).round(0, Big.roundUp).toNumber();

      addMaterial(materials, localFormData.branchPipePomno, branchPipeSpec, branchPipeMaterial, '', {
        module: '滴灌管',
        matname: branchPipeName,
        module_id: 12,
        mattype: branchPipeMaterial,
        spec1: branchPipeSpec,
        spec2: '',
        spec3: '',
        itemunit: `${materialLength}m`,
        matamount: materialQuantity,
        description: `滴灌管材`,
        order: 1,
        group: 4
      });
    }
  } else {
    // 其他情況：使用原有邏輯，預設長度為4m計價
    const defaultMaterialLength = 4;
    const totalLength = data.BranchAmt * data.width;
    const materialQuantity = new Big(totalLength).div(defaultMaterialLength).round(0, Big.roundUp).toNumber();

    addMaterial(materials, 12, branchSpecName, branchMaterialName, '', {
      module: '滴灌管',
      matname: `滴灌管 ${branchSpecName}`,
      module_id: 12,
      mattype: branchMaterialName,
      spec1: branchSpecName,
      spec2: '',
      spec3: '',
      itemunit: `${defaultMaterialLength}m`,
      matamount: materialQuantity,
      description: `滴灌管材`,
      order: 1,
      group: 4
    });
  }

  // 三通
  addMaterial(materials, 2, mainSpecName, '', '三通', {
    module: '滴灌配件',
    matname: '三通',
    module_id: 2,
    mattype: 'PVC',
    spec1: mainSpecName,
    spec2: branchSpecName,
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt),
    description: '主管轉滴灌管三通',
    order: 2,
    group: 4
  });

  // 制水閥
  // addMaterial(materials, 10, branchSpecName, '', '制水閥', {
  //   module: '滴灌配件',
  //   matname: '制水閥',
  //   module_id: 10,
  //   mattype: 'PVC',
  //   spec1: branchSpecName,
  //   spec2: '',
  //   spec3: '',
  //   itemunit: '個',
  //   matamount: Math.floor(data.BranchAmt),
  //   description: '滴灌管制水閥',
  //   order: 3,
  //   group: 4
  // });

  // 管首接頭
  addMaterial(materials, 2, branchSpecName, '', '管首接頭', {
    module: '滴灌配件',
    matname: '管首接頭',
    module_id: 2,
    mattype: 'PVC',
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt), // 原為 *2
    description: '滴灌管首端接頭',
    order: 3,
    group: 4
  });

  // 管尾束
  addMaterial(materials, 2, branchSpecName, '', '管尾束', {
    module: '滴灌配件',
    matname: '管尾束',
    module_id: 2,
    mattype: 'PVC',
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt),
    description: '滴灌管末端束扣',
    order: 4,
    group: 4
  });

  return {
    GroupNo: 4,
    GroupName: '滴灌系統組',
    List: materials
  };
};

// 生成滴嘴材料組 (單獨分組)
const generateDripperHeads = (data: any) => {
  const materials: MaterialItem[] = [];

  // 滴嘴 - 直接使用用戶選擇的末端設施 pomno 進行精確比對
  const dripperMatch = matchMaterialByPomno(localFormData.endFacilityPomno);
  materials.push({
    pomno: dripperMatch.pomno,
    module: '滴嘴',
    matname: dripperMatch.matchedData?.name || '滴嘴',
    module_id: 9,
    mattype: dripperMatch.matchedData?.material?.name || '塑膠',
    spec1: dripperMatch.matchedData?.diameter1?.name || '2L/hr',
    spec2: '',
    spec3: '',
    itemunit: '只',
    matprice: dripperMatch.matprice,
    matamount: Math.floor(data.NozzleAmt),
    description: '滴灌滴嘴',
    order: 1,
    group: 8,
    // debugMatchData: dripperMatch.matchedData
  });

  return {
    GroupNo: 8,
    GroupName: '末端設施',
    List: materials
  };
};

// 生成滴水管系統材料
const generateDripPipeIrrigationSystem = (data: any, mainPipeSpec: any) => {
  const materials: MaterialItem[] = [];
  const mainSpecName = pipeDiameterOptions.value.find(d => d.id === mainPipeSpec)?.name || '1"';

  // ID=8：規格從末端管材 (endFacilityPomno) 的 diameter1 取得，
  // 而非 branchPipeDiameterId（那是 ID=7 滴嘴滴灌系統的欄位）
  const endFacilityMatch = localFormData.endFacilityPomno
    ? matchMaterialByPomno(localFormData.endFacilityPomno)
    : { matchedData: null, pomno: null, matprice: null };
  const selectedEndFacility = localFormData.endFacilityPomno
    ? filteredEndFacilityPipeFittings.value.find(f => f.pomno === localFormData.endFacilityPomno)
    : undefined;
  const branchSpecName = endFacilityMatch.matchedData?.diameter1?.name
    || selectedEndFacility?.specName;

  // 滴水帶 - 管材用無條件進位
  // addMaterial(materials, 12, branchSpecName, 'PE', '', {
  //   module: '滴水帶',
  //   matname: `滴水帶 ${branchSpecName}`,
  //   module_id: 12,
  //   mattype: 'PE',
  //   spec1: branchSpecName,
  //   spec2: '',
  //   spec3: '',
  //   itemunit: 'm',
  //   matamount: Math.ceil(data.BranchAmt * data.width), // 管材用無條件進位
  //   description: '滴水帶材料',
  //   order: 1,
  //   group: 4
  // });

  // 末端管材 - 使用與滴水帶相同的計算公式（管材類：無條件進位）
  if (localFormData.endFacilityPomno && (endFacilityMatch.matchedData || selectedEndFacility)) {
    const endFacilityName = endFacilityMatch.matchedData?.name || selectedEndFacility?.displayName || '末端管材';
    const endFacilityMaterial = endFacilityMatch.matchedData?.material?.name || selectedEndFacility?.materialName || 'PE';

    // 計算管材數量：總長度除以標準長度，當length欄位為空值時固定除4
    const materialLength = endFacilityMatch.matchedData?.length || 4;
    const totalLength = data.BranchAmt * data.width;
    const materialQuantity = new Big(totalLength).div(materialLength).round(0, Big.roundUp).toNumber();

    addMaterial(materials, localFormData.endFacilityPomno, branchSpecName, endFacilityMaterial, '', {
      module: '滴灌管',
      matname: endFacilityName,
      module_id: 12, // 使用與滴水帶相同的模組ID，表示管材類
      mattype: endFacilityMaterial,
      spec1: branchSpecName,
      spec2: '',
      spec3: '',
      itemunit: `${materialLength}m`,
      matamount: materialQuantity,
      description: `滴灌管材`,
      order: 1,
      group: 4
    });
  }

  // 三通 - 配件用無條件捨去
  addMaterial(materials, 2, mainSpecName, '', '三通', {
    module: '滴灌配件',
    matname: '三通',
    module_id: 2,
    mattype: 'PVC',
    spec1: mainSpecName,
    spec2: branchSpecName,
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt),
    description: '主管轉滴灌管三通',
    order: 2,
    group: 4
  });

  // 制水閥 - 配件用無條件捨去
  // addMaterial(materials, 10, branchSpecName, '', '制水閥', {
  //   module: '滴水帶配件',
  //   matname: '制水閥',
  //   module_id: 10,
  //   mattype: 'PVC',
  //   spec1: branchSpecName,
  //   spec2: '',
  //   spec3: '',
  //   itemunit: '個',
  //   matamount: Math.floor(data.BranchAmt),
  //   description: '滴水帶制水閥',
  //   order: 3,
  //   group: 4
  // });

  // 管首接頭 - 配件用無條件捨去
  addMaterial(materials, 2, branchSpecName, '', '管首接頭', {
    module: '滴灌配件',
    matname: '管首接頭',
    module_id: 2,
    mattype: 'PE',
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt), // 原為 *2
    description: '滴灌管首端接頭',
    order: 3,
    group: 4
  });

  // 管尾束 - 配件用無條件捨去
  addMaterial(materials, 2, branchSpecName, '', '管尾束', {
    module: '滴灌配件',
    matname: '管尾束',
    module_id: 2,
    mattype: 'PE',
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: '只',
    matamount: Math.floor(data.BranchAmt),
    description: '滴灌管末端束扣',
    order: 4,
    group: 4
  });

  return {
    GroupNo: 4,
    GroupName: '滴灌系統組',
    List: materials
  };
};

// 統一的資料載入函數
const loadDataFromProps = (propsData: Record<string, unknown>) => {
  console.log('📥 loadDataFromProps called with:', propsData);

  if (!propsData || Object.keys(propsData).length === 0) {
    console.log('⚠️ No props data to load');
    return;
  }

  // 防止在更新過程中觸發新的更新
  if (isUpdating.value) {
    console.log('⚠️ Already updating, skipping loadDataFromProps');
    return;
  }

  // 🔥 修復 race condition：在函數內部設置狀態
  isUpdating.value = true;

  let loadedCount = 0;
  Object.keys(localFormData).forEach(key => {
    if (propsData[key] !== undefined) {
      const oldValue = localFormData[key];
      let newValue = propsData[key];

      // 🔥 如果正在清除末端設施，跳過相關欄位的載入
      if (isClearingEndFacility.value &&
          (key === 'endFacilitySpecId' || key === 'endFacilityPomno' ||
           key === 'endFacilityDiameter' || key === 'endFacilityMaterial')) {
        console.log(`⏸️ Skipping ${key} loading during end facility clearing`);
        return;
      }

      // 🔥 Good Taste：pipes/subsidyAmount/selfPaidAmount 只在 mounted 時載入一次
      // 之後完全由本地管理，永不從 props 反向載入（避免清除後被恢復）
      const localManagedFields = ['pipes', 'subsidyAmount', 'selfPaidAmount'];
      if (localManagedFields.includes(key)) {
        // console.log(`⏸️ Skipping ${key} - locally managed field`);
        return;
      }

      // 特殊處理：主管材質未設定時預設為 1 (PVC)
      if (key === 'mainPipeMaterialId' || key === 'mainPipe2MaterialId') {
        if (newValue === null || newValue === undefined || newValue === 0 || newValue === '') {
          newValue = 1; // 預設為 PVC
          console.log(`🔧 Setting default material for ${key}: ${oldValue} → ${newValue} (PVC)`);
        }
      }

      // 只有當值真的不同時才更新（包括 null 到具體值的轉換）
      if (oldValue !== newValue) {
        localFormData[key] = newValue;
        console.log(`📥 Loading ${key}: ${oldValue} → ${newValue}`);
        loadedCount++;
      }
    }
  });

  console.log(`✅ Loaded ${loadedCount} fields from props`);

  // 確保主管材質有預設值
  ensureDefaultMaterials();

  // 只有當實際載入了資料時才重新計算 width
  if (loadedCount > 0) {
    calculateWidth();
  }

  // 🔥 修復 race condition：函數結束後重置狀態
  isUpdating.value = false;
};

onMounted(async () => {
  isUpdating.value = true;

  // 🔥 統一架構 (2025-11-04) - step4.vue 對應 UI step 5
  // UI step 5 → Component step4.vue → formData[5]（1:1 映射，無需轉換）
  // const expectedUIStep = 5; // step4.vue 對應 UI step 5 (田間管路)
  // if (grantsStore.currentStep !== expectedUIStep) {
    // console.warn(`⚠️ Step4 component mounted but currentStep is ${grantsStore.currentStep}, expected ${expectedUIStep} (田間管路)`)
    // 可以發出事件通知父組件，但不直接修改
    // emit('step-mismatch', { expected: expectedUIStep, actual: grantsStore.currentStep })
  // }

  // 🔧 編輯狀態將在所有數據載入完成後統一設置（避免畫面閃爍）
  // 暫不設置 isEditingDesigner，保持初始值 false

  await loadDropdownOptions();

  // 1. 先從 props.formData 載入所有數據（包含 localStorage 數據）
  if (props.formData && Object.keys(props.formData).length > 0) {
    Object.keys(localFormData).forEach(key => {
      if (props.formData[key] !== undefined && props.formData[key] !== localFormData[key]) {
        const oldValue = localFormData[key];
        let newValue = props.formData[key];

        // 特殊處理：主管材質未設定時預設為 1 (PVC)
        if (key === 'mainPipeMaterialId' || key === 'mainPipe2MaterialId') {
          if (newValue === null || newValue === undefined || newValue === 0 || newValue === '') {
            newValue = 1; // 預設為 PVC
            console.log(`🔧 Setting default material for ${key}: ${oldValue} → ${newValue} (PVC)`);
          }
        }

        localFormData[key] = newValue;
        // console.log(`Loading ${key}: ${oldValue} → ${newValue}`);
      }
    });
  }

  // 2. 確保 step2 數據載入
  if (!getStepDataSafely(2)?.totalFacilityArea && grantsStore.currentGrant?.case_number) {
    await grantsStore.loadStepData(grantsStore.currentGrant.case_number, 2);
  }

  // 3. 確保 step3 數據載入（用於計算灌溉調控設施補助總額）
  // 🔥 統一架構 (2025-11-04): step3.vue (UI step 4) 現在儲存在 formData[4]
  if (!getStepDataSafely(4)?.facilities && grantsStore.currentGrant?.case_number) {
    await grantsStore.loadStepData(grantsStore.currentGrant.case_number, 4);
  }

  // 🔧 Linus式修正：不再需要手動設置 facilityArea，已改為 computed
  // facilityAreaFromStep2 會自動從 Step2 資料計算，無需初始化

  calculateWidth();

  // 4. 確保主管材質有預設值
  ensureDefaultMaterials();

  // 5. 如果有灌溉型式，載入末端設施選項
  if (localFormData.irrigationTypeId) {
    await loadEndFacilityOptions();
  }

  // 6. 初始化 ID=7 滴水管名稱選項 (如果已選擇了滴水管規格)
  if (localFormData.dripperSubtypeId === 7 && localFormData.branchPipeDiameterId) {
    console.log('🔄 Initializing ID=7 branch pipe fittings in onMounted');
    updateBranchPipeFittingsForId7();
  }

  // 💰 初始化補助額度查詢（必須在 calculateSubsidy 之前完成）
  if (grantsStore.currentGrant) {
    const applicantId = grantsStore.currentGrant.applicant_id;
    const year = grantsStore.currentGrant.year;
    const currentGrantId = grantsStore.currentGrant.id;

    if (applicantId && year) {
      try {
        await grantsStore.fetchSubsidySummary(applicantId, year, currentGrantId);
      } catch (error) {
        console.error('❌ [step4] 補助額度查詢失敗:', error);
      }
    }
  }

  // 如果有管路設施，計算補助金額（確保 subsidySummary 已載入）
  if (localFormData.pipes && localFormData.pipes.length > 0) {
    await calculateSubsidy();
  }

  // 🎯 UX 改進：在所有數據載入完成後，根據 designerName 最終確認編輯狀態
  const hasDesignerName = !!localFormData.designerName;
  isEditingDesigner.value = !hasDesignerName;

  isUpdating.value = false; // 結束更新標記

  // 只在 mounted 完成後才發送第一次更新
  updateFormData();
});

// 監聽父組件數據變化
watch(() => props.formData, (newVal, oldVal) => {
  // console.log("🔄 Step 4 props.formData changed:", newVal);

  // 防止在更新過程中觸發新的 watch
  if (isUpdating.value) {
    console.log('⚠️ Already updating, skipping watch');
    return;
  }

  // 只有當真的有新數據時才載入
  if (newVal && Object.keys(newVal).length > 0 && newVal !== oldVal) {
    // 修復 race condition：在 loadDataFromProps 內部設置 isUpdating
    loadDataFromProps(newVal);
  }
}, { deep: true });

// 🔧 Linus式修正：排除 designerName 的 watch 以避免 IME 衝突
// 其他欄位使用 deep watch 即時同步，designerName 改用 @blur
let previousDesignerName = localFormData.designerName;
watch(localFormData, () => {
  // 只在非 designerName 變化時觸發 updateFormData
  if (localFormData.designerName === previousDesignerName) {
    if (!isUpdating.value) {
      updateFormData();
    }
  } else {
    // 只更新追蹤值，不觸發 updateFormData（等 blur 時觸發）
    previousDesignerName = localFormData.designerName;
  }
}, { deep: true });

watch(localValid, (newVal) => {
  if (!isUpdating.value) {
    const parentValid = props.formData?.valid;
    if (parentValid !== newVal) {
      updateFormData();
    }
  }
});

watch(() => grantsStore.currentGrant?.office_id, async (newOfficeId) => {
  if (newOfficeId) {
    // console.log(`Current grant office_id changed to: ${newOfficeId}, refreshing pipe fittings`);
    await fetchPipeFittings();
  }
});

// Provide fallback options if no pipe fittings are found
watch(pipeDiameterOptions, (newOptions) => {
  if (newOptions.length === 0) {
    console.warn('No pipe diameter options found, using defaults');
  }
});

watch(pipeMaterialOptions, (newOptions) => {
  if (newOptions.length === 0) {
    console.warn('No pipe material options found, using defaults');
  }
});

// 監聽末端設施選擇變化，自動同步到豎管材質和規格
watch(() => localFormData.endFacilityPomno, (newPomno) => {
  // 只有在噴頭式系統(ID=2)或微噴系統(ID=3)時才需要同步豎管欄位
  if (localFormData.irrigationTypeId !== 2 && localFormData.irrigationTypeId !== 3) {
    return;
  }

  if (newPomno) {
    // 查找選中的末端設施
    const selectedFitting = filteredEndFacilityPipeFittings.value.find(f => f.pomno === newPomno);
    if (selectedFitting) {
      // 自動同步：豎管規格 = 末端設施規格
      localFormData.riserPipeSpecId = selectedFitting.specId || null;
      // 自動同步：豎管材質 = 末端設施材質
      localFormData.riserPipeMaterialId = selectedFitting.materialId || null;
      // console.log(`✅ 自動同步豎管欄位：材質ID=${selectedFitting.materialId}, 規格ID=${selectedFitting.specId}`);
    }
  } else {
    // 如果清空末端設施選擇，也清空豎管欄位
    localFormData.riserPipeSpecId = null;
    localFormData.riserPipeMaterialId = null;
  }
}, { immediate: false });

// 監聽 ID=7 相關欄位變化，自動更新滴水管名稱選項
watch(
  [() => localFormData.dripperSubtypeId, () => localFormData.branchPipeDiameterId],
  ([newDripperSubtypeId, newBranchPipeDiameterId], [oldDripperSubtypeId]) => {
    // 當切換 ID=7 或 ID=8 時，清除末端管徑選取內容並重新載入選項
    if (newDripperSubtypeId !== oldDripperSubtypeId &&
        (newDripperSubtypeId === 7 || newDripperSubtypeId === 8 || oldDripperSubtypeId === 7 || oldDripperSubtypeId === 8)) {
      console.log(`🔄 Switching between ID=7/8, clearing end facility spec: ${oldDripperSubtypeId} → ${newDripperSubtypeId}`);

      // 設置清除狀態，阻止 loadDataFromProps 重新載入這些欄位
      isClearingEndFacility.value = true;

      // 直接清除相關欄位，不調用函數以避免不必要的更新
      localFormData.endFacilitySpecId = null;
      localFormData.endFacilityPomno = null;
      localFormData.endFacilityDiameter = '';
      localFormData.endFacilityMaterial = '';

      console.log('🧹 Directly cleared end facility fields:', {
        endFacilitySpecId: localFormData.endFacilitySpecId,
        endFacilityPomno: localFormData.endFacilityPomno,
        endFacilityDiameter: localFormData.endFacilityDiameter,
        endFacilityMaterial: localFormData.endFacilityMaterial
      });

      // 立即更新父組件數據，防止 loadDataFromProps 重新載入舊數據
      updateFormData();

      // 重新載入末端設施選項，確保選項列表與新的滴頭類型匹配
      nextTick(async () => {
        await loadEndFacilityOptions();

        // 清除完成後解除阻止狀態
        setTimeout(() => {
          isClearingEndFacility.value = false;
          console.log('✅ End facility clearing completed, re-enabling data loading');
        }, 100);
      });
    }

    // 當切換到 ID=7 或滴水管規格改變時，更新滴水管名稱選項
    if (newDripperSubtypeId === 7 && newBranchPipeDiameterId) {
      console.log('🔄 ID=7 branch pipe diameter changed, updating pipe fittings options');
      updateBranchPipeFittingsForId7();
    } else if (newDripperSubtypeId !== 7 && oldDripperSubtypeId === 7) {
      // 從 ID=7 切換到其他選項時，清空 branchPipePomno
      console.log('🔄 Switched away from ID=7, clearing branchPipePomno');
      onSelectedBranchPipeChangeForId7(null);
    }
  },
  { immediate: false }
);

// 監聽「田間管路系統設計」欄位變化，清除管路設施列表
// 排除：灌溉水源(waterSourceId)、設施型式(installationType)、設計人(designerName)
// 主管配置：僅監聽長度和管徑，不監聽數量/單價/材質
//   - 數量/單價由管路設施列表 pipes[] 驅動（deep watch 同步），不應觸發重置
//   - 材質按使用者需求排除，不在本 watch 範圍
watch(
  [
    // 田間坵塊
    () => localFormData.fieldLength,

    // 田間主管配置（僅長度與管徑）
    () => localFormData.mainPipeLength,
    () => localFormData.mainPipeDiameterId,
    () => localFormData.mainPipe2Enabled,
    () => localFormData.mainPipe2Length,
    () => localFormData.mainPipe2DiameterId,

    // 灌溉管路配置
    () => localFormData.irrigationTypeId,
    () => localFormData.perforatedPipeDirection,
    () => localFormData.sprinklerSubtypeId,
    () => localFormData.dripperSubtypeId,
    () => localFormData.branchPipeSpacing_SL,
    () => localFormData.sprinklerSpacing_SS,
    () => localFormData.branchPipeMaterialId,
    () => localFormData.branchPipeDiameterId,
    () => localFormData.branchPipePomno,
    () => localFormData.enableBranchDiameterChange,
    () => localFormData.changeBranchSpecId,
    () => localFormData.riserHeight_H,
    () => localFormData.endFacilitySpecId,
    () => localFormData.endFacilityPomno,
    () => localFormData.riserPipeMaterialId,
    () => localFormData.riserPipeSpecId,
  ],
  (newValues, oldValues) => {
    // console.log('🔍 [管路清除監聽] watch 被觸發');
    // console.log('  - isUpdating:', isUpdating.value);
    // console.log('  - pipes.length:', localFormData.pipes.length);

    // 如果正在更新數據（例如從 API 載入），不執行清除操作
    if (isUpdating.value) {
      console.log('  ⏸️  isUpdating=true，跳過清除');
      return;
    }

    // 檢查是否有任何欄位真的發生了變化（排除初始化時的 undefined → value）
    const changedFields: string[] = [];
    const fieldNames = [
      'fieldLength',
      'mainPipeLength', 'mainPipeDiameterId',
      'mainPipe2Enabled', 'mainPipe2Length', 'mainPipe2DiameterId',
      'irrigationTypeId', 'perforatedPipeDirection', 'sprinklerSubtypeId', 'dripperSubtypeId',
      'branchPipeSpacing_SL', 'sprinklerSpacing_SS', 'branchPipeMaterialId', 'branchPipeDiameterId', 'branchPipePomno',
      'enableBranchDiameterChange', 'changeBranchSpecId', 'riserHeight_H',
      'endFacilitySpecId', 'endFacilityPomno', 'riserPipeMaterialId', 'riserPipeSpecId'
    ];

    newValues.forEach((newVal, index) => {
      const oldVal = oldValues?.[index];
      if (newVal !== oldVal && oldVal !== undefined) {
        changedFields.push(`${fieldNames[index]}: ${oldVal} → ${newVal}`);
      }
    });

    console.log('  - 變更的欄位:', changedFields.length > 0 ? changedFields : '無');

    const hasChanges = changedFields.length > 0;

    // 只有在有實際變化且管路設施列表不為空時才清除
    if (hasChanges && localFormData.pipes.length > 0) {
      console.log('🧹 田間管路系統設計欄位已變更，清除管路設施列表');
      console.log('  變更詳情:', changedFields);

      // 使用統一的清除函數
      clearPipelineData(true);
    } else if (hasChanges && localFormData.pipes.length === 0) {
      console.log('  ℹ️  有欄位變更但管路設施列表已為空，不需清除');
    } else {
      console.log('  ℹ️  無有效變更，不執行清除');
    }
  },
  { immediate: false }
);

// 手動新增材料相關方法
const openManualAddDialog = (preselectedGroupId?: number) => {
  showManualAddDialog.value = true;
  // 重置表單
  selectedMaterialPomno.value = null;
  selectedGroup.value = preselectedGroupId || null;
  materialQuantity.value = 1;
  materialSearchQuery.value = '';
};

const closeManualAddDialog = () => {
  showManualAddDialog.value = false;
  // 重置表單數據
  selectedMaterialPomno.value = null;
  materialQuantity.value = 1;
  materialRemark.value = '';
  selectedGroup.value = null;
  materialSearchQuery.value = '';
};

const onMaterialSearch = (query: string) => {
  materialSearchQuery.value = query;
};

// 工具函數：獲取管徑顯示
const getDiameterDisplay = (item: any) => {
  if (!item) return '';

  // 收集所有可用的管徑資訊
  const diameters = [];

  // 檢查 diameter1, diameter2, diameter3 - 不去重，顯示所有口徑
  if (item.diameter1?.name) {
    diameters.push(item.diameter1.name);
  }
  if (item.diameter2?.name) {
    diameters.push(item.diameter2.name);
  }
  if (item.diameter3?.name) {
    diameters.push(item.diameter3.name);
  }

  // 如果沒有找到 diameter 物件，回退到舊的邏輯
  if (diameters.length === 0) {
    const diameter = item.diameter?.name ||
                     item.diameter_name ||
                     item.diameter ||
                     item.spec1 ||
                     '';
    if (diameter) {
      diameters.push(diameter);
    }
  }

  // 格式化顯示
  if (diameters.length === 0) return '';
  if (diameters.length === 1) return `φ${diameters[0]}`;
  return `φ${diameters.join('×')}`;  // 多規格用 × 分隔
};

const addMaterialToList = async () => {
  if (!canAddMaterial.value || !selectedMaterial.value || !selectedGroup.value) return;

  isAddingMaterial.value = true;

  try {
    // 計算該群組內的下一個順序號碼
    const existingItemsInGroup = localFormData.pipes.filter(p => p.groupId === selectedGroup.value);
    const nextOrderInGroup = existingItemsInGroup.length > 0
      ? Math.max(...existingItemsInGroup.map(p => p.order || 0)) + 1
      : 1;

    // 創建新的材料項目
    const newMaterial = {
      pomno: selectedMaterial.value.pomno,
      groupId: selectedGroup.value,
      groupName: materialGroupOptions.value.find(g => g.id === selectedGroup.value)?.name || '',
      module: selectedMaterial.value.module?.name || '',
      matname: selectedMaterial.value.name,
      mattype: selectedMaterial.value.material?.name || '',
      specification: `${selectedMaterial.value.diameter1?.name || ''} ${selectedMaterial.value.diameter2?.name || ''} ${selectedMaterial.value.diameter3?.name || ''}`.trim(),
      spec1: selectedMaterial.value.diameter1?.name || '',
      spec2: selectedMaterial.value.diameter2?.name || '',
      spec3: selectedMaterial.value.diameter3?.name || '',
      itemunit: selectedMaterial.value.unit || '只',
      description: selectedMaterial.value.description || '',
      matprice: selectedMaterial.value.current_price || 0,
      matamount: materialQuantity.value,
      totalPrice: (selectedMaterial.value.current_price || 0) * materialQuantity.value,
      order: nextOrderInGroup,
      moduleType: selectedMaterial.value.module?.name || ''
    };

    // 添加到管路列表
    localFormData.pipes.push(newMaterial);

    // 重新計算補助金額
    await calculateSubsidy();

    // 關閉對話框
    closeManualAddDialog();

    // 更新表單數據
    updateFormData();

  } catch (error) {
    console.error('新增材料時發生錯誤:', error);
  } finally {
    isAddingMaterial.value = false;
  }
};
</script>

<style scoped>
.step-content {
  padding: 0;
  background-color: transparent !important;
}

/* 統一表單字段顏色 - 與 step1/step2 一致 */
:deep(.v-text-field:not([readonly]):not([disabled]) .v-field),
:deep(.v-select:not([readonly]):not([disabled]) .v-field),
:deep(.v-autocomplete:not([readonly]):not([disabled]) .v-field) {
  --v-field-border-color: #3ea0a3 !important;
  --v-theme-on-surface: #3ea0a3 !important;
}

:deep(.v-text-field:not([readonly]):not([disabled]) .v-field .v-field__input),
:deep(.v-select:not([readonly]):not([disabled]) .v-field .v-field__input),
:deep(.v-autocomplete:not([readonly]):not([disabled]) .v-field .v-field__input) {
  background-color: white;
}

:deep(.v-text-field[readonly] .v-field),
:deep(.v-text-field[disabled] .v-field) {
  background-color: rgb(var(--v-theme-grey-lighten-4));
}

/* 卡片懸停效果 */
.v-card.pa-4 {
  transition: all 0.3s ease;
}

/* .v-card.pa-4:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
} */

/* 穿孔管系統配置組件高度統一 */
.perforated-pipe-config {
  align-items: flex-end; /* 將所有組件底部對齊 */
}

.perforated-pipe-config .v-select,
.perforated-pipe-config .v-autocomplete {
  height: 56px; /* 統一高度為 56px (Vuetify 標準高度) */
}

.perforated-pipe-config .v-field {
  height: 56px !important;
}

.perforated-pipe-config .v-field__field {
  height: 56px !important;
}

/* 自定義的行距(SL) div 結構對齊調整 */
.perforated-pipe-config .me-3.mb-2 {
  display: flex;
  flex-direction: column;
  justify-content: flex-end; /* 讓內容向底部對齊 */
  height: 80px; /* 給足夠空間容納 label + input */
}

.perforated-pipe-config .me-3.mb-2 .v-text-field {
  margin-top: auto; /* 將 text-field 推到底部 */
}

/* 滴灌系統配置組件高度統一 */
.drip-system-config {
  align-items: flex-end; /* 將所有組件底部對齊 */
}

.drip-system-config .v-select,
.drip-system-config .v-autocomplete {
  height: 56px; /* 統一高度為 56px (Vuetify 標準高度) */
}

.drip-system-config .v-field {
  height: 56px !important;
}

.drip-system-config .v-field__field {
  height: 56px !important;
}

/* 自定義的滴水管行距(SL) div 結構對齊調整 */
.drip-system-config .me-3.mb-2 {
  display: flex;
  flex-direction: column;
  justify-content: flex-end; /* 讓內容向底部對齊 */
  height: 80px; /* 給足夠空間容納 label + input */
}

.drip-system-config .me-3.mb-2 .v-text-field {
  margin-top: auto; /* 將 text-field 推到底部 */
}

.border {
  border: 1px solid rgba(0, 0, 0, 0.12);
}

.v-card .v-card-title {
  line-height: 1.5;
}

.v-table {
  background-color: white;
  table-layout: fixed;
  width: 100%;
}

.v-table th {
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
  white-space: nowrap;
  padding: 8px !important;
}

.v-table td {
  padding: 4px !important;
  vertical-align: middle;
}

.material-input {
  font-size: 0.875rem;
}

.material-input .v-field {
  font-size: 0.875rem;
}

.material-input .v-field__input {
  min-height: 32px;
  padding: 4px 8px;
}

.irrigation-type-config {
  background-color: rgba(0, 0, 0, 0.02);
  padding: 10px 10px 2px 10px;
  border-radius: 8px;
}

/* 確保表格在小螢幕上也能正常顯示 */
@media (max-width: 1200px) {
  .v-table {
    font-size: 0.875rem;
  }

  .material-input {
    font-size: 0.8rem;
  }
}

/* 必填欄位紅色星號樣式 */
.required-asterisk {
  color: #ff0000 !important;
  font-weight: bold;
  margin-left: 2px;
}

</style>
