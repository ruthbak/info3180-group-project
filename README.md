# INFO3180 Final Project: DriftDater - Dating Application 

| Name | Role | Responsibility |
| :--- | :--- | :--- |
| Sukanayna Hoo @Sukanayna | Project Manager/Backend Lead | Oversees timeline, coordinates team efforts, API|
| Daniel Bingham @DannyB67 | QA/Testing Lead/ Backend Lead | Manages testing, validation, documentation, database, security  |
| Rashene Dillon @rashdill10 | Frontend Lead | Manages UI/UX, Vue 3 components |
| Ruth Bakare @ruthbak | Backend Lead/ Deployment Lead | Manages deployments, configurations, database|
| Darrin Belamy @Da-Bell | Frontend Lead | Manages UI/UX, Vue 3 components |


## Project Description
A DATING APPLICATION web platform (called DriftDater) that allows registered users to create detailed profiles, discover compatible matches, and initiate connections with other users. The application will be built using Vue 3 frontend framework and Flask backend API, with a database to store user profiles and matching information.

## Features
### 🚀 Key Features
- [ ] **Secure Authentication**: User registration and login with email validation and hashing.
- [ ] **Rich Profile Management**: Profiles including bio, location, and multiple interest tags.
- [ ] **Dynamic Image Uploads**: Built-in capability for users to upload and manage profile pictures.
- [ ] **Simple Matching Algorithm**: Get potential matches based on location, age range, preferences and shared interests/hobbies an what each user is looking for in a relationship
- [ ] **Interactive Discovery**: "Like/Dislike/Pass" functionality with mutual match detection.
- [ ] **Search & Filtering**: Tools to filter by name, age range, hobby, location name (e.g half way tree) (only for matched interests)
- [ ] **Messaging**: Persistent chat for matched users with reactive Vue.js updates.
- [ ] **Match Notifications**: Instant alerts when a mutual connection is established.
- [ ] **Bookmarks & Favorites**: Capability to save and organize profiles for quick access.


## 🛠️ Tech Stack
| Category | Technology | Key Implementations |
| :--- | :--- | :--- |
| **Backend** | **Flask (Python)** | RESTful API, Flask-Migrate, CORS, & Input Validation |
| **Frontend** | **Vue.js** | Pinia/Vuex State Management, Vue Router, & Responsive Design |
| **Database** | **SQLAlchemy ORM** | 4-5 Normalized Tables, Many-to-Many Relationships, & Indexes |
| **Authentication** | **JWT & Sessions** | Secure Login, Token-based Auth, & Password Hashing |
| **UI/UX** | **Component-based** | Reusable Components, Form Validation, & Loading States |


## SetUp Instructions 

## Prerequisites:
- Python 3.14 +
- Node.js 18+
- npm
- Postgresql
- Git Bash (optional for a terminal)

## Steps
### 1. Clone Repository 

```
git clone https://github.com/ruthbak/info3180-group-project.git
cd info3180-group-project
```
## Backend SetUp using Flask
### 2. Create and activate a virtual environment 
```
#Windows
python -m venv venv
.\venv\Scripts\activate

#Linus/Mac
python 3 -m venv venv
source /venv/bin/activate
```
### 3. Install dependencies 
```
#Dependency installation
pip install -r requirements.txt
```

### 4. Create a .env in the project root and configure
```
SECRET_KEY = 'yourkey'
DATABASE_URL=postgresql://username:password@host/databasename
```

### 5. Initialise databse if no migrations folder is present
```
flask --app app db init
flask --app app db migrate
flask --app app db upgrade
```
### 6. Run app
```
flask --app app run
```
## Frontend SetUp
### 7. Install npm and run
```
npm install
npm run dev
```

## 📡 API Endpoints Documentation
- Endpoints are at `https://localhost:5000`. 
- Flask cookie sessions are used for authentication (returns `401` if there is no login).
- JWT Tokens required for proteted routes.

---

## Base URL

```
http://localhost:5000/api
```

Production example:

```
https://api.yourdomain.com/api
```

---

## Authentication

Most endpoints require authentication using a Bearer Token.

Some example of these are:

---

GET `/users/`: Retrieve all users.

---

GET `/user/`: Get authenticated user profile.

---
POST `/profile` : Create or update user profile.

----
GET `/profile/<username>` :Get public profile by username.

----


### Header Format

```
Authorization: Bearer <your_token>
Content-Type: application/json
```

---

## 🔐 Auth Endpoints
### POST `/login`

Log in an existing user.

### Request Body

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Success Response — `200 OK`

```json
{
  "message": "Login successful.",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```
#### Errors : `400` missing fields and `401` for Invalid credentials

### POST `/register`

Register a new user.

### Request Body

```json
{
  "email": "user@example.com",
  "username": "dbrown",
  "firstname": "Dan"
  "lastname": "Brown"
  "dob": 2005-04-05
  "gender": "male"
  "looking for": "friendship"
  "password": "securepassword"
}
```

### Success Response — `201 Created`

```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "dbrown",
    "firstname": "Dan"
    "lastname": "Brown"
    "dob": 2005-04-05
    "gender": "male"
    "looking for": "friendship"
  }
}
```
#### Errors: `400` missing fields and `409` if email and username already exists

---

### Known issues/ limitations
- No password resent implemented
- No remember me feature is implemented
- Only active matches may be searched
- No real time matching






  


  
