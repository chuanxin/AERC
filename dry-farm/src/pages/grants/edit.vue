<template>
  <v-container
    fluid
    class="grants-edit-container px-6 pb-0 pt-0"
    style="background-color: white"
  >
    <!-- Loading indicator -->
    <v-overlay
      v-if="!isDataLoaded"
      :value="!isDataLoaded"
      class="d-flex align-center justify-center"
    >
      <v-progress-circular
        indeterminate
        size="64"
        color="#3ea0a3"
      />
      <span class="ml-4 text-h6">載入資料中...</span>
    </v-overlay>

    <!-- Step transition overlay -->
    <v-overlay
      v-model="isStepTransitioning"
      class="d-flex align-center justify-center step-transition-overlay"
      :opacity="0"
    >
      <div class="text-center">
        <v-progress-circular
          indeterminate
          size="48"
          color="#3ea0a3"
          width="3"
        />
        <div class="mt-3 text-body-1 font-weight-medium">
          載入步驟 {{ targetStep || currentStep }}...
        </div>
      </div>
    </v-overlay>

    <!-- Error display -->
    <v-alert
      v-if="grantsStore.error"
      type="error"
      class="mb-4"
      dismissible
      @click:close="grantsStore.clearError()"
    >
      {{ grantsStore.error }}
    </v-alert>

    <!-- Main content -->
    <v-row justify="center">
      <v-col
        cols="12"
        lg="11"
        align-self="center"
      >
        <div class="section-wrapper">
          <!-- Mobile temporary drawer -->
          <v-navigation-drawer
            v-if="isSmallScreen"
            v-model="drawerOpen"
            temporary
            width="280"
            class="navigation-drawer-glass"
          >
            <v-list
              height="55"
              class="pt-0 mt-0"
            >
              <v-list-item>
                <v-list-item-title
                  class="text-h6 font-weight-bold"
                  style="color: #2d8c8f"
                >
                  補助申請業務 {{ currentStep }}/{{ steps.length }}
                </v-list-item-title>
                <template #append>
                  <v-btn
                    icon
                    variant="text"
                    rounded="circle"
                    class="pl-0"
                    @click="isRailMode = !isRailMode"
                  >
                    <v-icon>{{ isRailMode ? 'mdi-chevron-right' : 'mdi-chevron-left' }}</v-icon>
                  </v-btn>
                </template>
              </v-list-item>
            </v-list>
            <v-divider />
            <v-list
              nav
              class="step-list"
            >
              <v-list-item
                v-for="step in steps"
                :key="step.value"
                :value="step.value"
                :active="currentStep === step.value"
                :disabled="isNavigating"
                variant="elevated"
                elevation="0"
                class="step-list-item"
                @click="handleStepClick(step.value)"
              >
                <template #prepend>
                  <v-icon
                    :color="getStepIconColor(step.value)"
                    size="large"
                  >
                    {{ getStepIcon(step.value) }}
                  </v-icon>
                </template>
                <v-list-item-title>
                  <span :class="{ 'text-primary font-weight-bold': currentStep === step.value }">
                    {{ step.title }}
                  </span>
                </v-list-item-title>
                <v-list-item-subtitle class="text-medium-emphasis">
                  {{ step.subtitle }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-navigation-drawer>

          <v-row
            class="pt-4 layout-row-with-gap"
          >
            <!-- Left sidebar: Navigation (類似 qualification 的 md="3") - 桌面端 -->
            <v-col
              v-if="!isSmallScreen"
              cols="3"
              :class="[
                'pa-0',
                'fixed-sidebar-col',
                { 'rail-mode': isRailMode }
              ]"
            >
              <v-card
                rounded="lg"
                class="navigation-drawer-glass"
                :style="{
                  width: isRailMode ? '60px' : '280px',
                  transition: 'width 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                }"
              >
                <v-list
                  height="55"
                  class="pa-0 ma-0"
                >
                  <v-list-item>
                    <v-list-item-title
                      class="text-h6 font-weight-bold"
                      style="color: #2d8c8f"
                    >
                      補助申請業務 {{ currentStep }}/{{ steps.length }}
                    </v-list-item-title>
                    <template #append>
                      <v-btn
                        v-if="isAdminMode"
                        icon
                        variant="text"
                        rounded="circle"
                        size="small"
                        class="mr-2"
                        color="warning"
                        @click="showResetStepDialog = true"
                      >
                        <v-icon size="small">
                          mdi-refresh
                        </v-icon>
                        <v-tooltip
                          activator="parent"
                          location="bottom"
                        >
                          重置當前步驟資料
                        </v-tooltip>
                      </v-btn>
                      <!-- <v-btn
                        icon
                        variant="text"
                        rounded="circle"
                        class="pl-0"
                        @click="isRailMode = !isRailMode"
                      >
                        <v-icon>{{ isRailMode ? 'mdi-chevron-right' : 'mdi-chevron-left' }}</v-icon>
                      </v-btn> -->
                    </template>
                  </v-list-item>
                </v-list>

                <!-- Step navigation list -->
                <v-list
                  nav
                  class="step-list"
                >
                  <v-list-item
                    v-for="step in steps"
                    :key="step.value"
                    :value="step.value"
                    :active="currentStep === step.value"
                    :disabled="isNavigating"
                    variant="elevated"
                    elevation="0"
                    class="step-list-item"
                    rounded
                    @click="handleStepClick(step.value)"
                  >
                    <template #prepend>
                      <v-icon
                        :color="getStepIconColor(step.value)"
                        size="large"
                      >
                        {{ getStepIcon(step.value) }}
                      </v-icon>
                    </template>

                    <v-list-item-title>
                      <span :class="{ 'text-primary font-weight-bold': currentStep === step.value }">
                        {{ step.title }}
                      </span>
                    </v-list-item-title>

                    <v-list-item-subtitle
                      v-if="!isRailMode"
                      :class="[
                        currentStep === step.value ? 'text-primary' : 'text-medium-emphasis'
                      ]"
                    >
                      {{ step.subtitle }}
                    </v-list-item-subtitle>

                    <template
                      v-if="currentStep === step.value && !isRailMode"
                      #append
                    >
                      <v-icon
                        color="primary"
                        size="small"
                        rounded="circle"
                      >
                        mdi-arrow-right
                      </v-icon>
                    </template>
                  </v-list-item>
                </v-list>

                <!-- 功能項目分隔線 -->
                <v-divider class="my-2" />

                <!-- 版本管理功能項目 -->
                <v-list
                  nav
                  class="function-list"
                >
                  <v-list-item
                    :disabled="isNavigating || designChangeLoading"
                    variant="plain"
                    class="design-change-item border-thin"
                    rounded
                    @click="handleDesignChangeClick"
                  >
                    <template #prepend>
                      <v-icon
                        :color="designChangeLoading ? 'grey' : '#3ea0a3'"
                        size="large"
                        :class="{ 'mdi-spin': designChangeLoading }"
                      >
                        {{ designChangeLoading ? 'mdi-loading' : 'mdi-content-copy' }}
                      </v-icon>
                    </template>

                    <v-list-item-title>
                      <span class="function-item-title">變更設計</span>
                    </v-list-item-title>

                    <v-list-item-subtitle
                      v-if="!isRailMode"
                      class="text-medium-emphasis"
                    >
                      建立新版本
                    </v-list-item-subtitle>

                    <!-- 版本資訊顯示 -->
                    <template
                      v-if="!isRailMode"
                      #append
                    >
                      <div class="version-info">
                        <v-chip
                          size="x-small"
                          color="#3ea0a3"
                          variant="outlined"
                          class="version-chip"
                        >
                          v{{ grantsStore.currentGrant?.active_version?.version || 1 }}
                        </v-chip>
                      </div>
                    </template>
                  </v-list-item>
                </v-list>
              </v-card>
            </v-col>

            <!-- Right content area: Main content (類似 qualification 的 md="9") -->
            <v-col
              cols="9"
              class="pa-0 fixed-content-col"
            >
              <div class="main-content pt-7">
                <div class="px-4 mb-1">
                  <!-- Small screen step indicator -->
                  <v-card
                    v-if="isSmallScreen"
                    class="mb-14 mt-0 pa-2 pt-0 mobile-step-card"
                  >
                    <div class="d-flex align-center">
                      <v-btn
                        icon
                        variant="text"
                        @click="drawerOpen = !drawerOpen"
                      >
                        <v-icon>mdi-menu</v-icon>
                      </v-btn>

                      <div class="ml-2">
                        <div class="text-subtitle-1">
                          補助申請業務 {{ currentStep }}/{{ steps.length }}
                        </div>
                        <div class="text-body-2">
                          {{ steps.find(s => s.value === currentStep)?.subtitle }}
                        </div>
                      </div>

                      <v-spacer />

                      <div class="d-flex">
                        <v-btn
                          v-if="currentStep > 1"
                          :disabled="isNavigating || !canGoToPreviousStep"
                          icon
                          variant="text"
                          rounded="circle"
                          @click="handleGoBack"
                        >
                          <v-icon>mdi-arrow-left</v-icon>

                          <!-- 禁用狀態提示 -->
                          <v-tooltip
                            v-if="!canGoToPreviousStep && navigationBlockingReason"
                            activator="parent"
                            location="top"
                          >
                            {{ navigationBlockingReason }}
                          </v-tooltip>
                        </v-btn>

                        <v-btn
                          v-if="currentStep < steps.length"
                          :disabled="isNavigating || !canGoToNextStep"
                          icon
                          variant="text"
                          rounded="circle"
                          @click="goToNextStep"
                        >
                          <v-icon>mdi-arrow-right</v-icon>

                          <!-- 禁用狀態提示 -->
                          <v-tooltip
                            v-if="!canGoToNextStep && navigationBlockingReason"
                            activator="parent"
                            location="top"
                          >
                            {{ navigationBlockingReason }}
                          </v-tooltip>
                        </v-btn>
                      </div>
                    </div>
                  </v-card>

                  <!-- Step components container -->
                  <v-card
                    class="section-card pb-0 mb-0"
                    rounded="lg"
                  >
                    <v-card-item class="custom-title">
                      <v-card-title class="text-h5 font-weight-black">
                        {{ steps.find(s => s.value === currentStep)?.title }}
                        <span
                          v-if="grantsStore.currentGrant?.case_number"
                          class="text-disabled"
                        >
                          <v-chip
                            color="grey-lighten-3"
                            size="small"
                            class="ml-4 mb-1"
                            variant="flat"
                            rounded="sm"
                          >
                            <span>案號: {{ grantsStore.currentGrant?.case_number }}</span>
                            <v-divider
                              v-if="grantsStore.currentGrant?.active_version?.version"
                              vertical
                              class="mx-2"
                              style="opacity: 0.5;"
                            />
                            <span
                              v-if="grantsStore.currentGrant?.active_version?.version"
                              class="text-caption"
                              style="opacity: 0.7; font-weight: 500;"
                            >
                              版本 {{ grantsStore.currentGrant.active_version.version }}
                            </span>
                          </v-chip>
                        </span>
                      </v-card-title>
                    </v-card-item>

                    <v-card-text class="pb-0 mb-0">
                      <!-- Autosave indicator when there are unsaved changes -->
                      <v-snackbar
                        v-model="grantsStore.hasUnsavedChanges"
                        variant="text"
                        color="info"
                        lines="one"
                        icon="mdi-content-save"
                        class="mb-4"
                      >
                        <template #text>
                          資料變更尚未儲存，系統將自動儲存
                          <span
                            v-if="grantsStore.lastSavedAt"
                            class="ms-2 text-caption"
                          >
                            (上次儲存於 {{ grantsStore.lastSavedTime }})
                          </span>
                        </template>

                        <template #actions>
                          <v-btn
                            variant="text"
                            :loading="grantsStore.isSaving"
                            @click="saveAllChanges"
                          >
                            立即儲存
                          </v-btn>
                        </template>
                        <v-progress-linear
                          :active="grantsStore.hasUnsavedChanges"
                          :indeterminate="grantsStore.hasUnsavedChanges"
                          color="cyan"
                          stream
                          location="bottom"
                        />
                      </v-snackbar>

                      <!-- Content Card for Step Components -->
                      <v-card
                        class="content-card"
                        rounded="lg"
                        elevation="0"
                      >
                        <!-- Step components -->
                        <step1
                          v-if="currentStep === 1"
                          ref="step1Ref"
                          :current-step="currentStep"
                          @step-data-changed="handleStepDataChanged"
                          @validation-changed="handleStepValidationChanged"
                          @ready-to-proceed="handleStepReadyToProceed"
                          @go-back-requested="handleGoBack"
                        />
                        <step2
                          v-if="currentStep === 2"
                          ref="step2Ref"
                          :current-step="currentStep"
                          @step-data-changed="handleStepDataChanged"
                          @validation-changed="handleStepValidationChanged"
                          @ready-to-proceed="handleStepReadyToProceed"
                          @go-back-requested="handleGoBack"
                          @navigation-state-changed="handleNavigationStateChanged"
                        />
                        <step5
                          v-if="currentStep === 3"
                          ref="step5Ref"
                          :form-data="grantsStore.formData[5]"
                          :current-step="currentStep"
                          :grant-id="grantsStore.currentGrant?.id || 0"
                          @update:form-data="(data) => handleFormDataUpdate(5, data)"
                          @validated="(event) => handleStepValidated({ valid: event.valid, step: currentStep })"
                          @go-back="handleGoBack"
                          @case-archived="handleCaseArchived"
                          @navigation-state-changed="handleNavigationStateChanged"
                          @button-config-changed="handleStep5ButtonConfigChanged"
                        />
                        <step3
                          v-if="currentStep === 4"
                          :form-data="grantsStore.formData[3]"
                          :current-step="currentStep"
                          @update:form-data="(data) => handleFormDataUpdate(3, data)"
                          @validated="(event) => handleStepValidated({ valid: event.valid, step: currentStep })"
                          @go-back="handleGoBack"
                        />
                        <step4
                          v-if="currentStep === 5"
                          :form-data="grantsStore.formData[4]"
                          :current-step="currentStep"
                          @update:form-data="(data) => handleFormDataUpdate(4, data)"
                          @validated="(event) => handleStepValidated({ valid: event.valid, step: currentStep })"
                          @go-back="handleGoBack"
                        />
                        <step6
                          v-if="currentStep === 6"
                          :form-data="grantsStore.formData[6]"
                          :current-step="currentStep"
                          @update:form-data="handleFormDataUpdate(6, $event)"
                          @validated="handleStepValidated"
                          @go-back="handleGoBack"
                        />
                        <step7
                          v-if="currentStep === 7"
                          ref="step7Ref"
                          :form-data="grantsStore.formData[7]"
                          :current-step="currentStep"
                          @update:form-data="handleFormDataUpdate(7, $event)"
                          @validated="handleStepValidated"
                          @go-back="handleGoBack"
                          @button-config-changed="handleStep7ButtonConfigChanged"
                          @save-for-improvement="handleSaveForImprovement"
                          @proceed-to-next-step="goToNextStep"
                        />
                        <step8
                          v-if="currentStep === 8"
                          :form-data="grantsStore.formData[8]"
                          :current-step="currentStep"
                          :grant-id="grantsStore.currentGrant?.id || 0"
                          @update:form-data="handleFormDataUpdate(8, $event)"
                          @validated="handleStepValidated"
                          @go-back="handleGoBack"
                        />
                      </v-card>
                    </v-card-text>

                    <!-- Step navigation buttons for desktop -->
                    <v-card-actions
                      v-if="!isSmallScreen"
                      class="pt-0"
                    >
                      <v-spacer />

                      <v-btn
                        v-if="currentStep > 1"
                        :disabled="isNavigating || !canGoToPreviousStep"
                        :class="{ 'navigation-blocked': !canGoToPreviousStep }"
                        size="x-large"
                        class="ml-6 mb-1 pr-6 navigation-btn"
                        color="#3ea0a3"
                        variant="text"
                        density="compact"
                        rounded="lg"
                        :ripple="false"
                        @click="handleGoBack"
                      >
                        <v-icon
                          start
                          :color="canGoToPreviousStep ? 'primary' : 'grey'"
                        >
                          mdi-arrow-left
                        </v-icon>
                        上一步

                        <!-- 禁用狀態提示 -->
                        <v-tooltip
                          v-if="!canGoToPreviousStep && navigationBlockingReason"
                          activator="parent"
                          location="top"
                        >
                          {{ navigationBlockingReason }}
                        </v-tooltip>
                      </v-btn>

                      <v-btn
                        :disabled="isNavigating || !canGoToNextStep"
                        :class="{ 'navigation-blocked': !canGoToNextStep }"
                        :color="getButtonColor()"
                        class="mr-6 pl-6 next-btn"
                        size="x-large"
                        variant="outlined"
                        density="compact"
                        rounded="lg"
                        :ripple="false"
                        @click="handleMainButtonClick"
                      >
                        <!-- 替換為更詳細的邏輯顯示不同的按鈕文字 -->
                        <template v-if="currentStep === 8">
                          完成
                        </template>
                        <template v-else-if="currentStep === 7">
                          {{ step7ButtonConfig.text }}
                        </template>
                        <template v-else-if="currentStep === 6">
                          完成申報
                        </template>
                        <template v-else-if="currentStep === 3">
                          {{ step5ButtonConfig.text }}
                        </template>
                        <template v-else>
                          下一步
                        </template>

                        <v-icon
                          v-if="currentStep === 8"
                          end
                          :color="canGoToNextStep ? 'white' : 'grey'"
                        >
                          mdi-check
                        </v-icon>
                        <v-icon
                          v-else-if="currentStep === 7"
                          end
                          :color="canGoToNextStep ? 'white' : 'grey'"
                        >
                          {{ step7ButtonConfig.icon }}
                        </v-icon>
                        <v-icon
                          v-else-if="currentStep === 3"
                          end
                          :color="canGoToNextStep ? 'white' : 'grey'"
                        >
                          {{ step5ButtonConfig.icon }}
                        </v-icon>
                        <v-icon
                          v-else
                          end
                          :color="canGoToNextStep ? 'white' : 'grey'"
                        >
                          mdi-arrow-right
                        </v-icon>

                        <!-- 禁用狀態提示 -->
                        <v-tooltip
                          v-if="!canGoToNextStep && navigationBlockingReason"
                          activator="parent"
                          location="top"
                        >
                          {{ navigationBlockingReason }}
                        </v-tooltip>
                      </v-btn>
                    </v-card-actions>
                  </v-card>
                </div>
              </div>
            </v-col>
          </v-row>
        </div>
      </v-col>
    </v-row>

    <!-- 處理中對話框 -->
    <v-dialog
      v-model="isNavigating"
      persistent
      width="300"
    >
      <v-card>
        <v-card-text class="text-center pa-5">
          <v-progress-circular
            indeterminate
            color="#3ea0a3"
            size="64"
            class="mb-3"
          />
          <div class="text-body-1">
            處理中，請稍候...
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- 🆕 統一的成功/錯誤回饋 Snackbar -->
    <v-snackbar
      v-model="showNotification"
      :color="notificationConfig.color"
      :timeout="notificationConfig.timeout"
      location="top center"
      variant="elevated"
      class="design-change-notification"
    >
      <div class="d-flex align-center">
        <v-icon
          :color="notificationConfig.iconColor"
          class="mr-3"
        >
          {{ notificationConfig.icon }}
        </v-icon>
        <div>
          <div class="text-subtitle-2 font-weight-medium">
            {{ notificationConfig.title }}
          </div>
          <div
            v-if="notificationConfig.message"
            class="text-body-2"
          >
            {{ notificationConfig.message }}
          </div>
        </div>
      </div>

      <template #actions>
        <v-btn
          variant="text"
          :color="notificationConfig.iconColor"
          @click="showNotification = false"
        >
          關閉
        </v-btn>
      </template>
    </v-snackbar>

    <!-- 🆕 變更設計確認對話框 -->
    <v-dialog
      v-model="showDesignChangeDialog"
      max-width="500"
      persistent
    >
      <v-card>
        <v-card-title class="text-h6 d-flex align-center pa-4">
          <v-icon
            color="#3ea0a3"
            class="mr-3"
          >
            mdi-content-copy
          </v-icon>
          <span>變更設計</span>
          <v-spacer />
          <v-btn
            icon
            variant="text"
            @click="showDesignChangeDialog = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <div class="mb-4">
            <p class="text-body-2 mb-3">
              系統將複製當前版本的所有資料，建立一個新的版本記錄。
            </p>

            <!-- 當前版本資訊 -->
            <v-card
              variant="outlined"
              color="#3ea0a3"
              class="mb-4"
            >
              <v-card-text class="pa-3">
                <div class="d-flex align-center">
                  <v-icon
                    color="#3ea0a3"
                    class="mr-2"
                  >
                    mdi-tag
                  </v-icon>
                  <div>
                    <div class="text-subtitle-2 font-weight-medium">
                      當前版本：版本 {{ grantsStore.currentGrant?.active_version?.version || 1 }}
                    </div>
                    <div class="text-caption text-medium-emphasis">
                      案件編號：{{ grantsStore.currentGrant?.case_number }}
                    </div>
                  </div>
                </div>
              </v-card-text>
            </v-card>

            <!-- 版本說明輸入 -->
            <v-textarea
              v-model="designChangeComment"
              label="版本說明（選填）"
              placeholder="請輸入此次變更設計的說明..."
              rows="3"
              variant="outlined"
              hide-details="auto"
              counter="255"
              maxlength="255"
            />
          </div>

          <!-- 未儲存變更警告 -->
          <v-alert
            v-if="grantsStore.hasUnsavedChanges"
            type="warning"
            variant="tonal"
            class="mb-3"
          >
            <v-icon>mdi-alert</v-icon>
            <span class="ml-2">系統偵測到未儲存的變更，將先自動儲存後再建立新版本。</span>
          </v-alert>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn
            variant="text"
            :disabled="designChangeLoading"
            @click="showDesignChangeDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            :loading="designChangeLoading"
            color="#3ea0a3"
            variant="elevated"
            @click="executeDesignChange(designChangeComment)"
          >
            <v-icon start>
              mdi-content-copy
            </v-icon>
            建立新版本
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 重置步驟資料確認對話框 -->
    <v-dialog
      v-model="showResetStepDialog"
      max-width="400"
      persistent
    >
      <v-card>
        <v-card-title class="text-h6 d-flex align-center pa-4">
          <v-icon
            color="warning"
            class="mr-3"
          >
            mdi-alert
          </v-icon>
          <span>重置步驟資料</span>
        </v-card-title>

        <v-divider />

        <v-card-text class="pa-4">
          <div class="mb-3">
            <v-alert
              type="warning"
              variant="tonal"
              density="compact"
            >
              <v-icon>mdi-information</v-icon>
              <span class="ml-2">
                這個操作將會清除 <strong>步驟 {{ currentStep }}</strong> 的所有資料。
              </span>
            </v-alert>
          </div>

          <div class="text-body-1 mb-2">
            您確定要重置當前步驟的資料嗎？
          </div>
          <div class="text-body-2 text-medium-emphasis">
            此操作<strong>無法復原</strong>，所有已填寫的資料將會被清除。
          </div>
        </v-card-text>

        <v-divider />

        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn
            variant="text"
            :disabled="resetStepLoading"
            @click="showResetStepDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            :loading="resetStepLoading"
            color="warning"
            variant="elevated"
            @click="handleResetStepData"
          >
            <v-icon left>
              mdi-refresh
            </v-icon>
            確認重置
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { nextTick } from 'vue'
import { useDisplay } from 'vuetify'
import { useRoute, useRouter, onBeforeRouteLeave } from 'vue-router'
import { useGrantsStore } from '@/stores/grants'
import { GrantStorage } from '@/utils/grant-storage'
import { debounce } from 'lodash-es'
// 🆕 導入版本管理服務函數
import { createGrantVersion } from '@/services/grantsService'

