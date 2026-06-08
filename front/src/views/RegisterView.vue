<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const phone = ref('')
const password = ref('')
const firstName = ref('')
const lastName = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(phone.value, password.value, firstName.value, lastName.value)
    router.push('/')
  } catch (e) {
    const data = e.response?.data
    error.value = data?.phone_number?.[0] || data?.password?.[0] || data?.non_field_errors?.[0] || 'Ошибка регистрации'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1>PulseHR</h1>
      <h2>Регистрация</h2>

      <form @submit.prevent="submit">
        <div class="field">
          <label>Номер телефона</label>
          <input v-model="phone" type="tel" placeholder="+79991234567" required />
        </div>
        <div class="row">
          <div class="field">
            <label>Имя</label>
            <input v-model="firstName" type="text" placeholder="Иван" />
          </div>
          <div class="field">
            <label>Фамилия</label>
            <input v-model="lastName" type="text" placeholder="Иванов" />
          </div>
        </div>
        <div class="field">
          <label>Пароль</label>
          <input v-model="password" type="password" required minlength="6" />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Регистрируемся...' : 'Зарегистрироваться' }}
        </button>
      </form>

      <p class="switch-link">
        Уже есть аккаунт? <RouterLink to="/login">Войти</RouterLink>
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
  box-shadow: 0 2px 16px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}
h1 { margin: 0 0 0.25rem; font-size: 1.6rem; color: #4f46e5; }
h2 { margin: 0 0 1.5rem; font-size: 1.1rem; color: #555; font-weight: 400; }
.field { margin-bottom: 1rem; }
.field label { display: block; margin-bottom: 0.3rem; font-size: 0.9rem; color: #333; }
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
.field input:focus { border-color: #4f46e5; }
.row { display: flex; gap: 0.75rem; }
.row .field { flex: 1; }
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
button:hover:not(:disabled) { background: #4338ca; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #e53e3e; font-size: 0.88rem; margin: 0.5rem 0; }
.switch-link { text-align: center; margin-top: 1.2rem; font-size: 0.9rem; color: #666; }
.switch-link a { color: #4f46e5; text-decoration: none; }
</style>
