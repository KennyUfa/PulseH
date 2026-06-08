import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/create-survey',
      name: 'create-survey',
      component: () => import('@/views/CreateSurveyView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/surveys',
      name: 'surveys',
      component: () => import('@/views/SurveysListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/surveys/:id',
      name: 'survey-detail',
      component: () => import('@/views/SurveyDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/surveys/:id/edit',
      name: 'survey-edit',
      component: () => import('@/views/EditSurveyView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/results',
      name: 'results',
      component: () => import('@/views/ResultsListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/results/:id',
      name: 'results-detail',
      component: () => import('@/views/ResultsDetailView.vue'),
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (to.meta.requiresAuth && !auth.isAuthenticated) return '/login';
  if (to.meta.guestOnly && auth.isAuthenticated) return '/';
});

export default router;
