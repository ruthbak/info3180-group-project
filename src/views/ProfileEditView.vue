<template>
  <div class="profile-edit-container">
    <div class="profile-edit-card">
      <h2 class="title">Edit Profile</h2>
 
      <form @submit.prevent="handleSubmit" class="profile-form">
        <!-- Profile Picture Upload -->
        <div class="form-group">
          <label class="form-label">Profile Picture</label>
          <div class="photo-upload-area">
            <div class="current-photo" v-if="imagePreview">
              <img :src="imagePreview" alt="Profile preview" class="preview-image" />
              <button type="button" @click="removeImage" class="remove-photo-btn">×</button>
            </div>
            <div v-else class="photo-placeholder">
              <svg class="placeholder-icon" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
              <span>Click or drag to upload</span>
            </div>
            <input
              type="file"
              ref="fileInput"
              @change="onFileChange"
              accept="image/jpeg,image/png"
              class="file-input"
            />
          </div>
          <p class="input-hint">Accepted formats: JPG, PNG (Max 5MB)</p>
        </div>
 
        <!-- Username -->
        <div class="form-group">
          <label class="form-label">Username</label>
          <input
            type="text"
            v-model="formData.username"
            class="dd-input"
            :class="{ 'input-error': errors.username }"
            placeholder="Enter username (min. 8 characters)"
          />
          <p v-if="errors.username" class="error-message">{{ errors.username }}</p>
          <p class="input-hint">Must start with a letter, can contain letters, numbers, dots, or underscores</p>
        </div>
 
        <!-- First Name -->
        <div class="form-group">
          <label class="form-label">First Name</label>
          <input
            type="text"
            v-model="formData.firstname"
            class="dd-input"
            :class="{ 'input-error': errors.firstname }"
            placeholder="Enter first name"
          />
          <p v-if="errors.firstname" class="error-message">{{ errors.firstname }}</p>
          <p class="input-hint">Only letters allowed, 2-50 characters</p>
        </div>
 
        <!-- Last Name -->
        <div class="form-group">
          <label class="form-label">Last Name</label>
          <input
            type="text"
            v-model="formData.lastname"
            class="dd-input"
            :class="{ 'input-error': errors.lastname }"
            placeholder="Enter last name"
          />
          <p v-if="errors.lastname" class="error-message">{{ errors.lastname }}</p>
          <p class="input-hint">Only letters allowed, 2-50 characters</p>
        </div>
 
        <!-- Hobbies -->
        <div class="form-group">
          <label class="form-label">Hobbies</label>
          <input
            type="text"
            v-model="formData.interests"
            class="dd-input"
            :class="{ 'input-error': errors.interests }"
            placeholder="e.g., Music, Sports, Travel, Photography"
          />
          <p v-if="errors.interests" class="error-message">{{ errors.interests }}</p>
          <p class="input-hint">Comma-separated hobbies (max. 200 characters)</p>
        </div>
 
        <!-- Bio -->
        <div class="form-group">
          <label class="form-label">Bio</label>
          <textarea
            v-model="formData.bio"
            class="dd-input"
            :class="{ 'input-error': errors.bio }"
            rows="4"
            placeholder="Tell others about yourself..."
          ></textarea>
          <div class="char-counter">{{ formData.bio.length }}/500</div>
          <p v-if="errors.bio" class="error-message">{{ errors.bio }}</p>
        </div>
 
        <!-- Looking For -->
        <div class="form-group">
          <label class="form-label">Looking For</label>
          <select v-model="formData.lookingfor" class="dd-input" :class="{ 'input-error': errors.lookingfor }">
            <option value="dating">Dating</option>
            <option value="friendship">Friendship</option>
            <option value="relationship">Relationship</option>
          </select>
          <p v-if="errors.lookingfor" class="error-message">{{ errors.lookingfor }}</p>
        </div>
 
        <!-- Age Preference -->
        <div class="form-group">
          <label class="form-label">Partner Age Preference</label>
          <div class="age-range-row">
            <div class="age-range-field">
              <label class="form-label-sub">Minimum Age</label>
              <input
                type="number"
                v-model.number="formData.minage"
                class="dd-input"
                :class="{ 'input-error': errors.minage }"
                placeholder="e.g., 18"
                min="18"
                max="99"
              />
              <p v-if="errors.minage" class="error-message">{{ errors.minage }}</p>
            </div>
            <div class="age-range-divider">—</div>
            <div class="age-range-field">
              <label class="form-label-sub">Maximum Age</label>
              <input
                type="number"
                v-model.number="formData.maxage"
                class="dd-input"
                :class="{ 'input-error': errors.maxage }"
                placeholder="e.g., 35"
                min="18"
                max="99"
              />
              <p v-if="errors.maxage" class="error-message">{{ errors.maxage }}</p>
            </div>
          </div>
          <p class="input-hint">Set the age range you'd like to match with (18–99)</p>
        </div>

        <!-- Max Distance -->
        <div class="form-group">
          <label class="form-label">Maximum Distance</label>
          <div class="distance-input-wrapper">
            <input
              type="number"
              v-model.number="formData.maxdistance"
              class="dd-input distance-input"
              :class="{ 'input-error': errors.maxdistance }"
              placeholder="e.g., 50"
              min="1"
              max="20000"
            />
            <span class="distance-unit">km</span>
          </div>
          <p v-if="errors.maxdistance" class="error-message">{{ errors.maxdistance }}</p>
          <p class="input-hint">Maximum distance from your location to match with partners (1–20000 km)</p>
        </div>
 
        <!-- Interested In (Gender) -->
        <div class="form-group">
          <label class="form-label required">Interested In</label>
          <div class="radio-group" :class="{ 'radio-group-error': errors.interested_in }">
            <label class="radio-label">
              <input type="radio" value="male" v-model="formData.interested_in" />
              <span>Male</span>
            </label>
            <label class="radio-label">
              <input type="radio" value="female" v-model="formData.interested_in" />
              <span>Female</span>
            </label>
          </div>
          <p v-if="errors.interested_in" class="error-message">{{ errors.interested_in }}</p>
        </div>
 
        <!-- Form Actions -->
        <div class="form-actions">
          <button type="button" @click="emit('cancel')" class="btn-secondary">Cancel</button>
          <button type="submit" :disabled="isSubmitting" class="btn-primary">
            <span v-if="isSubmitting" class="spinner"></span>
            {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </form>
 
      <!-- Success/Error Messages -->
      <div v-if="message" class="alert" :class="messageType">
        {{ message }}
      </div>
    </div>
  </div>
</template>
 
<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import { getToken } from "@/services/auth";
 
onMounted(() => {
  getCsrfToken();
});
 
function getCsrfToken() {
  fetch('/api/v1/csrf-token')
    .then((response) => response.json())
    .then((data) => {
      csrf_token.value = data.csrf_token;
    })
}
 
// ── Props & Emits ──────────────────────────────────────────────────────────────
const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({
      username: '',
      firstname: '',
      lastname: '',
      bio: '',
      interests: '',
      lookingfor: 'dating',
      interested_in: '',
      minage: null,
      maxage: null,
      maxdistance: null
    })
  }
})
 
