<template>
  <div class="dd-register-page">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100 py-5">
        <div class="col-12 col-sm-10 col-md-8 col-lg-6">
 
          <!-- Card -->
          <div class="dd-register-card">
 
            <!-- Header -->
            <div class="text-center mb-4">
              <div class="dd-register-icon mb-3">♥</div>
              <h2 class="dd-register-title">Create Your Account</h2>
              <p class="dd-register-sub">Join DriftDater and find your perfect flame</p>
            </div>
 
            <!-- Error Alert -->
            <div class="alert dd-alert-error" v-if="errorMessage">
              {{ errorMessage }}
            </div>
 
            <!-- Success Alert -->
            <div class="alert dd-alert-success" v-if="successMessage">
              {{ successMessage }}
            </div>
 
            <!-- Form -->
            <form @submit.prevent="handleRegister">
 
              <!-- Name Row -->
              <div class="row g-3 mb-3">
                <div class="col-6">
                  <label for="firstName" class="dd-label">First Name</label>
                  <input
                    type="text"
                    id="firstName"
                    v-model="form.firstName"
                    class="form-control dd-input"
                    :class="{ 'dd-input-error': errors.firstName }"
                    placeholder="First Name"
                  />
                  <span class="dd-error-text" v-if="errors.firstName">{{ errors.firstName }}</span>
                </div>
                <div class="col-6">
                  <label for="lastName" class="dd-label">Last Name</label>
                  <input
                    type="text"
                    id="lastName"
                    v-model="form.lastName"
                    class="form-control dd-input"
                    :class="{ 'dd-input-error': errors.lastName }"
                    placeholder="Last Name"
                  />
                  <span class="dd-error-text" v-if="errors.lastName">{{ errors.lastName }}</span>
                </div>
              </div>
 
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
 
              <!-- Username -->
              <div class="mb-3">
                <label for="username" class="dd-label">Username</label>
                <input
                  type="text"
                  id="username"
                  v-model="form.username"
                  class="form-control dd-input"
                  :class="{ 'dd-input-error': errors.username }"
                  placeholder="Choose a username"
                />
                <span class="dd-error-text" v-if="errors.username">{{ errors.username }}</span>
              </div>
 
              <!-- Date of Birth -->
              <div class="mb-3">
                <label for="dob" class="dd-label">Date of Birth</label>
                <input
                  type="date"
                  id="dob"
                  v-model="form.dob"
                  class="form-control dd-input"
                  :class="{ 'dd-input-error': errors.dob }"
                />
                <span class="dd-error-text" v-if="errors.dob">{{ errors.dob }}</span>
              </div>
 
              <!-- Gender & Looking For Row -->
              <div class="row g-3 mb-3">
                <div class="col-6">
                  <label for="gender" class="dd-label">Gender</label>
                  <select
                    id="gender"
                    v-model="form.gender"
                    class="form-select dd-input"
                    :class="{ 'dd-input-error': errors.gender }"
                  >
                    <option value="" disabled>Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="non-binary">Non-binary</option>
                    <option value="other">Other</option>
                    <option value="prefer-not">Prefer not to say</option>
                  </select>
                  <span class="dd-error-text" v-if="errors.gender">{{ errors.gender }}</span>
                </div>
                <div class="col-6">
                  <label for="lookingFor" class="dd-label">Looking For</label>
                  <select
                    id="lookingFor"
                    v-model="form.lookingFor"
                    class="form-select dd-input"
                    :class="{ 'dd-input-error': errors.lookingFor }"
                  >
                    <option value="" disabled>Select preference</option>
                    <option value="men">Men</option>
                    <option value="women">Women</option>
                    <option value="any">Any</option>
                  </select>
                  <span class="dd-error-text" v-if="errors.lookingFor">{{ errors.lookingFor }}</span>
                </div>
              </div>
 
              <!-- Password -->
              <div class="mb-3">
                <label for="password" class="dd-label">Password</label>
                <input
                  type="password"
                  id="password"
                  v-model="form.password"
                  class="form-control dd-input"
                  :class="{ 'dd-input-error': errors.password }"
                  placeholder="Create a password"
                />
                <span class="dd-error-text" v-if="errors.password">{{ errors.password }}</span>
              </div>
 
              <!-- Confirm Password -->
              <div class="mb-4">
                <label for="confirmPassword" class="dd-label">Confirm Password</label>
                <input
                  type="password"
                  id="confirmPassword"
                  v-model="form.confirmPassword"
                  class="form-control dd-input"
                  :class="{ 'dd-input-error': errors.confirmPassword }"
                  placeholder="Confirm your password"
                />
                <span class="dd-error-text" v-if="errors.confirmPassword">{{ errors.confirmPassword }}</span>
              </div>
 
              <!-- Submit -->
              <button type="submit" class="btn dd-btn-submit w-100" :disabled="isLoading">
                <span v-if="isLoading">Creating Account...</span>
                <span v-else>♥ Create Account</span>
              </button>
 
            </form>
 
            <!-- Footer link -->
            <p class="text-center mt-4 dd-register-footer">
              Already have an account?
              <RouterLink to="/login" class="dd-link-rose">Login here</RouterLink>
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
  firstName: '',
  lastName: '',
  email: '',
  username: '',
  dob: '',
  gender: '',
  lookingFor: '',
  password: '',
  confirmPassword: ''
})
 
// Validation errors
const errors = reactive({
  firstName: '',
  lastName: '',
  email: '',
  username: '',
  dob: '',
  gender: '',
  lookingFor: '',
  password: '',
  confirmPassword: ''
})
 
const errorMessage = ref('')
const successMessage = ref('')
const isLoading = ref(false)
 
