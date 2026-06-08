<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  back: { type: String, default: null },
  backLabel: { type: String, default: '← Назад' },
})

const auth = useAuthStore()
const router = useRouter()
const menuOpen = ref(false)

const fullName = computed(() => {
  const fn = auth.user?.first_name || ''
  const ln = auth.user?.last_name || ''
  return (fn + ' ' + ln).trim() || auth.user?.phone_number || ''
})

const initials = computed(() => {
  const fn = auth.user?.first_name || ''
  const ln = auth.user?.last_name || ''
  if (fn || ln) return (fn[0] || '') + (ln[0] || '')
  return auth.user?.phone_number?.slice(-2) || '?'
})

function nav(path) { router.push(path); menuOpen.value = false }

async function handleLogout() {
  menuOpen.value = false
  await auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-white border-b border-gray-200">
      <div class="max-w-[1080px] mx-auto px-6 h-14 flex items-center justify-between">
        <img
          src="/src/assets/logoImage04-2022_081041.svg"
          alt="PulseHR"
          class="h-8 w-auto cursor-pointer shrink-0"
          @click="nav('/')"
        />

        <div class="flex items-center gap-3">
          <button
            v-if="back"
            class="text-sm text-gray-500 border border-gray-200 rounded-lg px-3 py-1.5 hover:border-indigo-500 hover:text-indigo-600 transition-colors cursor-pointer bg-transparent"
            @click="router.push(back)"
          >{{ backLabel }}</button>

          <slot name="actions" />

          <!-- Avatar + dropdown -->
          <div class="relative">
            <button class="p-1 rounded-full cursor-pointer bg-transparent border-none" @click="menuOpen = !menuOpen">
              <div class="w-9 h-9 rounded-full border-2 border-gray-200 bg-gray-100 flex items-center justify-center text-xs font-bold uppercase text-gray-500 select-none">
                {{ initials }}
              </div>
            </button>

            <Transition
              enter-active-class="transition duration-150 ease-out"
              enter-from-class="opacity-0 -translate-y-1.5"
              leave-active-class="transition duration-100 ease-in"
              leave-to-class="opacity-0 -translate-y-1.5"
            >
              <div v-if="menuOpen" class="absolute right-0 top-[calc(100%+8px)] w-52 rounded-2xl overflow-hidden shadow-xl z-50" style="background:#E8390E">
                <div class="px-3.5 py-3 border-b border-white/15">
                  <p class="text-white font-bold text-sm truncate mb-0.5">{{ fullName }}</p>
                  <p class="text-white/70 text-xs mb-2">{{ auth.user?.phone_number }}</p>
                  <span class="inline-block bg-white/20 text-white text-[11px] font-semibold px-2 py-0.5 rounded-full">
                    {{ auth.isHR ? 'HR-специалист' : 'Сотрудник' }}
                  </span>
                </div>

                <template v-if="auth.isHR">
                  <div class="px-3.5 py-2 border-b border-white/15 flex flex-col gap-0.5">
                    <button class="text-left text-white text-sm font-semibold w-full py-1 hover:opacity-70 transition-opacity bg-transparent border-none cursor-pointer" @click="nav('/create-survey')">Создать опрос</button>
                    <button class="text-left text-white text-sm font-semibold w-full py-1 hover:opacity-70 transition-opacity bg-transparent border-none cursor-pointer" @click="nav('/surveys')">Список опросов</button>
                    <button class="text-left text-white text-sm font-semibold w-full py-1 hover:opacity-70 transition-opacity bg-transparent border-none cursor-pointer" @click="nav('/results')">Результаты опросов</button>
                  </div>
                </template>

                <div class="px-3.5 py-2">
                  <button class="text-left text-white/80 text-sm w-full py-1 hover:opacity-70 transition-opacity bg-transparent border-none cursor-pointer" @click="handleLogout">Выйти</button>
                </div>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </header>

    <div v-if="menuOpen" class="fixed inset-0 z-40" @click="menuOpen = false" />

    <slot name="wide" />

    <div class="max-w-[1080px] mx-auto px-6 py-8 pb-12">
      <slot />
    </div>
  </div>
</template>
