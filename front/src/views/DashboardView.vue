<script setup>
import { computed, ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { getSurveys } from '@/api/surveys';

const auth = useAuthStore();
const router = useRouter();

const activeSurveys = ref([]);

onMounted(async () => {
  try {
    const { data } = await getSurveys();
    const all = data.results ?? data;
    activeSurveys.value = all.filter((s) => s.status === 'active');
  } catch {
    // ignore
  }
});

const goToCreateSurveys = () => router.push('/create-survey');
const goToListSurveys = () => router.push('/surveys');

const fullName = computed(() => {
  const fn = auth.user?.first_name || '';
  const ln = auth.user?.last_name || '';
  return (fn + ' ' + ln).trim() || auth.user?.phone_number || '';
});

const initials = computed(() => {
  const fn = auth.user?.first_name || '';
  const ln = auth.user?.last_name || '';
  if (fn || ln) return (fn[0] || '') + (ln[0] || '');
  return auth.user?.phone_number?.slice(-2) || '?';
});

async function handleLogout() {
  await auth.logout();
  router.push('/login');
}
</script>

<template>
  <div class="dashboard">
    <header class="topbar">
      <img
        src="/src/assets/logoImage04-2022_081041.svg"
        alt="PulseHR"
        class="logo"
      />

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline">Меню</Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent>
          <DropdownMenuGroup>
            <DropdownMenuLabel>
              <p class="phone">{{ auth.user?.phone_number }}</p>
              <span
                class="badge"
                :class="auth.isHR ? 'badge-hr' : 'badge-employee'"
              >
                {{ auth.isHR ? 'HR-специалист' : 'Сотрудник' }}
              </span>
            </DropdownMenuLabel>
            <DropdownMenuGroup v-if="auth.isHR">
              <DropdownMenuSeparator />
              <DropdownMenuItem @click="goToCreateSurveys"
                >Создать опрос</DropdownMenuItem
              >
              <DropdownMenuItem @click="goToListSurveys"
                >Список опросов</DropdownMenuItem
              >
            </DropdownMenuGroup>
          </DropdownMenuGroup>
          <DropdownMenuSeparator />
          <DropdownMenuGroup>
            <DropdownMenuItem @click="handleLogout">Выйти</DropdownMenuItem>
          </DropdownMenuGroup>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>

    <main class="content">
      <!-- Profile card -->
      <div class="profile-card">
        <div class="avatar">{{ initials }}</div>
        <div class="info">
          <h2>{{ fullName }}</h2>
          <p class="phone">{{ auth.user?.phone_number }}</p>
          <span
            class="badge"
            :class="auth.isHR ? 'badge-hr' : 'badge-employee'"
          >
            {{ auth.isHR ? 'HR-специалист' : 'Сотрудник' }}
          </span>
        </div>
      </div>

      <!-- Active surveys -->
      <div class="surveys-section">
        <h2 class="section-title">Доступные опросы</h2>

        <div v-if="activeSurveys.length === 0" class="empty-msg">
          Активных опросов пока нет
        </div>

        <div v-else class="survey-list">
          <div
            v-for="survey in activeSurveys"
            :key="survey.id"
            class="survey-card"
            @click="router.push(`/surveys/${survey.id}`)"
          >
            <div class="survey-main">
              <div class="survey-title">{{ survey.title }}</div>
              <div v-if="survey.description" class="survey-desc">
                {{ survey.description }}
              </div>
            </div>
            <div class="survey-meta">
              <span v-if="survey.has_responded" class="badge-done">✓ Пройден</span>
              <span v-if="survey.is_anonymous" class="badge-anon">Анонимный</span>
              <span class="survey-questions">
                {{ survey.questions.length }}
                {{
                  survey.questions.length === 1
                    ? 'вопрос'
                    : survey.questions.length < 5
                      ? 'вопроса'
                      : 'вопросов'
                }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f5f5;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  height: 56px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
.logo {
  height: 32px;
  width: auto;
}

.content {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.profile-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 1.75rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}
.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #4f46e5;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  font-weight: 700;
  flex-shrink: 0;
  text-transform: uppercase;
}
.info h2 {
  margin: 0 0 0.25rem;
  font-size: 1.25rem;
}
.phone {
  margin: 0 0 0.6rem;
  color: #555;
  font-size: 0.9rem;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 500;
}
.badge-hr {
  background: #ede9fe;
  color: #6d28d9;
}
.badge-employee {
  background: #e0f2fe;
  color: #0369a1;
}

.section-title {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: #1a1a1a;
}

.empty-msg {
  color: #999;
  font-size: 0.95rem;
}

.survey-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.survey-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.07);
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.survey-card:hover {
  box-shadow: 0 4px 16px rgba(79, 70, 229, 0.13);
}

.survey-main {
  flex: 1;
  min-width: 0;
}
.survey-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a1a;
}
.survey-desc {
  font-size: 0.85rem;
  color: #777;
  margin-top: 0.2rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.survey-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}
.badge-done {
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 500;
  background: #dcfce7;
  color: #166534;
}
.badge-anon {
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-size: 0.78rem;
  background: #ede9fe;
  color: #6d28d9;
}
.survey-questions {
  font-size: 0.85rem;
  color: #888;
}
</style>
