<template>
  <div>
    <h2>Register</h2>

    <form id="RegisterForm" @submit.prevent="registerForm">

  <input name="email" v-model="form.email" />
  <input name="username" v-model="form.username" />
  <input name="firstname" v-model="form.firstname" />
  <input name="lastname" v-model="form.lastname" />
  <input name="dob" type="date" v-model="form.dob" />

  <select name="gender" v-model="form.gender">
    <option value="male">Male</option>
    <option value="female">Female</option>
  </select>

  <select name="lookingfor" v-model="form.lookingfor">
    <option value="dating">Dating</option>
    <option value="friendship">Friendship</option>
    <option value="relationship">Relationship</option>
  </select>

  <input name="password" type="password" v-model="form.password" />

  <!-- CSRF token (important for Flask-WTF) -->
  <input type="hidden" name="csrf_token" :value="csrfToken" />

  <button type="submit">Register</button>
</form>
  </div>
</template>

<script setup>
import { reactive } from "vue"
import { ref, onMounted } from "vue";


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

function registerForm() {
  console.log(form) // you already have endpoint, so plug fetch/axios here
  form = RegistrationForm(meta={'csrf': False})
  let registerForm = document.getElementById('RegisterForm'); 
  let form_data = new FormData(registerForm); 
    fetch('/api/v1/register', {
        method: 'POST',
        body: form_data
    }).then(function(response) {
            if (!response.ok) {
                return response.text().then(text => {
            throw new Error(text || "Request failed");
        });
            }
            return response.json();
        }).then(function (data) {
            console.log("user registered successfully:", data);
        }).catch(function (error) {
            console.error("Error submitting form:", error);
        });
}
</script>