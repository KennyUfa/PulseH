<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getSurveyResults } from '@/api/surveys'
import AppLayout from '@/components/AppLayout.vue'

const route = useRoute()
const data = ref(null)
const loading = ref(true)
const error = ref('')
const openResponse = ref(null)

const STATUS_LABEL = { draft: 'Черновик', active: 'Активный', completed: 'Завершён', archived: 'Архив' }
const STATUS_BADGE = {
  draft: 'bg-gray-100 text-gray-600',
  active: 'bg-green-100 text-green-700',
  completed: 'bg-blue-100 text-blue-700',
  archived: 'bg-gray-100 text-gray-400',
}

onMounted(async () => {
  try { const res = await getSurveyResults(route.params.id); data.value = res.data }
  catch { error.value = 'Не удалось загрузить результаты' }
  finally { loading.value = false }
})

const npsStats = computed(() => {
  if (!data.value?.responses?.length) return []
  const map = {}
  for (const resp of data.value.responses) {
    for (const ans of resp.answers) {
      if (ans.question_type === 'nps') {
        if (!map[ans.question_id]) map[ans.question_id] = { id: ans.question_id, text: ans.question_text, scores: [] }
        const s = parseInt(ans.text_answer)
        if (!isNaN(s)) map[ans.question_id].scores.push(s)
      }
    }
  }
  return Object.values(map).map(q => {
    const total = q.scores.length
    if (!total) return { ...q, total: 0, promoters: 0, neutrals: 0, critics: 0, nps: null }
    const promoters = q.scores.filter(s => s >= 9).length
    const neutrals  = q.scores.filter(s => s >= 7 && s <= 8).length
    const critics   = q.scores.filter(s => s <= 6).length
    const nps = Math.round((promoters / total) * 100) - Math.round((critics / total) * 100)
    return { ...q, total, promoters, neutrals, critics, nps }
  })
})

function npsColor(score) {
  if (score === null) return 'text-gray-400'
  if (score >= 50) return 'text-green-600'
  if (score >= 0) return 'text-amber-500'
  return 'text-red-600'
}

function pct(n, total) { return total ? Math.round((n / total) * 100) : 0 }
function toggle(id) { openResponse.value = openResponse.value === id ? null : id }
function fmtDate(iso) {
  return new Date(iso).toLocaleString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}
function answerDisplay(ans) {
  if (ans.question_type === 'scale' || ans.question_type === 'text') return ans.text_answer || '—'
  return ans.selected_options.length ? ans.selected_options.join(', ') : '—'
}
</script>

