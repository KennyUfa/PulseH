<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getSurveys } from '@/api/surveys'

const router = useRouter()
const auth = useAuthStore()
const surveys = ref([])
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
    const { data } = await getSurveys()
    surveys.value = data.results ?? data
  } catch {
    error.value = 'Не удалось загрузить опросы'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page">
    <header class="topbar">
      <span class="logo">PulseHR</span>
      <div class="topbar-actions">
        <button class="btn-create" @click="router.push('/create-survey')">+ Создать опрос</button>
        <button class="back-btn" @click="router.push('/')">← Назад</button>
      </div>
    </header>

    <main class="content">
      <h1>Список опросов</h1>

      <div v-if="loading" class="state-msg">Загрузка...</div>
      <div v-else-if="error" class="state-msg error">{{ error }}</div>
      <div v-else-if="surveys.length === 0" class="state-msg">Опросов пока нет</div>

      <div v-else class="survey-list">
        <div v-for="survey in surveys" :key="survey.id" class="survey-card" @click="router.push(`/surveys/${survey.id}`)">
          <div class="survey-main">
            <div class="survey-title">{{ survey.title }}</div>
            <div v-if="survey.description" class="survey-desc">{{ survey.description }}</div>
          </div>
          <div class="survey-meta">
            <span class="badge-status" :class="STATUS_CLASS[survey.status]">
              {{ STATUS_LABEL[survey.status] }}
            </span>
            <span v-if="survey.is_anonymous" class="badge-anon">Анонимный</span>
            <span class="survey-questions">
              {{ survey.questions.length }}
              {{ survey.questions.length === 1 ? 'вопрос' : survey.questions.length < 5 ? 'вопроса' : 'вопросов' }}
            </span>
            <button
              v-if="auth.isHR"
              class="btn-edit"
              @click.stop="router.push(`/surveys/${survey.id}/edit`)"
            >Изменить</button>
          </div>
        </div>
      </div>
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
.topbar-actions { display: flex; gap: 0.75rem; align-items: center; }

.btn-create {
  padding: 0.4rem 1rem;
  background: #4f46e5;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
}
.btn-create:hover { background: #4338ca; }

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

.content { max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
.content h1 { font-size: 1.6rem; margin-bottom: 1.5rem; }

.state-msg { color: #888; font-size: 0.95rem; }
.state-msg.error { color: #e53e3e; }

.survey-list { display: flex; flex-direction: column; gap: 0.75rem; }

.survey-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.07);
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.survey-card:hover { box-shadow: 0 4px 16px rgba(79,70,229,0.13); }
.survey-main { flex: 1; min-width: 0; }
.survey-title { font-size: 1rem; font-weight: 600; color: #1a1a1a; }
.survey-desc {
  font-size: 0.85rem;
  color: #777;
  margin-top: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.survey-meta { display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0; }

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

.survey-questions { font-size: 0.85rem; color: #888; }

.btn-edit {
  padding: 0.25rem 0.75rem;
  font-size: 0.8rem;
  background: none;
  border: 1px solid #c7c7f0;
  border-radius: 6px;
  color: #4f46e5;
  cursor: pointer;
  white-space: nowrap;
}
.btn-edit:hover { background: #f0f0ff; }
</style>
