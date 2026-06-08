<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSurvey, submitSurveyResponse, getMyResponse } from '@/api/surveys'
import AppLayout from '@/components/AppLayout.vue'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

const route = useRoute()
const router = useRouter()

const survey = ref(null)
const myResponse = ref(null)
const loading = ref(true)
const submitting = ref(false)
const submitted = ref(false)
const error = ref('')
const submitError = ref('')

const answers = reactive({})

const STATUS_LABEL = { draft: 'Черновик', active: 'Активный', completed: 'Завершён', archived: 'Архив' }
const STATUS_BADGE = {
  draft: 'bg-gray-100 text-gray-600',
  active: 'bg-green-100 text-green-700',
  completed: 'bg-blue-100 text-blue-700',
  archived: 'bg-gray-100 text-gray-400',
}

onMounted(async () => {
  try {
    const [surveyRes, responseRes] = await Promise.allSettled([
      getSurvey(route.params.id),
      getMyResponse(route.params.id),
    ])
    if (surveyRes.status === 'fulfilled') {
      survey.value = surveyRes.value.data
      for (const q of survey.value.questions) {
        if (q.question_type === 'multiple') answers[q.id] = new Set()
        else if (q.question_type === 'text') answers[q.id] = ''
        else answers[q.id] = null
      }
    } else { error.value = 'Опрос не найден или недоступен' }
    if (responseRes.status === 'fulfilled' && responseRes.value.status === 200) {
      myResponse.value = responseRes.value.data
    }
  } finally { loading.value = false }
})

const previousAnswers = computed(() => {
  if (!myResponse.value) return {}
  const map = {}
  for (const a of myResponse.value.answers) {
    map[a.question] = { options: new Set(a.selected_options), text: a.text_answer || '' }
  }
  return map
})

function isVisible(qi) {
  const q = survey.value.questions[qi]
  if (q.condition_question_index == null) return true
  const depQ = survey.value.questions[q.condition_question_index]
  if (!depQ) return true
  const depAnswer = answers[depQ.id]
  let selectedIds = depAnswer instanceof Set ? [...depAnswer] : (depAnswer !== null ? [depAnswer] : [])
  if (!selectedIds.length) return false
  return selectedIds.some(optId => {
    const opt = depQ.options.find(o => o.id === optId)
    return opt && opt.text === q.condition_option_text
  })
}

function npsLabel(score) {
  const n = parseInt(score)
  if (n >= 9) return 'Промоутер'
  if (n >= 7) return 'Нейтрал'
  return 'Критик'
}

function npsBtnClass(n, selected) {
  const isSelected = selected === String(n)
  if (n <= 6) return isSelected ? 'border-red-500 bg-red-500 text-white' : 'border-gray-200 bg-white text-gray-600 hover:border-red-400 hover:text-red-500'
  if (n <= 8) return isSelected ? 'border-amber-400 bg-amber-400 text-white' : 'border-gray-200 bg-white text-gray-600 hover:border-amber-400 hover:text-amber-500'
  return isSelected ? 'border-green-500 bg-green-500 text-white' : 'border-gray-200 bg-white text-gray-600 hover:border-green-400 hover:text-green-600'
}

function toggleMultiple(qid, oid) {
  const s = answers[qid]
  s.has(oid) ? s.delete(oid) : s.add(oid)
}

function isChecked(qid, oid) {
  const val = answers[qid]
  return val instanceof Set ? val.has(oid) : val === oid
}

async function submit() {
  submitError.value = ''
  const payload = {
    answers: survey.value.questions
      .filter((_, qi) => isVisible(qi))
      .map(q => {
        const val = answers[q.id]
        if (q.question_type === 'text' || q.question_type === 'scale' || q.question_type === 'nps') {
          return { question: q.id, selected_options: [], text_answer: val || '' }
        }
        return {
          question: q.id,
          selected_options: val instanceof Set ? [...val] : (val !== null ? [val] : []),
          text_answer: '',
        }
      }),
  }
  submitting.value = true
  try { await submitSurveyResponse(survey.value.id, payload); submitted.value = true }
  catch (e) { submitError.value = e.response?.data?.detail || 'Ошибка при отправке ответов' }
  finally { submitting.value = false }
}
</script>