<template>
  <AppLayout back="/results">
    <div v-if="loading" class="text-gray-400 text-sm">Загрузка...</div>
    <div v-else-if="error" class="text-red-500 text-sm">{{ error }}</div>

    <template v-else-if="data">
      <!-- Заголовок + статистика -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-4">
        <div class="flex gap-2 mb-2">
          <span class="text-xs font-medium px-2.5 py-0.5 rounded-full" :class="STATUS_BADGE[data.status]">{{ STATUS_LABEL[data.status] }}</span>
          <span v-if="data.is_anonymous" class="text-xs font-medium bg-violet-100 text-violet-700 px-2.5 py-0.5 rounded-full">Анонимный</span>
        </div>
        <h1 class="text-xl font-bold text-gray-900 mb-1">{{ data.title }}</h1>
        <p v-if="data.description" class="text-sm text-gray-400 mb-5">{{ data.description }}</p>

        <div class="flex items-center gap-6 flex-wrap mt-5">
          <div class="flex flex-col items-center min-w-[52px]">
            <span class="text-2xl font-bold leading-none text-green-600">{{ data.completed_count }}</span>
            <span class="text-[11px] text-gray-400 mt-0.5">прошли</span>
          </div>
          <div class="flex flex-col items-center min-w-[52px]">
            <span class="text-2xl font-bold leading-none text-red-500">{{ data.not_completed_count }}</span>
            <span class="text-[11px] text-gray-400 mt-0.5">не прошли</span>
          </div>
          <div class="flex flex-col items-center min-w-[52px]">
            <span class="text-2xl font-bold leading-none text-indigo-600">{{ data.total_users }}</span>
            <span class="text-[11px] text-gray-400 mt-0.5">всего</span>
          </div>
          <div class="flex-1 min-w-[120px] flex items-center gap-2">
            <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full bg-indigo-600 rounded-full transition-all duration-300" :style="{ width: pct(data.completed_count, data.total_users) + '%' }" />
            </div>
            <span class="text-sm font-semibold text-indigo-600 whitespace-nowrap">{{ pct(data.completed_count, data.total_users) }}%</span>
          </div>
        </div>
      </div>

      <!-- NPS-карточки -->
      <div v-if="npsStats.length" class="flex flex-col gap-3 mb-4">
        <div v-for="q in npsStats" :key="q.id" class="bg-white rounded-xl shadow-sm p-6">
          <p class="text-xs font-semibold uppercase tracking-wide text-indigo-600 mb-1">NPS-вопрос</p>
          <h3 class="font-semibold text-gray-900 mb-5">{{ q.text }}</h3>

          <div class="flex items-center gap-8 mb-5 flex-wrap">
            <!-- Итоговый балл -->
            <div class="text-center min-w-[80px]">
              <div class="text-5xl font-bold" :class="npsColor(q.nps)">
                {{ q.nps !== null ? (q.nps > 0 ? '+' : '') + q.nps : '—' }}
              </div>
              <div class="text-xs text-gray-400 mt-1">NPS-балл</div>
            </div>

            <!-- Разбивка -->
            <div class="flex gap-6">
              <div class="text-center">
                <div class="text-2xl font-bold text-green-600">{{ q.promoters }}</div>
                <div class="text-xs text-gray-500 font-medium">Промоутеры</div>
                <div class="text-xs text-gray-400">оценка 9–10</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-amber-500">{{ q.neutrals }}</div>
                <div class="text-xs text-gray-500 font-medium">Нейтралы</div>
                <div class="text-xs text-gray-400">оценка 7–8</div>
              </div>
              <div class="text-center">
                <div class="text-2xl font-bold text-red-500">{{ q.critics }}</div>
                <div class="text-xs text-gray-500 font-medium">Критики</div>
                <div class="text-xs text-gray-400">оценка 0–6</div>
              </div>
            </div>
          </div>

          <!-- Стек-бар -->
          <div class="h-3 rounded-full overflow-hidden flex bg-gray-100">
            <div class="h-full bg-red-400 transition-all duration-500" :style="{ width: (q.critics / q.total * 100) + '%' }" />
            <div class="h-full bg-amber-400 transition-all duration-500" :style="{ width: (q.neutrals / q.total * 100) + '%' }" />
            <div class="h-full bg-green-500 transition-all duration-500" :style="{ width: (q.promoters / q.total * 100) + '%' }" />
          </div>
          <div class="flex justify-between text-xs text-gray-400 mt-1">
            <span>Критики</span>
            <span>Промоутеры</span>
          </div>
        </div>
      </div>

      <!-- Нет ответов -->
      <div v-if="data.responses.length === 0" class="bg-white rounded-xl shadow-sm p-8 text-center text-gray-400 text-sm">
        Ещё никто не прошёл этот опрос
      </div>

      <template v-else>
        <h2 class="text-base font-bold text-gray-700 mb-3">
          {{ data.is_anonymous ? 'Анонимные ответы' : 'Ответы сотрудников' }}
          <span class="text-gray-400 font-normal text-sm ml-1">({{ data.responses.length }})</span>
        </h2>

        <div class="flex flex-col gap-2">
          <div v-for="resp in data.responses" :key="resp.id" class="bg-white rounded-xl shadow-sm overflow-hidden">
            <!-- Шапка ответа -->
            <div class="flex items-center justify-between px-5 py-4 cursor-pointer hover:bg-gray-50 transition-colors" @click="toggle(resp.id)">
              <div class="flex items-center gap-3">
                <template v-if="!data.is_anonymous && resp.user">
                  <div class="w-9 h-9 rounded-full bg-indigo-600 text-white flex items-center justify-center text-sm font-bold shrink-0">
                    {{ resp.user.name[0]?.toUpperCase() || '?' }}
                  </div>
                  <div>
                    <p class="text-sm font-semibold text-gray-900">{{ resp.user.name }}</p>
                    <p class="text-xs text-gray-400">{{ resp.user.phone }}</p>
                  </div>
                </template>
                <template v-else>
                  <div class="w-9 h-9 rounded-full bg-gray-400 text-white flex items-center justify-center text-sm font-bold shrink-0">?</div>
                  <p class="text-sm font-semibold text-gray-700">Анонимный участник</p>
                </template>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-xs text-gray-400">{{ fmtDate(resp.submitted_at) }}</span>
                <span class="text-gray-400 text-xl transition-transform duration-200 inline-block" :class="openResponse === resp.id ? 'rotate-90' : ''">›</span>
              </div>
            </div>

            <!-- Ответы -->
            <div v-if="openResponse === resp.id" class="border-t border-gray-100 px-5 py-4 flex flex-col gap-4">
              <div v-for="ans in resp.answers" :key="ans.question_id">
                <p class="text-xs text-gray-400 font-medium mb-1">{{ ans.question_text }}</p>
                <div class="text-sm font-medium text-gray-900">
                  <template v-if="ans.question_type === 'scale'">
                    <span class="inline-flex items-center justify-center w-9 h-9 rounded-lg bg-indigo-600 text-white font-bold text-base">{{ ans.text_answer || '—' }}</span>
                    <span class="text-xs text-gray-400 ml-2">/ 10</span>
                  </template>
                  <span v-else-if="ans.question_type === 'text'" class="font-normal text-gray-600 whitespace-pre-wrap">{{ answerDisplay(ans) }}</span>
                  <span v-else>{{ answerDisplay(ans) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </template>
  </AppLayout>
</template>
