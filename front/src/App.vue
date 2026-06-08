<script setup>
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

if (auth.isAuthenticated) {
  auth.fetchMe()
}
</script>

<template>
  <RouterView />
</template>
