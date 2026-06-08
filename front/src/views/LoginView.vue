<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const auth = useAuthStore();

const phone = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);

async function submit() {
  error.value = '';
  loading.value = true;
  try {
    await auth.login(phone.value, password.value);
    router.push('/');
  } catch (e) {
    error.value = e.response?.data?.non_field_errors?.[0] || 'Ошибка входа';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>PulseHR</h1>
      <h2>Вход</h2>

      <form @submit.prevent="submit">
        <div class="field">
          <label>Номер телефона</label>
          <input
            v-model="phone"
            type="tel"
            placeholder="+79991234567"
            required
          />
        </div>
        <div class="field">
          <label>Пароль</label>
          <input v-model="password" type="password" required />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Входим...' : 'Войти' }}
        </button>
      </form>

      <p class="switch-link">
        Нет аккаунта? <RouterLink to="/register">Зарегистрироваться</RouterLink>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}
.auth-card {
  background: #fff;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 380px;
}
h1 {
  margin: 0 0 0.25rem;
  font-size: 1.6rem;
  color: #4f46e5;
}
h2 {
  margin: 0 0 1.5rem;
  font-size: 1.1rem;
  color: #555;
  font-weight: 400;
}
.field {
  margin-bottom: 1rem;
}
.field label {
  display: block;
  margin-bottom: 0.3rem;
  font-size: 0.9rem;
  color: #333;
}
.field input {
  width: 100%;
  padding: 0.6rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.2s;
}
.field input:focus {
  border-color: #4f46e5;
}
button {
  width: 100%;
  padding: 0.7rem;
  background: #4f46e5;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 0.5rem;
  transition: background 0.2s;
}
button:hover:not(:disabled) {
  background: #4338ca;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error {
  color: #e53e3e;
  font-size: 0.88rem;
  margin: 0.5rem 0;
}
.switch-link {
  text-align: center;
  margin-top: 1.2rem;
  font-size: 0.9rem;
  color: #666;
}
.switch-link a {
  color: #4f46e5;
  text-decoration: none;
}
</style>