// Import step components
import step1 from '@/pages/grants/steps/step1.vue'
import step2 from '@/pages/grants/steps/step2.vue'
import step3 from '@/pages/grants/steps/step3.vue'
import step4 from '@/pages/grants/steps/step4.vue'
import step5 from '@/pages/grants/steps/step5.vue'
import step6 from '@/pages/grants/steps/step6.vue'
import step7 from '@/pages/grants/steps/step7.vue'
import step8 from '@/pages/grants/steps/step8.vue'

// Setup
const route = useRoute()
const router = useRouter()
const { name } = useDisplay()
const isSmallScreen = computed(() => name.value === 'xs' || name.value === 'sm')
const grantsStore = useGrantsStore()

// Admin mode detection - check if URL contains "admin"
const isAdminMode = computed(() => {
  return route.path.includes('admin') || route.fullPath.includes('admin')
})

// State refs
// 🔥 Linus式修復：延遲初始化 currentStep，避免錯誤渲染
// 使用 0 作為初始值，確保在 onMounted 完成前不渲染任何 step 組件
const currentStep = ref(0)
const submitting = ref(false)
const isDataLoaded = ref(false)
const isNavigating = ref(false)
const autoSaveTimer = ref<number | null>(null)

// 新增：導航狀態管理
const navigationStates = ref<Record<number, {
  canNavigate: boolean;
  isEditing: boolean;
  reason?: string;
}>>({})

