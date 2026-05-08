<template>
  <header>
    <nav class="navbar navbar-expand-lg fixed-top dd-navbar">
      <div class="container-fluid">
        <RouterLink to="/" class="navbar-brand dd-brand">
          <img src="@/assets/DriftDater Transparent.png" alt="DriftDater logo" class="dd-logo" />
          Drift<span>Dater</span>
        </RouterLink>       
      <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <RouterLink to="/login" class="nav-link dd-link">Login</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink to="/register" class="btn dd-btn-primary btn-sm ms-2">
                Register
              </RouterLink>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { RouterLink } from "vue-router";
</script>

<style>
.dd-navbar {
  background: rgba(255, 250, 247, 0.93);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(192, 57, 90, 0.15);
}
.dd-brand {
  font-family: 'Georgia', serif;
  font-size: 1.55rem;
  font-weight: 700;
  color: #C0395A !important;
  text-decoration: none;
}
.dd-brand span { font-style: italic; color: #E8563A; }
.dd-link {
  font-size: 0.9rem;
  font-weight: 500;
  color: #6B3A48 !important;
  border-radius: 100px;
  padding: 0.4rem 0.9rem !important;
  transition: background 0.2s, color 0.2s;
}
.dd-link:hover, .dd-link.router-link-active {
  background: #FDEEF2;
  color: #C0395A !important;
}
.dd-btn-primary {
  background: linear-gradient(135deg, #C0395A 0%, #E8563A 100%);
  color: #fff !important;
  border: none;
  border-radius: 100px;
  font-weight: 600;
  font-size: 0.88rem;
  text-decoration: none;
  transition: opacity 0.2s;
}
.dd-btn-primary:hover { opacity: 0.88; color: #fff !important; }
.navbar-toggler { border-color: rgba(192, 57, 90, 0.35); }
.navbar-toggler-icon {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3e%3cpath stroke='rgba(192,57,90,0.8)' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
}

.dd-logo {
  width: 100px;
  height: 100px;
  margin-right: 0.3rem;
  vertical-align: middle;
  
}
</style>
