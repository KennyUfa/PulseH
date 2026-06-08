<script setup>
import { computed, ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import { getSurveys } from '@/api/surveys';

const auth = useAuthStore();
const router = useRouter();

const activeSurveys = ref([]);
const search = ref('');
const menuOpen = ref(false);

onMounted(async () => {
  try {
    const { data } = await getSurveys();
    const all = data.results ?? data;
    activeSurveys.value = all.filter((s) => s.status === 'active');
  } catch {
    // ignore
  }
});

const filteredSurveys = computed(() => {
  const q = search.value.trim().toLowerCase();
  if (!q) return activeSurveys.value;
  return activeSurveys.value.filter(s => s.title?.toLowerCase().includes(q));
});

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

function closeMenu() { menuOpen.value = false; }

function nav(path) { router.push(path); closeMenu(); }

async function handleLogout() {
  closeMenu();
  await auth.logout();
  router.push('/login');
}
</script>

<template>
  <div class="page">
    <header class="header">
      <img src="/src/assets/logoImage04-2022_081041.svg" alt="PulseHR" class="logo" />

      <div class="user-wrap">
        <button class="user-btn" @click="menuOpen = !menuOpen">
          <div class="avatar">{{ initials }}</div>
        </button>

        <Transition name="dd">
          <div v-if="menuOpen" class="dropdown">
            <div class="dd-section">
              <p class="dd-sub">{{ fullName }}</p>
              <p class="dd-phone">{{ auth.user?.phone_number }}</p>
              <span class="badge" :class="auth.isHR ? 'badge-hr' : 'badge-employee'">
                {{ auth.isHR ? 'HR-специалист' : 'Сотрудник' }}
              </span>
            </div>

            <template v-if="auth.isHR">
              <div class="dd-section">
                <button class="dd-item" @click="nav('/create-survey')">Создать опрос</button>
                <button class="dd-item" @click="nav('/surveys')">Список опросов</button>
              </div>
            </template>

            <div class="dd-section">
              <button class="dd-item dd-logout" @click="handleLogout">Выйти</button>
            </div>
          </div>
        </Transition>
      </div>
    </header>

    <div v-if="menuOpen" class="backdrop" @click="closeMenu" />

    <div class="search-bar">
      <div class="search-input-wrap">
        <input v-model="search" type="text" placeholder="Поиск" class="search-input" />
      </div>
    </div>

    <div v-if="filteredSurveys.length === 0" class="empty">
      Нет доступных опросов
    </div>

    <div v-else class="list">
      <div
        v-for="survey in filteredSurveys"
        :key="survey.id"
        class="card"
        @click="router.push(`/surveys/${survey.id}`)"
      >
        <div class="card-main">
          <div class="card-left">
            <h3 class="card-title">{{ survey.title }}</h3>
            <p v-if="survey.description" class="card-desc">{{ survey.description }}</p>
          </div>
          <div class="card-right">
            <span v-if="survey.has_responded" class="badge-done">✓ Пройден</span>
            <span v-if="survey.is_anonymous" class="type-badge">Анон</span>
            <span class="card-questions">
              {{ survey.questions.length }}
              {{ survey.questions.length === 1 ? 'вопрос' : survey.questions.length < 5 ? 'вопроса' : 'вопросов' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { min-height: 100vh; background: #fff; }

.header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 1.25rem; height: 56px; background: #fff;
  border-bottom: 1px solid #eee;
  position: sticky; top: 0; z-index: 100;
}
.logo { height: 32px; width: auto; }

.user-wrap { position: relative; }
.user-btn { background: none; border: none; cursor: pointer; padding: 4px; border-radius: 50%; }
.avatar {
  width: 40px; height: 40px; border-radius: 50%;
  border: 2px solid #eee;
  background: #f5f5f5; display: flex; align-items: center; justify-content: center;
  font-size: 0.82rem; font-weight: 700; text-transform: uppercase; color: #888;
}

.dropdown {
  position: absolute; right: 0; top: calc(100% + 6px);
  background: #E8390E; border-radius: 14px;
  min-width: 200px; overflow: hidden;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2); z-index: 200;
}
.dd-section { padding: 0.6rem 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.15); }
.dd-section:last-child { border-bottom: none; }
.dd-sub { font-size: 0.85rem; color: #fff; font-weight: 700; margin: 0 0 0.15rem; }
.dd-phone { font-size: 0.78rem; color: rgba(255,255,255,0.75); margin: 0 0 0.35rem; }
.badge {
  display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px;
  font-size: 0.72rem; font-weight: 600; background: rgba(255,255,255,0.2); color: #fff;
}
.badge-hr { background: rgba(255,255,255,0.25); color: #fff; }
.badge-employee { background: rgba(255,255,255,0.15); color: #fff; }
.dd-item {
  display: block; width: 100%; text-align: left;
  padding: 0.45rem 0; background: none; border: none;
  cursor: pointer; color: #fff; font-size: 0.9rem; font-weight: 600;
  font-family: inherit; border-radius: 6px; transition: opacity 0.12s;
}
.dd-item:hover { opacity: 0.75; }
.dd-logout { font-weight: 400; color: rgba(255,255,255,0.85); }

.backdrop { position: fixed; inset: 0; z-index: 99; }
.dd-enter-active, .dd-leave-active { transition: opacity 0.15s, transform 0.15s; }
.dd-enter-from, .dd-leave-to { opacity: 0; transform: translateY(-6px); }

.search-bar { display: flex; gap: 0.5rem; padding: 0.75rem 1.25rem; background: #E8390E; }
.search-input-wrap { flex: 1; }
.search-input {
  width: 100%; padding: 0.5rem 0.75rem;
  border: 1.5px solid rgba(255,255,255,0.5);
  border-radius: 8px; background: transparent;
  color: #fff; font-size: 0.9rem; font-family: inherit;
  outline: none; box-sizing: border-box;
}
.search-input::placeholder { color: rgba(255,255,255,0.7); }
.search-input:focus { border-color: #fff; }

.empty { text-align: center; padding: 3rem 1.5rem; color: #888; font-size: 0.95rem; }

.list { background: #fff; }
.card { padding: 1rem 1.25rem; border-bottom: 1px solid #eee; cursor: pointer; transition: background 0.12s; }
.card:hover { background: #fafafa; }
.card:active { background: #f5f5f5; }
.card-main { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; }
.card-left { flex: 1; min-width: 0; }
.card-title { font-size: 1.05rem; font-weight: 700; color: #1a1a1a; margin: 0 0 0.2rem; }
.card-desc { font-size: 0.85rem; color: #888; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-right { display: flex; flex-direction: column; align-items: flex-end; gap: 0.3rem; flex-shrink: 0; }
.badge-done {
  font-size: 0.75rem; font-weight: 600;
  background: #dcfce7; color: #166534;
  padding: 0.15rem 0.5rem; border-radius: 999px;
  white-space: nowrap;
}
.type-badge { font-size: 0.75rem; color: #888; white-space: nowrap; }
.card-questions { font-size: 0.78rem; color: #aaa; white-space: nowrap; }
</style>
