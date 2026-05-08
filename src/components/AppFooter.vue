<template>
    <footer class="dd-footer mt-5">
        <div class="container">
            <div class="dd-footer-inner">
                <RouterLink to="/" class="navbar-brand dd-brand">
                    <img src="@/assets/DriftDater Transparent.png" alt="DriftDater logo" class="dd-footer-logo" />
                    Drift<span>Dater</span>
                </RouterLink>  
                <ul class="dd-footer-links">
                    <li><RouterLink to="/">Home</RouterLink></li>
                    <li><RouterLink to="/login">Login</RouterLink></li>
                    <li><RouterLink to="/register">Register</RouterLink></li>
                </ul>
                <p class="dd-footer-copy">
                    Copyright &copy; {{ year }} DriftDater. Made with ♥
                </p>
            </div>
        </div>
    </footer>
</template>

<script setup>
import { ref } from "vue";
import { RouterLink } from "vue-router";


const year = (new Date).getFullYear();
</script>

<style>
.dd-footer {
  background: #2A1018;
  color: rgba(255, 255, 255, 0.55);
  padding: 2.5rem 0 1.5rem;
}
.dd-footer-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.2rem;
  text-align: center;
}
.dd-footer-brand {
  font-family: 'Georgia', serif;
  font-size: 1.4rem;
  font-weight: 700;
  color: #fff !important;
  text-decoration: none;
}
.dd-footer-brand span {
  font-style: italic;
  color: #E8617F;
}
.dd-footer-logo {
  width: 100px;
  height: 100px;
  object-fit: contain;
  margin-right: 0.3rem;
  vertical-align: middle;
}
.dd-footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem 1.5rem;
}
.dd-footer-links a {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.55);
  text-decoration: none;
  transition: color 0.2s;
}
.dd-footer-links a:hover {
  color: #E8617F;
}
.dd-footer-copy {
  font-size: 0.8rem;
  margin: 0;
  color: rgba(255, 255, 255, 0.35);
}
</style>
