<template>
  <v-container
    fluid
  >
    <v-card
      class="mx-auto mb-10"
      density="compact"
      variant="text"
      max-width="1000"
      border
    >
      <v-sheet
        border
        rounded
      >
        <v-data-table
          :headers="headers"
          :hide-default-footer="books.length < 11"
          :items="books"
          class="text-h6"
        >
          <template #top>
            <v-toolbar flat>
              <v-toolbar-title>
                <v-icon
                  color="medium-emphasis"
                  icon="mdi-newspaper"
                  size="large"
                  start
                />
                最新消息
              </v-toolbar-title>

              <!-- <v-spacer />

              <v-btn
                class="me-2"
                prepend-icon="mdi-plus"
                rounded="lg"
                text="Add a Book"
                border
                @click="add"
              /> -->
            </v-toolbar>
          </template>

          <template #[`item.title`]="{ value }">
            <v-chip
              :text="value"
              border="thin opacity-25"
              prepend-icon="mdi-book"
              label
            >
              <template #prepend>
                <v-icon
                  color="medium-emphasis"
                />
              </template>
            </v-chip>
          </template>

          <template #[`item.actions`]="{ item }">
            <div class="d-flex ga-2 justify-end">
              <v-icon
                color="medium-emphasis"
                icon="mdi-pencil"
                size="small"
                @click="edit(item.id)"
              />

              <v-icon
                color="medium-emphasis"
                icon="mdi-delete"
                size="small"
                @click="remove(item.id)"
              />
            </div>
          </template>

          <template #no-data>
            <v-btn
              prepend-icon="mdi-backup-restore"
              rounded="lg"
              text="Reset data"
              variant="text"
              border
              @click="reset"
            />
          </template>
        </v-data-table>
      </v-sheet>
    </v-card>

    <v-dialog
      v-model="dialog"
      max-width="500"
    >
      <v-card
        :subtitle="`${isEditing ? 'Update' : 'Create'} your favorite book`"
        :title="`${isEditing ? 'Edit' : 'Add'} a Book`"
      >
        <template #text>
          <v-row>
            <v-col cols="12">
              <v-text-field
                v-model="record.title"
                label="Title"
              />
            </v-col>

            <v-col
              cols="12"
              md="6"
            >
              <v-text-field
                v-model="record.author"
                label="Author"
              />
            </v-col>

            <v-col
              cols="12"
              md="6"
            >
              <v-select
                v-model="record.genre"
                :items="['Fiction', 'Dystopian', 'Non-Fiction', 'Sci-Fi']"
                label="Genre"
              />
            </v-col>

            <v-col
              cols="12"
              md="6"
            >
              <v-text-field
                v-model="record.year"
                type="number"
                label="Year"
                :rules="[
                  (v: number) => !!v || 'Year is required',
                  (v: number) => v <= adapter.getYear(adapter.date()) || 'Year cannot be in future',
                  (v: number) => v >= 1 || 'Year must be positive'
                ]"
                :max="adapter.getYear(adapter.date())"
                :min="1"
                hide-spin-buttons
              />
            </v-col>

            <v-col
              cols="12"
              md="6"
            >
              <v-number-input
                v-model="record.pages"
                :min="1"
                label="Pages"
              />
            </v-col>
          </v-row>
        </template>

        <v-divider />

        <v-card-actions class="bg-surface-light">
          <v-btn
            text="Cancel"
            variant="plain"
            @click="dialog = false"
          />

          <v-spacer />

          <v-btn
            text="Save"
            @click="save"
          />
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-card
      class="mx-auto mb-10"
      density="compact"
      variant="text"
      max-width="1000"
      border
    >
      <v-sheet
        border
        rounded
      >
        <v-data-table
          :headers="headers"
          :hide-default-footer="books.length < 11"
          :items="books"
          class="text-h6"
        >
          <template #top>
            <v-toolbar flat>
              <v-toolbar-title>
                <v-icon
                  color="medium-emphasis"
                  icon="mdi-download"
                  size="large"
                  start
                />
                文件下載
              </v-toolbar-title>

              <v-spacer />
            </v-toolbar>
          </template>

          <template #[`item.title`]="{ value }">
            <v-chip
              :text="value"
              border="thin opacity-25"
              prepend-icon="mdi-book"
              label
            >
              <template #prepend>
                <v-icon
                  color="medium-emphasis"
                />
              </template>
            </v-chip>
          </template>

          <template #[`item.actions`]="{ item }">
            <div class="d-flex ga-2 justify-end">
              <v-icon
                color="medium-emphasis"
                icon="mdi-pencil"
                size="small"
                @click="edit(item.id)"
              />

              <v-icon
                color="medium-emphasis"
                icon="mdi-delete"
                size="small"
                @click="remove(item.id)"
              />
            </div>
          </template>

          <template #no-data>
            <v-btn
              prepend-icon="mdi-backup-restore"
              rounded="lg"
              text="Reset data"
              variant="text"
              border
              @click="reset"
            />
          </template>
        </v-data-table>
      </v-sheet>
    </v-card>

    <v-card
      class="mx-auto mb-10"
      density="compact"
      variant="text"
      max-width="1000"
      border
    >
      <v-toolbar flat>
        <v-toolbar-title>
          <v-icon
            color="medium-emphasis"
            icon="mdi-currency-usd"
            size="large"
            start
          />
          預算執行
        </v-toolbar-title>

        <v-spacer />
      </v-toolbar>
      <v-card-title class="text-overline">
        <div class="caption">
          執行率
        </div>

        <div class="text-green-darken-3 text-h3 font-weight-bold">
          90%
        </div>

        <div class="text-h6 text-medium-emphasis font-weight-regular">
          尚餘 NT$2,938.00 可支用
        </div>
      </v-card-title>
      <br>
      <v-card-text>
        <div
          :style="`right: calc(${review})`"
          class="position-absolute mt-n8 text-caption text-green-darken-3"
        >
          已驗收
        </div>
        <v-progress-linear
          color="green-darken-3"
          height="22"
          model-value="90"
          rounded="lg"
        >
          <v-badge
            :style="`right: ${review}`"
            class="position-absolute"
            color="white"
            dot
            inline
          />
        </v-progress-linear>

        <div class="d-flex justify-space-between py-3">
          <span class="text-green-darken-3 font-weight-medium">
            預定執行 NT$26,442.00
          </span>

          <span class="text-medium-emphasis"> 共編列 NT$29,380.00  </span>
        </div>
      </v-card-text>

      <v-divider />

      <v-list-item
        append-icon="mdi-chevron-right"
        lines="two"
        subtitle="本年度預算執行即時資訊"
        link
      />
    </v-card>

    <!-- 背景圖 -->
    <!-- <div
      class="login-background"
    /> -->
  </v-container>
  <div>
    <!-- <p
      class="login-background"
    /> -->
  </div>