// 新增：統一導航控制計算屬性
const canGoToPreviousStep = computed(() => {
  const currentStepState = navigationStates.value[currentStep.value]
  return currentStepState ? currentStepState.canNavigate : true
})

const canGoToNextStep = computed(() => {
  const currentStepState = navigationStates.value[currentStep.value]
  return currentStepState ? currentStepState.canNavigate : true
})

const navigationBlockingReason = computed(() => {
  const currentStepState = navigationStates.value[currentStep.value]
  return currentStepState?.reason || null
})

// Step7 按鈕配置
const step7ButtonConfig = ref({
  text: '結案',
  color: '#3ea0a3',
  icon: 'mdi-arrow-right',
  action: 'proceed'
})

// 新增：Step5 按鈕配置
const step5ButtonConfig = ref({
  text: '下一步',
  color: '#3ea0a3',
  icon: 'mdi-arrow-right',
  action: 'proceed'
})

// Step7 組件引用
const step7Ref = ref<{ handleActionRequest: (action: string) => void } | null>(null)

// 新增：Step5 組件引用
const step5Ref = ref<{ handleActionRequest: (action: string) => void; validateForm: () => boolean } | null>(null)

// 🆕 變更設計相關狀態
const designChangeLoading = ref(false)
const showDesignChangeDialog = ref(false)
const showResetStepDialog = ref(false)
const resetStepLoading = ref(false)
const designChangeComment = ref('')

