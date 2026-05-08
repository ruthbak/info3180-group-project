<template>
  <div>

    <!-- ══ WELCOME BANNER ══ -->
    <div class="dd-welcome-banner mb-4">
      <div class="dd-welcome-left">
        <p class="dd-welcome-eyebrow">✦ {{ today }}</p>
        <h2 class="dd-welcome-title">Welcome back, {{ user?.first_name }}! 👋</h2>
        <p class="dd-welcome-sub">
          You have <strong>{{ remainingMatches }} potential matches</strong> waiting for you today.
          Keep swiping and find your perfect flame.
        </p>
        <div class="dd-welcome-stats">
          <div class="dd-wstat">
            <span class="dd-wstat-num">{{ likedCount }}</span>
            <span class="dd-wstat-label">Liked</span>
          </div>
          <div class="dd-wstat-divider"></div>
          <div class="dd-wstat">
            <span class="dd-wstat-num">{{ matchCount }}</span>
            <span class="dd-wstat-label">Matches</span>
          </div>
          <div class="dd-wstat-divider"></div>
          <div class="dd-wstat">
            <span class="dd-wstat-num">{{ messageCount }}</span>
            <span class="dd-wstat-label">Messages</span>
          </div>
        </div>
      </div>
      <div class="dd-welcome-right d-none d-lg-flex">
        <div class="dd-welcome-card-stack">
          <div class="dd-stack-card dd-stack-card-3"></div>
          <div class="dd-stack-card dd-stack-card-2"></div>
          <div class="dd-stack-card dd-stack-card-1">
              <div class="dd-stack-avatar"><i class="bi bi-person-circle"></i></div>
            <div>
              <p class="dd-stack-name">Your next match</p>
              <p class="dd-stack-loc">📍 To Be Updated</p>
            </div>
            <span class="dd-stack-pct">??%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ PROFILE QUICK CARD ══ -->
    <div class="dd-profile-card mb-5">
      <div class="dd-pc-avatar"><img :src="user?.profile_photo" alt="Profile Photo" /></div>
      <div class="dd-pc-info flex-grow-1">
        <h6 class="dd-pc-name">{{ user?.first_name }} {{ user?.last_name }}</h6>
        <div class="dd-pc-meta">
        <span><i class="bi bi-cake2"></i> {{ user?.age }} yrs</span>
        <span><i class="bi bi-geo-alt-fill"></i> {{ user?.location }}</span>
        <span><i class="bi bi-heart-fill"></i> {{ user?.looking_for }}</span>
        </div>
        <p class="dd-pc-bio">{{ user?.bio }}</p>
      </div>
      <RouterLink to="/profile/edit" class="btn dd-btn-edit ms-auto">
        <i class="bi bi-pencil-square me-1"></i> Edit Profile
      </RouterLink>
    </div>

    <!-- ══ BROWSE MATCHES ══ -->
    <div class="d-flex align-items-center justify-content-between mb-3">
      <h5 class="dd-section-title mb-0">Browse Potential Matches</h5>
      <span class="dd-count-badge">{{ remainingMatches }} profiles</span>
    </div>

    <!-- Filter Bar -->
    <div class="dd-filter-bar mb-4">
      <div class="row g-2 align-items-center">
        <div class="col-12 col-md-3">
          <div class="dd-filter-input-wrap">
            <i class="bi bi-search dd-filter-icon"></i>
            <input type="text" v-model="filters.search"
              class="dd-filter-field" placeholder="Name..." />
          </div>
        </div>
        <div class="col-6 col-md-2">
          <select v-model="filters.ageRange" class="dd-filter-select">
            <option value="">All Ages</option>
            <option value="18-24">18 – 24</option>
            <option value="25-30">25 – 30</option>
            <option value="31-40">31 – 40</option>
            <option value="40+">40+</option>
          </select>
        </div>
        <div class="col-6 col-md-2">
          <div class="dd-filter-input-wrap">
            <i class="bi bi-geo-alt dd-filter-icon"></i>
            <input type="text" v-model="filters.location"
              class="dd-filter-field" placeholder="Location..." />
          </div>
        </div>
        <div class="col-6 col-md-2">
          <div class="dd-filter-input-wrap">
            <i class="bi bi-stars dd-filter-icon"></i>
            <input type="text" v-model="filters.interest"
              class="dd-filter-field" placeholder="Hobby..." />
          </div>
        </div>
        <div class="col-6 col-md-2">
          <select v-model="filters.sort" class="dd-filter-select">
            <option value="most_similar">Most Similar</option>
            <option value="newest">Newest</option>
            <option value="name">Name</option>
            <option value="age_low">Age Low</option>
            <option value="age_high">Age High</option>
          </select>
        </div>
        <div class="col-6 col-md-1">
          <button class="btn dd-btn-reset w-100" @click="searchProfiles">
            <i class="bi bi-funnel"></i>
          </button>
        </div>
        <div class="col-6 col-md-12 col-lg-1">
          <button class="btn dd-btn-reset w-100" @click="resetFilters">
            <i class="bi bi-x-circle"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div class="dd-empty text-center py-5" v-if="filteredMatches.length === 0">
      <div class="dd-empty-emoji">💔</div>
      <h6 class="dd-empty-title mt-3" v-if = errors != null>{{errors}}</h6>
      <h6 class="dd-empty-title mt-3" v-else>No profiles found</h6>
      <p class="dd-empty-sub">Try adjusting your filters.</p>
      <button class="btn dd-btn-primary mt-2" @click="resetFilters">Reset Filters</button>
    </div>

    <!-- Match Cards -->
    <div class="dd-cards-list" v-else>
      <div
        v-for="match in filteredMatches" :key="match.id"
        class="dd-match-card"
        :class="{ liked: match.status === 'liked', passed: match.status === 'passed' }"
      >
        <!-- Avatar -->
        <div class="dd-mc-avatar" :style="{ background: match.avatarBg }">
          <i class="bi bi-person-fill"></i>
        </div>

        <!-- Info -->
        <div class="dd-mc-info flex-grow-1">
          <div class="d-flex align-items-center gap-2 flex-wrap mb-1">
            <span class="dd-mc-name">{{ match.name }}, {{ match.age }}</span>
            <span class="dd-mc-score">{{ match.matchScore }}% match</span>
          </div>
          <div class="dd-mc-meta">
            <span><i class="bi bi-geo-alt-fill"></i> {{ match.location }}</span>
            <span><i class="bi bi-heart-fill"></i> {{ match.lookingFor }}</span>
          </div>
          <p class="dd-mc-bio">{{ match.bio }}</p>
          <div class="dd-mc-tags">
            <span class="dd-tag" v-for="i in match.interests" :key="i">{{ i }}</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="dd-mc-actions" v-if="match.status === 'pending'">
          <RouterLink :to="`/profile/${match.username}`" class="btn dd-btn-view-profile">
            <i class="bi bi-person-heart me-1"></i>View
          </RouterLink>
          <button class="btn dd-btn-fav" @click="toggleFavorite(match)">
            <i class="bi me-1" :class="match.isFavorite ? 'bi-bookmark-fill' : 'bi-bookmark'"></i>
            {{ match.isFavorite ? 'Saved' : 'Save' }}
          </button>
          <button class="btn dd-btn-like" @click="likeProfile(match)">
            <i class="bi bi-heart-fill me-1"></i>Like
          </button>
          <button class="btn dd-btn-pass" @click="passProfile(match)">
            <i class="bi bi-x-lg me-1"></i>Pass
          </button>
        </div>
        <div class="dd-mc-status liked-badge" v-else-if="match.status === 'liked'">
          <i class="bi bi-heart-fill me-1"></i>Liked!
        </div>
        <div class="dd-mc-status passed-badge" v-else>
          <i class="bi bi-x-lg me-1"></i>Passed
        </div>
      </div>
    </div>

    <!-- Toast -->
    <Transition name="toast">
      <div class="dd-toast" v-if="showToast">
        🎉 It's a match with <strong>{{ toastName }}</strong>!
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { getToken } from "@/services/auth";
onMounted(async () => {
    await fetchUserProfile();
    await getPotentialMatches();
    await fetchMatchCount();
// now to fetch the potential matches we will run the potential matches API to get the list of potential matches and store it in the potentialMatches ref. we will also calculate the match score for each potential match based on the user's profile and the potential match's profile, and store that in the match object as well. for simplicity, we will just calculate a random match score for now, but in a real application you would use a more sophisticated algorithm to calculate the match score based on factors like shared interests, location proximity, etc.
});
async function fetchUserProfile() {
  try {
    const token = getToken();

    const response = await fetch("/api/v1/user/", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) {
      response.text().then(text => {
      throw new Error(text || "request failed");
      });
    }
    
    const data = await response.json();


    user.value = data.user;


  } catch (err) {
    error.value = err.message;
    console.log(error.value)

  }
  }
