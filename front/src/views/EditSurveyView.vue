<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSurvey, updateSurvey } from '@/api/surveys'
import AppLayout from '@/components/AppLayout.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const saving = ref(false)
const error = ref('')

const STATUS_OPTIONS = [
  { value: 'draft', label: 'Черновик' },
  { value: 'active', label: 'Активный' },
  { value: 'completed', label: 'Завершён' },
  { value: 'archived', label: 'Архив' },
]

const form = reactive({ title: '', description: '', is_anonymous: false, status: 'draft', questions: [] })

onMounted(async () => {
  try {
    const { data } = await getSurvey(route.params.id)
    form.title = data.title
    form.description = data.description || ''
    form.is_anonymous = data.is_anonymous
    form.status = data.status
    form.questions = data.questions.map(q => ({
      text: q.text, question_type: q.question_type, order: q.order,
      options: q.options.map(o => ({ text: o.text, order: o.order })),
      condition_question_index: q.condition_question_index ?? null,
      condition_option_text: q.condition_option_text || '',
    }))
  } catch { error.value = 'Не удалось загрузить опрос' }
  finally { loading.value = false }
})

function newQuestion() {
  return { text: '', question_type: 'single', options: [{ text: '' }], condition_question_index: null, condition_option_text: '' }
}

function addQuestion() { form.questions.push(newQuestion()) }
function removeQuestion(qi) { form.questions.splice(qi, 1) }
function addOption(qi) { form.questions[qi].options.push({ text: '' }) }
function removeOption(qi, oi) { form.questions[qi].options.splice(oi, 1) }

function prevOptions(qi) {
  const result = []
  for (let i = 0; i < qi; i++) {
    const q = form.questions[i]
    if (q.question_type === 'single' || q.question_type === 'multiple') {
      for (const opt of q.options) {
        if (opt.text.trim()) result.push({ label: `Вопрос ${i + 1}: «${opt.text}»`, qIndex: i, optText: opt.text })
      }
    }
  }
  return result
}

function setCondition(qi, val) {
  if (val === '') { form.questions[qi].condition_question_index = null; form.questions[qi].condition_option_text = '' }
  else { const [qIndex, optText] = JSON.parse(val); form.questions[qi].condition_question_index = qIndex; form.questions[qi].condition_option_text = optText }
}

function conditionValue(q) {
  if (q.condition_question_index == null) return ''
  return JSON.stringify([q.condition_question_index, q.condition_option_text])
}

async function submit() {
  error.value = ''
  if (!form.title.trim()) { error.value = 'Введите название опроса'; return }
  const payload = {
    ...form,
    questions: form.questions.map((q, qi) => ({
      text: q.text, question_type: q.question_type, order: qi,
      options: (q.question_type === 'single' || q.question_type === 'multiple')
        ? q.options.filter(o => o.text.trim()).map((o, oi) => ({ text: o.text, order: oi })) : [],
      condition_question_index: q.condition_question_index,
      condition_option_text: q.condition_option_text,
    })),
  }
  saving.value = true
  try { await updateSurvey(route.params.id, payload); router.push('/surveys') }
  catch (e) { error.value = e.response?.data?.detail || 'Ошибка при сохранении' }
  finally { saving.value = false }
}
</script>

