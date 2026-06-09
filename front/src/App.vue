<script setup>
import { ref, watch } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import PushPermissionModal from '@/components/PushPermissionModal.vue'
import { getPushPermission, registerServiceWorker } from '@/utils/push'

const auth = useAuthStore()
const showPushModal = ref(false)

if (auth.isAuthenticated) {
  auth.fetchMe()
}

watch(
  () => auth.isAuthenticated,
  async (val) => {
    if (!val) return
    if (!('Notification' in window) || !('PushManager' in window)) return
    if (localStorage.getItem('push_dismissed')) return
    const permission = await getPushPermission()
    if (permission === 'default') showPushModal.value = true
    else if (permission === 'granted') registerServiceWorker()
  },
  { immediate: true },
)

function onModalClose() {
  showPushModal.value = false
}
</script>

<template>
  <RouterView />
  <PushPermissionModal v-if="showPushModal" @close="onModalClose" />
</template>
