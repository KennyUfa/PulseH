<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSurvey, updateSurvey } from '@/api/surveys'

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

const form = reactive({
  title: '',
  description: '',
  is_anonymous: false,
  status: 'draft',
  questions: [],
})

onMounted(async () => {
  try {
    const { data } = await getSurvey(route.params.id)
    form.title = data.title
    form.description = data.description || ''
    form.is_anonymous = data.is_anonymous
    form.status = data.status
    form.questions = data.questions.map(q => ({
      text: q.text,
      question_type: q.question_type,
      order: q.order,
      options: q.options.map(o => ({ text: o.text, order: o.order })),
    }))
  } catch {
    error.value = 'Не удалось загрузить опрос'
  } finally {
    loading.value = false
  }
})

function newQuestion() {
  return { text: '', question_type: 'single', options: [{ text: '' }] }
}

function addQuestion() { form.questions.push(newQuestion()) }
function removeQuestion(qi) { form.questions.splice(qi, 1) }
function addOption(qi) { form.questions[qi].options.push({ text: '' }) }
function removeOption(qi, oi) { form.questions[qi].options.splice(oi, 1) }

async function submit() {
  error.value = ''
  if (!form.title.trim()) { error.value = 'Введите название опроса'; return }

  const payload = {
    ...form,
    questions: form.questions.map((q, qi) => ({
      ...q,
      order: qi,
      options: q.options.filter(o => o.text.trim()).map((o, oi) => ({ text: o.text, order: oi })),
    })),
  }

  saving.value = true
  try {
    await updateSurvey(route.params.id, payload)
    router.push('/surveys')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Ошибка при сохранении'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="page">
    <header class="topbar">
      <span class="logo">PulseHR</span>
      <button class="back-btn" @click="router.push('/surveys')">← Назад</button>
    </header>

    <main class="content">
      <div v-if="loading" class="state-msg">Загрузка...</div>
      <div v-else-if="error && !form.title" class="state-msg error">{{ error }}</div>

      <template v-else>
        <h1>Редактировать опрос</h1>

        <section class="card">
          <h2>Основная информация</h2>

          <div class="field">
            <label>Название <span class="req">*</span></label>
            <input v-model="form.title" type="text" placeholder="Название опроса" />
          </div>

          <div class="field">
            <label>Описание</label>
            <textarea v-model="form.description" rows="3" placeholder="Краткое описание" />
          </div>

          <div class="field">
            <label>Статус</label>
            <select v-model="form.status" class="select">
              <option v-for="s in STATUS_OPTIONS" :key="s.value" :value="s.value">
                {{ s.label }}
              </option>
            </select>
          </div>

          <div class="field field-row">
            <label class="toggle-label">
              <span>Анонимный опрос</span>
              <span class="hint">Ответы не будут привязаны к пользователю</span>
            </label>
            <button
              class="toggle"
              :class="{ active: form.is_anonymous }"
              type="button"
              @click="form.is_anonymous = !form.is_anonymous"
            >
              <span class="toggle-knob" />
            </button>
          </div>
        </section>

        <section class="card">
          <h2>Вопросы</h2>

          <div v-if="form.questions.length === 0" class="empty-questions">
            Вопросов пока нет — нажмите «Добавить вопрос»
          </div>

          <div v-for="(question, qi) in form.questions" :key="qi" class="question-block">
            <div class="question-header">
              <span class="question-num">Вопрос {{ qi + 1 }}</span>
              <button class="btn-remove" type="button" @click="removeQuestion(qi)">✕</button>
            </div>

            <div class="field">
              <label>Текст вопроса <span class="req">*</span></label>
              <input v-model="question.text" type="text" placeholder="Введите вопрос" />
            </div>

            <div class="field">
              <label>Тип ответа</label>
              <div class="type-select">
                <label class="radio-label">
                  <input v-model="question.question_type" type="radio" value="single" />
                  Один вариант (radio)
                </label>
                <label class="radio-label">
                  <input v-model="question.question_type" type="radio" value="multiple" />
                  Несколько вариантов (checkbox)
                </label>
              </div>
            </div>

            <div class="field">
              <label>Варианты ответа</label>
              <div class="options-list">
                <div v-for="(option, oi) in question.options" :key="oi" class="option-row">
                  <input
                    :type="question.question_type === 'single' ? 'radio' : 'checkbox'"
                    disabled
                    class="option-preview"
                  />
                  <input
                    v-model="option.text"
                    type="text"
                    placeholder="Вариант ответа"
                    class="option-input"
                  />
                  <button
                    v-if="question.options.length > 1"
                    class="btn-remove-sm"
                    type="button"
                    @click="removeOption(qi, oi)"
                  >✕</button>
                </div>
              </div>
              <button class="btn-add-option" type="button" @click="addOption(qi)">
                + Добавить вариант
              </button>
            </div>
          </div>

          <button class="btn-add-question" type="button" @click="addQuestion">
            + Добавить вопрос
          </button>
        </section>

        <p v-if="error" class="error">{{ error }}</p>

        <div class="actions">
          <button class="btn-submit" :disabled="saving" @click="submit">
            {{ saving ? 'Сохраняем...' : 'Сохранить изменения' }}
          </button>
        </div>
      </template>
    </main>
  </div>
</template>

<style scoped>
.page { min-height: 100vh; background: #f5f5f5; }

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  height: 56px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.logo { font-size: 1.3rem; font-weight: 700; color: #4f46e5; }
.back-btn {
  background: none;
  border: 1px solid #ddd;
  padding: 0.4rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #555;
}
.back-btn:hover { border-color: #4f46e5; color: #4f46e5; }

.content { max-width: 760px; margin: 2rem auto; padding: 0 1rem; }
.content h1 { font-size: 1.6rem; margin-bottom: 1.5rem; }

.state-msg { color: #888; font-size: 0.95rem; }
.state-msg.error { color: #e53e3e; }

.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  padding: 1.75rem;
  margin-bottom: 1.5rem;
}
.card h2 { font-size: 1.1rem; margin-bottom: 1.25rem; color: #333; }

.field { margin-bottom: 1.1rem; }
.field label { display: block; font-size: 0.9rem; color: #444; margin-bottom: 0.35rem; font-weight: 500; }
.field input[type=text],
.field textarea {
  width: 100%;
  padding: 0.6rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.95rem;
  outline: none;
  box-sizing: border-box;
  resize: vertical;
  font-family: inherit;
}
.field input:focus, .field textarea:focus { border-color: #4f46e5; }

.select {
  width: 100%;
  padding: 0.6rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.95rem;
  outline: none;
  background: #fff;
  cursor: pointer;
}
.select:focus { border-color: #4f46e5; }

.req { color: #e53e3e; }
.hint { display: block; font-size: 0.8rem; color: #888; font-weight: 400; }

.field-row { display: flex; align-items: center; justify-content: space-between; }
.toggle {
  width: 44px; height: 24px;
  border-radius: 999px;
  border: none;
  background: #ddd;
  cursor: pointer;
  position: relative;
  transition: background 0.2s;
  flex-shrink: 0;
}
.toggle.active { background: #4f46e5; }
.toggle-knob {
  position: absolute;
  top: 3px; left: 3px;
  width: 18px; height: 18px;
  border-radius: 50%;
  background: #fff;
  transition: left 0.2s;
}
.toggle.active .toggle-knob { left: 23px; }

.empty-questions { color: #999; font-size: 0.9rem; margin-bottom: 1rem; }

.question-block {
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 1.25rem;
  margin-bottom: 1rem;
  background: #fafafa;
}
.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.question-num { font-weight: 600; color: #4f46e5; font-size: 0.95rem; }
.btn-remove { background: none; border: none; color: #aaa; cursor: pointer; font-size: 1rem; padding: 0.2rem 0.4rem; }
.btn-remove:hover { color: #e53e3e; }

.type-select { display: flex; gap: 1.5rem; }
.radio-label { display: flex; align-items: center; gap: 0.4rem; font-size: 0.9rem; cursor: pointer; }

.options-list { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 0.6rem; }
.option-row { display: flex; align-items: center; gap: 0.5rem; }
.option-preview { flex-shrink: 0; }
.option-input {
  flex: 1;
  padding: 0.45rem 0.7rem;
  border: 1px solid #ddd;
  border-radius: 7px;
  font-size: 0.9rem;
  outline: none;
}
.option-input:focus { border-color: #4f46e5; }
.btn-remove-sm { background: none; border: none; color: #bbb; cursor: pointer; font-size: 0.85rem; }
.btn-remove-sm:hover { color: #e53e3e; }

.btn-add-option {
  background: none;
  border: 1px dashed #bbb;
  padding: 0.35rem 0.8rem;
  border-radius: 7px;
  cursor: pointer;
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.25rem;
}
.btn-add-option:hover { border-color: #4f46e5; color: #4f46e5; }

.btn-add-question {
  width: 100%;
  padding: 0.65rem;
  background: none;
  border: 2px dashed #c7c7f0;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.95rem;
  color: #4f46e5;
  margin-top: 0.5rem;
}
.btn-add-question:hover { background: #f0f0ff; }

.error { color: #e53e3e; font-size: 0.9rem; margin-bottom: 1rem; }

.actions { display: flex; justify-content: flex-end; margin-bottom: 3rem; }
.btn-submit {
  padding: 0.7rem 2rem;
  background: #4f46e5;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
}
.btn-submit:hover:not(:disabled) { background: #4338ca; }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