// 🆕 通知系統狀態
const showNotification = ref(false)
const notificationConfig = ref({
  title: '',
  message: '',
  color: 'success',
  icon: 'mdi-check-circle',
  iconColor: 'white',
  timeout: 4000
})

// 🆕 錯誤類型定義 - 簡潔但完整
enum DesignChangeErrorType {
  NETWORK_ERROR = 'network',
  SAVE_ERROR = 'save',
  API_ERROR = 'api',
  VALIDATION_ERROR = 'validation',
  UNKNOWN_ERROR = 'unknown'
}

// 🆕 統一事件驅動架構：組件引用接口定義
interface StepComponent {
  handleProceedToNext: () => void;
  handleGoBack: () => void;
}

// 🆕 統一事件驅動架構：步驟組件引用映射
const stepRefs = reactive<Record<number, StepComponent | null>>({
  1: null,
  2: null,
  3: null,
  4: null,
  5: null,
  6: null,
  7: null,
  8: null
})

// 保持現有引用以便向後兼容
const step1Ref = ref<StepComponent | null>(null)
const step2Ref = ref<StepComponent | null>(null)

// Navigation drawer state
const drawerOpen = ref(true)
const isRailMode = ref(false) // Default to expanded
const drawerWidth = ref(280)

// Step transition state
const isStepTransitioning = ref(false)
const targetStep = ref<number | null>(null)

// Step definitions - 將現場勘查插入到 step2 與 step3 之間
const steps = [
  { title: '申請人資料', value: 1, subtitle: '申請人資料' },
  { title: '土地資料', value: 2, subtitle: '請填寫土地資料' },
  { title: '現場勘查', value: 3, subtitle: '請填寫現場勘查' }, // 顯示step5內容但位置在第3步
  { title: '灌溉調控設施', value: 4, subtitle: '請填寫灌溉調控設施' }, // 顯示step3內容但位置在第4步
  { title: '田間管路', value: 5, subtitle: '請填寫田間管路' }, // 顯示step4內容但位置在第5步
  { title: '文件列印及完成申報', value: 6, subtitle: '請填寫補助申請資料' },
  { title: '功能測試', value: 7, subtitle: '請填寫結案申報' },
  { title: '佐證及相關文件上傳', value: 8, subtitle: '請上傳佐證及相關文件' },
]


// 格式化日期
const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-TW')
}

// 🆕 統一的通知顯示函數
const showNotificationMessage = (
  title: string,
  message: string = '',
  type: 'success' | 'error' | 'warning' = 'success'
) => {
  const configs = {
    success: {
      color: 'success',
      icon: 'mdi-check-circle',
      iconColor: 'white',
      timeout: 4000
    },
    error: {
      color: 'error',
      icon: 'mdi-alert-circle',
      iconColor: 'white',
      timeout: 6000
    },
    warning: {
      color: 'warning',
      icon: 'mdi-alert',
      iconColor: 'white',
      timeout: 5000
    }
  }

  notificationConfig.value = {
    title,
    message,
    ...configs[type]
  }
  showNotification.value = true
}

// 🆕 錯誤分類處理器 - 遵循單一責任原則
const classifyError = (error: any): DesignChangeErrorType => {
  // 網路連線錯誤
  if (!navigator.onLine || error.code === 'NETWORK_ERROR') {
    return DesignChangeErrorType.NETWORK_ERROR
  }

  // HTTP 狀態碼錯誤
  if (error.response) {
    const status = error.response.status
    if (status >= 400 && status < 500) {
      return DesignChangeErrorType.VALIDATION_ERROR
    }
    if (status >= 500) {
      return DesignChangeErrorType.API_ERROR
    }
  }

  // 儲存相關錯誤
  if (error.message?.includes('save') || error.message?.includes('storage')) {
    return DesignChangeErrorType.SAVE_ERROR
  }

  return DesignChangeErrorType.UNKNOWN_ERROR
}

// 🆕 錯誤訊息映射 - 消除 if-else 特殊情況
const getErrorMessage = (errorType: DesignChangeErrorType, originalError: any) => {
  const errorMessages = {
    [DesignChangeErrorType.NETWORK_ERROR]: {
      title: '網路連線失敗',
      message: '請檢查網路連線後重試'
    },
    [DesignChangeErrorType.SAVE_ERROR]: {
      title: '資料儲存失敗',
      message: '無法儲存當前變更，請稍後重試'
    },
    [DesignChangeErrorType.API_ERROR]: {
      title: '伺服器錯誤',
      message: '伺服器發生內部錯誤，請聯繫管理員'
    },
    [DesignChangeErrorType.VALIDATION_ERROR]: {
      title: '資料驗證失敗',
      message: '請檢查輸入資料是否正確完整'
    },
    [DesignChangeErrorType.UNKNOWN_ERROR]: {
      title: '未知錯誤',
      message: '系統發生未知錯誤，請重新嘗試'
    }
  }

  return errorMessages[errorType]
}

// 🗑️ 移除舊的變更設計功能 - 已被 executeDesignChange 取代

// 新增：計算按鈕顏色
const getButtonColor = () => {
  if (currentStep.value === 3) {
    return step5ButtonConfig.value.color
  } else if (currentStep.value === 7) {
    return step7ButtonConfig.value.color
  }
  return '#3ea0a3'
}

// Step icon and color logic
const getStepIcon = (stepValue: number): string => {
  if (submitting.value && currentStep.value === stepValue) return 'mdi-loading mdi-spin'
  if (currentStep.value > stepValue) return 'mdi-check-circle'
  if (currentStep.value === stepValue) return 'mdi-numeric-'+stepValue+'-circle'
  return 'mdi-circle-outline'
}

const getStepIconColor = (stepValue: number) => {
  if (currentStep.value > stepValue) return 'success'
  if (currentStep.value === stepValue) return '#3ea0a3'
  return 'grey'
}

