<template>
  <div
    ref="stepContent"
    class="step-content"
  >
    <v-card
      class="mb-0 pa-0"
      flat
    >
      <v-card-text class="pb-0 pt-0">
        <v-form
          ref="form"
          v-model="localValid"
          @submit.prevent
        >
          <!-- STEP 1: 補助來源選擇 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-hand-coin
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">補助來源</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <v-select
                  v-model="localFormData.fundingSourceId"
                  :items="fundingSourceOptions"
                  item-title="name"
                  item-value="id"
                  variant="outlined"
                  density="comfortable"
                  style="max-width: 400px"
                  :rules="[v => (v !== null && v !== undefined) || '請選擇補助單位']"
                  @update:model-value="updateFormData"
                >
                  <template #label>
                    補助單位<span class="required-asterisk" />
                  </template>
                </v-select>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- STEP 2: 設施基地長寬長度調整 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-land-fields
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">田間坵塊</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <div class="d-flex flex-wrap align-center mb-4">
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
                    />
                  </div>

                  <div class="d-flex align-center me-4 mb-2">
                    <div class="text-body-2 me-2">
                      施設面積:
                    </div>
                    <v-text-field
                      :value="facilityAreaFromStep2"
                      suffix="m²"
                      type="number"
                      variant="outlined"
                      density="comfortable"
                      style="width: 120px"
                      readonly
                    />
                  </div>
                </div>
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- STEP 3: 田間主管資訊 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-pipe
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">田間主管配置</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
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
                    :rules="[v => (v !== null && v !== '') || '請輸入單價']"
                    @update:model-value="updateFormData"
                  />
                  <v-text-field
                    v-model.number="localFormData.mainPipeQuantity"
                    label="數量"
                    type="number"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 80px"
                    :rules="[v => (v !== null && v !== '') || '請輸入數量']"
                    @update:model-value="updateFormData"
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
                    :rules="[localFormData.mainPipe2Enabled ? (v => (v !== null && v !== '') || '請輸入單價') : true]"
                    @update:model-value="updateFormData"
                  />
                  <v-text-field
                    v-model.number="localFormData.mainPipe2Quantity"
                    label="主管2 數量"
                    type="number"
                    variant="outlined"
                    density="comfortable"
                    class="me-2 mb-2"
                    style="width: 80px"
                    :rules="[localFormData.mainPipe2Enabled ? (v => (v !== null && v !== '') || '請輸入數量') : true]"
                    @update:model-value="updateFormData"
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
            </v-card-text>
          </v-card>

          <!-- STEP 4: 灌溉型式與相關管路配置 -->
          <v-card
            class="mb-4"
            variant="outlined"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-sprinkler
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">灌溉管路配置</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <div class="d-flex align-center flex-wrap mb-3">
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
                    style="width: 180px"
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
                    style="width: 160px"
                    @update:model-value="updateFormData"
                  />
                </div>

                <!-- 穿孔管系统相关配置 -->
                <div
                  v-if="localFormData.irrigationTypeId === 1"
                  class="irrigation-type-config"
                >
                  <v-divider class="mb-3" />
                  <div class="text-subtitle-2 mb-3">
                    穿孔管系統配置
                  </div>

                  <div class="d-flex flex-wrap">
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
                      style="width: 160px"
                      @update:model-value="onEndFacilityParamsChange"
                    />

                    <!-- 支管行距(SL) -->
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
                          @update:model-value="() => { calculateBranchPipeQuantity(); calculateSprinklerQuantity(); }"
                        />
                        <span>M</span>
                      </div>
                    </div>

                    <!-- 支管變徑規格 -->
                    <v-select
                      v-model="localFormData.changeBranchSpecId"
                      :items="pipeDiameterOptions"
                      item-title="name"
                      item-value="id"
                      label="支管變徑規格"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      style="width: 150px"
                      clearable
                      hint="若不變徑則不選"
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2">
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
                      style="width: 150px"
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
                      style="width: 250px"
                      clearable
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
                  <v-divider class="mb-3" />
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
                      style="width: 180px"
                      @update:model-value="onEndFacilityParamsChange"
                    />

                    <!-- 設施型式 -->
                    <v-select
                      v-model="localFormData.facilityTypeId"
                      :items="facilityTypeOptions"
                      item-title="name"
                      item-value="id"
                      label="設施型式"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      style="width: 160px"
                      @update:model-value="onEndFacilityParamsChange"
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2">
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
                      style="width: 150px"
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
                      style="width: 150px"
                      @update:model-value="updateFormData"
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2">
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
                          @update:model-value="() => { calculateBranchPipeQuantity(); calculateSprinklerQuantity(); }"
                        />
                        <span>M</span>
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
                          @update:model-value="calculateSprinklerQuantity"
                        />
                        <span>M</span>
                      </div>
                    </div>

                    <!-- 支管變徑規格 -->
                    <v-select
                      v-model="localFormData.changeBranchSpecId"
                      :items="pipeDiameterOptions"
                      item-title="name"
                      item-value="id"
                      label="支管變徑規格"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      style="width: 150px"
                      clearable
                      hint="若不變徑則不選"
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2">
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
                      style="width: 150px"
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
                      style="width: 250px"
                      clearable
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

                  <div class="d-flex flex-wrap mt-2">
                    <!-- 豎管相關配置 -->
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
                        />
                        <span>M</span>
                      </div>
                    </div>

                    <v-select
                      v-model="localFormData.riserPipeMaterialId"
                      :items="pipeMaterialOptions"
                      item-title="name"
                      item-value="id"
                      label="豎管材質"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      style="width: 150px"
                      clearable
                    />

                    <v-select
                      v-model="localFormData.riserPipeSpecId"
                      :items="pipeDiameterOptions"
                      item-title="name"
                      item-value="id"
                      label="豎管規格"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      style="width: 150px"
                      clearable
                    />
                  </div>
                </div>

                <!-- 微噴系統相關配置 -->
                <div
                  v-else-if="localFormData.irrigationTypeId === 3"
                  class="irrigation-type-config"
                >
                  <v-divider class="mb-3" />
                  <div class="text-subtitle-2 mb-3">
                    微噴系統配置
                  </div>

                  <div class="d-flex flex-wrap">
                    <!-- 設施型式 -->
                    <v-select
                      v-model="localFormData.facilityTypeId"
                      :items="facilityTypeOptions"
                      item-title="name"
                      item-value="id"
                      label="設施型式"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      style="width: 160px"
                      @update:model-value="onEndFacilityParamsChange"
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2">
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
                      style="width: 150px"
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
                      style="width: 150px"
                      @update:model-value="updateFormData"
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2">
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
                          @update:model-value="() => { calculateBranchPipeQuantity(); calculateSprinklerQuantity(); }"
                        />
                        <span>M</span>
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
                          @update:model-value="calculateSprinklerQuantity"
                        />
                        <span>M</span>
                      </div>
                    </div>

                    <!-- 支管變徑規格 -->
                    <v-select
                      v-model="localFormData.changeBranchSpecId"
                      :items="pipeDiameterOptions"
                      item-title="name"
                      item-value="id"
                      label="支管變徑規格"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      style="width: 150px"
                      clearable
                      hint="若不變徑則不選"
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2">
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
                      style="width: 150px"
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
                      style="width: 250px"
                      clearable
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

                  <div class="d-flex flex-wrap mt-2">
                    <!-- 豎管相關配置 -->
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
                        />
                        <span>M</span>
                      </div>
                    </div>

                    <v-select
                      v-model="localFormData.riserPipeMaterialId"
                      :items="pipeMaterialOptions"
                      item-title="name"
                      item-value="id"
                      label="豎管材質"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      style="width: 150px"
                      clearable
                    />

                    <v-select
                      v-model="localFormData.riserPipeSpecId"
                      :items="pipeDiameterOptions"
                      item-title="name"
                      item-value="id"
                      label="豎管規格"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      style="width: 150px"
                      clearable
                    />
                  </div>
                </div>

                <!-- 滴灌系統相關配置 -->
                <div
                  v-else-if="localFormData.irrigationTypeId === 4"
                  class="irrigation-type-config"
                >
                  <v-divider class="mb-3" />
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
                      style="width: 180px"
                      @update:model-value="onEndFacilityParamsChange"
                    />

                    <!-- 設施型式 -->
                    <v-select
                      v-model="localFormData.facilityTypeId"
                      :items="facilityTypeOptions"
                      item-title="name"
                      item-value="id"
                      label="設施型式"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      style="width: 160px"
                      @update:model-value="onEndFacilityParamsChange"
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2">
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
                      style="width: 150px"
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
                      style="width: 150px"
                      @update:model-value="updateFormData"
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2">
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
                          @update:model-value="() => { calculateBranchPipeQuantity(); calculateSprinklerQuantity(); }"
                        />
                        <span>M</span>
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
                          @update:model-value="calculateSprinklerQuantity"
                        />
                        <span>M</span>
                      </div>
                    </div>

                    <!-- 支管變徑規格 -->
                    <v-select
                      v-model="localFormData.changeBranchSpecId"
                      :items="pipeDiameterOptions"
                      item-title="name"
                      item-value="id"
                      label="支管變徑規格"
                      variant="outlined"
                      density="comfortable"
                      class="me-3 mb-2"
                      style="width: 150px"
                      clearable
                      hint="若不變徑則不選"
                    />
                  </div>

                  <div class="d-flex flex-wrap mt-2">
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
                      style="width: 150px"
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
                      style="width: 250px"
                      clearable
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
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- STEP 6: 已新增管路設施列表 -->
          <v-card
            variant="outlined"
            class="mb-4"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-format-list-bulleted
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">管路設施列表</span>
            </v-card-title>
            <v-card-text class="pa-4">
              <v-sheet
                class="pa-3 rounded"
                color="grey-lighten-5"
              >
                <div class="text-body-2 mb-2 text-grey-darken-1">
                  點擊下方按鈕可根據您選擇的灌溉型式和設施配置，自動帶入相應的材料清單。
                </div>
                <v-btn
                  color="success"
                  class="mb-2"
                  :loading="isLoadingMaterials"
                  :disabled="!canAutoFillMaterials"
                  block
                  @click="autoFillMaterials"
                >
                  <v-icon
                    start
                    size="small"
                  >
                    mdi-autorenew
                  </v-icon>
                  自動帶入材料
                </v-btn>
                <v-btn
                  color="primary"
                  variant="outlined"
                  class="mb-2"
                  block
                  @click="openManualAddDialog"
                >
                  <v-icon
                    start
                    size="small"
                  >
                    mdi-plus
                  </v-icon>
                  手動新增材料
                </v-btn>
                <div
                  v-if="!canAutoFillMaterials"
                  class="text-caption text-red mt-1"
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
              </v-sheet>
            </v-card-text>

            <v-card-text class="pa-4">
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
                      style="width: 100px; min-width: 80px;"
                    >
                      單價
                    </th>
                    <th
                      class="text-center px-2"
                      style="width: 100px; min-width: 100px;"
                    >
                      數量
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
                      排序
                    </th>
                    <th
                      class="text-center px-2"
                      style="width: 80px; min-width: 30px;"
                    >
                      刪除
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
                      <td class="text-center px-2">
                        <div class="text-body-2 font-weight-medium">
                          {{ pipe.totalPrice?.toLocaleString() }}
                        </div>
                      </td>
                      <td class="text-center px-1">
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
                  <tr class="bg-grey-lighten-4">
                    <td
                      colspan="8"
                      class="text-right font-weight-bold px-2 py-2"
                    >
                      合計
                    </td>
                    <td class="text-center font-weight-bold px-2 py-2">
                      <div class="text-body-1 font-weight-bold text-primary">
                        {{ totalPipesPrice }}
                      </div>
                    </td>
                    <td colspan="2" />
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>

          <!-- 補助計算結果 -->
          <v-card
            variant="outlined"
            class="mt-4"
          >
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon
                class="me-2"
                size="small"
              >
                mdi-calculator
              </v-icon>
              <span class="text-subtitle-1 font-weight-medium">補助計算結果</span>
            </v-card-title>
            <v-card-text class="pa-4">
              <v-table
                class="rounded border"
                style="max-width: 600px"
              >
                <thead class="bg-grey-lighten-3">
                  <tr>
                    <th>項目</th>
                    <th class="text-center">
                      金額(NT$)
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>設施總經費</td>
                    <td class="text-center">
                      {{ subsidyTotalAmount }}
                    </td>
                  </tr>
                  <tr>
                    <td>A. 政府補助款</td>
                    <td class="text-center text-success font-weight-bold">
                      {{ subsidyAmount }}
                    </td>
                  </tr>
                  <tr>
                    <td>B. 農戶自備款</td>
                    <td class="text-center text-warning font-weight-bold">
                      {{ farmerSelfAmount }}
                    </td>
                  </tr>
                </tbody>
              </v-table>
              <v-btn
                color="primary"
                class="mt-4"
                :loading="isCalculatingSubsidy"
                :disabled="localFormData.pipes.length === 0"
                @click="calculateSubsidy"
              >
                計算輔助金額
              </v-btn>
            </v-card-text>
          </v-card>
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
    max-width="800"
  >
    <v-card>
      <v-card-title class="bg-primary text-white d-flex align-center">
        <v-icon class="me-2">
          mdi-plus
        </v-icon>
        手動新增材料
      </v-card-title>

      <v-card-text class="pa-4">
        <v-form ref="manualAddForm">
          <v-row>
            <!-- 材料搜尋與選擇 -->
            <v-col cols="12">
              <v-autocomplete
                v-model="selectedMaterialPomno"
                :items="filteredMaterialOptions"
                item-title="searchText"
                item-value="pomno"
                label="搜尋並選擇材料"
                placeholder="請輸入材料名稱、材質或管徑進行搜尋"
                clearable
                no-data-text="沒有找到相符的材料"
                @update:search="onMaterialSearch"
              >
                <template #item="{ props, item }">
                  <v-list-item v-bind="props">
                    <template #title>
                      {{ item.raw.name }}
                    </template>
                    <template #subtitle>
                      POMNO: {{ item.raw.pomno }} |
                      {{ item.raw.material?.name || 'N/A' }} |
                      {{ item.raw.module?.name || 'N/A' }} |
                      單價: ${{ item.raw.current_price?.toLocaleString() || 'N/A' }}
                    </template>
                  </v-list-item>
                </template>
              </v-autocomplete>
            </v-col>

            <!-- 選中材料的詳細資訊 -->
            <v-col
              v-if="selectedMaterial"
              cols="12"
            >
              <v-card
                variant="outlined"
                color="grey-lighten-5"
              >
                <v-card-text>
                  <div class="text-subtitle-2 mb-2">
                    選中的材料：
                  </div>
                  <div class="d-flex align-center">
                    <div class="flex-grow-1">
                      <div class="text-body-2 font-weight-medium">
                        {{ selectedMaterial.name }}
                      </div>
                      <div class="text-caption text-grey-darken-1">
                        POMNO: {{ selectedMaterial.pomno }} |
                        {{ selectedMaterial.material?.name || 'N/A' }} |
                        {{ selectedMaterial.module?.name || 'N/A' }} |
                        單價: ${{ selectedMaterial.current_price?.toLocaleString() || 'N/A' }}
                      </div>
                    </div>
                    <v-chip
                      size="small"
                      color="primary"
                      variant="outlined"
                    >
                      {{ selectedMaterial.unit || '個' }}
                    </v-chip>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

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
                required
                :rules="[v => !!v || '請選擇材料組別']"
              />
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
                min="1"
                step="1"
                required
                :rules="[
                  v => !!v || '請輸入數量',
                  v => v > 0 || '數量必須大於0'
                ]"
              />
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>

      <v-card-actions class="px-4 pb-4">
        <v-spacer />
        <v-btn
          variant="outlined"
          @click="closeManualAddDialog"
        >
          取消
        </v-btn>
        <v-btn
          color="primary"
          :disabled="!canAddMaterial"
          :loading="isAddingMaterial"
          @click="addMaterialToList"
        >
          新增材料
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { useGrantsStore } from '@/stores/grants';
import { useOfficesStore } from '@/stores/offices'
import { usePipeFittingsStore } from '@/stores/pipeFittingsStore'
import { usePFDiametersStore } from '@/stores/pfDiametersStore'
import { usePFMaterialsStore } from '@/stores/pfMaterialsStore'
import { useIrrigationTypesStore } from '@/stores/irrigationTypesStore'
import type { PipeFitting } from '@/types/pipeFittings'

