<template>
  <!-- Floating Report Bug Label -->
  <v-btn-group
    color="error"
    density="compact"
    rounded="pill"
    divided
    variant="flat"
    class="report-bug-btn"
    size="small"
  >
    <v-btn
      icon
      @click="printScreen"
    >
      <v-icon icon="mdi-menu-left" />
    </v-btn>
    <v-btn
      prepend-icon="mdi-bug"
      @click="handleReportBug"
    >
      <div>回報問題</div>
      <v-dialog
        activator="parent"
        max-width="500"
      >
        <template
          #default="{ isActive }"
        >
          <v-card rounded="lg">
            <v-card-title class="d-flex justify-space-between align-center">
              <div class="text-h5 text-medium-emphasis ps-2">
                問題回報
              </div>

              <v-btn
                icon="mdi-close"
                variant="text"
                rounded="circle"
                @click="isActive.value = false"
              />
            </v-card-title>

            <v-divider class="mb-4" />

            <v-card-text>
              <div class="text-medium-emphasis mb-4">
                Invite collaborators to your network and grow your
                connections.
              </div>

              <div class="mb-2">
                Message (optional)
              </div>

              <v-textarea
                :counter="300"
                class="mb-2"
                rows="2"
                variant="outlined"
                persistent-counter
              />

              <div class="text-overline mb-2">
                PREMIUM
              </div>

              <div class="text-medium-emphasis mb-1">
                Share with unlimited people and get more insights about your
                network. Try Premium Free for 30 days.
              </div>

              <v-btn
                class="text-none font-weight-bold ms-n4"
                color="primary"
                text="Retry Premium Free"
                variant="text"
              />
            </v-card-text>

            <v-divider class="mt-2" />

            <v-card-actions class="my-2 d-flex justify-end">
              <v-btn
                class="text-none"
                rounded="xl"
                text="Cancel"
                @click="isActive.value = false"
              />

              <v-btn
                class="text-none"
                color="primary"
                rounded="xl"
                text="Send"
                variant="flat"
                @click="isActive.value = false"
              />
            </v-card-actions>
          </v-card>
        </template>
      </v-dialog>
    </v-btn>
  </v-btn-group>
</template>

<script lang="ts" setup>
  const handleReportBug = () => {
    // Add your bug report logic here
    console.log('Report bug clicked')
  }
  const printScreen = () => {
    navigator.mediaDevices.getDisplayMedia({ video: true })
    .then((stream) => {
      // 建立 video 元素播放捕捉到的畫面
      const video = document.createElement('video');
      video.srcObject = stream;
      video.play();

      video.onloadedmetadata = () => {
        // 當 video 元素載入後，利用 canvas 截圖
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        } else {
          console.error("Failed to get 2D context from canvas.");
        }
        const imgData = canvas.toDataURL('image/png');

        // 停止視頻流
        stream.getTracks().forEach(track => track.stop());

        // 接續操作，例如顯示圖片或觸發下載
        const link = document.createElement('a');
        link.href = imgData;
        link.download = 'screenshot.png';
        link.click();
      }
    })
    .catch((error) => {
      console.error("Error capturing screen:", error);
    });
  }
</script>

<style scoped>
  .report-bug-btn {
    position: fixed;
    right: -165px;
    top: 50%;
    transform: rotate(-90deg);
    transform-origin: left bottom;
    z-index: 100;
  }
  /* Optional: Add hover effect to slightly reveal the button */
  .report-bug-btn:hover {
    right: -145px;
  }
</style>
