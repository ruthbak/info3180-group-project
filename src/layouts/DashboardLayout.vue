<template>
  <div class="dd-app-shell" :class="{ 'sidebar-collapsed': isCollapsed }">

    <!-- ── SIDEBAR ── -->
    <aside class="dd-sidebar">

      <!-- Sidebar Header -->
      <div class="dd-sidebar-header">
        <RouterLink to="/" class="dd-sidebar-brand" v-if="!isCollapsed">
          Drift<span>Dater</span> ♥
        </RouterLink>
        <span class="dd-sidebar-brand-icon" v-else>♥</span>
          <button class="dd-collapse-btn" @click="toggleSidebar">
            <i v-if="isCollapsed" class="bi bi-chevron-right"></i>
            <i v-else class="bi bi-chevron-left"></i>
          </button>
      </div>

      <!-- User Info -->
      <div class="dd-sidebar-user" v-if="!isCollapsed">
        <div class="dd-sidebar-avatar">{{ userInitials }}</div>
        <div class="dd-sidebar-user-info">
          <div class="dd-sidebar-name">{{ userName }}</div>
          <div class="dd-sidebar-status">  
            <span class="dd-online-dot"></span> Online
          </div>
        </div>
      </div>
      <div class="dd-sidebar-avatar-sm" v-else>{{ userInitials}}</div>

      <!-- Nav Links -->
      <nav class="dd-sidebar-nav">
        <RouterLink to="/dashboard" class="dd-nav-link" :title="isCollapsed ? 'Dashboard' : ''">
          <span class="dd-nav-icon"><i class="bi bi-columns-gap"></i></span>
          <span class="dd-nav-label" v-if="!isCollapsed">Dashboard</span>
        </RouterLink>
        <RouterLink to="/matches" class="dd-nav-link" :title="isCollapsed ? 'Matches' : ''">
          <span class="dd-nav-icon">♥</span>
          <span class="dd-nav-label" v-if="!isCollapsed">Matches</span>
        </RouterLink>
        <RouterLink to="/messages" class="dd-nav-link" :title="isCollapsed ? 'Messages' : ''">
          <span class="dd-nav-icon"><i class="bi bi-chat-square-dots"></i></span>
          <div class="dd-nav-chat-wrap">
          <span class="dd-nav-label" v-if="!isCollapsed">Messages</span>

          <span
            v-if="totalUnreadChats > 0 && !isCollapsed"
            class="dd-sidebar-chat-badge"
          >
            {{ totalUnreadChats }}
          </span>
        </div>
        </RouterLink>
        <RouterLink to="/profile/edit" class="dd-nav-link" :title="isCollapsed ? 'My Profile' : ''">
          <span class="dd-nav-icon"><i class="bi bi-person"></i></span>
          <span class="dd-nav-label" v-if="!isCollapsed">My Profile</span>
        </RouterLink>
        <RouterLink to="/reports" class="dd-nav-link" :title="isCollapsed ? 'Reports' : ''">
          <span class="dd-nav-icon"><i class="bi bi-bar-chart"></i></span>
          <span class="dd-nav-label" v-if="!isCollapsed">Reports</span>
        </RouterLink>
      </nav>

      <!-- Logout -->
      <div class="dd-sidebar-footer">
        <button class="dd-logout-btn" @click="logout" :title="isCollapsed ? 'Logout' : ''">
          <span class="dd-nav-icon"><i class="bi bi-box-arrow-left"></i></span>
          <span class="dd-nav-label" v-if="!isCollapsed">Logout</span>
        </button>
      </div>

    </aside>

    <!-- ── MAIN CONTENT ── -->
    <div class="dd-main-wrapper">

      <!-- Top Bar -->
      <header class="dd-topbar">
        <div class="dd-topbar-left">
          <h6 class="dd-page-title mb-0">{{ pageTitle }}</h6>
        </div>
        <div class="dd-topbar-right">
          <span class="dd-topbar-greeting">Welcome back, {{ userName }}! 👋</span>
        </div>
      </header>

      <!-- Page Content -->
      <main class="dd-content">
        <RouterView />
      </main>

    </div>

  </div>
</template>


<script setup>
import { ref, computed, onMounted } from 'vue'
import { logout, getToken } from "@/services/auth";
import { RouterLink, RouterView, useRouter, useRoute } from 'vue-router'
onMounted(async () => {
  try {
    const token = getToken();

    const response = await fetch("/api/v1/user/", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) {
      response.text().then(text => {
      throw new Error(text || "request failed");
      });
    }
    
    const data = await response.json();


    user.value = data.user;


  } catch (err) {
    error.value = err.message;

  }
});
const userInitials = computed(() => {

  if (!user.value) return "?"

  return (
    (user.value.first_name?.[0] || '') +
    (user.value.last_name?.[0] || '')
  ).toUpperCase()
})
const router = useRouter()
const route = useRoute()
const user = ref(null);
const error = ref("");
const isCollapsed = ref(false)

