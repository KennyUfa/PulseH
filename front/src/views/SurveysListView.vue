<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getSurveys } from '@/api/surveys'
import AppLayout from '@/components/AppLayout.vue'
import { Button } from '@/components/ui/button'

const router = useRouter()
const auth = useAuthStore()
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
  try {
    const { data } = await getSurveys()
    surveys.value = data.results ?? data
  } catch {
    error.value = 'Не удалось загрузить опросы'
  } finally {
    loading.value = false
  }
})

function plural(n) {
  return n === 1 ? 'вопрос' : n < 5 ? 'вопроса' : 'вопросов'
}
</script>

<template>
  <AppLayout back="/">
    <template #actions>
      <Button v-if="auth.isHR" size="sm" class="hover:opacity-80" @click="router.push('/create-survey')">
        + Создать опрос
      </Button>
    </template>

    <h1 class="text-2xl font-bold mb-6">Список опросов</h1>

    <p v-if="loading" class="text-gray-400 text-sm">Загрузка...</p>
    <p v-else-if="error" class="text-red-500 text-sm">{{ error }}</p>
    <p v-else-if="surveys.length === 0" class="text-gray-400 text-sm">Опросов пока нет</p>

    <div v-else class="flex flex-col gap-3">
      <div
        v-for="s in surveys"
        :key="s.id"
        class="bg-white rounded-xl shadow-sm px-5 py-4 flex items-center justify-between gap-4 cursor-pointer hover:shadow-md transition-shadow"
        @click="router.push(`/surveys/${s.id}`)"
      >
        <div class="flex-1 min-w-0">
          <p class="font-semibold text-gray-900">{{ s.title }}</p>
          <p v-if="s.description" class="text-sm text-gray-400 truncate mt-0.5">{{ s.description }}</p>
        </div>
        <div class="flex items-center gap-2 shrink-0 flex-wrap justify-end">
          <span class="text-xs font-medium px-2.5 py-0.5 rounded-full" :class="STATUS_BADGE[s.status]">{{ STATUS_LABEL[s.status] }}</span>
          <span v-if="s.is_anonymous" class="text-xs font-medium bg-violet-100 text-violet-700 px-2.5 py-0.5 rounded-full">Анонимный</span>
          <span class="text-sm text-gray-400">{{ s.questions.length }} {{ plural(s.questions.length) }}</span>
          <Button v-if="auth.isHR" variant="outline" size="xs" class="hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-300" @click.stop="router.push(`/surveys/${s.id}/edit`)">
            Изменить
          </Button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>
