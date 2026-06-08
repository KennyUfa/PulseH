<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSurvey } from '@/api/surveys'

const route = useRoute()
const router = useRouter()

const survey = ref(null)
const loading = ref(true)
const error = ref('')

const STATUS_LABEL = {
  draft: 'Черновик',
  active: 'Активный',
  completed: 'Завершён',
  archived: 'Архив',
}

const STATUS_CLASS = {
  draft: 'status-draft',
  active: 'status-active',
  completed: 'status-completed',
  archived: 'status-archived',
}

onMounted(async () => {
  try {
    const { data } = await getSurvey(route.params.id)
    survey.value = data
  } catch {
    error.value = 'Опрос не найден или недоступен'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page">
    <header class="topbar">
      <span class="logo">PulseHR</span>
      <button class="back-btn" @click="router.push('/surveys')">← Назад</button>
    </header>

    <main class="content">
      <div v-if="loading" class="state-msg">Загрузка...</div>
      <div v-else-if="error" class="state-msg error">{{ error }}</div>

      <template v-else-if="survey">
        <div class="survey-header">
          <div class="survey-title-row">
            <h1>{{ survey.title }}</h1>
            <div class="badges">
              <span class="badge-status" :class="STATUS_CLASS[survey.status]">
                {{ STATUS_LABEL[survey.status] }}
              </span>
              <span v-if="survey.is_anonymous" class="badge-anon">Анонимный</span>
            </div>
          </div>
          <p v-if="survey.description" class="survey-desc">{{ survey.description }}</p>
        </div>

        <div v-if="!survey.questions || survey.questions.length === 0" class="state-msg">
          В этом опросе пока нет вопросов
        </div>

        <div v-else class="questions-list">
          <div
            v-for="(question, qi) in survey.questions"
            :key="question.id"
            class="question-card"
          >
            <div class="question-num">Вопрос {{ qi + 1 }}</div>
            <div class="question-text">{{ question.text }}</div>

            <div class="options-list">
              <label
                v-for="option in question.options"
                :key="option.id"
                class="option-row"
              >
                <input
                  :type="question.question_type === 'single' ? 'radio' : 'checkbox'"
                  :name="`question-${question.id}`"
                  disabled
                  class="option-input"
                />
                <span>{{ option.text }}</span>
              </label>
            </div>
          </div>
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

.state-msg { color: #888; font-size: 0.95rem; }
.state-msg.error { color: #e53e3e; }

.survey-header {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.07);
  padding: 1.75rem;
  margin-bottom: 1.5rem;
}

.survey-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.75rem;
}
.survey-title-row h1 { font-size: 1.5rem; margin: 0; }

.badges { display: flex; gap: 0.5rem; flex-shrink: 0; align-items: center; }

.badge-status {
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 500;
}
.status-draft    { background: #f3f4f6; color: #555; }
.status-active   { background: #dcfce7; color: #166534; }
.status-completed { background: #dbeafe; color: #1e40af; }
.status-archived { background: #f3f4f6; color: #9ca3af; }

.badge-anon {
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-size: 0.78rem;
  background: #ede9fe;
  color: #6d28d9;
}

.survey-desc { margin: 0; color: #666; font-size: 0.95rem; line-height: 1.5; }

.questions-list { display: flex; flex-direction: column; gap: 1rem; }

.question-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.07);
  padding: 1.5rem;
}

.question-num { font-size: 0.8rem; font-weight: 600; color: #4f46e5; margin-bottom: 0.4rem; text-transform: uppercase; letter-spacing: 0.03em; }
.question-text { font-size: 1rem; font-weight: 600; color: #1a1a1a; margin-bottom: 1rem; }

.options-list { display: flex; flex-direction: column; gap: 0.6rem; }
.option-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.95rem;
  color: #333;
  cursor: default;
}
.option-input { flex-shrink: 0; }
</style>