// Type definitions for material generation
interface MaterialData {
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
  moduleType?: string;
  module_id?: number;
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
  module_id?: number;
}

interface MaterialGroup {
  id?: number;
  groupNo: number;
  groupName: string;
  items: MaterialData[];
  GroupNo: number;
  GroupName: string;
  List: MaterialData[];
}


interface PipeOption {
  id: number | string;
  name: string;
  standardLength?: number;
}

interface PipeItem {
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
  moduleType?: string;
}

interface EndFacilityPipeFitting {
    pomno: number;
    displayName: string; // 例如: "PVC噴頭 1/2吋"
    materialName: string;
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
  // mapNo: { // 對應舊 MapNo
  //   type: Number,
  //   required: false,
  //   default: 0
  // },
  // operatingUnitId: { // 對應舊 OperatingUnitId
  //   type: Number,
  //   required: false,
  //   default: 1
  // }
});

const emit = defineEmits(['update:formData', 'validated', 'go-back', 'show-snackbar']);

// Access the store
const grantsStore = useGrantsStore();
const officesStore = useOfficesStore();
const pipeFittingsStore = usePipeFittingsStore();
const pfDiametersStore = usePFDiametersStore();
const pfMaterialsStore = usePFMaterialsStore();
const irrigationTypesStore = useIrrigationTypesStore()


// Store the filtered pipe fittings
const filteredPipeFittings = ref([]);

// Form validation references
const form = ref<HTMLFormElement | null>(null); // 顯式類型
const localValid = ref(true);
const stepContent = ref<HTMLElement | null>(null); // 顯式類型

// 載入與計算狀態
const isLoadingMaterials = ref(false);

// 手動新增材料相關狀態
const showManualAddDialog = ref(false);
const selectedMaterialPomno = ref<number | null>(null);
const selectedGroup = ref<number | null>(null);
const materialQuantity = ref<number>(1);
const materialSearchQuery = ref('');
const isAddingMaterial = ref(false);
const isCalculatingSubsidy = ref(false);
const isUpdating = ref(false);


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
  changeBranchSpecId: null as number | null, // 變徑規格ID (原 variantType/Adjustable)
  branchPipeMaterialId: null as number | null, // 支管主要材質ID
  branchPipeDiameterId: null as number | null, // 支管主要管徑ID

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
  installationType: '',
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
  facilityTypeId: null as number | null,       // 設施型式ID (原 ddl_FacType)
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
  subsidyTotal: 0,
  subsidyAmount: 0,
  farmerSelfAmount: 0,

  // Always valid for seamless navigation
  valid: true
});


// 根據灌溉類型篩選末端設施選項
const endFacilityOptions = [
  { value: '穿孔管-單管', irrigationType: '穿孔管系統' },
  { value: '穿孔管-雙管', irrigationType: '穿孔管系統' },
  { value: '噴頭式-單口噴頭', irrigationType: '噴頭式系統' },
  { value: '噴頭式-雙口噴頭', irrigationType: '噴頭式系統' },
  { value: '微噴-單向微噴霧', irrigationType: '微噴系統' },
  { value: '微噴-雙向微噴霧', irrigationType: '微噴系統' },
  { value: '滴灌-滴嘴', irrigationType: '滴灌系統' },
  { value: '滴灌-滴水管', irrigationType: '滴灌系統' }
];


