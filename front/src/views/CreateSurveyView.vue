<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="page">
    <header class="topbar">
      <span class="logo">PulseHR</span>
      <button class="back-btn" @click="router.push('/')">← Назад</button>
    </header>
    <main class="content">
      <h1>Создать опрос</h1>
      <p class="soon">Раздел в разработке</p>
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
.content { max-width: 800px; margin: 3rem auto; padding: 0 1rem; }
.content h1 { font-size: 1.6rem; margin-bottom: 0.5rem; }
.soon { color: #888; }
</style>
