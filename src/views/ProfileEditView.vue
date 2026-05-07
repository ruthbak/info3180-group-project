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
          <label class="form-label required">Username</label>
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
          <label class="form-label required">First Name</label>
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
          <label class="form-label required">Last Name</label>
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

        <!-- Password Change -->
        <div class="form-group">
          <label class="form-label">New Password</label>
          <input 
            type="password" 
            v-model="formData.password"
            class="dd-input"
            :class="{ 'input-error': errors.password }"
            placeholder="Leave blank to keep current password"
          />
          <p v-if="errors.password" class="error-message">{{ errors.password }}</p>
          <p class="input-hint">Min. 12 characters with uppercase, lowercase, number, and special character</p>
        </div>

        <div class="form-group">
          <label class="form-label">Confirm Password</label>
          <input 
            type="password" 
            v-model="formData.confirmPassword"
            class="dd-input"
            :class="{ 'input-error': errors.confirmPassword }"
            placeholder="Confirm new password"
          />
          <p v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</p>
        </div>

        <!-- Interests -->
        <div class="form-group">
          <label class="form-label">Interests</label>
          <input 
            type="text" 
            v-model="formData.interests"
            class="dd-input"
            :class="{ 'input-error': errors.interests }"
            placeholder="e.g., Music, Sports, Travel, Photography"
          />
          <p v-if="errors.interests" class="error-message">{{ errors.interests }}</p>
          <p class="input-hint">Comma-separated interests (max. 200 characters)</p>
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
          <label class="form-label required">Looking For</label>
          <select v-model="formData.lookingfor" class="dd-input" :class="{ 'input-error': errors.lookingfor }">
            <option value="dating">Dating</option>
            <option value="friendship">Friendship</option>
            <option value="relationship">Relationship</option>
          </select>
          <p v-if="errors.lookingfor" class="error-message">{{ errors.lookingfor }}</p>
        </div>

        <!-- Interested In (Gender) -->
        <div class="form-group">
          <label class="form-label required">Interested In</label>
          <div class="radio-group">
            <label class="radio-label">
              <input type="radio" value="male" v-model="formData.interested" />
              <span>Male</span>
            </label>
            <label class="radio-label">
              <input type="radio" value="female" v-model="formData.interested" />
              <span>Female</span>
            </label>
          </div>
          <p v-if="errors.interested" class="error-message">{{ errors.interested }}</p>
        </div>

        <!-- Form Actions -->
        <div class="form-actions">
          <button type="button" @click="$emit('cancel')" class="btn-secondary">Cancel</button>
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

