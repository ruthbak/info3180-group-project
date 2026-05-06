<template>
  <div class="dd-login-page">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100">
        <div class="col-12 col-sm-10 col-md-7 col-lg-5">
 
          <!-- Card -->
          <div class="dd-login-card">
 
            <!-- Header -->
            <div class="text-center mb-4">
              <div class="dd-login-icon mb-3">♥</div>
              <h2 class="dd-login-title">Welcome Back</h2>
              <p class="dd-login-sub">Sign in to continue finding your flame</p>
            </div>
 
            <!-- Error Alert -->
            <div class="alert dd-alert-error" v-if="errorMessage">
              {{ errorMessage }}
            </div>
 
            <!-- Form -->
            <form @submit.prevent="handleLogin">
 
              <!-- Email -->
              <div class="mb-3">
                <label for="email" class="dd-label">Email Address</label>
                <input
                  type="email"
                  id="email"
                  v-model="form.email"
                  class="form-control dd-input"
                  :class="{ 'dd-input-error': errors.email }"
                  placeholder="your@email.com"
                />
                <span class="dd-error-text" v-if="errors.email">{{ errors.email }}</span>
              </div>
 
              <!-- Password -->
              <div class="mb-4">
                <label for="password" class="dd-label">Password</label>
                <input
                  type="password"
                  id="password"
                  v-model="form.password"
                  class="form-control dd-input"
                  :class="{ 'dd-input-error': errors.password }"
                  placeholder="Enter your password"
                />
                <span class="dd-error-text" v-if="errors.password">{{ errors.password }}</span>
              </div>
 
              <!-- Submit -->
              <button type="submit" class="btn dd-btn-submit w-100" :disabled="isLoading">
                <span v-if="isLoading">Signing in...</span>
                <span v-else>Sign In</span>
              </button>
 
            </form>
 
            <!-- Footer link -->
            <p class="text-center mt-4 dd-login-footer">
              Don't have an account?
              <RouterLink to="/register" class="dd-link-rose">Register here</RouterLink>
            </p>
 
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
 
<script setup>
import { ref, reactive } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
 
const router = useRouter()
 
// Form data
const form = reactive({
  email: '',
  password: ''
})
 
// Validation errors
const errors = reactive({
  email: '',
  password: ''
})
 
const errorMessage = ref('')
const isLoading = ref(false)
 
// Validate form
function validateForm() {
  let valid = true
 
  // Reset errors
  errors.email = ''
  errors.password = ''
 
  if (!form.email) {
    errors.email = 'Email is required.'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Please enter a valid email address.'
    valid = false
  }
 
  if (!form.password) {
    errors.password = 'Password is required.'
    valid = false
  } else if (form.password.length < 6) {
    errors.password = 'Password must be at least 6 characters.'
    valid = false
  }
 
  return valid
}
 
// Handle login submit
async function handleLogin() {
  errorMessage.value = ''
 
  if (!validateForm()) return
 
  isLoading.value = true
 
  try {
    // TODO: Replace with your actual Flask API call
    // const response = await fetch('/api/auth/login', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({ email: form.email, password: form.password })
    // })
    // const data = await response.json()
    // if (!response.ok) throw new Error(data.message || 'Login failed')
    // router.push({ name: 'dashboard' })
 
    // Temporary: simulate login for frontend testing
    await new Promise(resolve => setTimeout(resolve, 1000))
    router.push({ name: 'dashboard' })
 
  } catch (err) {
    errorMessage.value = err.message || 'Something went wrong. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>
 
<style>
.dd-login-page {
  background: linear-gradient(135deg, #fff6ee 0%, #fdeef2 50%, #fff0e8 100%);
  min-height: 100vh;
}
 
.dd-login-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 2.5rem 2rem;
  box-shadow: 0 16px 60px rgba(192, 57, 90, 0.12);
  border: 1px solid rgba(192, 57, 90, 0.08);
}
 
.dd-login-icon {
  width: 56px; height: 56px;
  background: linear-gradient(135deg, #C0395A 0%, #E8563A 100%);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem; color: #fff;
  margin: 0 auto;
  box-shadow: 0 6px 20px rgba(192, 57, 90, 0.30);
}
 
.dd-login-title {
  font-family: 'Georgia', serif;
  font-size: 1.8rem; font-weight: 700;
  color: #2A1018; letter-spacing: -0.02em;
}
 
.dd-login-sub {
  font-size: 0.9rem;
  color: #9E6373;
  margin: 0;
}
  
.dd-input-error {
  border-color: #E8563A !important;
}
 
.dd-error-text {
  font-size: 0.8rem;
  color: #E8563A;
  margin-top: 0.3rem;
  display: block;
}
 
.dd-login-footer {
  font-size: 0.88rem;
  color: #9E6373;
}
  
</style>