<template>
  <div>
    <h2>Register</h2>

    <form @submit.prevent="registerForm">

      <input name="email" v-model="form.email" placeholder="Email" />

      <input name="username" v-model="form.username" placeholder="Username" />

      <input name="firstname" v-model="form.firstname" placeholder="First Name" />

      <input name="lastname" v-model="form.lastname" placeholder="Last Name" />

      <input name="dob" type="date" v-model="form.dob" />

      <select name="gender" v-model="form.gender">
        <option disabled value="">Select Gender</option>
        <option value="male">Male</option>
        <option value="female">Female</option>
      </select>

      <select name="lookingfor" v-model="form.lookingfor">
        <option disabled value="">Looking For</option>
        <option value="dating">Dating</option>
        <option value="friendship">Friendship</option>
        <option value="relationship">Relationship</option>
      </select>

      <input name="password" type="password" v-model="form.password" placeholder="Password" />

      <button type="submit">Register</button>
    </form>

  </div>
</template>

<script setup>
import { reactive } from "vue"
import { ref, onMounted } from "vue";
onMounted(() => { 
getCsrfToken(); 
}); 
let csrf_token = ref(""); 
const form = reactive({
  email: "",
  username: "",
  firstname: "",
  lastname: "",
  dob: "",
  gender: "",
  lookingfor: "",
  password: ""
})
function getCsrfToken() { 
fetch('/api/v1/csrf-token') 
.then((response) => response.json()) 
.then((data) => { 
console.log(data); 
csrf_token.value = data.csrf_token; 
}) 
}
async function registerForm() {
  try {
    // Build FormData from Vue state
    const form_data = new FormData()

    for (let key in form) {
      form_data.append(key, form[key])
    }
    console.log("Submitting form data:", Object.fromEntries(form_data.entries()))
    const response = await fetch('/api/v1/register', {
      method: 'POST',
      body: form_data,
      headers: {
                "X-CSRFToken": csrf_token.value 
            }
    })
    console.log("Received response:", response)
    const data = await response.json()

    if (!response.ok) {
      console.error("Validation errors:", data.errors)
      return
    }

    console.log("User registered successfully:", data)

  } catch (error) {
    console.error("Error submitting form:", error)
  }
}
</script>