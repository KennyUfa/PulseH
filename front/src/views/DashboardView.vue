<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getSurveys } from '@/api/surveys'
import AppLayout from '@/components/AppLayout.vue'

const router = useRouter()
const activeSurveys = ref([])
const search = ref('')

onMounted(async () => {
  try {
    const { data } = await getSurveys()
    const all = data.results ?? data
    activeSurveys.value = all.filter(s => s.status === 'active')
  } catch {}
})

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return activeSurveys.value
  return activeSurveys.value.filter(s => s.title?.toLowerCase().includes(q))
})

function plural(n) {
  return n === 1 ? 'вопрос' : n < 5 ? 'вопроса' : 'вопросов'
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
          <span v-if="s.is_anonymous" class="text-xs font-medium bg-violet-100 text-violet-700 px-2.5 py-0.5 rounded-full">Анон</span>
          <span class="text-xs text-gray-400">{{ s.questions.length }} {{ plural(s.questions.length) }}</span>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