// Debounced URL update to prevent recursive update issues
const debouncedUpdateStepInURL = debounce((step: number) => {
  router.replace({
    query: { ...route.query, step: step.toString() }
  })
}, 100)

// URL management function that uses debouncing
const updateStepInURL = (step: number) => {
  debouncedUpdateStepInURL(step)
}

// 🎯 優化的下一步處理 - 加入導航狀態檢查
const goToNextStep = () => {
  // 檢查當前步驟是否允許導航
  if (!canGoToNextStep.value) {
    console.log('🚫 edit.vue: Navigation blocked -', navigationBlockingReason.value)
    return
  }

  // 檢查是否正在過渡中
  if (isStepTransitioning.value || isNavigating.value) {
    console.log('🚫 edit.vue: Step transition already in progress')
    return
  }

  if (currentStep.value < steps.length) {
    // 🆕 統一事件驅動：使用映射表統一處理所有步驟
    const stepComponent = stepRefs[currentStep.value]
    if (stepComponent) {
      console.log(`🎯 edit.vue: Calling step${currentStep.value}Ref.handleProceedToNext()`)
      stepComponent.handleProceedToNext()
    } else {
      // 對於沒有引用的步驟，使用傳統驗證方式
      console.log(`🎯 edit.vue: Step ${currentStep.value} has no ref, using traditional validation`)
      handleStepValidated({ valid: true, step: currentStep.value })
    }
  }
}

// 處理 Step7 按鈕配置變化
const handleStep7ButtonConfigChanged = (buttonConfig: { text: string; color: string; icon: string; action: string }) => {
  console.log('Step7 按鈕配置變化:', buttonConfig)
  step7ButtonConfig.value = buttonConfig
}

// 新增：處理 Step5 按鈕配置變化
const handleStep5ButtonConfigChanged = (buttonConfig: { text: string; color: string; icon: string; action: string }) => {
  console.log('Step5 按鈕配置變化:', buttonConfig)
  step5ButtonConfig.value = buttonConfig
}

// 新增：處理案件歸檔事件
const handleCaseArchived = async (eventData: {
  step: number;
  data: Record<string, unknown>;
  reason: string;
}) => {
  console.log('📦 [edit.vue] Handling case archived:', eventData)

  try {
    submitting.value = true

    // 1. 保存歸檔資料
    await grantsStore.updateFormData(eventData.step, eventData.data)
    await grantsStore.saveAllChanges(eventData.step)  // 🔥 使用正確的 dataStep

    // 2. 更新案件狀態為已歸檔
    if (grantsStore.currentGrant) {
      // 這裡可以調用 API 更新案件狀態
      console.log('案件已歸檔，原因：', eventData.reason)
    }

    // 3. 顯示歸檔成功提示
    showNotificationMessage(
      '案件已歸檔',
      `勘查結果不符合，案件已留存歸檔`,
      'warning'
    )

    // 4. 禁用後續編輯功能
    navigationStates.value[eventData.step] = {
      canNavigate: false,
      isEditing: false,
      reason: '案件已歸檔：勘查結果不符合'
    }

  } catch (error) {
    console.error('❌ [edit.vue] Failed to archive case:', error)
    showNotificationMessage(
      '歸檔失敗',
      '案件歸檔過程中發生錯誤',
      'error'
    )
  } finally {
    submitting.value = false
  }
}

// 處理存檔功能（限期改善）
const handleSaveForImprovement = async () => {
  console.log('處理存檔功能：現場勘查未通過驗收，將於改善後複驗')

  try {
    submitting.value = true

    // 保存當前數據
    await saveAllChanges()

    // 顯示成功訊息
    // 這裡可以添加 snackbar 或其他提示
    console.log('存檔成功，待改善後複驗')

    // 不進入下一步，停留在當前步驟
  } catch (error) {
    console.error('存檔失敗:', error)
  } finally {
    submitting.value = false
  }
}

// 新增：處理來自步驟組件的導航狀態變更
const handleNavigationStateChanged = (eventData: {
  step: number;
  canNavigate: boolean;
  isEditing: boolean;
  reason?: string;
}) => {
  console.log(`🎛️ edit.vue: Navigation state changed for step ${eventData.step}:`, eventData)

  // 更新對應步驟的導航狀態
  navigationStates.value[eventData.step] = {
    canNavigate: eventData.canNavigate,
    isEditing: eventData.isEditing,
    reason: eventData.reason
  }
}

// 修改現有的導航函數，結合新的導航狀態檢查
const handleMainButtonClick = () => {
  console.log('主按鈕點擊:', {
    currentStep: currentStep.value,
    step5ButtonConfig: step5ButtonConfig.value,
    step7ButtonConfig: step7ButtonConfig.value
  })

  if (currentStep.value === 3) {
    // 處理 step5（現場勘查）的按鈕點擊
    console.log('委派給 step5 組件處理動作:', step5ButtonConfig.value.action)
    if (step5Ref.value && step5Ref.value.handleActionRequest) {
      step5Ref.value.handleActionRequest(step5ButtonConfig.value.action)
    } else {
      console.error('step5Ref 或 handleActionRequest 方法不存在')
    }
  } else if (currentStep.value === 7) {
    // 委派給 step7 組件處理對應的動作
    console.log('委派給 step7 組件處理動作:', step7ButtonConfig.value.action)
    if (step7Ref.value && step7Ref.value.handleActionRequest) {
      step7Ref.value.handleActionRequest(step7ButtonConfig.value.action)
    } else {
      console.error('step7Ref 或 handleActionRequest 方法不存在')
    }
  } else {
    // 其他步驟的正常邏輯
    goToNextStep()
  }
}

// 🆕 變更設計點擊處理
const handleDesignChangeClick = () => {
  // 🔥 Linus式修復：總是顯示確認對話窗，讓使用者輸入版本說明
  showDesignChangeDialog.value = true
}

// 🆕 執行變更設計 - 重構錯誤處理
const executeDesignChange = async (comment?: string) => {
  if (!grantsStore.currentGrant?.case_number) {
    showNotificationMessage(
      '變更設計失敗',
      '無案件資料，無法建立新版本',
      'error'
    )
    return
  }

  try {
    designChangeLoading.value = true

    // 1. 先保存當前所有變更 - 分離儲存邏輯
    if (grantsStore.hasUnsavedChanges) {
      try {
        await grantsStore.saveAllChanges()
      } catch (saveError) {
        const errorType = classifyError(saveError)
        const errorMsg = getErrorMessage(errorType, saveError)
        showNotificationMessage(errorMsg.title, errorMsg.message, 'error')
        return
      }
    }

    // 2. 收集所有步驟資料 - 修復資料結構污染問題
    console.log('🔄 Implementing version inheritance for design change')

    // 先取得前一版本的完整資料
    const { getCurrentVersionData } = await import('../../services/grantsService')
    const previousVersionData = await getCurrentVersionData(grantsStore.currentGrant.case_number)

    // 🔥 Linus式修復：確保資料格式統一，避免前後端格式混合
    // 提取前一版本中的 steps 格式資料（後端正確格式）
    const previousStepsData = previousVersionData.steps || {}

    // 將當前編輯的資料轉換為 steps 格式
    const currentStepsData: Record<string, any> = {}
    Object.entries(grantsStore.formData).forEach(([stepKey, stepData]) => {
      if (stepKey !== '1' && stepData && Object.keys(stepData).length > 0) {
        currentStepsData[stepKey] = stepData
      }
    })

    // 合併資料：使用統一的 steps 格式
    const allStepsData = {
      steps: {
        ...previousStepsData,   // 前一版本的步驟資料
        ...currentStepsData     // 當前修改的步驟資料
      }
    }

    console.log('📋 Previous version steps:', Object.keys(previousStepsData))
    console.log('✏️ Current editing steps:', Object.keys(currentStepsData))
    console.log('🔄 Final merged structure:', Object.keys(allStepsData))
    console.log('🔄 Steps in final structure:', Object.keys(allStepsData.steps))

    // 3. 調用版本創建 API - 分離 API 邏輯
    const result = await createGrantVersion(
      grantsStore.currentGrant.case_number,
      allStepsData,
      comment || `變更設計 - ${new Date().toLocaleString('zh-TW')}`
    )

    // 4. 更新當前案件的版本資訊
    if (grantsStore.currentGrant.active_version) {
      grantsStore.currentGrant.active_version.version = String(result.version)
      grantsStore.currentGrant.active_version.created_at = result.created_at
    }

    // 5. 觸發版本比較資料的重新載入
    await nextTick()

    // 6. 統一成功回饋
    showNotificationMessage(
      '變更設計成功',
      `新版本 v${result.version} 建立完成`,
      'success'
    )

  } catch (error) {
    // 統一錯誤處理 - 不再有特殊情況
    const errorType = classifyError(error)
    const errorMsg = getErrorMessage(errorType, error)
    showNotificationMessage(errorMsg.title, errorMsg.message, 'error')
  } finally {
    // 清理狀態 - 無論成功失敗都執行
    designChangeLoading.value = false
    showDesignChangeDialog.value = false
    designChangeComment.value = ''
  }
}

