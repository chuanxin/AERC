<template>
  <div ref="stepContent" class="step-content">
    <v-card class="mb-0 pa-0" flat>
      <v-card-text class="pb-0 pt-0">
        <v-form ref="form" v-model="localValid" @submit.prevent>
          <!-- STEP 1: 補助來源選擇 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-hand-coin</v-icon>
              <span class="text-subtitle-1 font-weight-medium">補助來源</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <v-select
                  v-model="localFormData.fundingSourceId"
                  :items="fundingSourceOptions"
                  item-title="name"
                  item-value="id"
                  label="補助單位"
                  variant="outlined"
                  density="comfortable"
                  style="max-width: 400px"
                  :rules="[v => (v !== null && v !== undefined) || '請選擇補助單位']"
                  @update:model-value="updateFormData"
                />
              </v-sheet>
            </v-card-text>
          </v-card>

          <!-- STEP 2: 坵塊形狀長度調整 -->
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-land-fields</v-icon>
              <span class="text-subtitle-1 font-weight-medium">田間坵塊</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <div class="d-flex flex-wrap align-center mb-4">
                  <div class="d-flex align-center flex-wrap me-4 mb-2">
                    <div class="text-body-2 me-2">坵塊形狀:</div>
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
                    <div class="text-body-2 me-2">施設面積:</div>
                    <v-text-field
                      v-model.number="localFormData.facilityArea"
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
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-pipe</v-icon>
              <span class="text-subtitle-1 font-weight-medium">田間主管配置</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <!-- 主管1 -->
                <div class="text-subtitle-2 mb-1">主管 1（L1）</div>
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
                    <template v-slot:item="{ props, item }">
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
                    <template v-slot:item="{ props, item }">
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
                <div v-if="localFormData.mainPipe2Enabled" class="d-flex align-center flex-wrap mt-1">
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
                    <template v-slot:item="{ props, item }">
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
                    <template v-slot:item="{ props, item }">
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
          <v-card class="mb-4" variant="outlined">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-sprinkler</v-icon>
              <span class="text-subtitle-1 font-weight-medium">灌溉管路配置</span>
            </v-card-title>

            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
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
                <div v-if="localFormData.irrigationTypeId === 1" class="irrigation-type-config">
                  <v-divider class="mb-3"></v-divider>
                  <div class="text-subtitle-2 mb-3">穿孔管系統配置</div>

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
                      <div class="text-body-2 mb-1">支管行距(SL)</div>
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
                      <template v-slot:item="{ props, item }">
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
                <div v-else-if="localFormData.irrigationTypeId === 2" class="irrigation-type-config">
                  <v-divider class="mb-3"></v-divider>
                  <div class="text-subtitle-2 mb-3">噴頭式系統配置</div>

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
                      <div class="text-body-2 mb-1">支管行距(SL)</div>
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
                      <div class="text-body-2 mb-1">噴頭間距(SS)</div>
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
                      <template v-slot:item="{ props, item }">
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
                      <div class="text-body-2 mb-1">豎管高度(H)</div>
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
                <div v-else-if="localFormData.irrigationTypeId === 3" class="irrigation-type-config">
                  <v-divider class="mb-3"></v-divider>
                  <div class="text-subtitle-2 mb-3">微噴系統配置</div>

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
                      <div class="text-body-2 mb-1">支管行距(SL)</div>
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
                      <div class="text-body-2 mb-1">噴頭間距(SS)</div>
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
                      <template v-slot:item="{ props, item }">
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
                      <div class="text-body-2 mb-1">豎管高度(H)</div>
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
                <div v-else-if="localFormData.irrigationTypeId === 4" class="irrigation-type-config">
                  <v-divider class="mb-3"></v-divider>
                  <div class="text-subtitle-2 mb-3">滴灌系統配置</div>

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
                      <div class="text-body-2 mb-1">支管行距(SL)</div>
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
                      <div class="text-body-2 mb-1">噴頭間距(SS)</div>
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
                      <template v-slot:item="{ props, item }">
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
          <v-card variant="outlined" class="mb-4">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-format-list-bulleted</v-icon>
              <span class="text-subtitle-1 font-weight-medium">管路設施列表</span>
            </v-card-title>
            <v-card-text class="pa-4">
              <v-sheet class="pa-3 rounded" color="grey-lighten-5">
                <v-btn
                  color="success"
                  class="mb-2"
                  :loading="isLoadingMaterials"
                  :disabled="!canAutoFillMaterials"
                  block
                  @click="autoFillMaterials"
                >
                  <v-icon start size="small">mdi-autorenew</v-icon>
                  自動帶入材料
                </v-btn>
              </v-sheet>
            </v-card-text>

            <v-card-text class="pa-4">
              <v-table class="rounded border">
                <thead class="bg-grey-lighten-3">
                  <tr>
                    <th class="text-center" style="width: 80px">項目</th>
                    <th class="text-center" style="width: 100px">群組</th>
                    <th>名稱</th>
                    <th>類別</th>
                    <th>規格</th>
                    <th>單位</th>
                    <th>說明</th>
                    <th class="text-center">單價</th>
                    <th class="text-center">數量</th>
                    <th class="text-center">總價</th>
                    <th class="text-center" style="width: 50px">排序</th>
                    <th class="text-center" style="width: 80px">刪除</th>
                  </tr>
                </thead>
                <tbody>
                  <template v-for="(group, groupIndex) in groupedPipes" :key="`group-${group.groupNo}`">
                    <tr class="bg-grey-lighten-5">
                      <td colspan="12" class="py-2 px-4 font-weight-bold">
                        {{ groupIndex + 1 }}. {{ group.groupName }}
                      </td>
                    </tr>
                    <tr v-for="(pipe, pipeIndex) in group.items" :key="`pipe-${group.groupNo}-${pipe.pomno}-${pipeIndex}`">
                      <td class="text-center">{{ groupIndex + 1 }}-{{ pipe.order }}</td>
                      <td class="text-center">{{ group.groupName }}</td>
                      <td>{{ pipe.matname }}</td>
                      <td>{{ pipe.module }}</td>
                      <td>{{ pipe.specification }}</td>
                      <td>{{ pipe.itemunit }}</td>
                      <td>{{ pipe.description }}</td>
                      <td class="text-center">{{ pipe.matprice?.toLocaleString() }}</td>
                      <td class="text-center">{{ pipe.matamount }}</td>
                      <td class="text-center">{{ pipe.totalPrice?.toLocaleString() }}</td>
                      <td class="text-center">
                        <div class="d-flex flex-column align-center">
                          <v-btn
                            icon
                            size="x-small"
                            color="primary"
                            variant="text"
                            :disabled="pipeIndex === 0"
                            @click="movePipeUp(group.groupNo, pipeIndex)"
                          >
                            <v-icon size="small">mdi-chevron-up</v-icon>
                          </v-btn>
                          <v-btn
                            icon
                            size="x-small"
                            color="primary"
                            variant="text"
                            :disabled="pipeIndex === group.items.length - 1"
                            @click="movePipeDown(group.groupNo, pipeIndex)"
                          >
                            <v-icon size="small">mdi-chevron-down</v-icon>
                          </v-btn>
                        </div>
                      </td>
                      <td class="text-center">
                        <v-btn
                          icon
                          size="x-small"
                          color="error"
                          variant="text"
                          @click="removePipe(group.groupNo, pipeIndex)"
                        >
                          <v-icon>mdi-close</v-icon>
                        </v-btn>
                      </td>
                    </tr>
                  </template>

                  <tr v-if="localFormData.pipes.length === 0">
                    <td colspan="12" class="text-center py-3 text-grey">
                      點擊「自動帶入材料」或手動新增管路設施
                    </td>
                  </tr>
                  <tr class="text-muted text-caption bg-grey-lighten-4">
                    <td colspan="9" class="text-right font-weight-bold">合計</td>
                    <td class="text-center font-weight-bold">{{ totalPipesPrice }}</td>
                    <td colspan="2"></td>
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>

          <!-- 補助計算結果 -->
          <v-card variant="outlined" class="mt-4">
            <v-card-title class="bg-light-blue-lighten-4 d-flex align-center py-2 px-4">
              <v-icon class="me-2" size="small">mdi-calculator</v-icon>
              <span class="text-subtitle-1 font-weight-medium">補助計算結果</span>
            </v-card-title>
            <v-card-text class="pa-4">
              <v-table class="rounded border" style="max-width: 600px">
                <thead class="bg-grey-lighten-3">
                  <tr>
                    <th>項目</th>
                    <th class="text-center">金額(NT$)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>總經費</td>
                    <td class="text-center">{{ subsidyTotalAmount }}</td>
                  </tr>
                  <tr>
                    <td>政府補助</td>
                    <td class="text-center text-success font-weight-bold">{{ subsidyAmount }}</td>
                  </tr>
                  <tr>
                    <td>農民自付</td>
                    <td class="text-center text-warning font-weight-bold">{{ farmerSelfAmount }}</td>
                  </tr>
                </tbody>
              </v-table>
              <v-btn
                color="primary"
                class="mt-4"
                :loading="isCalculatingSubsidy"
                @click="calculateSubsidy"
                :disabled="localFormData.pipes.length === 0"
              >
                計算輔助金額
              </v-btn>
            </v-card-text>
          </v-card>
        </v-form>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { useGrantsStore } from '@/stores/grants';