<script>
export default {
  name: 'ProfileEditView',
  
  props: {
    initialData: {
      type: Object,
      default: () => ({
        username: '',
        firstname: '',
        lastname: '',
        bio: '',
        interests: '',
        lookingfor: 'dating',
        interested: 'male'
      })
    }
  },

  data() {
    return {
      formData: {
        username: '',
        firstname: '',
        lastname: '',
        password: '',
        confirmPassword: '',
        bio: '',
        interests: '',
        lookingfor: 'dating',
        interested: 'male'
      },
      imageFile: null,
      imagePreview: '',
      errors: {},
      isSubmitting: false,
      message: '',
      messageType: 'alert-success'
    }
  },

  watch: {
    initialData: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          this.formData = { ...this.formData, ...newVal }
        }
      }
    }
  },

  methods: {
    onFileChange(event) {
      const file = event.target.files[0]
      if (file) {
        if (file.size > 5 * 1024 * 1024) {
          this.showMessage('File size must be less than 5MB', 'alert-error')
          return
        }
        
        const validTypes = ['image/jpeg', 'image/png']
        if (!validTypes.includes(file.type)) {
          this.showMessage('Only JPG and PNG images are allowed', 'alert-error')
          return
        }
        
        this.imageFile = file
        const reader = new FileReader()
        reader.onload = (e) => {
          this.imagePreview = e.target.result
        }
        reader.readAsDataURL(file)
      }
    },

    removeImage() {
      this.imageFile = null
      this.imagePreview = ''
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    },

    validateForm() {
      this.errors = {}
      
      // Username validation
      const usernameRegex = /^[A-Za-z][A-Za-z0-9_.]*$/
      if (!this.formData.username) {
        this.errors.username = 'Username is required'
      } else if (this.formData.username.length < 8 || this.formData.username.length > 35) {
        this.errors.username = 'Username must be 8-35 characters'
      } else if (!usernameRegex.test(this.formData.username)) {
        this.errors.username = 'Username must start with a letter and contain only letters, numbers, dots, or underscores'
      }
      
      // First name validation
      const nameRegex = /^[A-Za-z]+$/
      if (!this.formData.firstname) {
        this.errors.firstname = 'First name is required'
      } else if (this.formData.firstname.length < 2 || this.formData.firstname.length > 50) {
        this.errors.firstname = 'First name must be 2-50 characters'
      } else if (!nameRegex.test(this.formData.firstname)) {
        this.errors.firstname = 'First name must contain only letters'
      }
      
      // Last name validation
      if (!this.formData.lastname) {
        this.errors.lastname = 'Last name is required'
      } else if (this.formData.lastname.length < 2 || this.formData.lastname.length > 50) {
        this.errors.lastname = 'Last name must be 2-50 characters'
      } else if (!nameRegex.test(this.formData.lastname)) {
        this.errors.lastname = 'Last name must contain only letters'
      }
      
      // Password validation (only if provided)
      const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$/
      if (this.formData.password) {
        if (this.formData.password.length < 12) {
          this.errors.password = 'Password must be at least 12 characters'
        } else if (!passwordRegex.test(this.formData.password)) {
          this.errors.password = 'Password must contain uppercase, lowercase, number, and special character (@$!%*?&)'
        }
        
        if (this.formData.password !== this.formData.confirmPassword) {
          this.errors.confirmPassword = 'Passwords do not match'
        }
      }
      
      // Bio validation
      if (this.formData.bio && this.formData.bio.length > 500) {
        this.errors.bio = 'Bio must be less than 500 characters'
      }
      
      // Interests validation
      if (this.formData.interests && this.formData.interests.length > 200) {
        this.errors.interests = 'Interests must be less than 200 characters'
      }
      
      // Looking for validation
      if (!this.formData.lookingfor) {
        this.errors.lookingfor = 'Please select what you are looking for'
      }
      
      // Interested validation
      if (!this.formData.interested) {
        this.errors.interested = 'Please select who you are interested in'
      }
      
      return Object.keys(this.errors).length === 0
    },

    async handleSubmit() {
      if (!this.validateForm()) {
        this.showMessage('Please fix the errors above', 'alert-error')
        return
      }
      
      this.isSubmitting = true
      this.message = ''
      
      try {
        const submitData = new FormData()
        submitData.append('username', this.formData.username)
        submitData.append('firstname', this.formData.firstname)
        submitData.append('lastname', this.formData.lastname)
        submitData.append('bio', this.formData.bio)
        submitData.append('interests', this.formData.interests)
        submitData.append('lookingfor', this.formData.lookingfor)
        submitData.append('interested', this.formData.interested)
        
        if (this.formData.password) {
          submitData.append('password', this.formData.password)
        }
        
        if (this.imageFile) {
          submitData.append('photo', this.imageFile)
        }
        
        // Emit the data to parent component
        this.$emit('submit', submitData)
        this.showMessage('Profile updated successfully!', 'alert-success')
        
        // Clear password fields after successful submission
        this.formData.password = ''
        this.formData.confirmPassword = ''
      } catch (error) {
        console.error('Error updating profile:', error)
        this.showMessage('An error occurred while updating your profile', 'alert-error')
      } finally {
        this.isSubmitting = false
      }
    },

    showMessage(msg, type) {
      this.message = msg
      this.messageType = type
      setTimeout(() => {
        this.message = ''
      }, 5000)
    }
  }
}
</script>

<style scoped>
.profile-edit-container {
  min-height: 100vh;
  background:
    linear-gradient(135deg, #fff6ee 0%, #fdeef2 50%, #fff0e8 100%);
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-edit-card {
  max-width: 800px;
  width: 100%;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(192,57,90,0.10);
  border-radius: 20px;
  box-shadow: 0 14px 40px rgba(192,57,90,0.12);  padding: 2rem;
  animation: slideUp 0.5s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

.form-label.required::after {
  content: '*';
  color: #e74c3c;
  margin-left: 4px;
}


.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--dd-rose);
  box-shadow: 0 0 0 3px rgba(192,57,90,0.10);
}

textarea.form-textarea {
  resize: vertical;
  min-height: 100px;
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

/* Photo Upload Area */
.photo-upload-area {
  position: relative;
  border: 2px dashed rgba(192,57,90,0.18);
  background: rgba(255,255,255,0.7);
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

.remove-photo-btn:hover {
  transform: scale(1.1);
}

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
  background: linear-gradient(
    135deg,
    var(--dd-rose) 0%,
    var(--dd-coral) 100%
  );

  color: white;
  border: none;

  border-radius: 100px;

  font-weight: 600;

  box-shadow:
    0 8px 20px rgba(192,57,90,0.22);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: rgba(255,255,255,0.85);
  color: var(--dd-mid);
  border: 1px solid rgba(192,57,90,0.12);
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
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.alert-success {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid rgba(34,197,94,0.22);
}

.alert-error {
  background: #FDEEF2;
  color: var(--dd-rose);
  border: 1px solid rgba(192,57,90,0.18);
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

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .profile-edit-container {
    padding: 1rem;
  }
  
  .profile-edit-card {
    padding: 1.5rem;
  }
  
  .title {
    font-size: 1.5rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
  }
}
</style>