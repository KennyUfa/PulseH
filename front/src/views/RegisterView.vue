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
  <div class="auth-wrap">
    <div class="auth-card">
      <div class="auth-header">
        <div class="logo-circle">
          <img src="@/assets/logosks.jpg" alt="PulseHR logo" class="logo-img" />
        </div>
        <h1 class="brand">PulseHR</h1>
      </div>

      <form @submit.prevent="submit" class="auth-form">
        <div class="field">
          <input v-model="phone" type="tel" placeholder="+79991234567" required />
        </div>
        <div class="row">
          <div class="field">
            <input v-model="firstName" type="text" placeholder="Имя" />
          </div>
          <div class="field">
            <input v-model="lastName" type="text" placeholder="Фамилия" />
          </div>
        </div>
        <div class="field">
          <input v-model="password" type="password" placeholder="Пароль (мин. 6 символов)" required minlength="6" />
        </div>
        <p v-if="error" class="err">{{ error }}</p>
        <button type="submit" :disabled="loading" class="btn-primary">
          {{ loading ? 'Регистрируемся...' : 'Зарегистрироваться' }}
        </button>
      </form>

      <p class="switch">
        Уже есть аккаунт? <RouterLink to="/login">Войти</RouterLink>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  padding: 1.5rem;
}
.auth-card {
  background: #E8390E;
  border-radius: 20px;
  padding: 2rem;
  width: 100%;
  max-width: 320px;
}
.auth-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; }
.logo-circle {
  width: 44px; height: 44px; border-radius: 50%;
  background: rgba(255,255,255,0.2);
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}
.logo-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
.brand { font-size: 2rem; font-weight: 800; color: #fff; letter-spacing: -0.5px; margin: 0; }
.auth-form { display: flex; flex-direction: column; gap: 0.75rem; }
.row { display: flex; gap: 0.5rem; }
.row .field { flex: 1; }
.field input {
  width: 100%; padding: 0.75rem 1rem; border: none; border-radius: 10px;
  background: #fff; font-size: 0.95rem; font-family: 'Manrope', sans-serif;
  outline: none; color: #333; box-sizing: border-box;
}
.field input::placeholder { color: #999; }
.btn-primary {
  width: 100%; padding: 0.75rem; background: #fff; color: #E8390E;
  border: none; border-radius: 10px; font-size: 1rem; font-weight: 700;
  font-family: 'Manrope', sans-serif; cursor: pointer; margin-top: 0.25rem; transition: opacity 0.15s;
}
.btn-primary:hover:not(:disabled) { opacity: 0.9; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.err { color: #ffd0c7; font-size: 0.85rem; text-align: center; margin: 0; }
.switch { text-align: center; margin-top: 1.25rem; color: rgba(255,255,255,0.8); font-size: 0.88rem; }
.switch a { color: #fff; font-weight: 600; text-decoration: none; }
</style>