import { useOfficesStore } from '@/stores/offices'
import { usePipeFittingsStore } from '@/stores/pipeFittingsStore'
import { usePFDiametersStore } from '@/stores/pfDiametersStore'
import { usePFMaterialsStore } from '@/stores/pfMaterialsStore'
import { useIrrigationTypesStore } from '@/stores/irrigationTypesStore'


interface PipeOption {
  id: number | string; // 或者後端期望的類型
  name: string;
  // 其他可能需要的屬性，例如管材的標準長度
  standardLength?: number;
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
  // 新增上下文 ID
  mapNo: { // 對應舊 MapNo，可能是案件 ID
    type: Number,
    required: true // 或 false，取決於您的流程
  },
  operatingUnitId: { // 對應舊 Session["UnitID"]
    type: Number,
    required: true // 或 false
  }
});

const emit = defineEmits(['update:formData', 'validated', 'go-back']);

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
const isCalculatingSubsidy = ref(false);

// 本地表單數據
const localFormData = reactive({
  // 栅塊形狀和面積
  fieldLength: '100',
  fieldWidth: '100',
  facilityArea: '1000',

  // 補助來源
  fundingSourceId: null as number | null, // 存儲ID

  // 主管
  mainPipeLength: null as number | null,
  mainPipeDiameterId: null as number | null, // 管徑ID
  mainPipeMaterialId: null as number | null, // 材質ID
  mainPipeUnitPrice: null as number | null,
  mainPipeQuantity: null as number | null,
  mainPipeStandardLength: 4, // 主管1的標準長度，應動態獲取

  //主管2
  mainPipe2Enabled: false,
  mainPipe2Length: null as number | null,
  mainPipe2DiameterId: null as number | null,
  mainPipe2MaterialId: null as number | null,
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

  variantType: '',
  branchPipeLength: '',
  branchPipeDiameter: '',
  branchPipeMaterial: '',
  branchPipeUnitPrice: '',
  branchPipeQuantity: '',

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

  // Load diameters and materials reference data
  await pfDiametersStore.fetchDiameters();
  await pfMaterialsStore.fetchMaterials();

  // Load pipe fittings filtered by module_id=1 (main pipe) and current office
  await fetchPipeFittings();

  await irrigationTypesStore.fetchIrrigationTypeOptions()

  // 模擬設施型式和水源選項
  facilityTypeOptions.value = [ {id: 1, name: '埋設固定式'}, {id: 2, name: '地表定置式'}, {id: 3, name: '附掛棚架式'}];
  waterSourceOptions.value = [ {id:1, name: '灌溉渠道'}, {id:2, name: '野溪'} /* ... */];
};

const pipeDiameterOptions = computed(() => {
  // 使用主管模塊的管件來提取管徑選項
  const mainPipeFittings = filteredPipeFittingsByModule.value.mainPipe || [];

  // 获取材质-管径组合的有效选项 (有价格的组合)
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
const convertToSelectOptions = (fittings) => {
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

const getFilteredDiameterOptions = (currentMaterialId) => {
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

const getFilteredMaterialOptions = (currentDiameterId) => {
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

  const result = {};

  // 針對每種模塊類型創建過濾後的列表
  Object.entries(moduleFilters).forEach(([key, moduleId]) => {
    result[key] = pipeFittingsStore.pipeFittings.filter(
      fitting => fitting.module_id === moduleId
    );
  });

  return result;
});

const fundingSourceOptions = computed(() => {
  // console.log('Computing fundingSourceOptions, offices:', officesStore.offices)
  // console.log('Offices length:', officesStore.offices.length)

  const filtered = officesStore.offices
    .filter(office => {
      // console.log('Office:', office.name, 'is_funding_source:', office.is_funding_source)
      return office.is_funding_source === true
    })
    .map(office => ({
      id: office.id,
      name: office.name
    }))

  // console.log('Filtered funding sources:', filtered)
  return filtered
});

// 根據灌溉類型篩選末端設施選項
const filteredEndFacilityOptions = computed(() => {
  if (!localFormData.irrigationType) return [];
  return endFacilityOptions
    .filter(option => option.irrigationType === localFormData.irrigationType)
    .map(option => option.value);
});

// 是否顯示末端設施類型選擇
const showEndFacilityType = computed(() => {
  return ['穿孔管系統', '噴頭式系統', '滴灌系統'].includes(localFormData.irrigationType);
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
  // const groups = {};
  const groups: Record<number, { groupNo: number; groupName: string; items: any[] }> = {};

  // 找出所有群組ID
  const groupIds = [...new Set(localFormData.pipes.map(pipe => pipe.groupId))];

  // 定義群組名稱
  const groupNames = {
    1: '主管配件',
    2: '支管配件',
    3: '末端設施',
    4: '閥件',
    5: '集水槽',
    6: '控制系統',
    7: '雜項',
  };

  const groupNameMapping: Record<number, string> = {
    1: '主管路組',
    2: '支管路組',
    3: '穿孔管組', // 穿孔管末端
    4: '滴灌組',   // 滴灌末端
    5: '豎管組',
    6: '固定設施組',
    7: '消耗性材料',
    8: '噴頭/微噴/滴嘴組' // 各類末端頭
    // ... 其他組別根據後端 MaterialModule.cs 中的 StdMat.Group 設定
  };

  // 為每個群組建立條目
  groupIds.forEach(groupId => {
    const items = localFormData.pipes.filter(pipe => pipe.groupId === groupId);
    if (items.length > 0) {
      groups[groupId] = {
        id: groupId,
        name: groupNames[groupId] || `群組 ${groupId}`,
        items: items
      };
    }
  });

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
  // 按 GroupNo 排序
  return Object.values(groups).sort((a, b) => a.groupNo - b.groupNo);

  // 返回排序後的群組陣列
  // return Object.values(groups).sort((a, b) => a.id - b.id);
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

// 驗證條件
const canAutoFillMaterials = computed(() => {
  return (
    !!localFormData.fieldLength &&
    !!localFormData.fieldWidth &&
    (localFormData.fundingSourceId !== null) && // 使用ID
    !!localFormData.irrigationTypeId && // 使用ID
    !!localFormData.facilityTypeId &&   // 使用ID
    (localFormData.mainPipeLength !== null) &&
    !!localFormData.mainPipeMaterialId && // 使用ID
    (localFormData.branchPipeSpacing_SL !== null) &&
    (localFormData.sprinklerSpacing_SS !== null)
  );
});

const calculateWidth = () => {
  const length = localFormData.fieldLength || 0;
  const area = localFormData.facilityArea || 0;
  if (length > 0 && area > 0) {
    localFormData.fieldWidth = Math.round(area / length);
  }
  // updateFormData();
};

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
    console.log(`Fetched all pipe fittings for office_id: ${officeId}`);
    // Store the filtered pipe fittings
    // filteredPipeFittings.value = pipeFittingsStore.pipeFittings;
    // console.log(`Fetched ${filteredPipeFittings.value.length} pipe fittings for office_id: ${officeId}`);
  } catch (error) {
    console.error('Error fetching pipe fittings:', error);
  }
};

const getStandardPipeLength = async (materialId: number | null, diameterId: number | null, moduleId: number = 1): Promise<number> => {
  if (!materialId || !diameterId) return 4; // 預設長度
  // 從 pipeFittingsStore 中尋找匹配的管件
  const matchingPipe = pipeFittingsStore.pipeFittings.find(pipe =>
      pipe.material_id === materialId &&
      pipe.diameter1_id === diameterId &&
      pipe.module_id === moduleId
  );

  // 如果找到匹配的管件且有 length 屬性，返回該長度值
  if (matchingPipe && matchingPipe.length) {
      console.log(`Found matching pipe with length: ${matchingPipe.length} for materialId=${materialId}, diameterId=${diameterId}, moduleId=${moduleId}`);
      return matchingPipe.length;
  }

  // 未找到匹配的管件，返回預設長度
  console.warn(`No matching pipe found for materialId=${materialId}, diameterId=${diameterId}, moduleId=${moduleId}, using default length: 4`);
  return 4;
};

// 計算主管數量（根據長度）
const calculateMainPipeQuantity = async () => {
  const length = localFormData.mainPipeLength || 0;
  if (length > 0) {
    const standardLength = await getStandardPipeLength(
        localFormData.mainPipeMaterialId,
        localFormData.mainPipeDiameterId,
        1 // module_id=1 for main pipe
    );
    localFormData.mainPipeStandardLength = standardLength;
    localFormData.mainPipeQuantity = Math.ceil(length / standardLength);
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
    localFormData.mainPipe2Quantity = Math.ceil(length / standardLength);
  }
  updateFormData();
};

const toggleMainPipe2 = () => {
  if (!localFormData.mainPipe2Enabled) {
    localFormData.mainPipe2Length = null;
    localFormData.mainPipe2DiameterId = null;
    localFormData.mainPipe2MaterialId = null;
    localFormData.mainPipe2UnitPrice = null;
    localFormData.mainPipe2Quantity = null;
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

    // 暫時移除自動填充末端設施數量，此數量應由後端計算更佳
    // if (localFormData.irrigationTypeId === 2 ||  // 噴頭
    //     localFormData.irrigationTypeId === 3 ||  // 微噴
    //     localFormData.irrigationTypeId === 4 && localFormData.dripperSubtypeId === 7 // 滴嘴
    // ) {
    //   // localFormData.endFacilityQuantity = totalSprinklers; // 數量應由後端計算並返回
    // }
  }
  updateFormData();
};


// 灌溉類型變更
const onIrrigationTypeChange = async () => {
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
  await loadEndFacilityOptions(); // 重新載入與當前規格匹配的末端設施選項
};

const loadEndFacilityOptions = async () => {
  // TODO: API Call to fetch end facility options (pipe_fittings)
  // based on irrigationTypeId, sprinklerSubtypeId, dripperSubtypeId, facilityTypeId, operating_unit_id
  // This API should return a list of objects like EndFacilityPipeFitting interface
  // Example: filteredEndFacilityPipeFittings.value = await pipeFittingsService.getTerminalFittings({ type: localFormData.irrigationTypeId, ... });
  // 根據灌溉類型和末端設施規格篩選末端設施選項
  const irrigationTypeId = localFormData.irrigationTypeId;
  const dripperSubtypeId = localFormData.dripperSubtypeId;
  const endFacilitySpecId = localFormData.endFacilitySpecId;

  let fittings = [];

  console.log(`loadEndFacilityOptions: irrigationTypeId=${irrigationTypeId}, dripperSubtypeId=${dripperSubtypeId}`);

  if (irrigationTypeId === 1) {
    // 穿孔管系統
    fittings = filteredPipeFittingsByModule.value.perforatedPipe || [];
    console.log(`Using perforatedPipe fittings, count: ${fittings.length}`);
  }
  else if (irrigationTypeId === 2 || localFormData.sprinklerSubtypeId === 6) {
    // 噴頭式系統
    fittings = filteredPipeFittingsByModule.value.sprinkler || [];
    console.log(`Using sprinkler fittings, count: ${fittings.length}`);
  }
  else if (irrigationTypeId === 3) {
    // 微噴系統
    fittings = filteredPipeFittingsByModule.value.microSprinkler || [];
    console.log(`Using microSprinkler fittings, count: ${fittings.length}`);
  }
  else if (irrigationTypeId === 4) { // 滴灌系統
    if (dripperSubtypeId === 8) {
      // 滴水管滴灌系統
      fittings = filteredPipeFittingsByModule.value.pipeDrip || [];
      console.log(`Using pipeDrip fittings for drip pipe system, count: ${fittings.length}`);
    } else {
      // 默認使用滴嘴系統 (dripperSubtypeId === 7 或未設置)
      fittings = filteredPipeFittingsByModule.value.nozzleDrip || [];
      console.log(`Using nozzleDrip fittings for drip nozzle system, count: ${fittings.length}`);
    }
  }


  // 根據選擇的規格進一步篩選
  if (endFacilitySpecId) {
    fittings = fittings.filter(f => f.diameter1_id === endFacilitySpecId);
  }

  // 轉換為末端設施選項格式
  filteredEndFacilityPipeFittings.value = fittings.map(fitting => ({
    pomno: fitting.pomno,
    displayName: fitting.name || `${fitting.material_name || ''} ${fitting.diameter1_name || ''}`.trim(),
    materialName: fitting.material.name || '',
    specName: fitting.diameter1_name || '',
    specId: fitting.diameter1_id
  }));

  console.log(`已載入 ${filteredEndFacilityPipeFittings.value.length} 個末端設施選項`);
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
    console.log(`Workspaceing pipe ${pipeNumber} price for: materialId=${materialId}, diameterId=${diameterId}`);
     // 從 filteredPipeFittingsByModule 中篩選出主管類型的管件
    const mainPipeFittings = filteredPipeFittingsByModule.value.mainPipe || [];

    // 進一步篩選符合 materialId 和 diameterId 的管件
    const matchingPipe = mainPipeFittings.find(pipe =>
      pipe.material_id === materialId &&
      pipe.diameter1_id === diameterId
    );

    if (matchingPipe) {
      console.log(`Found matching pipe: ${matchingPipe.name}, price: ${matchingPipe.current_price}, length: ${matchingPipe.length}`);

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

      // 未找到匹配的管件，使用預設值
      // const defaultPrice = Math.floor(Math.random() * 100) + 50; // 預設隨機價格
      // const standardLength = pipeDiameterOptions.value.find(opt => opt.id === diameterId)?.standardLength || 4;

      if (pipeNumber === 1) {
        localFormData.mainPipeUnitPrice = 0;
        // localFormData.mainPipeStandardLength = standardLength;
        await calculateMainPipeQuantity();
      } else {
        localFormData.mainPipe2UnitPrice = 0;
        // localFormData.mainPipe2StandardLength = standardLength;
        await calculateMainPipe2Quantity();
      }

      // console.log(`Using default price: ${defaultPrice} and standard length: ${standardLength}`);
    }
  } catch (error) {
    console.error(`Error fetching pipe ${pipeNumber} price:`, error);
  }
  updateFormData();
};


// 獲取支管價格
const fetchBranchPipePrice = async () => {
  if (!localFormData.branchPipeMaterial || !localFormData.branchPipeDiameter) return;

  try {
    // 模擬API調用獲取價格
    console.log('Fetching branch pipe price for:', localFormData.branchPipeMaterial, localFormData.branchPipeDiameter);

    // 模擬延遲
    await new Promise(resolve => setTimeout(resolve, 300));

    // 模擬價格
    const price = Math.floor(Math.random() * 80) + 40;
    localFormData.branchPipeUnitPrice = price.toString();

    updateFormData();
  } catch (error) {
    console.error('Error fetching branch pipe price:', error);
  }
};

// 獲取末端設施價格
const fetchEndFacilityPrice = async () => {
  if (!localFormData.endFacilityType || !localFormData.endFacilityDiameter) return;

  try {
    // 模擬API調用獲取價格
    console.log('Fetching end facility price for:', localFormData.endFacilityType, localFormData.endFacilityDiameter);

    // 模擬延遲
    await new Promise(resolve => setTimeout(resolve, 300));

    // 模擬價格
    const price = Math.floor(Math.random() * 60) + 30;
    localFormData.endFacilityUnitPrice = price.toString();

    updateFormData();
  } catch (error) {
    console.error('Error fetching end facility price:', error);
  }
};

// 添加主管
const addMainPipe = () => {
  if (canAddMainPipe.value) {
    const length = parseFloat(localFormData.mainPipeLength);
    const unitPrice = parseFloat(localFormData.mainPipeUnitPrice);
    const quantity = parseFloat(localFormData.mainPipeQuantity);

    localFormData.pipes.push({
      groupId: 1, // 主管配件組
      moduleType: '主管',
      name: `${localFormData.mainPipeMaterial} ${localFormData.mainPipeDiameter}`,
      specification: `${localFormData.mainPipeDiameter}`,
      unit: '支',
      description: `主管管線(${localFormData.mainPipeMaterial})`,
      unitPrice: unitPrice,
      quantity: quantity,
      totalPrice: Math.round(unitPrice * quantity)
    });

    // 保留補助來源，清空其他欄位
    const fundingSource = localFormData.fundingSource;
    localFormData.mainPipeLength = '';
    localFormData.mainPipeDiameter = '';
    localFormData.mainPipeMaterial = '';
    localFormData.mainPipeUnitPrice = '';
    localFormData.mainPipeQuantity = '';
    localFormData.fundingSource = fundingSource;

    updateFormData();
  }
};

// 添加支管
const addBranchPipe = () => {
  if (canAddBranchPipe.value) {
    const length = parseFloat(localFormData.branchPipeLength);
    const unitPrice = parseFloat(localFormData.branchPipeUnitPrice);
    const quantity = parseFloat(localFormData.branchPipeQuantity);

    localFormData.pipes.push({
      groupId: 2, // 支管配件組
      moduleType: '支管',
      name: `${localFormData.branchPipeMaterial} ${localFormData.branchPipeDiameter}`,
      specification: `${localFormData.branchPipeDiameter}`,
      unit: '支',
      description: `支管管線(${localFormData.branchPipeMaterial})`,
      unitPrice: unitPrice,
      quantity: quantity,
      totalPrice: Math.round(unitPrice * quantity)
    });

    // 保留部分欄位，清空其他欄位
    const fundingSource = localFormData.fundingSource;
    const branchPipeSpacing = localFormData.branchPipeSpacing;
    const sprinklerSpacing = localFormData.sprinklerSpacing;
    const riserHeight = localFormData.riserHeight;
    const variantType = localFormData.variantType;

    localFormData.branchPipeLength = '';
    localFormData.branchPipeDiameter = '';
    localFormData.branchPipeMaterial = '';
    localFormData.branchPipeUnitPrice = '';
    localFormData.branchPipeQuantity = '';

    localFormData.fundingSource = fundingSource;
    localFormData.branchPipeSpacing = branchPipeSpacing;
    localFormData.sprinklerSpacing = sprinklerSpacing;
    localFormData.riserHeight = riserHeight;
    localFormData.variantType = variantType;

    updateFormData();
  }
};

// 添加末端設施
const addEndFacility = () => {
  if (canAddEndFacility.value) {
    const unitPrice = parseFloat(localFormData.endFacilityUnitPrice);
    const quantity = parseFloat(localFormData.endFacilityQuantity);

    localFormData.pipes.push({
      groupId: 3, // 末端設施組
      moduleType: '末端設施',
      name: localFormData.endFacilityType,
      specification: `${localFormData.endFacilityDiameter}`,
      unit: '個',
      description: `${localFormData.endFacilityType}(${localFormData.endFacilityMaterial})`,
      unitPrice: unitPrice,
      quantity: quantity,
      totalPrice: Math.round(unitPrice * quantity)
    });

    // 保留部分欄位，清空其他欄位
    const fundingSource = localFormData.fundingSource;
    const irrigationType = localFormData.irrigationType;
    const installationType = localFormData.installationType;
    const waterSource = localFormData.waterSource;
    const perforatedPipeType = localFormData.perforatedPipeType;
    const sprinklerType = localFormData.sprinklerType;
    const dripperType = localFormData.dripperType;

    localFormData.endFacilityType = '';
    localFormData.endFacilityDiameter = '';
    localFormData.endFacilityMaterial = '';
    localFormData.endFacilityUnitPrice = '';
    localFormData.endFacilityQuantity = '';

    localFormData.fundingSource = fundingSource;
    localFormData.irrigationType = irrigationType;
    localFormData.installationType = installationType;
    localFormData.waterSource = waterSource;
    localFormData.perforatedPipeType = perforatedPipeType;
    localFormData.sprinklerType = sprinklerType;
    localFormData.dripperType = dripperType;

    updateFormData();
  }
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
  const groupItems = localFormData.pipes.filter(p => p.groupId === groupNo).sort((a,b) => (a.order || 0) - (b.order || 0));
  const actualPipeIndex1 = localFormData.pipes.findIndex(p => p.pomno === groupItems[pipeIndexInGroup].pomno && p.order === groupItems[pipeIndexInGroup].order);
  const actualPipeIndex2 = localFormData.pipes.findIndex(p => p.pomno === groupItems[pipeIndexInGroup-1].pomno && p.order === groupItems[pipeIndexInGroup-1].order);

  if(actualPipeIndex1 !== -1 && actualPipeIndex2 !== -1){
    // 交換 order 屬性
    const order1 = localFormData.pipes[actualPipeIndex1].order;
    localFormData.pipes[actualPipeIndex1].order = localFormData.pipes[actualPipeIndex2].order;
    localFormData.pipes[actualPipeIndex2].order = order1;
  }
  updateFormData();
};


// 下移管路順序
const movePipeDown = (groupNo: number, pipeIndexInGroup: number) => {
  const groupItems = localFormData.pipes.filter(p => p.groupId === groupNo).sort((a,b) => (a.order || 0) - (b.order || 0));
  if (pipeIndexInGroup >= groupItems.length - 1) return;

  const actualPipeIndex1 = localFormData.pipes.findIndex(p => p.pomno === groupItems[pipeIndexInGroup].pomno && p.order === groupItems[pipeIndexInGroup].order);
  const actualPipeIndex2 = localFormData.pipes.findIndex(p => p.pomno === groupItems[pipeIndexInGroup+1].pomno && p.order === groupItems[pipeIndexInGroup+1].order);

  if(actualPipeIndex1 !== -1 && actualPipeIndex2 !== -1){
    // 交換 order 屬性
    const order1 = localFormData.pipes[actualPipeIndex1].order;
    localFormData.pipes[actualPipeIndex1].order = localFormData.pipes[actualPipeIndex2].order;
    localFormData.pipes[actualPipeIndex2].order = order1;
  }
  updateFormData();
};


// 自動帶入材料
// const autoFillMaterials = async () => {
//   if (!canAutoFillMaterials.value) {
//     console.error('Not all required fields filled for auto-filling materials');
//     return;
//   }

//   isLoadingMaterials.value = true;

//   try {
//     // 構建請求數據
//     const requestData = {
//       // 栅塊數據
//       Length: parseInt(localFormData.fieldLength),
//       width: parseInt(localFormData.fieldWidth),

//       // 主管數據
//       L1Len: parseFloat(localFormData.mainPipeLength),
//       L1Material: parseInt(getMatTypeId(localFormData.mainPipeMaterial)),
//       L1Spec: parseInt(getSpecId(localFormData.mainPipeDiameter)),
//       L1Price: parseFloat(localFormData.mainPipeUnitPrice) || 0,
//       L1MatAmt: parseInt(localFormData.mainPipeQuantity) || 0,

//       // 支管數據
//       L2Len: 0,
//       L2Material: 1,
//       L2Spec: 1,
//       L2Price: 0,
//       L2MatAmt: 0,

//       // 灌溉系統數據
//       ddl_EndType: getEndTypeId(localFormData.irrigationType),
//       ddl_Sprinkler: localFormData.sprinklerType || 2,
//       ddl_Drop: localFormData.dripperType || 7,
//       ddl_Perforated: localFormData.perforatedPipeType || 1,

//       // 設施類型
//       ddl_FacType: localFormData.installationType || 1,

//       // 灌溉水源
//       ddl_WtaerSrc: localFormData.waterSource || 1,

//       // 支管與噴頭間距
//       SL: parseFloat(localFormData.branchPipeSpacing) || 0,
//       SS: parseFloat(localFormData.sprinklerSpacing) || 0,

//       // 支管材質與規格
//       BranchMaterial: parseInt(getMatTypeId(localFormData.branchPipeMaterial)) || 1,
//       BranchSpec: parseInt(getSpecId(localFormData.branchPipeDiameter)) || 1,

//       // 變徑規格
//       ChangeBranchSpec: localFormData.variantType || 1,

//       // 豎管高度
//       StdpipeHei: parseFloat(localFormData.riserHeight) || 1,

//       // 其他需要的參數
//       StdpipeSpec: 1,
//       StdpipeMat: 1,
//       NozzleMaterial: 1,
//       NozzleSpec: 1
//     };

//     console.log('Auto-filling materials with data:', requestData);

//     // 模擬API調用（實際使用中替換為真實的API調用）
//     // const response = await axios.post('../FarmerSys/GetStdSysByConditionAddGroup', requestData);

//     // 模擬延遲
//     await new Promise(resolve => setTimeout(resolve, 1500));

//     // 模擬API響應數據
//     const mockResponse = {
//       data: getMockMaterialData()
//     };

//     // 處理響應數據
//     const materialGroups = mockResponse.data;

//     // 清空當前管路列表
//     localFormData.pipes = [];

//     // 添加新的材料列表
//     materialGroups.forEach(group => {
//       group.List.forEach(material => {
//         localFormData.pipes.push({
//           groupId: group.GroupNo,
//           moduleType: material.module,
//           name: material.matname,
//           specification: `${material.spec1} ${material.spec2} ${material.spec3}`.trim(),
//           unit: material.itemunit,
//           description: material.description,
//           unitPrice: material.matprice,
//           quantity: material.matamount,
//           totalPrice: Math.round(material.matprice * material.matamount)
//         });
//       });
//     });

//     // 計算輔助金額
//     calculateSubsidy();
//   } catch (error) {
//     console.error('Error auto-filling materials:', error);
//   } finally {
//     isLoadingMaterials.value = false;
//   }
// };
const autoFillMaterials = async () => {
  if (!form.value?.validate()) {
     console.error('Form validation failed for auto-filling materials');
     return;
  }
  if (!canAutoFillMaterials.value) {
    console.error('Not all required fields for auto-filling materials are filled or valid.');
    // 可以加入提示訊息給使用者
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

    console.log('Auto-filling materials with payload:', JSON.stringify(requestPayload, null, 2));

    // 【TODO: API Call】替換為真實的 FastAPI 端點呼叫
    // const response = await yourApiService.post('/api/materials/calculate-standard', requestPayload);
    // const materialGroupsFromApi = response.data;

    // 模擬延遲和響應
    await new Promise(resolve => setTimeout(resolve, 1500));
    const materialGroupsFromApi = getMockMaterialData(requestPayload.form_inputs); // 將payload傳給mock

    localFormData.pipes = []; // 清空現有
    materialGroupsFromApi.forEach(group => {
      group.List.forEach(material => {
        localFormData.pipes.push({
          pomno: material.pomno,
          groupId: group.GroupNo,
          groupName: group.GroupName,
          module: material.module,
          matname: material.matname,
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
          order: material.order
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
    const mainPipesData = [];
    if (localFormData.mainPipeLength && localFormData.mainPipeMaterialId && localFormData.mainPipeDiameterId) {
        mainPipesData.push({
            Length: localFormData.mainPipeLength,
            Mat: pipeMaterialOptions.value.find(m => m.id === localFormData.mainPipeMaterialId)?.name || '', // 材質名稱
            Spec: localFormData.mainPipeDiameterId, // 規格ID
            LPrice: localFormData.mainPipeUnitPrice || 0,
            Amount: localFormData.mainPipeQuantity || 0
        });
    }
    if (localFormData.mainPipe2Enabled && localFormData.mainPipe2Length && localFormData.mainPipe2MaterialId && localFormData.mainPipe2DiameterId) {
        mainPipesData.push({
            Length: localFormData.mainPipe2Length,
            Mat: pipeMaterialOptions.value.find(m => m.id === localFormData.mainPipe2MaterialId)?.name || '', // 材質名稱
            Spec: localFormData.mainPipe2DiameterId, // 規格ID
            LPrice: localFormData.mainPipe2UnitPrice || 0,
            Amount: localFormData.mainPipe2Quantity || 0
        });
    }

    const requestPayload = {
        map_no: props.mapNo, // 需要傳入
        // operating_unit_id: props.operatingUnitId, // GetTotalPrice 可能不需要此參數，但後端可按需加入

        // 以下對應 ParaJsonData
        Unit: localFormData.fundingSourceId, // 補助單位ID
        Block: `${localFormData.fieldLength}x${localFormData.fieldWidth}`,
        IrrWCode: localFormData.waterSourceId, // 灌溉水源ID

        EndTypeDataAry: [{ // 這裡簡化為只處理第一個末端系統，若有多個需擴展
            Endtype: localFormData.irrigationTypeId, // 末端型式主ID
            Fac: localFormData.facilityTypeId,       // 設施型式ID
            BranchPipeMaterial: pipeMaterialOptions.value.find(m=>m.id === localFormData.branchPipeMaterialId)?.name || '', // 支管材質名稱
            BranchPipeSpec: localFormData.branchPipeDiameterId, // 支管規格ID
            SS: localFormData.sprinklerSpacing_SS,
            SL: localFormData.branchPipeSpacing_SL,
            StdpipeHei: localFormData.riserHeight_H,
            NozzleSpec: localFormData.endFacilitySpecId, // 末端設施主要規格ID
            NozzleType: filteredEndFacilityPipeFittings.value.find(f => f.pomno === localFormData.endFacilityPomno)?.displayName || '', // 末端設施名稱或類型描述
            StdpipeMat: pipeMaterialOptions.value.find(m => m.id === localFormData.riserPipeMaterialId)?.name || '', // 豎管材質名稱
            StdpipeSpec: localFormData.riserPipeSpecId,   // 豎管規格ID
            PerforatedPipe: localFormData.irrigationTypeId === 1 ? localFormData.perforatedPipeDirection : 1
        }],
        MainJsonDataAry: mainPipesData,
        PriceJsonDataAry: localFormData.pipes.map(pipe => ({
            POMNo: pipe.pomno,
            Group: pipe.groupId,
            Order: pipe.order || 1, // 確保有值
            Amt: pipe.matamount,
            Price: pipe.matprice,
            TotalPrice: pipe.totalPrice
        })),
        FacNo: null, // 公版設施系統代號, 若有選擇公版系統則傳入, 此處可能為null或特定值
        // TotalPrice: parseFloat(totalPipesPrice.value.replace(/,/g, '')) // 由後端計算，或前端先計算一次傳給後端參考
    };

    console.log('Calculating subsidy with payload:', JSON.stringify(requestPayload, null, 2));

    // 【TODO: API Call】 替換為真實的 FastAPI 端點呼叫
    // const response = await yourApiService.post('/api/subsidy/calculate-total-price', requestPayload);
    // const priceData = response.data.split(';'); // 假設後端返回 "總價;補助金額;自付金額"

     // 模擬延遲和響應
    await new Promise(resolve => setTimeout(resolve, 1000));
    const currentTotalPipesPrice = parseFloat(totalPipesPrice.value.replace(/,/g, ''));
    const mockApiResponse = `${currentTotalPipesPrice};${Math.round(currentTotalPipesPrice * 0.49)};${currentTotalPipesPrice - Math.round(currentTotalPipesPrice * 0.49)}`; // 假設49%補助
    const priceData = mockApiResponse.split(';');


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
  // 在此處進行任何必要的驗證
  // localValid.value = form.value?.validate() ?? false; // 如果需要Vuetify的表單驗證

  const dataToEmit = {
    ...props.formData, // 保留父組件的其他步驟數據
    step4Data: { ...localFormData }, // 將此步驟的數據嵌套
    valid: localValid.value // 或總是true，取決於您的導航邏輯
  };
  // console.log('Emitting update:formData with:', JSON.parse(JSON.stringify(dataToEmit)));
  emit('update:formData', dataToEmit);
};


// 實用函數
// 模擬取得物料編號
const getPOMNo = (moduleType, name) => {
  // 實際應用中，這裡應該使用真實的物料編號邏輯
  // 這裡僅返回一個隨機模擬編號
  return Math.floor(Math.random() * 10000) + 10000;
};

// 獲取總價格
const getTotalPrice = () => {
  return localFormData.pipes.reduce((sum, pipe) => sum + pipe.totalPrice, 0);
};

// 獲取模擬材料數據
// 模擬材料數據 (應根據API的真實響應結構調整)
const getMockMaterialData = (formInputs: any) => {
  console.log("Mock data generation based on form inputs:", formInputs);
  const L1Length = formInputs.L1Len || 0;
  const L1Qty = Math.ceil(L1Length / (localFormData.mainPipeStandardLength || 4));

  return [
    {
      GroupNo: 1,
      GroupName: '主管路組',
      List: [
        {
          pomno: 1001, module: '主管', matname: `${pipeMaterialOptions.value.find(m=>m.id===formInputs.L1Material)?.name || 'PVC管'} ${pipeDiameterOptions.value.find(d=>d.id===formInputs.L1Spec)?.name || '1"'}`,
          mattype: pipeMaterialOptions.value.find(m=>m.id===formInputs.L1Material)?.name || 'PVC',
          spec1: pipeDiameterOptions.value.find(d=>d.id===formInputs.L1Spec)?.name || '1"', spec2: '', spec3: '',
          itemunit: '支', matprice: formInputs.L1Price || 60, matamount: L1Qty,
          description: '主管1管材', order: 1, group: 1
        },
        {
          pomno: 1002, module: '主管配件', matname: '彎頭', mattype: 'PVC',
          spec1: pipeDiameterOptions.value.find(d=>d.id===formInputs.L1Spec)?.name || '1"', spec2: '', spec3: '',
          itemunit: '個', matprice: 20, matamount: 3,
          description: '90度彎頭', order: 2, group: 1
        },
        // ... L2主管相關材料 (如果啟用)
      ].filter(Boolean) // 過濾掉可能的 undefined (如果L2未啟用)
    },
    // ... 其他組別的模擬材料，根據 formInputs.ddl_EndType 等動態生成
    {
      GroupNo: 2, GroupName: '支管路組', List: [
        { pomno: 2001, module: '支管', matname: 'PE軟管 3/4"', mattype: 'PE', spec1: '3/4"', itemunit: '捲', matprice: 150, matamount: Math.ceil((formInputs.Length / formInputs.SL) * formInputs.width / 100), description: '支管用PE軟管(100米/捲)', order: 1, group: 2},
        { pomno: 2002, module: '支管配件', matname: '三通接頭', mattype: 'PVC', spec1: `${pipeDiameterOptions.value.find(d=>d.id===formInputs.L1Spec)?.name || '1"'}轉3/4"`, itemunit: '個', matprice: 15, matamount: Math.ceil(formInputs.Length / formInputs.SL) , description: '主管轉支管三通', order: 2, group: 2}
      ]
    },
    {
        GroupNo: 8, GroupName: '噴頭/微噴/滴嘴組', List: [
            { pomno: 8001, module: '末端', matname: '可調式噴頭', mattype: '塑膠', spec1: '1/2"', itemunit: '個', matprice:30, matamount: Math.ceil(formInputs.Length / formInputs.SL) * Math.ceil(formInputs.width / formInputs.SS) , description: '末端噴灑裝置', order: 1, group: 8 }
        ]
    }
  ];
};

// 初始化數據
onMounted(async () => {
  await loadDropdownOptions(); // 載入下拉選單數據

  // Populate localFormData with its own persisted data from props.formData (grantsStore.formData[4])
  if (props.formData) {
    const dataToLoad = props.formData.step4Data || props.formData; // step4Data for edit, root for create
    Object.keys(localFormData).forEach(key => {
      if (dataToLoad[key] !== undefined) {
        if (key === 'pipes' && Array.isArray(dataToLoad[key])) {
          localFormData.pipes = [...dataToLoad[key]];
        } else if (key !== 'pipes') {
          localFormData[key] = dataToLoad[key];
        }
      }
    });
    // Explicitly load facilityArea if it's directly on props.formData and not in step4Data
    // This handles cases where facilityArea might be at the root of props.formData for this step
    if (props.formData.facilityArea !== undefined && !props.formData.step4Data?.facilityArea) {
        localFormData.facilityArea = props.formData.facilityArea;
    }
  }

  // Load step 2 data if not already present in store to ensure facilityArea is available
  // This might be redundant if edit.vue preloads all relevant steps, but good for robustness
  if (!grantsStore.formData[2]?.facilityArea && grantsStore.currentGrant?.case_number) {
    await grantsStore.loadStepData(grantsStore.currentGrant.case_number, 2);
  }

  const step2FacilityArea = grantsStore.formData[2]?.facilityArea;
  if (step2FacilityArea !== undefined) {
    localFormData.facilityArea = parseFloat(step2FacilityArea) || 0; // Or keep as string if appropriate
    console.log("Using facilityArea from Step 2 data:", localFormData.facilityArea);
  } else if (props.formData?.facilityArea !== undefined) { // Fallback to current step's persisted data
    localFormData.facilityArea = parseFloat(props.formData.facilityArea) || 0;
    console.log("Using facilityArea from props.formData (Step 4 persisted):", localFormData.facilityArea);
  } else {
    // If facilityArea is still not set (e.g. was not in step2 and not in props.formData.facilityArea),
    // it might have been set from props.formData.step4Data.facilityArea during the initial population.
    // If it's still undefined, null, or empty string after all that, then default.
    const currentLocalFacilityArea = parseFloat(localFormData.facilityArea);
    if (isNaN(currentLocalFacilityArea) || currentLocalFacilityArea === 0) {
        localFormData.facilityArea = 10000; // Default if not found anywhere
        console.log("facilityArea not found, using default:", localFormData.facilityArea);
    } else {
        // This means it was likely populated from props.formData.step4Data.facilityArea
        console.log("Using facilityArea from self-persisted step4Data ("+localFormData.facilityArea+"), as Step2 and props.formData.facilityArea were undefined.");
    }
  }

  calculateWidth(); // Ensure width is calculated with the correct facilityArea
  // ... existing code ...
  if(localFormData.pipes.length > 0){ // This part was in the original, keep it
      await calculateSubsidy();
  }
  updateFormData(); // Emit initial data
});

// 監聽父組件數據變化
watch(() => props.formData, (newVal) => {
  console.log("Step 4 props.formData changed. NewVal step2 facilityArea:", grantsStore.formData[2]?.facilityArea);
  if (newVal) {
    // Prioritize facilityArea from Step 2 store data
    const step2FacilityArea = grantsStore.formData[2]?.facilityArea;
    if (step2FacilityArea !== undefined) {
      localFormData.facilityArea = parseFloat(step2FacilityArea) || 0;
    } else if (newVal.step4Data?.facilityArea !== undefined) { // Fallback to persisted step4Data
      localFormData.facilityArea = parseFloat(newVal.step4Data.facilityArea) || 0;
    } else if (newVal.facilityArea !== undefined) { // Fallback to root of formData prop
       localFormData.facilityArea = parseFloat(newVal.facilityArea) || 0;
    }
    // else, keep existing localFormData.facilityArea or default from onMounted

    // Update other fields from newVal.step4Data or newVal
    const dataToProcess = newVal.step4Data || newVal;
    Object.keys(localFormData).forEach(key => {
      if (key !== 'facilityArea' && dataToProcess[key] !== undefined &&
          JSON.stringify(dataToProcess[key]) !== JSON.stringify(localFormData[key])) {
        localFormData[key] = dataToProcess[key];
      }
    });
    calculateWidth(); // Recalculate width if facilityArea might have changed
  }
}, { deep: true });

// 監聽本地數據變化，更新父組件
watch(localFormData, () => {
  updateFormData();
}, { deep: true });

// 監聽本地表單驗證狀態
// watch(localValid, (newVal) => {
//   if (props.formData?.valid !== newVal) {
//     updateFormData();
//   }
// });
watch(localValid, (newVal) => {
    const parentValid = props.formData?.step4Data?.valid;
    if (parentValid !== newVal) {
        updateFormData();
    }
});

watch(() => grantsStore.currentGrant?.office_id, async (newOfficeId) => {
  if (newOfficeId) {
    console.log(`Current grant office_id changed to: ${newOfficeId}, refreshing pipe fittings`);
    await fetchPipeFittings();
  }
});

// Provide fallback options if no pipe fittings are found
watch(pipeDiameterOptions, (newOptions) => {
  if (newOptions.length === 0) {
    console.warn('No pipe diameter options found, using defaults');
    // Provide default options
    pipeDiameterOptions.value = [
      { id: 26, name: '1/2"', standardLength: 4 },
      { id: 27, name: '3/4"', standardLength: 4 },
      { id: 28, name: '1"', standardLength: 4 },
      { id: 3, name: '1-1/4"', standardLength: 4 },
      { id: 4, name: '1-1/2"', standardLength: 4 },
      { id: 29, name: '2"', standardLength: 4 },
    ];
  }
});

watch(pipeMaterialOptions, (newOptions) => {
  if (newOptions.length === 0) {
    console.warn('No pipe material options found, using defaults');
    // Provide default options
    pipeMaterialOptions.value = [
      { id: 1, name: 'PVC管' },
      { id: 6, name: 'PE管(10kgf)' },
      { id: 7, name: 'PE管(6kgf)' }
    ];
  }
});
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
}

.v-table th {
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
}

.irrigation-type-config {
  background-color: rgba(0, 0, 0, 0.02);
  padding: 15px;
  border-radius: 8px;
}
</style>
