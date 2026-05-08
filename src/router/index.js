import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // ── Public routes ──
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue')
    },

    // ── Authenticated routes (use DashboardLayout with sidebar) ──
    {
      path: '/',
      component: () => import('../layouts/DashboardLayout.vue'),
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue')
        },
        {
          path: 'matches',
          name: 'matches',
          component: () => import('../views/MatchesView.vue')
        },
        {
          path: 'messages',
          name: 'messages',
          component: () => import('../views/MessagesView.vue')
        },
        {
          path: 'profile/edit',
          name: 'profile-edit',
          component: () => import('../views/ProfileEditView.vue')
        },
        {
          path: 'reports',
          name: 'reports',
          component: () => import('../views/ReportsView.vue')
        },
        {
          path: 'profile/:id',
          name: 'profile-view',
          component: () => import('../views/ViewProfileView.vue')
        }
      ]
    }
  ]
})

export default router