</template>

<script lang="ts" setup>
  import { useDate } from 'vuetify'
  const review = '18%'
  // const headers = [
  //   { title: '公告', key: 'title', align: 'start', sortable: true },
  //   { title: '內容', key: 'content', align: 'start', sortable: false },
  //   { title: '發佈時間', key: 'publishDate', align: 'end', sortable: true },
  // ]
  const adapter = useDate()

  const DEFAULT_RECORD = {
    id: 0,
    title: '',
    author: '',
    genre: '',
    year: adapter.getYear(adapter.date()),
    pages: 1,
  }

  interface Book {
    id: number;
    title: string;
    author: string;
    genre: string;
    year: number;
    pages: number;
  }

  const books = ref<Book[]>([])
  const record = ref(DEFAULT_RECORD)
  const dialog = shallowRef(false)
  const isEditing = shallowRef(false)

  const headers = [
    { title: '公告', key: 'title', align: 'start' as const },
    { title: '內容', key: 'author', align: 'start' as const },
    { title: '發布時間', key: 'year', align: 'end' as const }
  ]

  onMounted(() => {
    reset()
  })

  // function add() {
  //   isEditing.value = false
  //   record.value = DEFAULT_RECORD
  //   dialog.value = true
  // }

  function edit(id: number) {
    isEditing.value = true

    const found = books.value.find(book => book.id === id)

    if (found) {
      record.value = {
        id: found.id,
        title: found.title,
        author: found.author,
        genre: found.genre,
        year: found.year,
        pages: found.pages,
      }
    }

    dialog.value = true
  }

  function remove(id: number) {
    const index = books.value.findIndex(book => book.id === id)
    books.value.splice(index, 1)
  }

  function save() {
    if (isEditing.value) {
      const index = books.value.findIndex(book => book.id === record.value.id)
      books.value[index] = record.value
    } else {
      record.value.id = books.value.length + 1
      books.value.push(record.value)
    }

    dialog.value = false
  }

  function reset() {
    dialog.value = false
    record.value = DEFAULT_RECORD
    books.value = [
      {
        id: 1,
        title: 'To Kill a Mockingbird',
        author: 'Harper Lee',
        genre: 'Fiction',
        year: 1960,
        pages: 281,
      },
      {
        id: 2,
        title: '1984',
        author: 'George Orwell',
        genre: 'Dystopian',
        year: 1949,
        pages: 328,
      },
      {
        id: 3,
        title: 'The Great Gatsby',
        author: 'F. Scott Fitzgerald',
        genre: 'Fiction',
        year: 1925,
        pages: 180,
      },
      {
        id: 4,
        title: 'Sapiens',
        author: 'Yuval Noah Harari',
        genre: 'Non-Fiction',
        year: 2011,
        pages: 443,
      },
      {
        id: 5,
        title: 'Dune',
        author: 'Frank Herbert',
        genre: 'Sci-Fi',
        year: 1965,
        pages: 412,
      },
    ]
  }

</script>

<style scoped>

</style>