const emit = defineEmits(['submit', 'cancel'])
 
// ── Reactive State ─────────────────────────────────────────────────────────────
const formData = reactive({
  username: '',
  firstname: '',
  lastname: '',
  bio: '',
  interests: '',
  lookingfor: 'dating',
  interested_in: '',
  minage: null,
  maxage: null,
  maxdistance: null
})
 
const fileInput    = ref(null)
const imageFile    = ref(null)
const imagePreview = ref('')
const errors       = reactive({})
const isSubmitting = ref(false)
const message      = ref('')
const messageType  = ref('alert-success')
const csrf_token   = ref('')
 
// ── Sync initialData into formData ─────────────────────────────────────────────
watch(
  () => props.initialData,
  (newVal) => {
    if (newVal) Object.assign(formData, newVal)
  },
  { immediate: true }
)
 
// ── Photo Handlers ─────────────────────────────────────────────────────────────
function onFileChange(event) {
  const file = event.target.files[0]
  if (!file) return
 
  imageFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => { imagePreview.value = e.target.result }
  reader.readAsDataURL(file)
}
 
function removeImage() {
  imageFile.value    = null
  imagePreview.value = ''
  if (fileInput.value) fileInput.value.value = ''
}
 
// ── Submit ─────────────────────────────────────────────────────────────────────
function handleSubmit() {
  isSubmitting.value = true
  message.value = ''
  Object.keys(errors).forEach(key => delete errors[key])

  if (!formData.interested_in) {
    errors.interested_in = 'Please select who you are interested in.'
    showMessage('Please select who you are interested in.', 'alert-error')
    isSubmitting.value = false
    return
  }
 
  const payload = new FormData()
  payload.append('username',      formData.username)
  payload.append('firstname',     formData.firstname)
  payload.append('lastname',      formData.lastname)
  payload.append('bio',           formData.bio)
  payload.append('interests',     formData.interests)
  payload.append('lookingfor',    formData.lookingfor)
  payload.append('interested_in', formData.interested_in)

  // optional numeric fields
  if (formData.minage !== null && formData.minage !== undefined && formData.minage !== '') {
    payload.append('min_age', formData.minage)
  }

  if (formData.maxage !== null && formData.maxage !== undefined && formData.maxage !== '') {
    payload.append('max_age', formData.maxage)
  }

  if (formData.maxdistance !== null && formData.maxdistance !== undefined && formData.maxdistance !== '') {
    payload.append('max_distance', formData.maxdistance)
  }

  // optional file
  if (imageFile.value) {
    payload.append('photo', imageFile.value)
  }
 
  console.log("Submitting profile update:", Object.fromEntries(payload.entries()))
 
  fetch('/api/v1/profile', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getToken()}`,
      'X-CSRFToken': csrf_token.value
    },
    body: payload
  })
    .then(function(response) {
      console.log("Response status:", response.status)
      if (!response.ok) {
        return response.text().then(text => {
          throw new Error(text || "Request failed")
        })
      }
      return response.json()
    })
    .then(function(data) {
      console.log("Success:", data)
      showMessage(data.message || 'Profile updated successfully!', 'alert-success')
      emit('submit', data)
    })
    .catch(function(error) {
      console.error("Error:", error)
      try {
        const parsed = JSON.parse(error.message)
        if (parsed.errors) {
          Object.entries(parsed.errors).forEach(([field, messages]) => {
            const key = field === 'interested' ? 'interested_in' : field
            errors[key] = Array.isArray(messages) ? messages[0] : messages
          })
        }
        showMessage(parsed.message || 'Please fix the errors above', 'alert-error')
      } catch {
        showMessage('An error occurred while updating your profile', 'alert-error')
      }
    })
    .finally(function() {
      isSubmitting.value = false
    })
}
 
// ── Helpers ────────────────────────────────────────────────────────────────────
function showMessage(msg, type) {
  message.value     = msg
  messageType.value = type
  setTimeout(() => { message.value = '' }, 5000)
}
</script>
 
<style scoped>
.profile-edit-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #fff6ee 0%, #fdeef2 50%, #fff0e8 100%);
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
 
.profile-edit-card {
  max-width: 800px;
  width: 100%;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(192, 57, 90, 0.10);
  border-radius: 20px;
  box-shadow: 0 14px 40px rgba(192, 57, 90, 0.12);
  padding: 2rem;
  animation: slideUp 0.5s ease-out;
}
 
@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to   { opacity: 1; transform: translateY(0); }
}
 
.title {
  font-size: 2rem;
  color: var(--dd-dark);
  margin-bottom: 1.5rem;
  text-align: center;
  font-weight: 600;
  letter-spacing: -0.5px;
}
 
.profile-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
 
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
 
.form-label {
  font-weight: 600;
  color: var(--dd-mid);
  font-size: 0.95rem;
}
 
.form-label-sub {
  font-weight: 500;
  color: var(--dd-mid);
  font-size: 0.85rem;
}
 
.form-label.required::after {
  content: '*';
  color: #e74c3c;
  margin-left: 4px;
}
 
.input-error {
  border-color: #e74c3c !important;
}
 
.error-message {
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}
 
.input-hint {
  color: #999;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}
 
.char-counter {
  text-align: right;
  font-size: 0.75rem;
  color: #999;
  margin-top: 0.25rem;
}
 
/* Age Range Row */
.age-range-row {
  display: flex;
  align-items: flex-end;
  gap: 0.75rem;
}
 
.age-range-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
}
 
.age-range-divider {
  font-size: 1.2rem;
  color: #bbb;
  padding-bottom: 0.6rem;
  flex-shrink: 0;
}

/* Distance Input */
.distance-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.distance-input {
  padding-right: 3rem !important;
}

.distance-unit {
  position: absolute;
  right: 0.85rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--dd-mid);
  pointer-events: none;
  opacity: 0.6;
}
 
/* Photo Upload Area */
.photo-upload-area {
  position: relative;
  border: 2px dashed rgba(192, 57, 90, 0.18);
  background: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}
 
.photo-upload-area:hover {
  border-color: var(--dd-rose);
  background: var(--dd-rose-pale);
}
 
.current-photo {
  position: relative;
  display: inline-block;
}
 
.preview-image {
  max-width: 200px;
  max-height: 200px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
 
.remove-photo-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  cursor: pointer;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}
 
.remove-photo-btn:hover { transform: scale(1.1); }
 
.photo-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #999;
}
 
.placeholder-icon {
  width: 48px;
  height: 48px;
  opacity: 0.5;
}
 
.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}
 
/* Radio Group */
.radio-group {
  display: flex;
  gap: 1.5rem;
  padding: 0.5rem 0;
}

.radio-group-error {
  border: 1px solid #e74c3c;
  border-radius: 10px;
  padding: 0.75rem;
}
 
.radio-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
}
 
.radio-label input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}
 
/* Form Actions */
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}
 
.btn-primary,
.btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}
 
.btn-primary {
  background: linear-gradient(135deg, var(--dd-rose) 0%, var(--dd-coral) 100%);
  color: white;
  border-radius: 100px;
  box-shadow: 0 8px 20px rgba(192, 57, 90, 0.22);
}
 
.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(192, 57, 90, 0.4);
}
 
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
 
.btn-secondary {
  background: rgba(255, 255, 255, 0.85);
  color: var(--dd-mid);
  border: 1px solid rgba(192, 57, 90, 0.12);
}
 
.btn-secondary:hover {
  background: #e0e0e0;
  transform: translateY(-2px);
}
 
/* Alert Messages */
.alert {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 10px;
  text-align: center;
  animation: fadeIn 0.3s ease;
}
 
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to   { opacity: 1; transform: translateY(0); }
}
 
.alert-success {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid rgba(34, 197, 94, 0.22);
}
 
.alert-error {
  background: #FDEEF2;
  color: var(--dd-rose);
  border: 1px solid rgba(192, 57, 90, 0.18);
}
 
/* Spinner */
.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 8px;
}
 
@keyframes spin { to { transform: rotate(360deg); } }
 
/* Responsive */
@media (max-width: 768px) {
  .profile-edit-container { padding: 1rem; }
  .profile-edit-card { padding: 1.5rem; }
  .title { font-size: 1.5rem; }
  .form-actions { flex-direction: column; }
  .btn-primary, .btn-secondary { width: 100%; }
}
</style>
