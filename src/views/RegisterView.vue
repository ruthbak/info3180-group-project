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
            <form @submit.prevent="registerForm" id="register_form">

              <!-- Name Row -->
              <div class="row g-3 mb-3">
                <div class="col-6">
                  <label for="firstname" class="dd-label">First Name</label>
                  <input
                    type="text"
                    id="firstname"
                    v-model="firstname"
                    name="firstname"
                    class="form-control dd-input"
                    placeholder="First Name"
                  />
                </div>
                <div class="col-6">
                  <label for="lastname" class="dd-label">Last Name</label>
                  <input
                    type="text"
                    id="lastname"
                    v-model="lastname"
                    name="lastname"
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
                  v-model="email"
                  name="email"
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
                  v-model="username"
                  name="username"
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
                  name="dob"
                  v-model="dob"
                  class="form-control dd-input"
                />
              </div>

              <!-- Gender & Looking For Row -->
              <div class="row g-3 mb-3">
                <div class="col-6">
                  <label for="gender" class="dd-label">Gender</label>
                  <select
                    id="gender"
                    name="gender"
                    v-model="gender"
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
                    name="lookingfor"
                    v-model="lookingfor"
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
                  v-model="password"
                  name="password"
                  class="form-control dd-input"
                  placeholder="Create a password (min. 12 characters)"
                />
                <small class="dd-hint">
                  Must be 12+ characters with uppercase, lowercase, number and special character.
                </small>
              </div>

              <!-- Submit -->
              <button type="submit" class="btn dd-btn-submit w-100" :disabled="isLoading || !latitude || !longitude">
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
import { ref, onMounted } from "vue";
onMounted(() => {
  getCsrfToken();
  getLocation();
});
let csrf_token = ref("");
const latitude = ref(null)
const longitude = ref(null)
const locationError = ref("")
const email = ref("");
const username = ref("");
const firstname = ref("");
const lastname = ref("");
const dob = ref("");
const gender = ref("");
const lookingfor = ref("");
const password = ref("");
const successMessage = ref("");
const errorMessage = ref("");
const isLoading     = ref(false);

function getCsrfToken() {
  fetch('/api/v1/csrf-token')
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      csrf_token.value = data.csrf_token;
    })
}
async function getLocationName(lat, lon) {
  const response = await fetch(
    `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`
  )
  const data = await response.json()


  return data.address // full readable address
}
function getLocation() {
  if (!navigator.geolocation) {
    locationError.value = "Geolocation not supported"
    return
  }

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      latitude.value = position.coords.latitude
      longitude.value = position.coords.longitude
      locationError.value = ""
      console.log("Location:", latitude.value, longitude.value)
      const locationName = await getLocationName(latitude.value, longitude.value)
      console.log("Location name:", locationName.village || locationName.town || locationName.city || "Unknown")
    },
    (error) => {
      locationError.value = "Location permission denied"
      console.error(error)
    }
  )
}


function registerForm(){
  let register_form = document.getElementById("register_form");
  let form_data = new FormData(register_form);
                  fetch("/api/v1/register",{
                    method: "POST",
                    body: form_data,
                    headers: {
                      "X-CSRFToken": csrf_token.value
                    }
                  })
                  .then(function(response){
                    if (!response.ok) {
                      return response.text().then(text => {
                        throw new Error(text || "request failed");
                      });
                    }
                    return response.json();
                  })
                  .then(function (data){
                    successMessage.value = data.message;
                    console.log("Success:", data);
                    errorMessage.value = "";
                    email.value = "";
                    username.value = "";
                    firstname.value = "";
                    lastname.value = "";
                    dob.value = "";
                    gender.value = "";
                    lookingfor.value = "";
                    password.value = "";
                  })
                  .catch(function(error){
                    errorMessage.value = error.message;
                    successMessage.value = "";
                    console.error("Error:", error);
                  });
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