// 重置步驟資料處理函數
const handleResetStepData = async () => {
  if (!grantsStore.currentGrant?.case_number || !currentStep.value) {
    showNotificationMessage(
      '重置失敗',
      '無案件資料或當前步驟資訊',
      'error'
    )
    return
  }

  resetStepLoading.value = true

  try {
    // 清空當前步驟的資料
    const emptyData = getDefaultStepData(currentStep.value)

    // 使用現有 API 更新步驟資料為空值
    await grantsStore.saveStepData(currentStep.value, emptyData)

    // 清除 store 中的該步驟資料
    grantsStore.formData[currentStep.value] = {}

    // 觸發當前步驟組件重新載入
    await nextTick()

    showNotificationMessage(
      '重置成功',
      `步驟 ${currentStep.value} 的資料已清除`,
      'success'
    )

  } catch (error) {
    console.error('Reset step data failed:', error)
    showNotificationMessage(
      '重置失敗',
      '清除步驟資料時發生錯誤',
      'error'
    )
  } finally {
    resetStepLoading.value = false
    showResetStepDialog.value = false
  }
}

// 獲取步驟的預設空資料
const getDefaultStepData = (step: number): Record<string, unknown> => {
  // 根據步驟返回預設的空資料結構
  switch (step) {
    case 1:
      return { valid: true }
    case 2:
      return { valid: true }
    case 3:
      return { facilities: [], valid: true }
    case 4:
      return { pipes: [], valid: true }
    case 5:
      return { valid: true }
    case 6:
      return { valid: true }
    case 7:
      return { valid: true }
    case 8:
      return { valid: true }
    default:
      return { valid: true }
  }
}

// 🎯 優化的滾動處理 - 提前滾動避免看到頁面底部內容
const scrollToTopInstantly = () => {
  // 立即滾動到頂部，無動畫
  window.scrollTo(0, 0)
  document.documentElement.scrollTop = 0
  document.body.scrollTop = 0
}





// 🎯 優化的步驟驗證處理 - 加入過渡效果
const handleStepValidated = async ({ valid, step }: { valid: boolean; step: number }) => {
  if (valid && !isNavigating.value && !isStepTransitioning.value) {
    const nextStep = step + 1

    try {
      // 1️⃣ 立即開始過渡狀態
      isNavigating.value = true
      isStepTransitioning.value = true
      submitting.value = true

      // 2️⃣ 立即滾動到頂部
      scrollToTopInstantly()

      // 3️⃣ 保存當前步驟數據
      await saveAllChanges()

      // 4️⃣ 進入下一步或完成表單
      if (step < steps.length) {
        targetStep.value = nextStep
        currentStep.value = nextStep

        // 更新 grantsStore 中的 current_step
        grantsStore.updateCurrentStep(currentStep.value)
        console.log(`Step validated: Updating grantsStore.current_step to ${currentStep.value}`)

        // 更新 URL 和載入下一步數據
        updateStepInURL(currentStep.value)
        await loadStepData(currentStep.value)

        // 5️⃣ 短暫延遲後結束過渡
        setTimeout(() => {
          isStepTransitioning.value = false
          targetStep.value = null
        }, 300)

      } else {
        // 在最後一步完成時也更新 current_step
        grantsStore.updateCurrentStep(steps.length)
        console.log(`Final step completed: Setting grantsStore.current_step to ${steps.length}`)

        // 完成表單，跳轉到申請列表
        isStepTransitioning.value = false
        router.push('/grants')
      }
    } catch (error) {
      console.error('Error saving step data:', error)
      // 發生錯誤時重置狀態
      isStepTransitioning.value = false
      targetStep.value = null
    } finally {
      submitting.value = false
      // Add a delay before allowing navigation again
      setTimeout(() => {
        isNavigating.value = false
      }, 500)
    }
  }
}

// Handle form data updates from step components - 修復無限循環問題
const handleFormDataUpdate = (dataStep: number, data: Record<string, unknown>) => {
  console.log(`🔄 edit.vue handleFormDataUpdate called for dataStep ${dataStep}`);
  console.log('📤 Received data keys:', Object.keys(data));

  // 🔥 關鍵修復：不修改 currentStep，只更新對應 dataStep 的資料
  // currentStep 表示 UI 顯示的步驟，dataStep 表示資料儲存的步驟
  grantsStore.updateFormData(dataStep, data)

  console.log('📊 After updateFormData - grantsStore.hasUnsavedChanges:', grantsStore.hasUnsavedChanges);
  console.log('📊 Updated formData for dataStep:', dataStep);
  console.log('📊 UI currentStep remains:', currentStep.value);

  // Setup autosave if changes are made
  if (grantsStore.hasUnsavedChanges && !autoSaveTimer.value) {
    console.log('⏰ Setting up autosave timer (3 seconds)');
    autoSaveTimer.value = window.setTimeout(async () => {
      console.log('💾 Autosave triggered for current dataStep', dataStep);
      await grantsStore.saveAllChanges(dataStep)  // 🔥 傳遞正確的 dataStep
      autoSaveTimer.value = null
    }, 3000) // Autosave after 3 seconds of inactivity
  } else if (grantsStore.hasUnsavedChanges) {
    console.log('⏰ Autosave timer already exists');
  } else {
    console.log('⚠️ No unsaved changes detected');
  }
}

// 🆕 統一事件驅動架構：通用步驟事件處理器
interface StepEventData {
  step: number
  data: Record<string, unknown>
  valid: boolean
}

// 🆕 統一資料變更事件處理
const handleStepDataChanged = (eventData: StepEventData) => {
  const { step, data, valid } = eventData
  console.log(`📥 edit.vue: Received step-data-changed event from step${step}`)
  console.log(`📊 Step: ${step}, Valid: ${valid}, Data keys:`, Object.keys(data))

  // 使用現有的 handleFormDataUpdate 邏輯處理資料
  handleFormDataUpdate(step, { ...data, valid })
}

// 🆕 統一驗證狀態變更事件處理
const handleStepValidationChanged = (eventData: { step: number, valid: boolean }) => {
  const { step, valid } = eventData
  console.log(`📋 edit.vue: Received validation-changed event from step${step} - Step: ${step}, Valid: ${valid}`)

  // 確保步驟狀態同步
  if (grantsStore.currentStep !== step) {
    grantsStore.updateCurrentStep(step)
  }

  // 更新驗證狀態到 grantsStore
  if (grantsStore.formData[step]) {
    grantsStore.formData[step].valid = valid
  }
}

// 🆕 統一準備進入下一步事件處理
const handleStepReadyToProceed = async (eventData: { step: number, data: Record<string, unknown> }) => {
  const { step, data } = eventData
  console.log(`✅ edit.vue: Received ready-to-proceed event from step${step}`)
  console.log(`📊 Step: ${step}, Data keys:`, Object.keys(data))

  // 先更新最新的資料
  handleFormDataUpdate(step, { ...data, valid: true })

  // 觸發步驟驗證邏輯（進入下一步）
  await handleStepValidated({ valid: true, step })
}

// Save all unsaved changes
const saveAllChanges = async (targetDataStep?: number) => {
  if (autoSaveTimer.value) {
    clearTimeout(autoSaveTimer.value)
    autoSaveTimer.value = null
  }

  return grantsStore.saveAllChanges(targetDataStep)
}

