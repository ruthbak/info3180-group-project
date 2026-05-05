<script setup>
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import AppHeader from "@/components/AppHeader.vue";
import AppFooter from "@/components/AppFooter.vue";

const route = useRoute()

const dashboardRoutes = ['dashboard', 'matches', 'messages', 'profile-edit', 'reports']
const showPublicLayout = computed(() => !dashboardRoutes.includes(route.name))
</script>

<template>
  <AppHeader v-if="showPublicLayout" />
  <main>
    <RouterView />
  </main>
  <AppFooter v-if="showPublicLayout" />
</template>

<style>
body {
  padding-top: 0;
}

/* Only apply top padding on public pages */
.public-page {
  padding-top: 75px;
}
</style>