async function getPotentialMatches() {
  console.log("Fetching potential matches...");
  try {
    const token = getToken();

    const response = await fetch("/api/v1/possible-matches", {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    // handle HTTP errors properly
    if (!response.ok) {
      const errorText = await response.text();

      let errorData;
      try {
        errorData = JSON.parse(errorText);
      } catch {
        throw new Error(errorText || "Request failed");
      }

      throw new Error(JSON.stringify(errorData));
    }

    const data = await response.json();
    const matches = data.matches || data.match_list || [];

    potentialMatches.value = matches.map(normalizeMatch);

    console.log("Fetched potential matches:", potentialMatches.value);

  } catch (error) {

  try {
    const parsed = JSON.parse(error.message);

    if (parsed.errors) {
      errors.value = parsed.errors;

    } else if (parsed.message) {
      errors.value = parsed.message;

    } else {
      errors.value = ["An unknown error occurred."];
    }

  } catch {
    errors.value = [error.message];
  }

  console.error("Error:", error);
}
}
const user = ref(null);
const error = ref("");
const errors = ref("");
const matchCount   = ref(0)
const messageCount = ref(0)




const userInitials = computed(() => {
  if (!user.value?.firstname && !user.value?.lastname) return '?'
  return (user.value.firstname[0] || '') + (user.value.lastname[0] || '')
})



const today = new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric' })

const potentialMatches = ref([])

function normalizeMatch(match) {
  return {
    id: match.id || match.user_id,
    user_id: match.user_id,
    username: match.username,
    name: match.name || `${match.first_name || ''} ${match.last_name || ''}`.trim() || match.username,
    age: match.age,
    bio: match.bio || match.description || '',
    location: match.location || '',
    lookingFor: match.lookingFor || (Array.isArray(match.looking_for) ? match.looking_for.join(', ') : match.looking_for) || '',
    interests: match.interests || match.common_hobbies || [],
    matchScore: match.matchScore || match.match_score || 0,
    status: match.status || 'pending',
    isFavorite: Boolean(match.isFavorite),
    avatarBg: match.avatarBg || 'linear-gradient(135deg, #C0395A, #E8563A)'
  };
}

const filters = reactive({ search: '', ageRange: '', location: '', interest: '', sort: 'most_similar' })
const resetFilters = async () => {
  filters.search = '';
  filters.ageRange = '';
  filters.location = '';
  filters.interest = '';
  filters.sort = 'most_similar';
  await getPotentialMatches();
}

const filteredMatches = computed(() => potentialMatches.value.filter(m => {
  const s = filters.search.toLowerCase()
  const okSearch   = !s || m.name.toLowerCase().includes(s) || m.bio.toLowerCase().includes(s)
  const okLocation = !filters.location || m.location.toLowerCase().includes(filters.location.toLowerCase())
  const okInterest = !filters.interest || m.interests.some(i => i.toLowerCase().includes(filters.interest.toLowerCase()))
  let okAge = true
  if (filters.ageRange === '18-24') okAge = m.age >= 18 && m.age <= 24
  else if (filters.ageRange === '25-30') okAge = m.age >= 25 && m.age <= 30
  else if (filters.ageRange === '31-40') okAge = m.age >= 31 && m.age <= 40
  else if (filters.ageRange === '40+') okAge = m.age > 40
  return okSearch && okLocation && okInterest && okAge
}))

const remainingMatches = computed(() => potentialMatches.value.filter(m => m.status === 'pending').length)
const likedCount       = computed(() => potentialMatches.value.filter(m => m.status === 'liked').length)

const showToast = ref(false)
const toastName = ref('')
function fireToast(name) { toastName.value = name; showToast.value = true; setTimeout(() => showToast.value = false, 3000) }

async function parseResponse(response) {
  const text = await response.text();
  if (!text) return {};

  try {
    return JSON.parse(text);
  } catch {
    return { message: text };
  }
}

async function getCsrfToken() {
  const response = await fetch('/api/v1/csrf-token');
  const data = await parseResponse(response);

  if (!response.ok) {
    throw new Error(data.message || 'Failed to fetch CSRF token');
  }

  return data.csrf_token;
}

async function fetchMatchCount() {
  try {
    const token = getToken();
    const response = await fetch('/api/v1/matches', {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (!response.ok) return;

    const data = await response.json();
    matchCount.value = data.total || data.matches?.length || 0;
  } catch (err) {
    console.error('Failed to fetch match count:', err);
  }
}

function getAgeParams() {
  if (filters.ageRange === '18-24') return { min_age: 18, max_age: 24 };
  if (filters.ageRange === '25-30') return { min_age: 25, max_age: 30 };
  if (filters.ageRange === '31-40') return { min_age: 31, max_age: 40 };
  if (filters.ageRange === '40+') return { min_age: 41 };
  return {};
}

async function searchProfiles() {
  try {
    const token = getToken();
    const params = new URLSearchParams();
    const ageParams = getAgeParams();

    if (filters.search) params.set('name', filters.search);
    if (filters.location) params.set('location', filters.location);
    if (filters.interest) params.set('interest', filters.interest);
    if (filters.sort) params.set('sort', filters.sort);
    if (ageParams.min_age) params.set('min_age', ageParams.min_age);
    if (ageParams.max_age) params.set('max_age', ageParams.max_age);

    const response = await fetch(`/api/v1/search?${params.toString()}`, {
      headers: { "Authorization": `Bearer ${token}` }
    });
    const data = await parseResponse(response);
    if (!response.ok) throw new Error(data.message || 'Failed to search profiles');

    potentialMatches.value = (data.matches || data.users || []).map(normalizeMatch);
    errors.value = '';
  } catch (err) {
    errors.value = err.message;
    console.error('Failed to search profiles:', err);
  }
}

async function likeProfile(match) {
  try {
    const token = getToken();
    const csrfToken = await getCsrfToken();
    const response = await fetch(`/api/v1/likes/${match.username}`, {
      method: 'POST',
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify({ match_score: match.matchScore })
    });

    const data = await parseResponse(response);
    if (!response.ok) throw new Error(data.message || 'Failed to like profile');

    match.status = 'liked';
    if (data.matched) {
      fireToast(match.name);
      matchCount.value += 1;
    }
  } catch (err) {
    errors.value = err.message;
    console.error('Failed to like profile:', err);
  }
}

async function passProfile(match) {
  try {
    const token = getToken();
    const csrfToken = await getCsrfToken();
    const response = await fetch(`/api/v1/pass/${match.username}`, {
      method: 'POST',
      headers: {
        "Authorization": `Bearer ${token}`,
        "X-CSRFToken": csrfToken
      }
    });

    const data = await parseResponse(response);
    if (!response.ok) throw new Error(data.message || 'Failed to pass profile');

    match.status = 'passed';
  } catch (err) {
    errors.value = err.message;
    console.error('Failed to pass profile:', err);
  }
}

async function toggleFavorite(match) {
  try {
    const token = getToken();
    const csrfToken = await getCsrfToken();
    const response = await fetch(`/api/v1/favourites/${match.username}`, {
      method: match.isFavorite ? 'DELETE' : 'POST',
      headers: {
        "Authorization": `Bearer ${token}`,
        "X-CSRFToken": csrfToken
      }
    });

    const data = await parseResponse(response);
    if (!response.ok && response.status !== 409) {
      throw new Error(data.message || 'Failed to update favourite');
    }

    match.isFavorite = response.status === 409 ? true : !match.isFavorite;
  } catch (err) {
    errors.value = err.message;
    console.error('Failed to update favourite:', err);
  }
}
</script>

<style scoped>
/* ══ WELCOME BANNER ══ */
.dd-welcome-banner {
  background: linear-gradient(135deg, #C0395A 0%, #9B2040 40%, #E8563A 100%);
  border-radius: 20px;
  padding: 2rem 2.2rem;
  display: flex; align-items: center; justify-content: space-between;
  gap: 2rem; overflow: hidden; position: relative;
  box-shadow: 0 12px 40px rgba(192,57,90,0.30);
}
.dd-welcome-banner::before {
  content: '♥';
  position: absolute; right: -1rem; top: -2rem;
  font-size: 14rem; color: rgba(255,255,255,0.05);
  pointer-events: none;
}

.dd-welcome-eyebrow {
  font-size: 0.75rem; font-weight: 600; letter-spacing: 0.1em;
  text-transform: uppercase; color: rgba(255,255,255,0.6);
  margin-bottom: 0.5rem;
}
.dd-welcome-title {
  font-family: 'Georgia', serif;
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 700; color: #fff;
  margin-bottom: 0.6rem; letter-spacing: -0.02em;
}
.dd-welcome-sub {
  font-size: 0.9rem; color: rgba(255,255,255,0.75);
  margin-bottom: 1.5rem; max-width: 400px; line-height: 1.65;
}
.dd-welcome-sub strong { color: #fff; }

/* Stats row inside banner */
.dd-welcome-stats {
  display: flex; align-items: center; gap: 1.5rem;
}
.dd-wstat { display: flex; flex-direction: column; }
.dd-wstat-num {
  font-family: 'Georgia', serif;
  font-size: 1.6rem; font-weight: 700; color: #fff; line-height: 1;
}
.dd-wstat-label { font-size: 0.72rem; color: rgba(255,255,255,0.55); margin-top: 0.1rem; }
.dd-wstat-divider { width: 1px; height: 36px; background: rgba(255,255,255,0.2); }

/* Stacked cards visual */
.dd-welcome-right { align-items: center; justify-content: center; }
.dd-welcome-card-stack { position: relative; width: 210px; height: 90px; }
.dd-stack-card {
  position: absolute; border-radius: 14px;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255,255,255,0.2);
}
.dd-stack-card-3 { width: 170px; height: 70px; top: 14px; left: 20px; transform: rotate(-6deg); }
.dd-stack-card-2 { width: 185px; height: 75px; top: 8px; left: 12px; transform: rotate(-2deg); }
.dd-stack-card-1 {
  width: 200px; height: 80px; top: 0; left: 0;
  background: rgba(255,255,255,0.22);
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0 1rem;
}
.dd-stack-avatar { 
  font-size: 1.6rem;
  color: rgba(255,255,255,0.85);
  }
.dd-stack-name { font-size: 0.84rem; font-weight: 700; color: #fff; margin: 0; }
.dd-stack-loc  { font-size: 0.72rem; color: rgba(255,255,255,0.65); margin: 0; }
.dd-stack-pct  {
  margin-left: auto; font-size: 0.75rem; font-weight: 700;
  background: rgba(255,255,255,0.25); color: #fff;
  padding: 0.2rem 0.55rem; border-radius: 100px;
}

/* ══ PROFILE QUICK CARD ══ */
.dd-profile-card {
  background: #fff; border-radius: 20px;
  padding: 1.6rem 2.2rem;
  display: flex; align-items: center; gap: 1.3rem; flex-wrap: wrap;
  box-shadow: 0 4px 20px rgba(192,57,90,0.07);
  border: 1px solid rgba(192,57,90,0.08);
  width: 100%;
}
.dd-pc-avatar {
  width: 58px; height: 58px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, #C0395A, #E8563A);
  color: #fff; font-weight: 700; font-size: 1.1rem;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 14px rgba(192,57,90,0.28);
}
.dd-pc-avatar img {
  width: 100%; height: 100%; border-radius: 50%;
  object-fit: cover;
  border: black 1px solid;
}
.dd-pc-name { font-weight: 700; font-size: 1rem; color: #2A1018; margin: 0 0 0.25rem; }
.dd-pc-meta { display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.8rem; color: #9E6373; margin-bottom: 0.3rem; }
.dd-pc-bio { font-size: 0.85rem; color: #6B3A48; margin: 0; }
.dd-btn-edit {
  background: #FDEEF2; color: #C0395A;
  border: 1.5px solid rgba(192,57,90,0.22);
  border-radius: 100px; font-size: 0.83rem; font-weight: 600;
  white-space: nowrap; transition: background 0.18s;
}
.dd-btn-edit:hover { background: #f9d0da; color: #C0395A; }

/* ══ SECTION HEADER ══ */
.dd-section-title {
  font-family: 'Georgia', serif;
  font-size: 1.1rem; font-weight: 700; color: #2A1018;
}
.dd-count-badge {
  font-size: 0.8rem; font-weight: 600;
  background: #FDEEF2; color: #C0395A;
  padding: 0.28rem 0.8rem; border-radius: 100px;
}

/* ══ FILTER BAR ══ */
.dd-filter-bar {
  background: #fff; border-radius: 14px;
  padding: 1rem 1.3rem;
  box-shadow: 0 2px 12px rgba(192,57,90,0.06);
  border: 1px solid rgba(192,57,90,0.08);
}
.dd-filter-input-wrap {
  position: relative; display: flex; align-items: center;
}
.dd-filter-icon {
  position: absolute; left: 0.85rem;
  color: #C09AAA; font-size: 0.82rem; pointer-events: none;
}
.dd-filter-field {
  width: 100%; padding: 0.55rem 0.9rem 0.55rem 2.2rem;
  border: 1.5px solid rgba(192,57,90,0.16);
  border-radius: 10px; font-size: 0.86rem; color: #2A1018;
  outline: none; transition: border-color 0.18s, box-shadow 0.18s;
  background: #FFFAF7;
}
.dd-filter-field:focus {
  border-color: #C0395A;
  box-shadow: 0 0 0 3px rgba(192,57,90,0.09);
}
.dd-filter-select {
  width: 100%; padding: 0.55rem 0.9rem;
  border: 1.5px solid rgba(192,57,90,0.16);
  border-radius: 10px; font-size: 0.86rem; color: #2A1018;
  outline: none; background: #FFFAF7;
  transition: border-color 0.18s;
}
.dd-filter-select:focus { border-color: #C0395A; }
.dd-btn-reset {
  background: #f4ede8; color: #9E6373;
  border: 1.5px solid rgba(192,57,90,0.12);
  border-radius: 10px; font-size: 0.84rem; font-weight: 600;
  transition: background 0.18s;
}
.dd-btn-reset:hover { background: #FDEEF2; color: #C0395A; }

/* ══ MATCH CARDS ══ */
.dd-cards-list { display: flex; flex-direction: column; gap: 0.85rem; }
.dd-match-card {
  background: #fff; border-radius: 16px;
  padding: 1.25rem 1.6rem;
  display: flex; align-items: center; gap: 1.2rem; flex-wrap: wrap;
  border: 1px solid rgba(192,57,90,0.08);
  box-shadow: 0 2px 14px rgba(192,57,90,0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}
.dd-match-card:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(192,57,90,0.11); }
.dd-match-card.liked  { background: #fffafc; border-color: rgba(192,57,90,0.22); opacity: 0.85; }
.dd-match-card.passed { opacity: 0.4; }

.dd-mc-avatar {
  width: 60px; height: 60px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 1.5rem;
}
.dd-mc-name { font-weight: 700; font-size: 0.95rem; color: #2A1018; }
.dd-mc-score {
  font-size: 0.72rem; font-weight: 700;
  background: #FDEEF2; color: #C0395A;
  padding: 0.18rem 0.55rem; border-radius: 100px;
}
.dd-mc-meta {
  display: flex; gap: 0.9rem; font-size: 0.8rem; color: #9E6373;
  margin-bottom: 0.3rem; flex-wrap: wrap;
}
.dd-mc-meta i { font-size: 0.75rem; }
.dd-mc-bio { font-size: 0.85rem; color: #6B3A48; margin: 0; line-height: 1.5; }
.dd-mc-tags { display: flex; gap: 0.35rem; flex-wrap: wrap; margin-top: 0.5rem; }
.dd-tag {
  font-size: 0.72rem; font-weight: 500;
  background: #FFF0E8; color: #D4770A;
  padding: 0.18rem 0.6rem; border-radius: 100px;
}

/* Actions */
.dd-mc-actions { display: flex; flex-direction: column; gap: 0.45rem; flex-shrink: 0; }
.dd-btn-like {
  background: linear-gradient(135deg, #C0395A, #E8563A);
  color: #fff; border: none; border-radius: 100px;
  font-size: 0.82rem; font-weight: 600; padding: 0.42rem 1.1rem;
  box-shadow: 0 4px 12px rgba(192,57,90,0.28);
  transition: opacity 0.18s, transform 0.15s;
  white-space: nowrap;
}
.dd-btn-like:hover { opacity: 0.88; transform: scale(1.04); color: #fff; }
.dd-btn-pass {
  background: #f0e8e5; color: #9E6373;
  border: none; border-radius: 100px;
  font-size: 0.82rem; font-weight: 600; padding: 0.42rem 1.1rem;
  transition: background 0.18s; white-space: nowrap;
}
.dd-btn-pass:hover { background: #e8d8d0; }

.dd-btn-view-profile {
  background: #fff; color: #C0395A;
  border: 1.5px solid rgba(192,57,90,0.14);
  border-radius: 100px;
  font-size: 0.82rem; font-weight: 600; padding: 0.42rem 1.1rem;
  transition: background 0.18s; white-space: nowrap;
}
.dd-btn-view-profile:hover { background: #FDEEF2; color: #C0395A; }

.dd-btn-fav {
  background: #FFF6EE; color: #D4770A;
  border: none; border-radius: 100px;
  font-size: 0.82rem; font-weight: 600; padding: 0.42rem 1.1rem;
  transition: background 0.18s; white-space: nowrap;
}
.dd-btn-fav:hover { background: #FFE6D2; color: #B95F05; }

.dd-mc-status {
  font-size: 0.8rem; font-weight: 600;
  padding: 0.35rem 0.9rem; border-radius: 100px;
  white-space: nowrap; flex-shrink: 0;
}
.liked-badge  { background: #FDEEF2; color: #C0395A; }
.passed-badge { background: #f0e8e5; color: #9E6373; }

/* ══ EMPTY ══ */
.dd-empty-emoji { font-size: 3rem; }
.dd-empty-title { font-weight: 700; color: #2A1018; }
.dd-empty-sub   { font-size: 0.88rem; color: #9E6373; }
.dd-btn-primary {
  background: linear-gradient(135deg, #C0395A, #E8563A);
  color: #fff; border: none; border-radius: 100px;
  font-weight: 600; font-size: 0.88rem; transition: opacity 0.18s;
}
.dd-btn-primary:hover { opacity: 0.88; color: #fff; }

/* ══ TOAST ══ */
.dd-toast {
  position: fixed; bottom: 2rem; left: 50%; transform: translateX(-50%);
  background: linear-gradient(135deg, #C0395A, #E8563A);
  color: #fff; font-size: 0.92rem; font-weight: 600;
  padding: 0.8rem 2rem; border-radius: 100px;
  box-shadow: 0 8px 28px rgba(192,57,90,0.35);
  z-index: 9999; white-space: nowrap;
}
.toast-enter-active, .toast-leave-active { transition: opacity 0.3s, transform 0.3s; }
.toast-enter-from { opacity: 0; transform: translateX(-50%) translateY(16px); }
.toast-leave-to   { opacity: 0; transform: translateX(-50%) translateY(16px); }
</style>