// --- 選項列表 (應從API獲取) ---
const perforatedPipeTypeOptions = ref([ { value: 1, title: '單向' }, { value: 2, title: '雙向' } ]); // 這個選項較固定
const facilityTypeOptions = ref<PipeOption[]>([]);   // 設施型式
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

// --- 模擬API獲取下拉選單數據 (您需要用真實的API呼叫替換) ---
const loadDropdownOptions = async () => {
  await officesStore.fetchOffices();
  // fundingSourceOptions.value = await fundingSourcesService.getAll();
  // pipeDiameterOptions.value = await pfDiametersService.getAll();
  // pipeMaterialOptions.value = await pfMaterialsService.getAll();
  // irrigationTypeOptions.value = await irrigationTypesService.getAll();
  // facilityTypeOptions.value = await facilityTypesService.getAll();
  // waterSourceOptions.value = await waterSourcesService.getAll();

  await pfDiametersStore.fetchDiameters();
  await pfMaterialsStore.fetchMaterials();
  await irrigationTypesStore.fetchIrrigationTypeOptions()
  await fetchPipeFittings();

  // 模擬設施型式和水源選項
  facilityTypeOptions.value = [ {id: 1, name: '埋設固定式'}, {id: 2, name: '地表定置式'}, {id: 3, name: '附掛棚架式'}];
  waterSourceOptions.value = [ {id:1, name: '灌溉渠道'}, {id:2, name: '山溪溝'}, {id:3, name: '埤(池)塘'}, {id:4, name: '地下水'}, {id:5, name: '其他'} /* ... */];
};