// Validate form
function validateForm() {
  let valid = true
 
  // Reset all errors
  Object.keys(errors).forEach(key => errors[key] = '')
 
  if (!form.firstName.trim()) {
    errors.firstName = 'First name is required.'
    valid = false
  }
 
  if (!form.lastName.trim()) {
    errors.lastName = 'Last name is required.'
    valid = false
  }
 
  if (!form.email) {
    errors.email = 'Email is required.'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Please enter a valid email address.'
    valid = false
  }
 
  if (!form.username.trim()) {
    errors.username = 'Username is required.'
    valid = false
  } else if (form.username.length < 3) {
    errors.username = 'Username must be at least 3 characters.'
    valid = false
  }
 
  if (!form.dob) {
    errors.dob = 'Date of birth is required.'
    valid = false
  } else {
    // Must be at least 18 years old
    const today = new Date()
    const birthDate = new Date(form.dob)
    const age = today.getFullYear() - birthDate.getFullYear()
    if (age < 18) {
      errors.dob = 'You must be at least 18 years old to register.'
      valid = false
    }
  }
 
  if (!form.gender) {
    errors.gender = 'Please select your gender.'
    valid = false
  }
 
  if (!form.lookingFor) {
    errors.lookingFor = 'Please select a preference.'
    valid = false
  }
 
  if (!form.password) {
    errors.password = 'Password is required.'
    valid = false
  } else if (form.password.length < 6) {
    errors.password = 'Password must be at least 6 characters.'
    valid = false
  }
 
  if (!form.confirmPassword) {
    errors.confirmPassword = 'Please confirm your password.'
    valid = false
  } else if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match.'
    valid = false
  }
 
  return valid
}
 
// Handle register submit
async function handleRegister() {
  errorMessage.value = ''
  successMessage.value = ''
 
  if (!validateForm()) return
 
  isLoading.value = true
 
  try {
    // TODO: Replace with your actual Flask API call
    // const response = await fetch('/api/auth/register', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({
    //     first_name: form.firstName,
    //     last_name: form.lastName,
    //     email: form.email,
    //     username: form.username,
    //     dob: form.dob,
    //     gender: form.gender,
    //     looking_for: form.lookingFor,
    //     password: form.password
    //   })
    // })
    // const data = await response.json()
    // if (!response.ok) throw new Error(data.message || 'Registration failed')
    // router.push({ name: 'login' })
 
    // Temporary: simulate registration for frontend testing
    await new Promise(resolve => setTimeout(resolve, 1000))
    successMessage.value = 'Account created successfully! Redirecting to login...'
    setTimeout(() => router.push({ name: 'login' }), 2000)
 
  } catch (err) {
    errorMessage.value = err.message || 'Something went wrong. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>
 
<style scoped>
.dd-register-page {
  background: linear-gradient(135deg, #fff6ee 0%, #fdeef2 50%, #fff0e8 100%);
  min-height: 100vh;
}
 
.dd-register-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 2.5rem 2rem;
  box-shadow: 0 16px 60px rgba(192, 57, 90, 0.12);
  border: 1px solid rgba(192, 57, 90, 0.08);
}
 
.dd-register-icon {
  width: 56px; height: 56px;
  background: linear-gradient(135deg, #C0395A 0%, #E8563A 100%);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem; color: #fff;
  margin: 0 auto;
  box-shadow: 0 6px 20px rgba(192, 57, 90, 0.30);
}
 
.dd-register-title {
  font-family: 'Georgia', serif;
  font-size: 1.8rem; font-weight: 700;
  color: #2A1018; letter-spacing: -0.02em;
}
 
.dd-register-sub {
  font-size: 0.9rem;
  color: #9E6373;
  margin: 0;
}
 
.dd-label {
  font-size: 0.88rem;
  font-weight: 600;
  color: #6B3A48;
  margin-bottom: 0.4rem;
  display: block;
}
 
.dd-input {
  border: 1.5px solid rgba(192, 57, 90, 0.20);
  border-radius: 10px;
  padding: 0.65rem 1rem;
  font-size: 0.93rem;
  color: #2A1018;
  transition: border-color 0.2s, box-shadow 0.2s;
}
 
.dd-input:focus {
  border-color: #C0395A;
  box-shadow: 0 0 0 3px rgba(192, 57, 90, 0.12);
  outline: none;
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
 
.dd-alert-error {
  background: #FDEEF2;
  border: 1px solid rgba(192, 57, 90, 0.25);
  color: #C0395A;
  border-radius: 10px;
  font-size: 0.88rem;
  padding: 0.75rem 1rem;
}
 
.dd-alert-success {
  background: #f0fdf4;
  border: 1px solid rgba(34, 197, 94, 0.25);
  color: #16a34a;
  border-radius: 10px;
  font-size: 0.88rem;
  padding: 0.75rem 1rem;
}
 
.dd-btn-submit {
  background: linear-gradient(135deg, #C0395A 0%, #E8563A 100%);
  color: #fff;
  border: none;
  border-radius: 100px;
  font-weight: 600;
  font-size: 0.95rem;
  padding: 0.75rem;
  box-shadow: 0 6px 20px rgba(192, 57, 90, 0.28);
  transition: opacity 0.2s, transform 0.15s;
}
 
.dd-btn-submit:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
  color: #fff;
}
 
.dd-btn-submit:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
 
.dd-register-footer {
  font-size: 0.88rem;
  color: #9E6373;
}
 
.dd-link-rose {
  color: #C0395A;
  font-weight: 600;
  text-decoration: none;
  transition: opacity 0.2s;
}
 
.dd-link-rose:hover { opacity: 0.75; }
</style>
 