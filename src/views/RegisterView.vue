<template>
  <div>
    <h2>Register</h2>

    <form @submit.prevent="registerForm" id="register_form">

      <input name="email" v-model="email" placeholder="Email" />

      <input name="username" v-model="username" placeholder="Username" />

      <input name="firstname" v-model="firstname" placeholder="First Name" />

      <input name="lastname" v-model="lastname" placeholder="Last Name" />

      <input name="dob" type="date" v-model="dob" />

      <select name="gender" v-model="gender">
        <option disabled value="">Select Gender</option>
        <option value="male">Male</option>
        <option value="female">Female</option>
      </select>

      <select name="lookingfor" v-model="lookingfor">
        <option disabled value="">Looking For</option>
        <option value="dating">Dating</option>
        <option value="friendship">Friendship</option>
        <option value="relationship">Relationship</option>
      </select>

      <input name="password" type="password" v-model="password" placeholder="Password" />

      <button type="submit">Register</button>
    </form>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
onMounted(() => {
  getCsrfToken();
});
let csrf_token = ref("");
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

function getCsrfToken() {
  fetch('/api/v1/csrf-token')
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      csrf_token.value = data.csrf_token;
    })
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
/*import { ref, onMounted } from "vue";
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
}*/
</script>