// 🎯 優化的步驟切換處理 - 加入過渡效果和預滾動
const handleStepClick = async (stepValue: number) => {
  if (stepValue === currentStep.value || isNavigating.value || isStepTransitioning.value) return

  try {
    // 1️⃣ 立即開始過渡狀態
    isNavigating.value = true
    isStepTransitioning.value = true
    targetStep.value = stepValue

    // 2️⃣ 立即滾動到頂部，避免看到新頁面底部內容
    scrollToTopInstantly()

    // 3️⃣ 保存當前數據
    await saveAllChanges()

    // 4️⃣ 更新步驟狀態
    currentStep.value = stepValue
    grantsStore.updateCurrentStep(stepValue)
    console.log(`Step clicked: Updating grantsStore.current_step to ${stepValue}`)

    // 5️⃣ 更新 URL 和載入新步驟數據
    updateStepInURL(stepValue)
    await loadStepData(stepValue)

    // 6️⃣ 關閉移動端側邊欄
    if (isSmallScreen.value) {
      drawerOpen.value = false
    }

    // 7️⃣ 短暫延遲後結束過渡
    setTimeout(() => {
      isStepTransitioning.value = false
      targetStep.value = null
      isNavigating.value = false
    }, 300)

  } catch (error) {
    console.error('Failed to switch step:', error)
    // 發生錯誤時重置狀態
    isStepTransitioning.value = false
    targetStep.value = null
    isNavigating.value = false
  }
}

// 🎯 優化的返回處理 - 加入過渡效果和預滾動
const handleGoBack = async () => {
  // 檢查當前步驟是否允許導航
  if (!canGoToPreviousStep.value) {
    console.log('🚫 edit.vue: Navigation blocked -', navigationBlockingReason.value)
    return
  }

  if (currentStep.value > 1 && !isNavigating.value && !isStepTransitioning.value) {
    const previousStep = currentStep.value - 1

    try {
      // 1️⃣ 立即開始過渡狀態
      isNavigating.value = true
      isStepTransitioning.value = true
      targetStep.value = previousStep
      submitting.value = true

      // 2️⃣ 立即滾動到頂部
      scrollToTopInstantly()

      // 3️⃣ 保存當前步驟數據
      await saveAllChanges()

      // 4️⃣ 更新步驟狀態
      currentStep.value = previousStep
      grantsStore.updateCurrentStep(previousStep)
      console.log(`Going back: Updating grantsStore.current_step to ${previousStep}`)

      // 5️⃣ 更新 URL 和載入上一步數據
      updateStepInURL(previousStep)
      await loadStepData(previousStep)

      // 6️⃣ 短暫延遲後結束過渡
      setTimeout(() => {
        isStepTransitioning.value = false
        targetStep.value = null
      }, 300)

    } catch (error) {
      console.error('Error going back to previous step:', error)
      // 發生錯誤時重置狀態
      isStepTransitioning.value = false
      targetStep.value = null
    } finally {
      submitting.value = false
      setTimeout(() => {
        isNavigating.value = false
      }, 500)
    }
  }
}

const ensureCorrectStep = (expectedStep: number) => {
  if (grantsStore.currentStep !== expectedStep) {
    console.warn(`Step mismatch detected. Expected: ${expectedStep}, Actual: ${grantsStore.currentStep}`)
    grantsStore.updateCurrentStep(expectedStep)
  }
}

// 獲取當前步驟對應的資料步驟 - 簡化映射
const getDataStepForCurrentStep = (currentStepValue: number): number => {
  // 直接映射：step3→5, step4→3, step5→4, 其他保持不變
  const mapping: Record<number, number> = {
    3: 5, // 現場勘查使用 step5 的資料
    4: 3, // 灌溉調控設施使用 step3 的資料
    5: 4  // 田間管路使用 step4 的資料
  }
  return mapping[currentStepValue] || currentStepValue
}

// Improved data loading with race condition prevention
let isLoadingData = false
const loadStepData = async (step: number) => {
  if (!route.query.id || isLoadingData) return;

  ensureCorrectStep(step)

  // 🆕 架構重構：step1.vue 和 step2.vue 採用自主載入模式
  // step1.vue 和 step2.vue 會在自己的 onMounted 中直接載入資料，不需要父組件控制
  // 這解決了從 index 導航時的 watch 時序問題
  if (step === 1 || step === 2) {
    console.log(`[edit.vue loadStepData] Skipping step ${step} - autonomous loading`);
    isDataLoaded.value = true;
    return;
  }

  // 🔥 修復步驟重組邏輯：根據直接映射載入正確的資料
  const dataStep = getDataStepForCurrentStep(step)
  console.log(`[edit.vue loadStepData] Step ${step} maps to dataStep ${dataStep}`)

  isLoadingData = true;
  const caseNum = route.query.id as string;
  submitting.value = true; // This seems more like an isLoadingData flag
  isDataLoaded.value = false; // Indicate data for the new step is not yet loaded
  console.log(`[edit.vue loadStepData] Attempting to load data for step: ${step} (dataStep: ${dataStep}), caseNumber: ${caseNum}`);

  try {
    await grantsStore.loadStepData(caseNum, dataStep);
    console.log(`[edit.vue loadStepData] grantsStore.loadStepData for dataStep ${dataStep} successful. Form data for dataStep ${dataStep}:`, JSON.stringify(grantsStore.formData[dataStep], null, 2));
    isDataLoaded.value = true;
  } catch (error) {
    console.error(`[edit.vue loadStepData] Failed to load data for dataStep ${dataStep}:`, error);
  } finally {
    submitting.value = false; // Reset the flag
    isLoadingData = false;
  }
};

// Initialize data with better error handling
onMounted(async () => {
  const caseNumberFromRoute = route.query.id as string;
  const stepParam = route.query.step;
  console.log(`[edit.vue onMounted] Case number from route: ${caseNumberFromRoute}, Step param: ${stepParam}`);

  if (!caseNumberFromRoute) {
    console.error('[edit.vue onMounted] No case number in route, redirecting to /grants.');
    router.push('/grants');
    return;
  }

  try {
    console.log(`[edit.vue onMounted] Calling grantsStore.loadGrant with caseNumber: ${caseNumberFromRoute}`);
    await grantsStore.loadGrant(caseNumberFromRoute);
    console.log('[edit.vue onMounted] grantsStore.loadGrant successful. Current grant:', JSON.stringify(grantsStore.currentGrant, null, 2));

    // 檢查 localStorage 中是否有已保存的 currentStep
    const grantData = GrantStorage.getGrant(caseNumberFromRoute);
    const savedCurrentStep = grantData?.currentStep;

    let startStep = 1;
    if (stepParam) {
      // URL 中有指定步驟，使用 URL 中的步驟
      const stepValue = parseInt(stepParam as string, 10);
      if (!isNaN(stepValue) && stepValue >= 1 && stepValue <= steps.length) {
        startStep = stepValue;
        console.log(`[edit.vue onMounted] startStep determined from route.query.step: ${startStep}`);
      } else {
        console.warn(`[edit.vue onMounted] Invalid stepParam in route: ${stepParam}. Using saved step: ${savedCurrentStep} or defaulting to 1.`);
        startStep = savedCurrentStep || 1;
      }
    } else {
      // URL 中沒有步驟參數，優先使用 localStorage 中保存的步驟
      if (savedCurrentStep && savedCurrentStep >= 1 && savedCurrentStep <= steps.length) {
        startStep = savedCurrentStep;
        console.log(`[edit.vue onMounted] Using saved current_step from localStorage: ${startStep}`);
      } else {
        console.log('[edit.vue onMounted] No valid saved step found, defaulting to step 1.');
        startStep = 1;
      }
    }

    // 使用 updateCurrentStep 來確保步驟同步到 localStorage
    grantsStore.updateCurrentStep(startStep);
    currentStep.value = startStep; // Update local currentStep ref

    console.log(`[edit.vue onMounted] Final startStep: ${startStep}. grantsStore.current_step updated to: ${grantsStore.currentStep}`);

    if (!stepParam) {
      updateStepInURL(startStep); // Update URL if it was not set
    }

    console.log(`[edit.vue onMounted] Calling loadStepData for step: ${startStep}`);
    await loadStepData(startStep);
    console.log(`[edit.vue onMounted] loadStepData for step ${startStep} finished. grantsStore.formData[${startStep}]:`, JSON.stringify(grantsStore.formData[startStep], null, 2));

    isDataLoaded.value = true;
  } catch (error) {
    console.error('[edit.vue onMounted] Failed to initialize grant data:', error);
    // grantsStore.handleError might be called internally, or add a specific error display here
  }
});

