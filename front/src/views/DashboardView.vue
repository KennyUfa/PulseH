<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSurveys } from '@/api/surveys'
import AppLayout from '@/components/AppLayout.vue'

const router = useRouter()
const activeSurveys = ref([])
const search = ref('')

async function fetchSurveys() {
  try {
    const { data } = await getSurveys()
    const all = data.results ?? data
    activeSurveys.value = all.filter(s => s.status === 'active')
  } catch {}
}

let pollTimer = null

onMounted(() => {
  fetchSurveys()
  pollTimer = setInterval(fetchSurveys, 30000)
})

onUnmounted(() => { clearInterval(pollTimer) })

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return activeSurveys.value
  return activeSurveys.value.filter(s => s.title?.toLowerCase().includes(q))
})

function plural(n) {
  return n === 1 ? 'вопрос' : n < 5 ? 'вопроса' : 'вопросов'
}

function deadlineBadge(survey) {
  if (!survey.end_date) return null
  const diff = new Date(survey.end_date) - Date.now()
  if (diff <= 0) return { text: 'Истёк', cls: 'bg-red-100 text-red-600' }
  const days = Math.ceil(diff / 86400000)
  if (days === 0) return { text: 'Сегодня', cls: 'bg-orange-100 text-orange-600' }
  return { text: `Осталось ${days} дн.`, cls: days <= 3 ? 'bg-orange-100 text-orange-600' : 'bg-blue-50 text-blue-600' }
}
</script>

<template>
  <AppLayout>
    <template #wide>
      <div class="bg-[#E8390E] px-6 py-3">
        <input
          v-model="search"
          type="text"
          placeholder="Поиск"
          class="w-full max-w-[1080px] mx-auto block px-3.5 py-2 rounded-lg bg-transparent border border-white/50 text-white placeholder-white/70 text-sm outline-none focus:border-white transition-colors"
        />
      </div>
    </template>

    <div v-if="filtered.length === 0" class="text-center py-12 text-gray-400 text-sm">
      Нет доступных опросов
    </div>

    <div v-else class="flex flex-col gap-3">
      <div
        v-for="s in filtered"
        :key="s.id"
        class="bg-white rounded-xl shadow-sm px-5 py-4 flex items-center justify-between gap-4 cursor-pointer hover:shadow-md transition-shadow"
        @click="router.push(`/surveys/${s.id}`)"
      >
        <div class="flex-1 min-w-0">
          <h3 class="text-base font-bold text-gray-900 mb-0.5">{{ s.title }}</h3>
          <p v-if="s.description" class="text-sm text-gray-400 truncate">{{ s.description }}</p>
        </div>
        <div class="flex flex-col items-end gap-1 shrink-0">
          <span v-if="s.has_responded" class="text-xs font-semibold bg-green-100 text-green-700 px-2.5 py-0.5 rounded-full">✓ Пройден</span>
          <span v-if="deadlineBadge(s)" class="text-xs font-medium px-2.5 py-0.5 rounded-full" :class="deadlineBadge(s).cls">{{ deadlineBadge(s).text }}</span>
          <span v-if="s.is_anonymous" class="text-xs font-medium bg-violet-100 text-violet-700 px-2.5 py-0.5 rounded-full">Анон</span>
          <span class="text-xs text-gray-400">{{ s.questions.length }} {{ plural(s.questions.length) }}</span>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
