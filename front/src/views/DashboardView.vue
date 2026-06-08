<script setup>
import { computed } from 'vue';
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

const auth = useAuthStore();
const router = useRouter();

const goToCreateSurveys = () => {
  router.push('/create-survey');
};
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
      <span class="logo">PulseHR</span>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline">Open</Button>
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
              </span></DropdownMenuLabel
            >
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem v-if="auth.isHR" @click="goToCreateSurveys"
              >Создать опрос</DropdownMenuItem
            >
          </DropdownMenuGroup>
          <DropdownMenuSeparator />
          <DropdownMenuGroup>
            <DropdownMenuItem @click="handleLogout">Выйти</DropdownMenuItem>
          </DropdownMenuGroup>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>

    <main class="content">
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
  font-size: 1.3rem;
  font-weight: 700;
  color: #4f46e5;
}

.content {
  margin: 3rem auto;
  padding: 0 1rem;
}
.profile-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1.5rem;
}
.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #4f46e5;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  flex-shrink: 0;
  text-transform: uppercase;
}
.info h2 {
  margin: 0 0 0.3rem;
  font-size: 1.3rem;
}
.phone {
  margin: 0 0 0.75rem;
  color: #0a0303;
  font-size: 0.95rem;
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
</style>
