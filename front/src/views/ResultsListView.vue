<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSurveyResultsList } from '@/api/surveys'
import AppLayout from '@/components/AppLayout.vue'

const router = useRouter()
const surveys = ref([])
const loading = ref(true)
const error = ref('')

const STATUS_LABEL = { draft: 'Черновик', active: 'Активный', completed: 'Завершён', archived: 'Архив' }
const STATUS_BADGE = {
  draft: 'bg-gray-100 text-gray-600',
  active: 'bg-green-100 text-green-700',
  completed: 'bg-blue-100 text-blue-700',
  archived: 'bg-gray-100 text-gray-400',
}

onMounted(async () => {
  try { const { data } = await getSurveyResultsList(); surveys.value = data }
  catch { error.value = 'Не удалось загрузить данные' }
  finally { loading.value = false }
})

function pct(n, total) { return total ? Math.round((n / total) * 100) : 0 }
</script>

<template>
  <AppLayout back="/">
    <h1 class="text-2xl font-bold mb-6">Результаты опросов</h1>

    <p v-if="loading" class="text-gray-400 text-sm">Загрузка...</p>
    <p v-else-if="error" class="text-red-500 text-sm">{{ error }}</p>
    <p v-else-if="surveys.length === 0" class="text-gray-400 text-sm">Опросов пока нет</p>

    <div v-else class="flex flex-col gap-3">
      <div
        v-for="s in surveys"
        :key="s.id"
        class="bg-white rounded-xl shadow-sm p-5 cursor-pointer hover:shadow-md transition-shadow"
        @click="router.push(`/results/${s.id}`)"
      >
        <div class="flex gap-2 mb-2">
          <span class="text-xs font-medium px-2.5 py-0.5 rounded-full" :class="STATUS_BADGE[s.status]">{{ STATUS_LABEL[s.status] }}</span>
          <span v-if="s.is_anonymous" class="text-xs font-medium bg-violet-100 text-violet-700 px-2.5 py-0.5 rounded-full">Анонимный</span>
        </div>
        <h3 class="font-bold text-gray-900 mb-4">{{ s.title }}</h3>

        <!-- Stats -->
        <div class="flex items-center gap-6 flex-wrap">
          <div class="flex flex-col items-center min-w-[52px]">
            <span class="text-2xl font-bold leading-none text-green-600">{{ s.completed_count }}</span>
            <span class="text-[11px] text-gray-400 mt-0.5">прошли</span>
          </div>
          <div class="flex flex-col items-center min-w-[52px]">
            <span class="text-2xl font-bold leading-none text-red-500">{{ s.not_completed_count }}</span>
            <span class="text-[11px] text-gray-400 mt-0.5">не прошли</span>
          </div>
          <div class="flex flex-col items-center min-w-[52px]">
            <span class="text-2xl font-bold leading-none text-indigo-600">{{ s.total_users }}</span>
            <span class="text-[11px] text-gray-400 mt-0.5">всего</span>
          </div>
          <div class="flex-1 min-w-[120px] flex items-center gap-2">
            <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-indigo-600 rounded-full transition-all duration-300" :style="{ width: pct(s.completed_count, s.total_users) + '%' }" />
            </div>
            <span class="text-sm font-semibold text-indigo-600 whitespace-nowrap">{{ pct(s.completed_count, s.total_users) }}%</span>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