function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value
}

// Dynamic page title based on current route
const pageTitle = computed(() => {
  const titles = {
    dashboard: 'Dashboard',
    matches: 'Your Matches',
    messages: 'Messages',
    profile: 'Edit Profile',
    reports: 'Reports'
  }
  return titles[route.name] || 'Dashboard'
})


</script>

<style scoped>
/* ── App Shell ── */
.dd-app-shell {
  display: flex;
  min-height: 100vh;
  background: #FFF6EE;
}

/* ── Sidebar ── */
.dd-sidebar {
  width: 240px;
  min-height: 100vh;
  background: #2A1018;
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0; bottom: 0;
  z-index: 200;
  transition: width 0.3s ease;
  overflow: hidden;
}

.sidebar-collapsed .dd-sidebar {
  width: 70px;
}

/* Sidebar Header */
.dd-sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.2rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  min-height: 65px;
}

.dd-sidebar-brand {
  font-family: 'Georgia', serif;
  font-size: 1.2rem;
  font-weight: 700;
  color: #fff !important;
  text-decoration: none;
  white-space: nowrap;
}

.dd-sidebar-brand span {
  font-style: italic;
  color: #E8617F;
}

.dd-sidebar-brand-icon {
  font-size: 1.3rem;
  color: #E8617F;
  margin: 0 auto;
}

.dd-collapse-btn {
  background: rgba(255, 255, 255, 0.08);
  border: none;
  color: rgba(255, 255, 255, 0.6);
  width: 28px; height: 28px;
  border-radius: 6px;
  font-size: 0.7rem;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.2s;
  flex-shrink: 0;
}

.dd-collapse-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

/* User Info */
.dd-sidebar-user {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 1rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.dd-sidebar-avatar {
  width: 40px; height: 40px;
  border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, #C0395A 0%, #E8563A 100%);
  color: #fff; font-weight: 700; font-size: 0.85rem;
  display: flex; align-items: center; justify-content: center;
}

.dd-sidebar-avatar-sm {
  width: 40px; height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #C0395A 0%, #E8563A 100%);
  color: #fff; font-weight: 700; font-size: 0.85rem;
  display: flex; align-items: center; justify-content: center;
  margin: 1rem auto;
}

.dd-sidebar-name {
  font-size: 0.88rem;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
}

.dd-sidebar-status {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
}

/* Nav Links */
.dd-sidebar-nav {
  flex: 1;
  padding: 1rem 0.6rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.dd-nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.7rem 0.9rem;
  border-radius: 10px;
  text-decoration: none;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  font-weight: 500;
  transition: background 0.2s, color 0.2s;
  white-space: nowrap;
}

.dd-nav-link:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.dd-nav-link.router-link-active {
  background: linear-gradient(135deg, #C0395A 0%, #E8563A 100%);
  color: #fff;
  box-shadow: 0 4px 14px rgba(192, 57, 90, 0.30);
}

.dd-nav-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
  width: 20px;
  text-align: center;
}

.dd-nav-label { white-space: nowrap; }

/* Sidebar Footer */
.dd-sidebar-footer {
  padding: 0.8rem 0.6rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.dd-logout-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.7rem 0.9rem;
  border-radius: 10px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  width: 100%;
  transition: background 0.2s, color 0.2s;
  white-space: nowrap;
}

.dd-logout-btn:hover {
  background: rgba(232, 86, 58, 0.15);
  color: #E8617F;
}

/* ── Main Wrapper ── */
.dd-main-wrapper {
  margin-left: 240px;
  flex: 1;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
  min-height: 100vh;
}

.sidebar-collapsed .dd-main-wrapper {
  margin-left: 70px;
}

/* Top Bar */
.dd-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: #fff;
  border-bottom: 1px solid rgba(192, 57, 90, 0.10);
  position: sticky;
  top: 0; z-index: 100;
  box-shadow: 0 2px 12px rgba(192, 57, 90, 0.06);
}

.dd-page-title {
  font-family: 'Georgia', serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: #2A1018;
}

.dd-topbar-greeting {
  font-size: 0.88rem;
  color: #9E6373;
}

/* Page Content */
.dd-content {
  padding: 2rem;
  flex: 1;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .dd-sidebar {
    width: 70px;
  }
  .dd-main-wrapper {
    margin-left: 70px;
  }
  .sidebar-collapsed .dd-sidebar {
    width: 0;
    padding: 0;
  }
  .sidebar-collapsed .dd-main-wrapper {
    margin-left: 0;
  }
}

.dd-online-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #4ade80; display: inline-block;
  margin-right: 0.25rem;
}

.dd-nav-chat-wrap {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.dd-sidebar-chat-badge {
  min-width: 18px;
  height: 18px;

  border-radius: 50%;

  background: #fff;
  color: var(--dd-rose);

  display: flex;
  align-items: center;
  justify-content: center;

  font-size: 0.68rem;
  font-weight: 700;

  padding: 0 0.35rem;
}
</style>