// Watch for URL step parameter changes with improved logic
watch(() => route.query.step, (newStepParam, oldStepParam) => {
  // Skip if values are effectively the same or we're currently navigating
  if (isNavigating.value ||
      newStepParam === oldStepParam ||
      (newStepParam && parseInt(newStepParam as string) === currentStep.value)) {
    return
  }

  if (newStepParam) {
    const newStep = parseInt(newStepParam as string, 10)
    if (!isNaN(newStep) && newStep >= 1 && newStep <= steps.length && newStep !== currentStep.value) {
      // Set navigating flag to prevent other updates during this operation
      isNavigating.value = true

      // If step changed in URL, save current step data before changing
      saveAllChanges().then(() => {
        currentStep.value = newStep
        return loadStepData(newStep)
      }).catch(error => {
        console.error('Failed to save data before step change:', error)
      }).finally(() => {
        // Release the navigation lock after a short delay
        setTimeout(() => {
          isNavigating.value = false
        }, 500)
      })
    }
  }
})

// Watch for screen size changes and adapt UI
watch(isSmallScreen, (smallScreen) => {
  if (smallScreen) {
    isRailMode.value = false
    drawerOpen.value = false
  } else {
    drawerOpen.value = true
    isRailMode.value = false // Keep expanded by default
  }
}, { immediate: true })

// Clean up on component unmount
onUnmounted(() => {
  if (autoSaveTimer.value) {
    clearTimeout(autoSaveTimer.value)
    autoSaveTimer.value = null
  }
})

// Route leave guard with unsaved changes check
onBeforeRouteLeave((to, from, next) => {
  // If there are unsaved changes, confirm before leaving
  if (grantsStore.hasUnsavedChanges) {
    if (window.confirm('您有未保存的更改，確定要離開嗎？')) {
      next()
    } else {
      next(false)
    }
  } else {
    next()
  }
})
</script>

<style scoped>
/* 添加背景圖片樣式 */
.grants-edit-container {
  background-image: url('@/assets/bg_index.svg');
  /* background-size: cover;
  background-position: center bottom;
  background-repeat: no-repeat;
  background-attachment: fixed;
  min-height: 100vh; */
}

/* Main content area - Grid layout, no need for complex flex */
.main-content {
  width: 100%;
  transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 0;
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
  /* padding: 0 16px !important; */
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
  /* padding-left: 16px; */
}

/* 內容卡片樣式 */
.content-card {
  background-color: rgba(255, 255, 255, 0.7) !important;
  border: 1px solid rgba(62, 160, 163, 0.1);
  overflow: hidden;
}

/* Navigation drawer with glass effect */
.navigation-drawer-glass {
  /* background-color: rgba(255, 255, 255, 0.5) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.3) !important; */

  /* position: relative; */
  /* overflow: visible !important; */
  /* border-top-left-radius: 0 !important; */
  /* transition: all 0.3s ease; */

  /* 毛玻璃效果 */
  background-color: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(10px) !important;
  -webkit-backdrop-filter: blur(10px) !important;

  /* 調整邊框和陰影效果與 section-card 一致 */
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  /* box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05) !important; */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;

  /* 關鍵修改：調整邊距和高度 */
  margin: 0px 0 !important; /* 與 section-card 一致的上下邊距 */
  /* max-height: calc(100% - 8px) !important; 減去上下邊距總和 */
  border-radius: 12px !important; /* 添加與卡片相同的圓角 */
  /* overflow: hidden !important; */
}

/* Step list items */
.step-list-item {
  margin-bottom: 4px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.step-list-item:hover {
  background-color: rgba(62, 160, 163, 0.1) !important;
}

/* Mobile step card with glass effect */
.mobile-step-card {
  background-color: rgba(255, 255, 255, 0.7) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  border-radius: 12px;
}

/* 固定左右欄位間距的佈局容器 */
.layout-row-with-gap {
  display: flex !important;
  gap: 18px !important; /* 固定24px間距，你可以調整這個數值 */
  flex-wrap: nowrap !important;
}

/* 左側導航欄固定寬度 */
.fixed-sidebar-col {
  flex: 0 0 280px !important; /* 固定280px寬度 */
  max-width: 280px !important;
  /* min-width: 280px !important;
  /* height: auto !important; 根據內容自動調整高度 */
  /* align-self: flex-start !important; 從上方開始排列，不拉伸 */
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Rail 模式時的左側導航欄 */
.fixed-sidebar-col.rail-mode {
  flex: 0 0 60px !important; /* Rail模式時固定60px寬度 */
  max-width: 60px !important;
  min-width: 60px !important;
}

/* 右側內容區域自動填充 */
.fixed-content-col {
  flex: 1 1 auto !important; /* 自動填充剩餘空間 */
  min-width: 0 !important; /* 防止內容溢出 */
  width: auto !important;
}

/* 在小螢幕上保持 Vuetify 原有的響應式行為 */
@media (max-width: 960px) {
  .layout-row-with-gap {
    flex-direction: column !important;
    gap: 16px !important;
  }

  .fixed-sidebar-col,
  .fixed-content-col {
    flex: 1 1 100% !important;
    max-width: 100% !important;
    min-width: 100% !important;
  }
}

/* 禁用狀態樣式 */
.navigation-blocked {
  position: relative;
  transition: all 0.3s ease;

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(158, 158, 158, 0.1);
    border-radius: inherit;
    pointer-events: none;
  }

  /* 禁用時的視覺回饋 */
  &:hover {
    transform: none !important;
    box-shadow: none !important;
  }
}

/* 按鈕懸停效果 */
.next-btn {
  font-weight: 500;
  margin: 8px 0 12px 0;
  transition: all 0.2s ease;
}

.next-btn:hover:not(.navigation-blocked) {
  background-color: #3ea0a3 !important;
  color: white !important;
}

/* Navigation buttons */
.navigation-btn {
  transition: all 0.2s ease;
  font-weight: 500;
}

.navigation-btn:hover:not(.navigation-blocked) {
  box-shadow: 0 2px 8px rgba(62, 160, 163, 0.2) !important;
}

/* 編輯模式狀態指示器 */
.step-indicator {
  .v-chip {
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  }

  .editing-pulse {
    animation: editingPulse 2s ease-in-out infinite;
  }
}

@keyframes editingPulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(255, 193, 7, 0);
  }
}

/* Spinner animation for loading icon */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.mdi-loading.mdi-spin {
  animation: spin 1s infinite linear;
}

/* 🆕 功能項目樣式 */
/* .function-list {
  background-color: rgba(62, 160, 163, 0.02);
  margin: 0 8px;
  border-radius: 8px;
} */

.design-change-item {
  margin-bottom: 4px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.design-change-item:hover {
  background-color: rgba(62, 160, 163, 0.1) !important;
}

/* 🎯 步驟切換過渡效果 */
.step-transition-overlay {
  z-index: 9999;
  backdrop-filter: blur(2px);
  background-color: rgba(255, 255, 255, 0.85) !important;
}

.step-transition-overlay .v-progress-circular {
  margin-bottom: 8px;
}

/* 步驟內容過渡動畫 */
.step-content {
  transition: opacity 0.2s ease-in-out;
}

.step-content.transitioning {
  opacity: 0.3;
}

.function-item-title {
  color: #3ea0a3;
  font-weight: 500;
}

.version-chip {
  font-size: 10px;
  height: 16px;
}

.version-info {
  display: flex;
  align-items: center;
}

/* Rail 模式下的特殊處理 */
.v-navigation-drawer--rail .function-list {
  margin: 0 4px;
}

.v-navigation-drawer--rail .design-change-item {
  min-height: 48px;
}

/* 載入動畫 */
.mdi-spin {
  animation: spin 1s infinite linear;
}
</style>