<template>
  <AppLayout :back="router.currentRoute.value.query.from || '/'" back-label="← Назад">
    <div v-if="loading" class="text-gray-400 text-sm">Загрузка...</div>
    <div v-else-if="error" class="text-red-500 text-sm">{{ error }}</div>

    <!-- Успех -->
    <div v-else-if="submitted" class="bg-white rounded-xl shadow-sm p-12 text-center">
      <div class="w-16 h-16 rounded-full bg-green-100 text-green-700 text-2xl flex items-center justify-center mx-auto mb-5">✓</div>
      <h2 class="text-xl font-bold mb-2">Ответы отправлены!</h2>
      <p class="text-gray-400 mb-6">Спасибо за прохождение опроса.</p>
      <Button class="hover:opacity-80" @click="router.push('/')">На главную</Button>
    </div>

    <template v-else-if="survey">
      <!-- Заголовок -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-3">
        <div class="flex items-start justify-between gap-4 mb-2">
          <h1 class="text-xl font-bold text-gray-900">{{ survey.title }}</h1>
          <div class="flex gap-2 shrink-0 flex-wrap">
            <span class="text-xs font-medium px-2.5 py-0.5 rounded-full" :class="STATUS_BADGE[survey.status]">{{ STATUS_LABEL[survey.status] }}</span>
            <span v-if="survey.is_anonymous" class="text-xs font-medium bg-violet-100 text-violet-700 px-2.5 py-0.5 rounded-full">Анонимный</span>
          </div>
        </div>
        <p v-if="survey.description" class="text-sm text-gray-500 leading-relaxed">{{ survey.description }}</p>
      </div>

      <!-- Уже пройден -->
      <div v-if="myResponse" class="flex items-center justify-between bg-green-50 text-green-800 rounded-xl px-5 py-3 text-sm font-medium mb-3">
        <span>✓ Вы уже прошли этот опрос</span>
        <span class="text-xs font-normal opacity-80">
          {{ new Date(myResponse.submitted_at).toLocaleDateString('ru-RU', { day:'numeric', month:'long', year:'numeric' }) }}
        </span>
      </div>

      <div v-if="!survey.questions?.length" class="text-gray-400 text-sm">В этом опросе пока нет вопросов</div>

      <template v-else>
        <div class="flex flex-col gap-3 mb-5">
          <template v-for="(question, qi) in survey.questions" :key="question.id">
            <div v-if="myResponse || isVisible(qi)" class="bg-white rounded-xl shadow-sm p-5" :class="{ 'opacity-90': !!myResponse }">
              <p class="text-[11px] font-semibold uppercase tracking-wide text-indigo-600 mb-1.5">Вопрос {{ qi + 1 }}</p>
              <p class="text-base font-semibold text-gray-900 mb-4">{{ question.text }}</p>

              <!-- Режим просмотра -->
              <template v-if="myResponse">
                <div v-if="question.question_type === 'scale'" class="flex items-center gap-3">
                  <span class="text-sm text-gray-400">Ваш ответ:</span>
                  <span class="w-11 h-11 rounded-lg bg-indigo-600 text-white font-bold text-base flex items-center justify-center">
                    {{ previousAnswers[question.id]?.text || '—' }}
                  </span>
                </div>
                <div v-else-if="question.question_type === 'nps'" class="flex items-center gap-3">
                  <span class="text-sm text-gray-400">Ваш ответ:</span>
                  <span
                    class="w-11 h-11 rounded-lg text-white font-bold text-base flex items-center justify-center"
                    :class="parseInt(previousAnswers[question.id]?.text) >= 9 ? 'bg-green-500' : parseInt(previousAnswers[question.id]?.text) >= 7 ? 'bg-amber-400' : 'bg-red-500'"
                  >{{ previousAnswers[question.id]?.text || '—' }}</span>
                  <span class="text-sm text-gray-500">{{ npsLabel(previousAnswers[question.id]?.text) }}</span>
                </div>
                <div v-else-if="question.question_type === 'text'" class="bg-gray-50 rounded-lg px-3 py-2.5 text-sm text-gray-700 min-h-10 whitespace-pre-wrap">
                  {{ previousAnswers[question.id]?.text || '—' }}
                </div>
                <div v-else class="flex flex-col gap-1">
                  <div v-for="opt in question.options" :key="opt.id" class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors" :class="previousAnswers[question.id]?.options.has(opt.id) ? 'bg-green-50 text-green-800 font-medium' : 'text-gray-500'">
                    <span class="shrink-0 w-4 text-center">
                      <span v-if="previousAnswers[question.id]?.options.has(opt.id)" class="text-green-600">{{ question.question_type === 'single' ? '●' : '✓' }}</span>
                      <span v-else class="text-gray-300">{{ question.question_type === 'single' ? '○' : '□' }}</span>
                    </span>
                    {{ opt.text }}
                  </div>
                </div>
              </template>

              <!-- Интерактивный режим -->
              <template v-else>
                <div v-if="question.question_type === 'scale'" class="flex gap-2 flex-wrap">
                  <button
                    v-for="n in 10"
                    :key="n"
                    class="w-11 h-11 rounded-lg border-2 text-base font-semibold cursor-pointer transition-all"
                    :class="answers[question.id] === String(n)
                      ? 'border-indigo-600 bg-indigo-600 text-white'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-indigo-400 hover:text-indigo-600'"
                    type="button"
                    @click="answers[question.id] = String(n)"
                  >{{ n }}</button>
                </div>
                <div v-else-if="question.question_type === 'nps'" class="space-y-2">
                  <div class="flex gap-1.5 flex-wrap">
                    <button
                      v-for="n in 11"
                      :key="n - 1"
                      class="w-11 h-11 rounded-lg border-2 text-base font-semibold cursor-pointer transition-all"
                      :class="npsBtnClass(n - 1, answers[question.id])"
                      type="button"
                      @click="answers[question.id] = String(n - 1)"
                    >{{ n - 1 }}</button>
                  </div>
                  <div class="flex justify-between text-xs text-gray-400 px-0.5">
                    <span>Точно не порекомендую</span>
                    <span>Точно порекомендую</span>
                  </div>
                </div>
                <Textarea v-else-if="question.question_type === 'text'" v-model="answers[question.id]" :rows="3" placeholder="Введите ваш ответ..." />
                <div v-else-if="question.question_type === 'single'" class="flex flex-col gap-1">
                  <label v-for="opt in question.options" :key="opt.id" class="flex items-center gap-2.5 px-3 py-2 rounded-lg cursor-pointer hover:bg-indigo-50 text-sm transition-colors text-gray-700">
                    <input type="radio" :name="`q-${question.id}`" :value="opt.id" :checked="answers[question.id] === opt.id" class="shrink-0 cursor-pointer" @change="answers[question.id] = opt.id" />
                    {{ opt.text }}
                  </label>
                </div>
                <div v-else-if="question.question_type === 'multiple'" class="flex flex-col gap-1">
                  <label v-for="opt in question.options" :key="opt.id" class="flex items-center gap-2.5 px-3 py-2 rounded-lg cursor-pointer hover:bg-indigo-50 text-sm transition-colors text-gray-700">
                    <input type="checkbox" :checked="isChecked(question.id, opt.id)" class="shrink-0 cursor-pointer" @change="toggleMultiple(question.id, opt.id)" />
                    {{ opt.text }}
                  </label>
                </div>
              </template>
            </div>
          </template>
        </div>

        <template v-if="!myResponse">
          <p v-if="submitError" class="text-red-500 text-sm mb-3">{{ submitError }}</p>
          <div class="flex items-center gap-4">
            <Button :disabled="submitting || survey.status !== 'active'" class="hover:opacity-80" @click="submit">
              {{ submitting ? 'Отправляем...' : 'Отправить ответы' }}
            </Button>
            <span v-if="survey.status !== 'active'" class="text-sm text-gray-400">Опрос не активен</span>
          </div>
        </template>
      </template>
    </template>
  </AppLayout>
</template>