<template>
  <AppLayout back="/surveys">
    <div v-if="loading" class="text-gray-400 text-sm">Загрузка...</div>
    <div v-else-if="error && !form.title" class="text-red-500 text-sm">{{ error }}</div>

    <template v-else>
      <h1 class="text-2xl font-bold mb-6">Редактировать опрос</h1>

      <!-- Основная информация -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-4">
        <h2 class="text-base font-semibold text-gray-700 mb-5">Основная информация</h2>

        <div class="mb-4">
          <Label class="mb-1.5 block">Название <span class="text-red-500">*</span></Label>
          <Input v-model="form.title" placeholder="Название опроса" />
        </div>

        <div class="mb-4">
          <Label class="mb-1.5 block">Описание</Label>
          <Textarea v-model="form.description" :rows="3" placeholder="Краткое описание" />
        </div>

        <div class="mb-4">
          <Label class="mb-1.5 block">Статус</Label>
          <select v-model="form.status" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none bg-white focus:border-indigo-500 cursor-pointer">
            <option v-for="s in STATUS_OPTIONS" :key="s.value" :value="s.value">{{ s.label }}</option>
          </select>
        </div>

        <div class="flex items-center justify-between">
          <div>
            <Label class="block">Анонимный опрос</Label>
            <p class="text-xs text-gray-400 mt-0.5">Ответы не будут привязаны к пользователю</p>
          </div>
          <button
            class="relative w-11 h-6 rounded-full border-none cursor-pointer transition-colors duration-200 shrink-0"
            :class="form.is_anonymous ? 'bg-indigo-600' : 'bg-gray-300'"
            type="button"
            @click="form.is_anonymous = !form.is_anonymous"
          >
            <span
              class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-sm transition-transform duration-200"
              :class="form.is_anonymous ? 'translate-x-5' : 'translate-x-0'"
            />
          </button>
        </div>
      </div>

      <!-- Вопросы -->
      <div class="bg-white rounded-xl shadow-sm p-6 mb-4">
        <h2 class="text-base font-semibold text-gray-700 mb-5">Вопросы</h2>

        <p v-if="form.questions.length === 0" class="text-sm text-gray-400 mb-4">
          Вопросов пока нет — нажмите «Добавить вопрос»
        </p>

        <div v-for="(question, qi) in form.questions" :key="qi" class="border border-gray-200 rounded-xl p-5 mb-3 bg-gray-50/70">
          <div class="flex justify-between items-center mb-4">
            <span class="text-sm font-semibold text-indigo-600">Вопрос {{ qi + 1 }}</span>
            <button class="text-gray-400 hover:text-red-500 transition-colors text-sm bg-transparent border-none cursor-pointer" type="button" @click="removeQuestion(qi)">✕</button>
          </div>

          <div class="mb-3">
            <Label class="mb-1.5 block">Текст вопроса <span class="text-red-500">*</span></Label>
            <Input v-model="question.text" placeholder="Введите вопрос" />
          </div>

          <div class="mb-3">
            <Label class="mb-2 block">Тип ответа</Label>
            <div class="flex gap-5 flex-wrap">
              <label v-for="[val, lbl] in [['single','Один вариант'],['multiple','Несколько вариантов'],['scale','Шкала 1–10'],['text','Текстовый ответ'],['nps','NPS (0–10)']]" :key="val" class="flex items-center gap-1.5 text-sm cursor-pointer text-gray-700">
                <input v-model="question.question_type" type="radio" :value="val" class="cursor-pointer" /> {{ lbl }}
              </label>
            </div>
          </div>

          <div v-if="question.question_type === 'single' || question.question_type === 'multiple'" class="mb-3">
            <Label class="mb-2 block">Варианты ответа</Label>
            <div class="flex flex-col gap-2 mb-2">
              <div v-for="(opt, oi) in question.options" :key="oi" class="flex items-center gap-2">
                <input :type="question.question_type === 'single' ? 'radio' : 'checkbox'" disabled class="shrink-0" />
                <Input v-model="opt.text" placeholder="Вариант ответа" class="flex-1" />
                <button v-if="question.options.length > 1" class="text-gray-300 hover:text-red-500 text-sm transition-colors bg-transparent border-none cursor-pointer shrink-0" type="button" @click="removeOption(qi, oi)">✕</button>
              </div>
            </div>
            <button class="text-sm text-gray-500 border border-dashed border-gray-300 hover:border-indigo-400 hover:text-indigo-600 px-3 py-1 rounded-lg transition-colors bg-transparent cursor-pointer" type="button" @click="addOption(qi)">+ Добавить вариант</button>
          </div>

          <div v-if="prevOptions(qi).length > 0">
            <Label class="mb-1.5 block">Условие показа</Label>
            <select class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none bg-white focus:border-indigo-500 cursor-pointer" :value="conditionValue(question)" @change="setCondition(qi, $event.target.value)">
              <option value="">— Всегда показывать —</option>
              <option v-for="opt in prevOptions(qi)" :key="opt.label" :value="JSON.stringify([opt.qIndex, opt.optText])">{{ opt.label }}</option>
            </select>
          </div>
        </div>

        <button class="w-full py-2.5 bg-transparent border-2 border-dashed border-indigo-200 rounded-xl text-sm text-indigo-600 hover:bg-indigo-50 transition-colors cursor-pointer mt-1" type="button" @click="addQuestion">
          + Добавить вопрос
        </button>
      </div>

      <p v-if="error" class="text-red-500 text-sm mb-4">{{ error }}</p>

      <div class="flex justify-end">
        <Button :disabled="saving" class="hover:opacity-80" @click="submit">
          {{ saving ? 'Сохраняем...' : 'Сохранить изменения' }}
        </Button>
      </div>
    </template>
  </AppLayout>
</template>
