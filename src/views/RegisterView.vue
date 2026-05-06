<template>
  <div class="dd-register-page">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100 py-5">
        <div class="col-12 col-sm-10 col-md-8 col-lg-6">

          <!-- Card -->
          <div class="dd-register-card">

            <!-- Header -->
            <div class="text-center mb-4">
              <div class="dd-register-icon mb-3">
                <i class="bi bi-heart-fill"></i>
              </div>
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
                  <label for="firstname" class="dd-label">First Name</label>
                  <input
                    type="text"
                    id="firstname"
                    v-model="form.firstname"
                    class="form-control dd-input"
                    placeholder="First Name"
                  />
                </div>
                <div class="col-6">
                  <label for="lastname" class="dd-label">Last Name</label>
                  <input
                    type="text"
                    id="lastname"
                    v-model="form.lastname"
                    class="form-control dd-input"
                    placeholder="Last Name"
                  />
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
                  placeholder="your@email.com"
                />
              </div>

              <!-- Username -->
              <div class="mb-3">
                <label for="username" class="dd-label">Username</label>
                <input
                  type="text"
                  id="username"
                  v-model="form.username"
                  class="form-control dd-input"
                  placeholder="Choose a username"
                />
              </div>

              <!-- Date of Birth -->
              <div class="mb-3">
                <label for="dob" class="dd-label">Date of Birth</label>
                <input
                  type="date"
                  id="dob"
                  v-model="form.dob"
                  class="form-control dd-input"
                />
              </div>

              <!-- Gender & Looking For Row -->
              <div class="row g-3 mb-3">
                <div class="col-6">
                  <label for="gender" class="dd-label">Gender</label>
                  <select
                    id="gender"
                    v-model="form.gender"
                    class="form-select dd-input"
                  >
                    <option value="" disabled>Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>
                <div class="col-6">
                  <label for="lookingfor" class="dd-label">Looking For</label>
                  <select
                    id="lookingfor"
                    v-model="form.lookingfor"
                    class="form-select dd-input"
                  >
                    <option value="" disabled>Select preference</option>
                    <option value="dating">Dating</option>
                    <option value="friendship">Friendship</option>
                    <option value="relationship">Relationship</option>
                  </select>
                </div>
              </div>

              <!-- Password -->
              <div class="mb-4">
                <label for="password" class="dd-label">Password</label>
                <input
                  type="password"
                  id="password"
                  v-model="form.password"
                  class="form-control dd-input"
                  placeholder="Create a password (min. 12 characters)"
                />
                <small class="dd-hint">
                  Must be 12+ characters with uppercase, lowercase, number and special character.
                </small>
              </div>

              <!-- Submit -->
              <button type="submit" class="btn dd-btn-submit w-100" :disabled="isLoading">
                <span v-if="isLoading">
                  <span class="spinner-border spinner-border-sm me-2"></span>
                  Creating Account...
                </span>
                <span v-else>
                  <i class="bi bi-heart-fill me-2"></i>Create Account
                </span>
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

// Form data — field names match Flask forms.py exactly
const form = reactive({
  firstname:  '',
  lastname:   '',
  email:      '',
  username:   '',
  dob:        '',
  gender:     '',
  lookingfor: '',
  password:   ''
})

const errorMessage  = ref('')
const successMessage = ref('')
const isLoading     = ref(false)

async function handleRegister() {
  errorMessage.value  = ''
  successMessage.value = ''
  isLoading.value     = true

  try {
    // TODO: Uncomment when Flask backend is ready
    // const response = await fetch('/api/auth/register', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify({
    //     firstname:  form.firstname,
    //     lastname:   form.lastname,
    //     email:      form.email,
    //     username:   form.username,
    //     dob:        form.dob,
    //     gender:     form.gender,
    //     lookingfor: form.lookingfor,
    //     password:   form.password
    //   })
    // })
    // const data = await response.json()
    // if (!response.ok) throw new Error(data.message || 'Registration failed')
    // router.push({ name: 'login' })

    // Temporary: simulate for frontend testing
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
  font-size: 1.4rem; color: #fff; margin: 0 auto;
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

.dd-register-footer { 
  font-size: 0.88rem; 
  color: #9E6373; 
}

</style>