const pipeDiameterOptions = computed(() => {
  // 使用主管模塊的管件來提取管徑選項
  const mainPipeFittings = filteredPipeFittingsByModule.value.mainPipe || [];

  const validCombinations = mainPipeFittings.map(fitting => ({
    materialId: fitting.material_id,
    diameterId: fitting.diameter1_id
  }));

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
        name: diameterInfo?.name || `直径ID: ${id}`,
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

// 🔧 Linus式修正：建立正確的資料依賴關係
// Step4 的設施面積應該直接從 Step2 的總施作面積計算得出
const facilityAreaFromStep2 = computed(() => {
  const step2Data = grantsStore.formData[2]

  if (!step2Data || !step2Data.lands || !Array.isArray(step2Data.lands)) {
    console.log('📊 step4.vue: No Step2 lands data available')
    return 0
  }

  // 計算所有土地的施作面積總和（與 Step2 的 totalFacilityArea 邏輯一致）
  const totalArea = step2Data.lands.reduce((total, land) => {
    const area = parseFloat(land.facilityArea || '0')
    return total + (isNaN(area) ? 0 : area)
  }, 0)

  console.log(`📊 step4.vue: Calculated facility area from Step2: ${totalArea} m²`)
  return totalArea
})

// 創建新的計算屬性用於支管的選項
const branchPipeDiameterOptions = computed(() => {
  const branchPipeFittings = filteredPipeFittingsByModule.value.branchPipe || [];
  // 與 pipeDiameterOptions 類似的邏輯，但使用支管模塊的數據
  // ...
});

const branchPipeMaterialOptions = computed(() => {
  const branchPipeFittings = filteredPipeFittingsByModule.value.branchPipe || [];
  // 與 pipeMaterialOptions 類似的邏輯，但使用支管模塊的數據
  // ...
});

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

const fundingSourceOptions = computed(() => {
  const filtered = officesStore.offices
    .filter(office => {
      return office.is_funding_source === true
    })
    .map(office => ({
      id: office.id,
      name: office.name
    }))

  return filtered
});

// 根據灌溉類型篩選末端設施選項
const filteredEndFacilityOptions = computed(() => {
  if (!localFormData.irrigationTypeId) return [];
  // Get irrigation type name for comparison
  const irrigationType = irrigationTypesStore.irrigationTypes.find(type => type.id === localFormData.irrigationTypeId);
  if (!irrigationType) return [];

  return endFacilityOptions
    .filter(option => option.irrigationType === irrigationType.name)
    .map(option => option.value);
});

// 是否顯示末端設施類型選擇
const showEndFacilityType = computed(() => {
  if (!localFormData.irrigationTypeId) return false;
  const irrigationType = irrigationTypesStore.irrigationTypes.find(type => type.id === localFormData.irrigationTypeId);
  return irrigationType && ['穿孔管系統', '噴頭式系統', '滴灌系統'].includes(irrigationType.name);
});

// Add missing computed properties
const canAddMainPipe = computed(() => {
  return !!(localFormData.mainPipeLength &&
           localFormData.mainPipeMaterialId &&
           localFormData.mainPipeDiameterId &&
           localFormData.mainPipeUnitPrice &&
           localFormData.mainPipeQuantity);
});

const canAddBranchPipe = computed(() => {
  return !!(localFormData.branchPipeLength &&
           localFormData.branchPipeMaterialId &&
           localFormData.branchPipeDiameterId &&
           localFormData.branchPipeUnitPrice &&
           localFormData.branchPipeQuantity);
});

const canAddEndFacility = computed(() => {
  return !!(localFormData.endFacilityPomno &&
           localFormData.endFacilitySpecId);
});

// Computed Properties
const mainPipeTotalPrice = computed(() => {
  if (!localFormData.mainPipeQuantity || !localFormData.mainPipeUnitPrice) return '0';
  return Math.round(localFormData.mainPipeQuantity * localFormData.mainPipeUnitPrice).toLocaleString();
});
const mainPipe2TotalPrice = computed(() => {
  if (!localFormData.mainPipe2Enabled || !localFormData.mainPipe2Quantity || !localFormData.mainPipe2UnitPrice) return '0';
  return Math.round(localFormData.mainPipe2Quantity * localFormData.mainPipe2UnitPrice).toLocaleString();
});

// 支管總價等原有的 computed properties 保持不變或按需調整
const branchPipeTotalPrice = computed(() => {
  // 支管的價格通常由後端自動帶入材料列表時一併給出，此處計算可能僅為UI示意
  const unitPrice = parseFloat(localFormData.branchPipeUnitPrice?.toString() || '0');
  const quantity = parseFloat(localFormData.branchPipeQuantity?.toString() || '0');
  return Math.round(unitPrice * quantity).toLocaleString();
});


const endFacilityTotalPrice = computed(() => {
  return '0'; // 暫時，因為末端設施通常是POMNo選擇
});

// 將管路按群組分類
const groupedPipes = computed(() => {
  const groups: Record<number, { groupNo: number; groupName: string; items: any[] }> = {};

  // 定義群組名稱映射
  const groupNameMapping: Record<number, string> = {
    1: '主管組',
    2: '支管組',
    3: '穿孔管組', // 穿孔管末端
    4: '滴水管組',   // 滴灌末端
    5: '豎管組',
    6: '固定設施組',
    7: '消耗性材料',
    8: '末端設施' // 噴頭/微噴/滴嘴組各類末端頭
    // ... 其他組別根據後端 MaterialModule.cs 中的 StdMat.Group 設定
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
const subsidyTotalAmount = computed(() => {
  return localFormData.subsidyTotal.toLocaleString();
});

const subsidyAmount = computed(() => {
  return localFormData.subsidyAmount.toLocaleString();
});

const farmerSelfAmount = computed(() => {
  return localFormData.farmerSelfAmount.toLocaleString();
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
      !!localFormData.facilityTypeId &&
      (localFormData.branchPipeSpacing_SL !== null && localFormData.branchPipeSpacing_SL > 0) &&
      (localFormData.sprinklerSpacing_SS !== null && localFormData.sprinklerSpacing_SS > 0) &&
      !!localFormData.branchPipeMaterialId &&
      !!localFormData.branchPipeDiameterId &&
      (localFormData.riserHeight_H !== null && localFormData.riserHeight_H > 0) &&
      !!localFormData.endFacilitySpecId &&
      !!localFormData.endFacilityPomno;
  }
  // 滴灌系統 (irrigationTypeId === 4)
  else if (localFormData.irrigationTypeId === 4) {
    irrigationTypeSpecificConditions =
      !!localFormData.dripperSubtypeId &&
      !!localFormData.facilityTypeId &&
      (localFormData.branchPipeSpacing_SL !== null && localFormData.branchPipeSpacing_SL > 0) &&
      !!localFormData.branchPipeMaterialId &&
      !!localFormData.branchPipeDiameterId &&
      !!localFormData.endFacilitySpecId &&
      !!localFormData.endFacilityPomno;
  }

  const result = basicConditions && mainPipe2Conditions && irrigationTypeSpecificConditions;

  // 輸出判斷結果供調試
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
  if (!materialSearchQuery.value) {
    return pipeFittingsStore.pipeFittings.map(fitting => ({
      ...fitting,
      searchText: `${fitting.name} ${fitting.material?.name || ''} ${fitting.module?.name || ''}`
    }));
  }

  const query = materialSearchQuery.value.toLowerCase();
  return pipeFittingsStore.pipeFittings
    .filter(fitting => {
      const searchText = `${fitting.name} ${fitting.material?.name || ''} ${fitting.module?.name || ''}`.toLowerCase();
      return searchText.includes(query);
    })
    .map(fitting => ({
      ...fitting,
      searchText: `${fitting.name} ${fitting.material?.name || ''} ${fitting.module?.name || ''}`
    }));
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
  { id: 4, name: '滴水管組' },
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
  if (length > 0 && area > 0) {
    localFormData.fieldWidth = Math.round(area / length);
  }
  // updateFormData();
};

// 🔧 Linus式修正：監聽 Step2 面積變化，自動重新計算 fieldWidth
watch(facilityAreaFromStep2, (newArea, oldArea) => {
  if (newArea !== oldArea) {
    console.log(`📊 step4.vue: facilityArea changed from ${oldArea} to ${newArea}, recalculating width`);
    calculateWidth();
  }
}, { immediate: false });

// 也監聽 fieldLength 變化
watch(() => localFormData.fieldLength, (newLength, oldLength) => {
  if (newLength !== oldLength && newLength > 0) {
    console.log(`📊 step4.vue: fieldLength changed from ${oldLength} to ${newLength}, recalculating width`);
    calculateWidth();
  }
}, { immediate: false });

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
      append: true,
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
    localFormData.mainPipeQuantity = Math.ceil(length / standardLength); // 無條件進位
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
    localFormData.mainPipe2Quantity = Math.ceil(length / standardLength); // 無條件進位
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

// 計算支管數量
const calculateBranchPipeQuantity = () => {
  // 這個函數在原 .NET 中主要用於計算 BN (支管列數)
  // 支管的總材料數量 (如多少支標準長度的管材) 是在 MaterialModule 中詳細計算的
  // 前端此處可能不需要直接計算支管的 "數量" 欄位，除非有特定UI需求
  // BN = fieldLength / branchPipeSpacing_SL
  updateFormData();
};

// 計算噴頭數量
const calculateSprinklerQuantity = () => {
  // 這個函數在原 .NET 中主要用於計算 SN (每列支管上的噴頭數)
  // 並進一步計算末端設施總數 BN * SN
  // 此處更新 endFacilityQuantity 是合理的
  const fieldLength = localFormData.fieldLength || 0;
  const fieldWidth = localFormData.fieldWidth || 0;
  const branchPipeSpacing = localFormData.branchPipeSpacing_SL || 0;
  const sprinklerSpacing = localFormData.sprinklerSpacing_SS || 0;

  if (fieldLength > 0 && fieldWidth > 0 && branchPipeSpacing > 0 && sprinklerSpacing > 0) {
    const branchPipes = Math.ceil(fieldLength / branchPipeSpacing);
    const sprinklersPerBranch = Math.ceil(fieldWidth / sprinklerSpacing);
    const totalSprinklers = branchPipes * sprinklersPerBranch;
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
  updateFormData();
};

const onEndFacilitySpecChange = async () => {
  localFormData.endFacilityPomno = null; // 清除之前選擇的末端設施
  await loadEndFacilityOptions(); // 重新載入與當前規格比對的末端設施選項
};

const loadEndFacilityOptions = async () => {
  // TODO: API Call to fetch end facility options (pipe_fittings)
  // based on irrigationTypeId, sprinklerSubtypeId, dripperSubtypeId, facilityTypeId, operating_unit_id
  // This API should return a list of objects like EndFacilityPipeFitting interface
  // Example: filteredEndFacilityPipeFittings.value = await pipeFittingsService.getTerminalFittings({ type: localFormData.irrigationTypeId, ... });
  // 保存當前選擇的項目
  const currentSelection = localFormData.endFacilityPomno;

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
    materialName: fitting.material.name || '',
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

  filteredEndFacilityPipeFittings.value = uniqueFittings;
};

const onSelectedEndFacilityChange = (selectedPomno: number | null) => {
    if (selectedPomno) {
        const selectedFitting = filteredEndFacilityPipeFittings.value.find(f => f.pomno === selectedPomno);
        if (selectedFitting) {
            localFormData.endFacilitySpecId = selectedFitting.specId || null;
            // 單價等也應從此 fitting 物件或後續API獲取
        }
    } else {
        localFormData.endFacilitySpecId = null;
    }
    updateFormData();
};

// 設施類型變更
const onInstallationTypeChange = () => {
  updateFormData();
};

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
  pipe.totalPrice = Math.round(pipe.matprice * newQuantity);

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
  pipe.totalPrice = Math.round(pipe.matprice * pipe.matamount);

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

  // 如果是主管材料，同步更新田間主管配置的單價
  if (pipe.isMainPipeMaterial) {
    if (pipe.groupId === 1) { // 主管組
      if (pipe.matname.includes('主管 1') || pipe.matname.includes('L1')) {
        localFormData.mainPipeUnitPrice = newPrice;
      } else if (pipe.matname.includes('主管 2') || pipe.matname.includes('L2')) {
        localFormData.mainPipe2UnitPrice = newPrice;
      }
    }
  }

  // 更新父組件數據
  updateFormData();
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

// 顯示除錯資訊
const showDebugInfo = (pipe: any) => {
  selectedMaterialDebugInfo.value = {
    // 生成的材料資訊
    generated: {
      pomno: pipe.pomno,
      module: pipe.module,
      matname: pipe.matname,
      module_id: pipe.module_id,
      mattype: pipe.mattype,
      spec1: pipe.spec1,
      spec2: pipe.spec2,
      spec3: pipe.spec3,
      itemunit: pipe.itemunit,
      matprice: pipe.matprice,
      matamount: pipe.matamount,
      description: pipe.description,
      order: pipe.order,
      group: pipe.group
    },
    // 比對的 pipeFittingsStore 資料
    matched: pipe.debugMatchData,
    // 比對狀態
    matchStatus: pipe.debugMatchData ? 'success' : 'failed',
    // 比對條件
    matchCriteria: {
      module_id: pipe.module_id,
      spec1: pipe.spec1,
      mattype: pipe.mattype || null
    }
  };
  debugDialog.value = true;
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
      if (!localFormData.facilityTypeId) {
        errorMessage += '- 設施型式\n';
      }
      if (localFormData.branchPipeSpacing_SL === null || localFormData.sprinklerSpacing_SS === null) {
        errorMessage += '- 支管行距(SL)和噴頭間距(SS)\n';
      }
      if (!localFormData.branchPipeMaterialId || !localFormData.branchPipeDiameterId) {
        errorMessage += '- 支管材質和規格\n';
      }
      if (!localFormData.riserHeight_H) {
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
      if (!localFormData.facilityTypeId) {
        errorMessage += '- 設施型式\n';
      }
      if (localFormData.branchPipeSpacing_SL === null) {
        errorMessage += '- 支管行距(SL)\n';
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
        ddl_FacType: localFormData.facilityTypeId,
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

    // console.log('Auto-filling materials with payload:', JSON.stringify(requestPayload, null, 2));

    // 使用真實的前端輸入條件動態生成材料，基於14種舊系統公式
    // console.log('Generating materials using dynamic formula calculation...');

    // 直接使用真實的前端數據進行材料計算
    const materialGroupsFromApi = getMockMaterialData(requestPayload.form_inputs);

    localFormData.pipes = []; // 清空現有
    materialGroupsFromApi.forEach(group => {
      group.List.forEach(material => {
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
          totalPrice: Math.round(material.matprice * material.matamount),
          order: material.order,
          debugMatchData: material.debugMatchData // 加入除錯比對資料
        });
      });
    });
    await calculateSubsidy(); // 自動帶入材料後觸發補助計算
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
    localFormData.subsidyTotal = 0;
    localFormData.subsidyAmount = 0;
    localFormData.farmerSelfAmount = 0;
    return;
  }
  isCalculatingSubsidy.value = true;
  try {
    // const mainPipesData = [];
    // if (localFormData.mainPipeLength && localFormData.mainPipeMaterialId && localFormData.mainPipeDiameterId) {
    //     mainPipesData.push({
    //         Length: localFormData.mainPipeLength,
    //         Mat: pipeMaterialOptions.value.find(m => m.id === localFormData.mainPipeMaterialId)?.name || '', // 材質名稱
    //         Spec: localFormData.mainPipeDiameterId, // 規格ID
    //         LPrice: localFormData.mainPipeUnitPrice || 0,
    //         Amount: localFormData.mainPipeQuantity || 0
    //     });
    // }
    // if (localFormData.mainPipe2Enabled && localFormData.mainPipe2Length && localFormData.mainPipe2MaterialId && localFormData.mainPipe2DiameterId) {
    //     mainPipesData.push({
    //         Length: localFormData.mainPipe2Length,
    //         Mat: pipeMaterialOptions.value.find(m => m.id === localFormData.mainPipe2MaterialId)?.name || '', // 材質名稱
    //         Spec: localFormData.mainPipe2DiameterId, // 規格ID
    //         LPrice: localFormData.mainPipe2UnitPrice || 0,
    //         Amount: localFormData.mainPipe2Quantity || 0
    //     });
    // }

    // const requestPayload = {
    //     map_no: props.mapNo, // 需要傳入
    //     // operating_unit_id: props.operatingUnitId, // GetTotalPrice 可能不需要此參數，但後端可按需加入

    //     // 以下對應 ParaJsonData
    //     Unit: localFormData.fundingSourceId, // 補助單位ID
    //     Block: `${localFormData.fieldLength}x${localFormData.fieldWidth}`,
    //     IrrWCode: localFormData.waterSourceId, // 灌溉水源ID

    //     EndTypeDataAry: [{ // 這裡簡化為只處理第一個末端系統，若有多個需擴展
    //         Endtype: localFormData.irrigationTypeId, // 末端型式主ID
    //         Fac: localFormData.facilityTypeId,       // 設施型式ID
    //         BranchPipeMaterial: pipeMaterialOptions.value.find(m=>m.id === localFormData.branchPipeMaterialId)?.name || '', // 支管材質名稱
    //         BranchPipeSpec: localFormData.branchPipeDiameterId, // 支管規格ID
    //         SS: localFormData.sprinklerSpacing_SS,
    //         SL: localFormData.branchPipeSpacing_SL,
    //         StdpipeHei: localFormData.riserHeight_H,
    //         NozzleSpec: localFormData.endFacilitySpecId, // 末端設施主要規格ID
    //         NozzleType: filteredEndFacilityPipeFittings.value.find(f => f.pomno === localFormData.endFacilityPomno)?.displayName || '', // 末端設施名稱或類型描述
    //         StdpipeMat: pipeMaterialOptions.value.find(m => m.id === localFormData.riserPipeMaterialId)?.name || '', // 豎管材質名稱
    //         StdpipeSpec: localFormData.riserPipeSpecId,   // 豎管規格ID
    //         PerforatedPipe: localFormData.irrigationTypeId === 1 ? localFormData.perforatedPipeDirection : 1
    //     }],
    //     MainJsonDataAry: mainPipesData,
    //     PriceJsonDataAry: localFormData.pipes.map(pipe => ({
    //         POMNo: pipe.pomno,
    //         Group: pipe.groupId,
    //         Order: pipe.order || 1, // 確保有值
    //         Amt: pipe.matamount,
    //         Price: pipe.matprice,
    //         TotalPrice: pipe.totalPrice
    //     })),
    //     FacNo: null, // 公版設施系統代號, 若有選擇公版系統則傳入, 此處可能為null或特定值
    //     // TotalPrice: parseFloat(totalPipesPrice.value.replace(/,/g, '')) // 由後端計算，或前端先計算一次傳給後端參考
    // };

    // console.log('Calculating subsidy with payload:', JSON.stringify(requestPayload, null, 2));

    // 【TODO: API Call】 替換為真實的 FastAPI 端點呼叫
    // const response = await yourApiService.post('/api/subsidy/calculate-total-price', requestPayload);
    // const priceData = response.data.split(';'); // 假設後端返回 "總價;補助金額;自付金額"

    // 根據灌溉型式和原民區域狀態計算補助金額
    await new Promise(resolve => setTimeout(resolve, 1000));

    const currentTotalPipesPrice = parseFloat(totalPipesPrice.value.replace(/,/g, ''));
    const facilityAreaInHectares = facilityAreaFromStep2.value / 10000; // 轉換為公頃

    // 從 step2 數據中獲取原民區域狀態
    const isAboriginalArea = grantsStore.formData[2]?.isAboriginalArea || false;

    // 根據灌溉型式和原民區域狀態設定每公頃補助金額
    let subsidyPerHectare = 0;
    const irrigationTypeId = localFormData.irrigationTypeId;

    if (irrigationTypeId === 1) { // 穿孔管系統
      subsidyPerHectare = isAboriginalArea ? 68200 : 62000;
    } else if (irrigationTypeId === 2) { // 噴頭式系統
      subsidyPerHectare = isAboriginalArea ? 132000 : 120000;
    } else if (irrigationTypeId === 3) { // 微噴系統
      subsidyPerHectare = isAboriginalArea ? 198000 : 180000;
    } else if (irrigationTypeId === 4) { // 滴灌系統
      subsidyPerHectare = isAboriginalArea ? 220000 : 200000;
    }

    // 計算政府補助金額上限
    const maxSubsidyAmount = Math.round(facilityAreaInHectares * subsidyPerHectare);

    // 計算實際補助金額和農民自付金額
    let actualSubsidyAmount, farmerSelfAmount;

    if (currentTotalPipesPrice > maxSubsidyAmount) {
      // 總價超過補助上限，農民需自付超出部分
      actualSubsidyAmount = maxSubsidyAmount;
      farmerSelfAmount = currentTotalPipesPrice - maxSubsidyAmount;
    } else {
      // 總價不超過補助上限，政府全額補助
      actualSubsidyAmount = currentTotalPipesPrice;
      farmerSelfAmount = 0;
    }

    // 模擬 API 回傳格式
    const mockApiResponse = `${currentTotalPipesPrice};${actualSubsidyAmount};${farmerSelfAmount}`;
    const priceData = mockApiResponse.split(';');

    console.log('💰 補助計算結果:', {
      灌溉型式: irrigationTypeId,
      原民區域: isAboriginalArea,
      施設面積公頃: facilityAreaInHectares,
      每公頃補助額: subsidyPerHectare,
      補助上限: maxSubsidyAmount,
      總工程費: currentTotalPipesPrice,
      政府補助: actualSubsidyAmount,
      農民自付: farmerSelfAmount
    });

    localFormData.subsidyTotal = parseInt(priceData[0]) || 0;
    localFormData.subsidyAmount = parseInt(priceData[1]) || 0;
    localFormData.farmerSelfAmount = parseInt(priceData[2]) || 0;

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

  console.log('🔄 step4.vue updateFormData called');
  console.log('📤 Emitting update:formData with facilityArea from Step2:', dataToEmit.facilityArea);

  emit('update:formData', dataToEmit);
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
      'facilityTypeId': !!localFormData.facilityTypeId ? '✓' : '✗',
      'branchPipeSpacing_SL': (localFormData.branchPipeSpacing_SL !== null) ? '✓' : '✗',
      'sprinklerSpacing_SS': (localFormData.sprinklerSpacing_SS !== null) ? '✓' : '✗',
      'branchPipeMaterialId': !!localFormData.branchPipeMaterialId ? '✓' : '✗',
      'branchPipeDiameterId': !!localFormData.branchPipeDiameterId ? '✓' : '✗',
      'riserHeight_H': !!localFormData.riserHeight_H ? '✓' : '✗',
      'endFacilitySpecId': !!localFormData.endFacilitySpecId ? '✓' : '✗',
      'endFacilityPomno': !!localFormData.endFacilityPomno ? '✓' : '✗'
    };
  } else if (irrigationType === 4) { // 滴灌系統
    typeSpecificStatus = {
      'dripperSubtypeId': !!localFormData.dripperSubtypeId ? '✓' : '✗',
      'facilityTypeId': !!localFormData.facilityTypeId ? '✓' : '✗',
      'branchPipeSpacing_SL': (localFormData.branchPipeSpacing_SL !== null) ? '✓' : '✗',
      'branchPipeMaterialId': !!localFormData.branchPipeMaterialId ? '✓' : '✗',
      'branchPipeDiameterId': !!localFormData.branchPipeDiameterId ? '✓' : '✗',
      'endFacilitySpecId': !!localFormData.endFacilitySpecId ? '✓' : '✗',
      'endFacilityPomno': !!localFormData.endFacilityPomno ? '✓' : '✗'
    };
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

  // 輸出完整診斷資訊到控制台
  // console.log('自動帶入材料必填欄位狀態:', allStatus);
  // console.log('原始表單數據:', JSON.parse(JSON.stringify(localFormData)));

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
    message = '所有必填欄位皆已填寫，但可能有其他條件未滿足。請檢查控制台以獲取更多信息。';
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
    'facilityTypeId': '設施型式',
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


// 實用函數
// 模擬取得物料編號
const getPOMNo = (moduleType: string, name: string) => {
  // 實際應用中，這裡應該使用真實的物料編號邏輯
  // 這裡僅返回一個隨機模擬編號
  return Math.floor(Math.random() * 10000) + 10000;
};

// 獲取總價格
const getTotalPrice = () => {
  return localFormData.pipes.reduce((sum, pipe) => sum + pipe.totalPrice, 0);
};

// 獲取材料數據 - 實現14種公式條件的動態材料計算
const getMockMaterialData = (formInputs: FormInputs) => {
  // console.log("Dynamic material calculation based on form inputs:", formInputs);

  // 映射前端欄位到legacy欄位名稱
  const legacyData = mapToLegacyFields(formInputs);
  // console.log("Legacy data mapping:", legacyData);

  // 決定使用哪個公式
  const formulaNumber = determineFormula(legacyData);
  // console.log(`Using formula ${formulaNumber} for material calculation`);

  // 根據公式生成材料列表
  return generateMaterialsByFormula(formulaNumber, legacyData);
};

// 映射前端欄位到Legacy系統欄位
const mapToLegacyFields = (formInputs: FormInputs) => {
  const fieldLength = localFormData.fieldLength || formInputs.Length || 0;
  const fieldWidth = localFormData.fieldWidth || formInputs.width || 0;
  const branchPipeSpacing = localFormData.branchPipeSpacing_SL || formInputs.SL || 0;
  const sprinklerSpacing = localFormData.sprinklerSpacing_SS || formInputs.SS || 0;

  // 計算支管數量和末端設施數量
  // 穿孔管配件計算使用 Math.floor (無條件捨去)
  const branchAmt = branchPipeSpacing > 0 ? Math.floor(fieldLength / branchPipeSpacing) : 0;
  const branchLength = fieldWidth; // 支管長度通常等於田區寬度
  const nozzlePerBranch = sprinklerSpacing > 0 ? Math.ceil(fieldWidth / sprinklerSpacing) : 0;
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
    StandPipeLength: localFormData.riserHeight_H || 1,
    StdpipeMat: localFormData.riserPipeMaterialId || 1,

    // 變更相關
    ChangeBranchSpec: 0, // 預設無變更規格
    NewBranchSpec: null,

    // 設施類型
    ddl_FacType: localFormData.facilityTypeId || 1,
    ddl_WtaerSrc: localFormData.waterSourceId || 1
  };
};

// 決定使用哪個公式
const determineFormula = (data: MaterialData): number => {
  const endType = data.ddl_EndType;
  const hasL2 = data.L2MatAmt > 0;
  const hasSpecChange = data.ChangeBranchSpec !== 0;
  const dropType = data.ddl_Drop;

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

// 材料數量取整函數
const calculateMaterialAmount = (amount: number, itemType: string): number => {
  // 管材類型：無條件進位取整數
  const pipeTypes = ['主管', '支管', '穿孔管', '滴灌管', '滴水帶', '豎管'];
  if (pipeTypes.includes(itemType)) {
    return Math.ceil(amount);
  }

  // 配件類型：無條件捨去取整數
  const fittingTypes = ['主管配件', '支管配件', '穿孔管配件', '滴灌配件', '滴水帶配件', '豎管配件', '固定設施', '噴頭', '微噴頭', '滴嘴'];
  if (fittingTypes.includes(itemType)) {
    return Math.floor(amount);
  }

  // 預設使用無條件進位
  return Math.ceil(amount);
};

// 直接根據 pomno 比對材料 - 用於用戶已明確選擇的材料
const matchMaterialByPomno = (pomno: string | number): { pomno: number | null, matprice: number | null, matchedData: any | null } => {
  if (!pipeFittingsStore.pipeFittings || pipeFittingsStore.pipeFittings.length === 0) {
    return { pomno: null, matprice: null, matchedData: null };
  }

  const matchedMaterial = pipeFittingsStore.pipeFittings.find(fitting => fitting.pomno === pomno);

  if (matchedMaterial) {
    // console.log(`[matchMaterialByPomno] 直接比對成功: pomno=${pomno} -> ${matchedMaterial.name}`);
    return {
      pomno: matchedMaterial.pomno,
      matprice: matchedMaterial.current_price || null,
      matchedData: matchedMaterial
    };
  }

  // console.warn(`[matchMaterialByPomno] 直接比對失敗: pomno=${pomno}`);
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
      // console.log('[fuzzyTextMatch] Empty input:', { searchText, targetText });
      return false;
    }

    const search = searchText.toLowerCase().trim();
    const target = targetText.toLowerCase().trim();

    // console.log('[fuzzyTextMatch] Comparing:', { search, target });

    // 完全比對
    if (target.includes(search)) {
      // console.log('[fuzzyTextMatch] Complete match found');
      return true;
    }

    // 反向比對 - 檢查搜尋詞是否包含目標詞
    if (search.includes(target)) {
      // console.log('[fuzzyTextMatch] Reverse match found');
      return true;
    }

    // 關鍵字比對 - 將搜尋文字拆分成關鍵字進行比對
    const searchKeywords = search.split(/[\s\-_、，,]+/).filter(keyword => keyword.length > 0);
    const targetKeywords = target.split(/[\s\-_、，,]+/).filter(keyword => keyword.length > 0);

    // console.log('[fuzzyTextMatch] Keywords:', { searchKeywords, targetKeywords });

    // 檢查搜尋關鍵字是否在目標文字中
    const matchedFromSearch = searchKeywords.filter(keyword => target.includes(keyword));

    // 檢查目標關鍵字是否在搜尋文字中
    const matchedFromTarget = targetKeywords.filter(keyword => search.includes(keyword));

    // console.log('[fuzzyTextMatch] Matched keywords:', { matchedFromSearch, matchedFromTarget });

    // 如果搜尋關鍵字中有超過一半比對，或者目標關鍵字中有任一比對
    const searchMatchRatio = matchedFromSearch.length / searchKeywords.length;
    const targetMatchRatio = matchedFromTarget.length / targetKeywords.length;

    const isMatch = searchMatchRatio >= 0.5 || targetMatchRatio >= 0.5 || matchedFromTarget.length > 0;

    // console.log('[fuzzyTextMatch] Match result:', {
    //   searchMatchRatio,
    //   targetMatchRatio,
    //   isMatch,
    //   reason: isMatch ? 'Keywords matched' : 'No sufficient keyword match'
    // });

    return isMatch;
  };

  // 輔助函數：檢查規格相容性
  const checkSpecCompatibility = (fitting: any, spec1: string, spec2?: string, spec3?: string): boolean => {
    // console.log(`[checkSpecCompatibility] Checking fitting:`, {
    //   fittingName: fitting.name,
    //   spec1,
    //   diameter1: fitting.diameter1,
    //   diameter2: fitting.diameter2,
    //   diameter3: fitting.diameter3
    // });

    // 如果沒有提供規格要求，則認為相容
    if (!spec1 || spec1.trim() === '') {
      // console.log(`[checkSpecCompatibility] No spec requirement, compatible`);
      return true;
    }

    const spec1Value = parseSpecValue(spec1);

    // 檢查是否有任何 diameter 比對
    const diameterChecks = [
      { check: fitting.diameter1?.value === spec1Value, desc: `diameter1.value(${fitting.diameter1?.value}) === spec1Value(${spec1Value})` },
      { check: fitting.diameter2?.value === spec1Value, desc: `diameter2.value(${fitting.diameter2?.value}) === spec1Value(${spec1Value})` },
      { check: fitting.diameter3?.value === spec1Value, desc: `diameter3.value(${fitting.diameter3?.value}) === spec1Value(${spec1Value})` },
      { check: fitting.diameter1?.name === spec1, desc: `diameter1.name(${fitting.diameter1?.name}) === spec1(${spec1})` },
      { check: fitting.diameter2?.name === spec1, desc: `diameter2.name(${fitting.diameter2?.name}) === spec1(${spec1})` },
      { check: fitting.diameter3?.name === spec1, desc: `diameter3.name(${fitting.diameter3?.name}) === spec1(${spec1})` }
    ];

    const hasAnyDiameterMatch = diameterChecks.some(dc => {
      if (dc.check) {
        // console.log(`[checkSpecCompatibility] Match found: ${dc.desc}`);
        return true;
      }
      return false;
    });

    // 對於配件類，如果名稱已經比對了，我們可以更寬鬆地處理規格
    // 特別是一些通用配件可能沒有嚴格的規格限制
    const isCompatible = hasAnyDiameterMatch ||
                        // 沒有設定規格的配件
                        (!fitting.diameter1_id && !fitting.diameter2_id && !fitting.diameter3_id);

    // console.log(`[checkSpecCompatibility] Result: ${isCompatible}, hasAnyDiameterMatch: ${hasAnyDiameterMatch}`);

    return isCompatible;
  };

  const spec1Value = parseSpecValue(spec1);
  const spec2Value = spec2 ? parseSpecValue(spec2) : 0;
  const spec3Value = spec3 ? parseSpecValue(spec3) : 0;

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
  materials: any[],
  moduleIdOrPomno: number | string,
  spec1: string = '',
  mattype: string = '',
  matname: string = '',
  materialConfig: {
    module: string;
    matname: string;
    module_id: number;
    mattype: string;
    spec1: string;
    spec2?: string;
    spec3?: string;
    itemunit: string;
    matamount: number;
    description: string;
    order: number;
    group: number;
  }
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
      debugMatchData: match.matchedData
    });

    // console.log(`[addMaterial] Successfully matched: ${materialConfig.matname} -> ${match.matchedData?.name} (${materialConfig.description})`);
    return true;
  } else {
    // 比對失敗：使用原始材料配置，但 pomno 和 matprice 設為空值
    materials.push({
      ...materialConfig,
      pomno: null,
      matprice: null,
      debugMatchData: null
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

// 舊版函數保留以供向後相容 - 只有成功比對的材料才會被添加
// const addMaterialIfMatched = (
//   materials: any[],
//   moduleId: number,
//   spec1: string,
//   mattype: string = '',
//   matname: string = '',
//   materialConfig: {
//     module: string;
//     matname: string;
//     module_id: number;
//     mattype: string;
//     spec1: string;
//     spec2?: string;
//     spec3?: string;
//     itemunit: string;
//     matamount: number;
//     description: string;
//     order: number;
//     group: number;
//   }
// ): boolean => {
//   const match = matchMaterialFromStore(moduleId, spec1, materialConfig.spec2 || '', materialConfig.spec3 || '', mattype, matname);

//   if (match.pomno !== null && match.matprice !== null) {
//     materials.push({
//       ...materialConfig,
//       pomno: match.pomno,
//       matprice: match.matprice,
//       matname: match.matchedData?.name || materialConfig.matname, // 使用真實名稱
//       debugMatchData: match.matchedData
//     });

//     console.log(`[addMaterialIfMatched] Successfully added: ${materialConfig.matname} -> ${match.matchedData?.name} (${materialConfig.description})`);
//     return true;
//   } else {
//     console.warn(`[addMaterialIfMatched] No match found for: ${materialConfig.matname}`, {
//       moduleId,
//       spec1,
//       mattype,
//       matname,
//       description: materialConfig.description
//     });
//     return false;
//   }
// };

// 根據公式生成材料列表
const generateMaterialsByFormula = (formulaNumber: number, data: MaterialData): Array<typeof localFormData.pipes[0]> => {
  const materialGroups: any[] = [];

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
      materialGroups.push(generateNozzleChangeSystem(data, data.L1Spec));
      break;
    case 6:
      materialGroups.push(generateNozzleChangeSystem(data, data.L1Spec));
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
      materialGroups.push(generateMicroSprinklerChangeSystem(data, data.L1Spec));
      break;
    case 10:
      materialGroups.push(generateMicroSprinklerChangeSystem(data, data.L1Spec));
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

  return materialGroups.filter(group => group.List.length > 0);
};

// 添加主管材料的專用函數，使用自定義單價
const addMainPipeMaterial = (
  materials: any[],
  materialConfig: any,
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
    debugMatchData: match.matchedData,
    isMainPipeMaterial: true, // 標記為主管材料
    customPrice: customPrice // 保存自定義價格
  });

  console.log(`[addMainPipeMaterial] 使用自定義單價: ${materialConfig.matname} -> ${customPrice}元`);
  return true;
};

// 生成主管1材料 (L1MainPipeLine)
const generateL1MainPipeLine = (data: any) => {
  const materials = [];
  const L1MaterialName = pipeMaterialOptions.value.find(m => m.id === data.L1Material)?.name;
  const L1SpecName = pipeDiameterOptions.value.find(d => d.id === data.L1Spec)?.name;

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
    matamount: Math.ceil(data.L1MatAmt || Math.ceil(data.L1Len / 4)),
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
    itemunit: '個',
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
    itemunit: '個',
    matprice: valveMatch.matprice,
    matamount: Math.floor(1),
    description: '鍍鋅鋼主管制水閥',
    order: 1,
    group: 4,
    debugMatchData: valveMatch.matchedData // 除錯用資料
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

  const materials = [];
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
    matamount: Math.ceil(data.L2MatAmt || Math.ceil(data.L2Len / 4)),
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
  const materials = [];
  // 新的穿孔管管材計算方式:
  // 1. 行數 = Math.floor(fieldLength / branchPipeSpacing_SL) (已在BranchAmt中實現)
  // 2. 穿孔管長度 = 行數 * fieldWidth
  // 3. 穿孔管數量 = Math.ceil(穿孔管長度 / 100) (以100m為單位計價)
  // 注意：雙向出水時穿孔管管材長度不變，只有配件數量會加倍
  const perforatedTotalLength = data.BranchAmt * data.BranchLength; // 總穿孔管長度
  const isDoubleDirection = data.PerforatedPipe === 2;
  const multiplier = isDoubleDirection ? 2 : 1; // 僅用於配件計算

  // 計算以100m為單位的穿孔管數量（不受雙向影響）
  const perforatedQuantityPer100m = Math.ceil(perforatedTotalLength / 100);

  // 從用戶選擇的末端設施中獲取正確的規格和材質資訊
  const selectedEndFacility = pipeFittingsStore.pipeFittings.find(
    fitting => fitting.pomno === localFormData.endFacilityPomno
  );

  // 如果找到用戶選擇的末端設施，使用其規格和材質；否則使用預設值
  let nozzleSpecName, endFacilityMaterial;
  if (selectedEndFacility) {
    // 使用末端設施的第一個管徑作為穿孔管規格
    nozzleSpecName = selectedEndFacility.diameter1?.name ||
                     selectedEndFacility.diameter2?.name ||
                     selectedEndFacility.diameter3?.name;
    endFacilityMaterial = selectedEndFacility.material?.name;
    // console.log(`[generatePerforatedPipe] 使用末端設施規格: ${nozzleSpecName}, 材質: ${endFacilityMaterial}`);
  } else {
    // 回退到舊邏輯
    // nozzleSpecName = pipeDiameterOptions.value.find(d => d.id === data.NozzleMaterial)?.name || '3/4"';
    // endFacilityMaterial = 'PE';
    // console.warn(`[generatePerforatedPipe] 未找到末端設施 pomno=${localFormData.endFacilityPomno}，使用預設規格: ${nozzleSpecName}`);
  }

  const mainSpecName = pipeDiameterOptions.value.find(d => d.id === mainPipeSpec)?.name;

  // 穿孔管 - 直接使用用戶選擇的末端設施 pomno 進行精確比對
  const perforatedPipeMatch = matchMaterialByPomno(localFormData.endFacilityPomno);

  // 取得實際的標準長度，若無資料則預設為100
  const standardLength = perforatedPipeMatch.matchedData?.length || 100;

  // 計算穿孔管數量 = Math.ceil(總長度 / 標準長度)
  const perforatedQuantity = Math.ceil(perforatedTotalLength / standardLength);

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
    matamount: perforatedQuantity * multiplier,
    description: `穿孔管材(${standardLength}m計價)`,
    order: 1,
    group: 3
  });

  // 三通或四通
  const fittingName = data.PerforatedPipe === 1 ? '三通' : '四通';
  const fittingSpec = `${mainSpecName}×${nozzleSpecName}`;
  addMaterial(materials, 2, fittingSpec, '', fittingName, {
    module: '穿孔管配件',
    matname: fittingName,
    module_id: 2,
    mattype: 'PVC',
    spec1: fittingSpec,
    spec2: '',
    spec3: '',
    itemunit: '個',
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
    itemunit: '個',
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
    itemunit: '個',
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
    itemunit: '個',
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

// 生成噴頭系統材料
// const generateNozzleSystem = (data: any, mainPipeSpec: any) => {
//   const materials = [];

//   // 支管材料
//   materials.push(...generateBranchPipeMaterials(data, mainPipeSpec, 2));

//   // 豎管材料
//   materials.push(...generateStandPipeMaterials(data, 5));

//   // 固定設施
//   materials.push(...generateFixedFacilities(data, 6));

//   // 噴頭
//   materials.push(...generateSprinklerHeads(data, 8));

//   return {
//     GroupNo: 2,
//     GroupName: '噴頭系統組',
//     List: materials
//   };
// };

// 生成支管組材料 (獨立分組)
const generateBranchPipeGroup = (data: any, mainPipeSpec: any) => {
  const materials = generateBranchPipeMaterials(data, mainPipeSpec, 2);
  return {
    GroupNo: 2,
    GroupName: '支管組',
    List: materials
  };
};

// 生成支管材料的通用函數
const generateBranchPipeMaterials = (data: any, mainPipeSpec: any, groupId: number) => {
  const materials = [];
  const branchMaterialName = pipeMaterialOptions.value.find(m => m.id === data.BranchMaterial)?.name;
  const branchSpecName = pipeDiameterOptions.value.find(d => d.id === data.BranchSpec)?.name;
  const mainSpecName = pipeDiameterOptions.value.find(d => d.id === mainPipeSpec)?.name;

  // TODO: 以實際的支管材質的長度規格做為計價單位，目前假設支管長度為4m計價
  // 支管
  addMaterial(materials, 1, branchSpecName, branchMaterialName, '', {
    module: '支管',
    matname: `${branchMaterialName} ${branchSpecName}`,
    module_id: 1,
    mattype: branchMaterialName,
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: '4m',
    matamount: Math.ceil((data.BranchAmt * data.BranchLength) / 4), // 每4m計價
    description: '支管管材(4m計價)',
    order: 1,
    group: groupId
  });

  // 三通
  const teeSpec = `${mainSpecName}×${branchSpecName}`;
  addMaterial(materials, 2, teeSpec, '', '三通', {
    module: '支管配件',
    matname: '三通',
    module_id: 2,
    mattype: 'PVC',
    spec1: teeSpec,
    spec2: '',
    spec3: '',
    itemunit: '個',
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
    itemunit: '個',
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
    itemunit: '個',
    matamount: Math.floor(data.BranchAmt),
    description: '支管末端塞口',
    order: 4,
    group: groupId
  });

  return materials;
};

// 生成豎管組材料 (獨立分組)
const generateStandPipeGroup = (data: any) => {
  const materials = generateStandPipeMaterials(data, 5);
  return {
    GroupNo: 5,
    GroupName: '豎管組',
    List: materials
  };
};

// 生成豎管材料
const generateStandPipeMaterials = (data: any, groupId: number) => {
  const materials = [];
  const standPipeMaterialName = pipeMaterialOptions.value.find(m => m.id === data.StdpipeMat)?.name;
  const standPipeSpecName = pipeDiameterOptions.value.find(d => d.id === data.StandPipeSpec)?.name;
  const branchSpecName = pipeDiameterOptions.value.find(d => d.id === data.BranchSpec)?.name;

  // TODO: 以實際的豎管材質的長度規格做為計價單位，目前假設豎管長度為4m計價
  // 豎管
  addMaterial(materials, 4, standPipeSpecName, standPipeMaterialName, '', {
    module: '豎管',
    matname: `${standPipeSpecName} ${standPipeMaterialName} 豎管`,
    module_id: 4,
    mattype: standPipeMaterialName,
    spec1: standPipeSpecName,
    spec2: '',
    spec3: '',
    itemunit: '4m',
    matamount: Math.ceil((data.NozzleAmt * data.StandPipeLength)/4), // 每4m計價
    description: '豎管材料(4m計價)',
    order: 1,
    group: groupId
  });

  // 豎管三通
  addMaterial(materials, 2, `${branchSpecName}×${standPipeSpecName}`, '', '三通', {
    module: '豎管配件',
    matname: '三通',
    module_id: 2,
    mattype: 'PVC',
    spec1: `${branchSpecName}×${standPipeSpecName}`,
    spec2: '',
    spec3: '',
    itemunit: '個',
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
    itemunit: '個',
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
    itemunit: '個',
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

// 生成固定設施組材料 (獨立分組)
const generateFixedFacilitiesGroup = (data: any) => {
  const materials = generateFixedFacilities(data, 6);
  return {
    GroupNo: 6,
    GroupName: '固定設施組',
    List: materials
  };
};

// 生成固定設施材料
const generateFixedFacilities = (data: any, groupId: number) => {
  const materials = [];

  addMaterial(materials, 11, '支架用', '', '鍍鋅鋼管', {
    module: '固定設施',
    matname: '鍍鋅鋼管',
    module_id: 11,
    mattype: '鋼管',
    spec1: '支架用',
    spec2: '',
    spec3: '',
    itemunit: '支',
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
  const materials = [];

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
    itemunit: '個',
    matprice: sprinklerMatch.matprice,
    matamount: Math.floor(data.NozzleAmt), // 配件用無條件捨去
    description: '末端噴灑裝置',
    order: 1,
    group: groupId,
    debugMatchData: sprinklerMatch.matchedData
  });

  return materials;
};

// 生成噴頭變更系統材料 (規格變更)
const generateNozzleChangeSystem = (data: any, mainPipeSpec: any) => {
  // 基本上與generateNozzleSystem相同，但會處理規格變更
  // 這裡簡化實現，實際應該根據ChangeBranchSpec處理新舊規格
  return generateNozzleSystem(data, mainPipeSpec);
};

// 生成微噴系統材料
const generateMicroSprinklerSystem = (data: any, mainPipeSpec: any) => {
  const materials = [];

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
  const materials = [];

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
    itemunit: '個',
    matprice: microSprinklerMatch.matprice,
    matamount: Math.floor(data.NozzleAmt), // 配件用無條件捨去
    description: '微噴頭裝置',
    order: 1,
    group: groupId,
    debugMatchData: microSprinklerMatch.matchedData
  });

  return materials;
};

// 生成微噴變更系統材料
const generateMicroSprinklerChangeSystem = (data: any, mainPipeSpec: any) => {
  // 與generateMicroSprinklerSystem相同，但處理規格變更
  return generateMicroSprinklerSystem(data, mainPipeSpec);
};

// 生成滴灌系統材料 (滴嘴)
const generateDripIrrigationSystem = (data: any, mainPipeSpec: any) => {
  const materials = [];
  const branchMaterialName = pipeMaterialOptions.value.find(m => m.id === data.BranchMaterial)?.name || 'PE管';
  const branchSpecName = pipeDiameterOptions.value.find(d => d.id === data.BranchSpec)?.name || '16mm';
  const mainSpecName = pipeDiameterOptions.value.find(d => d.id === mainPipeSpec)?.name || '1"';

  // 滴灌管
  addMaterial(materials, 12, branchSpecName, branchMaterialName, '', {
    module: '滴灌管',
    matname: `滴灌管 ${branchSpecName}`,
    module_id: 12,
    mattype: branchMaterialName,
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: 'm',
    matamount: Math.ceil(data.BranchAmt * data.width), // 管材用無條件進位
    description: '滴灌管材',
    order: 1,
    group: 4
  });

  // 三通
  const dripTeeSpec = `${mainSpecName}×${branchSpecName}`;
  addMaterial(materials, 2, dripTeeSpec, '', '三通', {
    module: '滴灌配件',
    matname: '三通',
    module_id: 2,
    mattype: 'PVC',
    spec1: dripTeeSpec,
    spec2: '',
    spec3: '',
    itemunit: '個',
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
    itemunit: '個',
    matamount: Math.floor(data.BranchAmt * 2),
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
    itemunit: '個',
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
  const materials = [];

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
    itemunit: '個',
    matprice: dripperMatch.matprice,
    matamount: Math.floor(data.NozzleAmt),
    description: '滴灌滴嘴',
    order: 1,
    group: 8,
    debugMatchData: dripperMatch.matchedData
  });

  return {
    GroupNo: 8,
    GroupName: '末端設施',
    List: materials
  };
};

// 生成滴水管系統材料
const generateDripPipeIrrigationSystem = (data: any, mainPipeSpec: any) => {
  const materials = [];
  const branchSpecName = pipeDiameterOptions.value.find(d => d.id === data.BranchSpec)?.name || '16mm';
  const mainSpecName = pipeDiameterOptions.value.find(d => d.id === mainPipeSpec)?.name || '1"';

  // 滴水帶 - 管材用無條件進位
  addMaterial(materials, 12, branchSpecName, 'PE', '', {
    module: '滴水帶',
    matname: `滴水帶 ${branchSpecName}`,
    module_id: 12,
    mattype: 'PE',
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: 'm',
    matamount: Math.ceil(data.BranchAmt * data.width), // 管材用無條件進位
    description: '滴水帶材料',
    order: 1,
    group: 4
  });

  // 三通 - 配件用無條件捨去
  const dripTapeTeeSpec = `${mainSpecName}×${branchSpecName}`;
  addMaterial(materials, 2, dripTapeTeeSpec, '', '三通', {
    module: '滴水帶配件',
    matname: '三通',
    module_id: 2,
    mattype: 'PVC',
    spec1: dripTapeTeeSpec,
    spec2: '',
    spec3: '',
    itemunit: '個',
    matamount: Math.floor(data.BranchAmt),
    description: '主管轉滴水帶三通',
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
    module: '滴水帶配件',
    matname: '管首接頭',
    module_id: 2,
    mattype: 'PE',
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: '個',
    matamount: Math.floor(data.BranchAmt * 2),
    description: '滴水帶首端接頭',
    order: 3,
    group: 4
  });

  // 管尾束 - 配件用無條件捨去
  addMaterial(materials, 2, branchSpecName, '', '管尾束', {
    module: '滴水帶配件',
    matname: '管尾束',
    module_id: 2,
    mattype: 'PE',
    spec1: branchSpecName,
    spec2: '',
    spec3: '',
    itemunit: '個',
    matamount: Math.floor(data.BranchAmt),
    description: '滴水帶末端束扣',
    order: 4,
    group: 4
  });

  return {
    GroupNo: 4,
    GroupName: '滴水帶系統組',
    List: materials
  };
};

// 初始化數據
// onMounted(async () => {
//   await loadDropdownOptions(); // 載入下拉選單數據

//   if (props.formData) {
//     Object.keys(localFormData).forEach(key => {
//       if (props.formData[key] !== undefined) {
//         localFormData[key] = props.formData[key];
//       }
//     });
//   }

//   // console.log('🔄 step4.vue onMounted - props.formData:', props.formData);
//   // console.log('🔄 step4.vue onMounted - localFormData before loading:', JSON.stringify(localFormData, null, 2));

//   // 如果 props.formData 有資料就載入，否則等 watch 觸發
//   if (props.formData && Object.keys(props.formData).length > 0) {
//     // console.log('📥 Loading data in onMounted');
//     // loadDataFromProps(props.formData);
//   } else {
//     // console.log('⏰ No data in props.formData, waiting for watch to trigger');
//   }
//   // Load step 2 data if not already present in store to ensure facilityArea is available
//   // This might be redundant if edit.vue preloads all relevant steps, but good for robustness
//   if (!grantsStore.formData[2]?.facilityArea && grantsStore.currentGrant?.case_number) {
//     await grantsStore.loadStepData(grantsStore.currentGrant.case_number, 2);
//   }

//   // 最終 facilityArea 處理：如果沒有載入到值，使用預設值
//   if (!localFormData.facilityArea || localFormData.facilityArea === 0 || localFormData.facilityArea === '0') {
//     const step2FacilityArea = grantsStore.formData[2]?.facilityArea;
//     if (step2FacilityArea !== undefined) {
//       localFormData.facilityArea = parseFloat(step2FacilityArea) || 0;
//       // console.log("Final: Using facilityArea from Step 2 data:", localFormData.facilityArea);
//     } else {
//       // localFormData.facilityArea = 10000;
//       // console.log("Final: facilityArea not found, using default:", localFormData.facilityArea);
//     }
//   }
//   calculateWidth(); // Ensure width is calculated with the correct facilityArea

//   // 如果有管路設施，計算補助金額
//   if(localFormData.pipes && localFormData.pipes.length > 0){
//       await calculateSubsidy();
//   }

//   updateFormData(); // Emit initial data
// });

// 統一的資料載入函數
const loadDataFromProps = (propsData: any) => {
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

  let loadedCount = 0;
  Object.keys(localFormData).forEach(key => {
    if (propsData[key] !== undefined) {
      const oldValue = localFormData[key];
      let newValue = propsData[key];

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
};

onMounted(async () => {
  isUpdating.value = true;

  if (grantsStore.currentStep !== 4) {
    console.warn(`⚠️ Step4 component mounted but currentStep is ${grantsStore.currentStep}, not 4`)
    // 可以發出事件通知父組件，但不直接修改
    // emit('step-mismatch', { expected: 4, actual: grantsStore.currentStep })
  }

  await loadDropdownOptions();

  console.log('🔄 step4.vue onMounted - props.formData:', props.formData);

  // 1. 先從 props.formData 載入所有數據（包含 localStorage 數據）
  if (props.formData && Object.keys(props.formData).length > 0) {
    console.log('📥 Loading data from props.formData in onMounted');
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
  if (!grantsStore.formData[2]?.totalFacilityArea && grantsStore.currentGrant?.case_number) {
    await grantsStore.loadStepData(grantsStore.currentGrant.case_number, 2);
  }

  // 🔧 Linus式修正：不再需要手動設置 facilityArea，已改為 computed
  // facilityAreaFromStep2 會自動從 Step2 資料計算，無需初始化
  console.log("📊 step4.vue: facilityAreaFromStep2 computed will handle Step2 sync automatically");

  calculateWidth();

  // 4. 確保主管材質有預設值
  ensureDefaultMaterials();

  // 5. 如果有灌溉型式，載入末端設施選項
  if (localFormData.irrigationTypeId) {
    // console.log('🔄 Loading end facility options in onMounted');
    await loadEndFacilityOptions();
  }

  // 如果有管路設施，計算補助金額
  if (localFormData.pipes && localFormData.pipes.length > 0) {
    await calculateSubsidy();
  }

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
    isUpdating.value = true;
    loadDataFromProps(newVal);
    isUpdating.value = false;
  }
}, { deep: true });

// 修改本地數據的 watch，添加防護
watch(localFormData, () => {
  if (!isUpdating.value) {
    updateFormData();
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

// 手動新增材料相關方法
const openManualAddDialog = () => {
  showManualAddDialog.value = true;
  // 重置表單
  selectedMaterialPomno.value = null;
  selectedGroup.value = null;
  materialQuantity.value = 1;
  materialSearchQuery.value = '';
};

const closeManualAddDialog = () => {
  showManualAddDialog.value = false;
};

const onMaterialSearch = (query: string) => {
  materialSearchQuery.value = query;
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
      itemunit: selectedMaterial.value.unit || '個',
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
}

.v-card-title {
  color: rgba(0, 0, 0, 0.87);
  font-size: 1.25rem;
  font-weight: 500;
  padding: 16px;
}

.bg-light-blue-lighten-4 {
  background-color: #B3E5FC !important;
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
  padding: 15px;
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
