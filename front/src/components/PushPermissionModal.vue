<script setup>
import { ref } from 'vue'
import { subscribeToPush } from '@/utils/push'
import { Button } from '@/components/ui/button'

const emit = defineEmits(['close'])
const loading = ref(false)
const error = ref('')

async function enable() {
  loading.value = true
  error.value = ''
  try {
    const permission = await Notification.requestPermission()
    if (permission === 'granted') await subscribeToPush()
  } catch {
    error.value = 'Не удалось подключить уведомления'
  } finally {
    loading.value = false
    emit('close')
  }
}

function dismiss() {
  localStorage.setItem('push_dismissed', '1')
  emit('close')
}
</script>

<template>
  <div class="fixed inset-0 z-[200] flex items-end sm:items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/30" @click="dismiss" />
    <div class="relative bg-white rounded-2xl shadow-2xl max-w-sm w-full p-6 z-10">
      <div class="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center mb-4">
        <svg class="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
      </div>
      <h3 class="text-lg font-bold text-gray-900 mb-2">Уведомления об опросах</h3>
      <p class="text-sm text-gray-500 mb-5">Получайте уведомления о новых опросах прямо в браузере — не пропустите ни один опрос.</p>
      <p v-if="error" class="text-xs text-red-500 mb-3">{{ error }}</p>
      <div class="flex gap-3">
        <Button class="flex-1 hover:opacity-80" :disabled="loading" @click="enable">
          {{ loading ? 'Подключаем...' : 'Включить' }}
        </Button>
        <Button variant="outline" class="flex-1" @click="dismiss">Не сейчас</Button>
      </div>
    </div>
  </div>
</template>
