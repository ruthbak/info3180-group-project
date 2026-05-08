<template>
  <div class="dd-profile-page">

    <!-- HERO -->
    <section class="dd-profile-hero">
      <div class="dd-profile-avatar-wrap">
        <div class="dd-profile-avatar">
          <img
            v-if="profile.photoUrl"
            :src="profile.photoUrl"
            :alt="`${profile.firstName}`"
            class="dd-avatar-img"
          />
          <span v-else class="dd-avatar-initials">
            {{ profile.firstName?.charAt(0) ?? '?' }}
          </span>
        </div>
        <span class="dd-online-badge">
          <i class="bi bi-circle-fill"></i> Online
        </span>
      </div>

      <div class="dd-profile-hero-content">
        <div class="dd-hero-top">
          <h2 class="dd-profile-name">
            {{ profile.firstName }} {{ profile.lastName }}<span class="dd-age">, {{ profile.age }}</span>
          </h2>
          <span class="dd-match-score">
            <i class="bi bi-stars me-1"></i>{{ profile.matchScore }}% Match
          </span>
        </div>

        <div class="dd-profile-meta">
          <span v-if="profile.location">
            <i class="bi bi-geo-alt-fill"></i> {{ profile.location }}
          </span>
          <span v-if="profile.lookingFor">
            <i class="bi bi-heart-fill"></i> Looking for {{ profile.lookingFor }}
          </span>
          <span v-if="profile.distance">
            <i class="bi bi-signpost-2-fill"></i> {{ profile.distance }} km away
          </span>
        </div>

        <p class="dd-profile-bio">{{ profile.bio }}</p>

        <div class="dd-profile-actions">
          <RouterLink v-if="isOwnProfile" to="/profile/edit" class="btn dd-btn-primary">
            <i class="bi bi-pencil-square me-2"></i>Edit Profile
          </RouterLink>
          <RouterLink v-else to="/messages" class="btn dd-btn-primary">
            <i class="bi bi-chat-heart-fill me-2"></i>Chat
          </RouterLink>
          <button v-if="!isOwnProfile" class="btn dd-btn-outline" @click="toggleLike">
            <i :class="liked ? 'bi bi-heart-fill' : 'bi bi-heart'" class="me-2"></i>
            {{ liked ? 'Liked' : 'Like' }}
          </button>
        </div>
      </div>
    </section>

    <!-- BODY: Bootstrap row so it plays nice with the existing grid -->
    <div class="row g-4 mt-2">

      <!-- LEFT: About + Hobbies -->
      <div class="col-12 col-lg-8">
        <div class="dd-body-col">

          <div class="dd-profile-card">
            <h5 class="dd-card-title">
              <i class="bi bi-person-lines-fill dd-title-icon"></i> About
            </h5>
            <p class="dd-card-text">{{ profile.about }}</p>
          </div>

          <div class="dd-profile-card">
            <h5 class="dd-card-title">
              <i class="bi bi-lightning-charge-fill dd-title-icon"></i> Hobbies
            </h5>
            <div class="dd-interest-wrap">
              <span
                class="dd-interest-tag"
                v-for="interest in profile.interests"
                :key="interest"
              >{{ interest }}</span>
              <span v-if="!profile.interests?.length" class="dd-empty-hint">
                No hobbies listed yet.
              </span>
            </div>
          </div>

        </div>
      </div>

      <!-- RIGHT: Details -->
      <div class="col-12 col-lg-4">
        <div class="dd-profile-card">
          <h5 class="dd-card-title">
            <i class="bi bi-card-list dd-title-icon"></i> Details
          </h5>

          <div class="dd-detail-item">
            <span class="dd-detail-label"><i class="bi bi-calendar3"></i> Age</span>
            <span class="dd-detail-value">{{ profile.age }}</span>
          </div>

          <div class="dd-detail-item">
            <span class="dd-detail-label"><i class="bi bi-geo-alt"></i> Location</span>
            <span class="dd-detail-value">{{ profile.location }}</span>
          </div>

          <div class="dd-detail-item">
            <span class="dd-detail-label"><i class="bi bi-search-heart"></i> Looking For</span>
            <span class="dd-detail-value">{{ profile.lookingFor }}</span>
          </div>

          <div class="dd-detail-item" v-if="profile.distance">
            <span class="dd-detail-label"><i class="bi bi-signpost-2"></i> Distance</span>
            <span class="dd-detail-value">{{ profile.distance }} km</span>
          </div>
        </div>
      </div>

    </div>

    <!-- ERROR BANNER -->
    <div v-if="error" class="dd-error-banner mt-3">
      <i class="bi bi-exclamation-circle-fill me-2"></i>{{ error }}
    </div>

  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getToken } from '@/services/auth'

const error = ref('')
const liked = ref(false)
const route = useRoute()
const currentUsername = ref('')

const isOwnProfile = computed(() => (
  currentUsername.value &&
  profile.value.username &&
  currentUsername.value === profile.value.username
))

const profile = ref({
  firstName:        'Sophia',
  lastName:         'Williams',
  age:              24,
  location:         'Kingston',
  lookingFor:       'Long-term connection',
  relationshipGoal: 'Meaningful Relationship',
  bio:              'Coffee lover and beach enthusiast ☕',
  about:            'I enjoy traveling, music, and spontaneous adventures. Looking for someone genuine and fun to connect with.',
  matchScore:       94,
  interests:        ['Travel', 'Music', 'Photography', 'Movies'],
  photoUrl:         '',
  distance:         null
})

async function parseResponse(response) {
  const text = await response.text()
  if (!text) return {}

  try {
    return JSON.parse(text)
  } catch {
    return { message: text }
  }
}

async function getCsrfToken() {
  const response = await fetch('/api/v1/csrf-token')
  const data = await parseResponse(response)
  if (!response.ok) throw new Error(data.message || 'Failed to fetch CSRF token')
  return data.csrf_token
}

function normalizeProfile(data) {
  return {
    username: data.username,
    firstName: data.firstName || data.first_name || '',
    lastName: data.lastName || data.last_name || '',
    age: data.age,
    location: data.location || '',
    lookingFor: data.lookingFor || (Array.isArray(data.looking_for) ? data.looking_for.join(', ') : data.looking_for) || '',
    bio: data.bio || data.description || '',
    about: data.about || data.description || '',
    matchScore: data.matchScore || data.match_score || 0,
    interests: data.interests || data.hobbies || [],
    photoUrl: data.photoUrl || data.photo || '',
    distance: data.distance || null,
    matched: Boolean(data.matched)
  }
}

async function toggleLike() {
  try {
    if (liked.value) return

    const token = getToken()
    const csrfToken = await getCsrfToken()
    const response = await fetch(`/api/v1/likes/${profile.value.username}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ match_score: profile.value.matchScore })
    })
    const data = await parseResponse(response)
    if (!response.ok && response.status !== 409) {
      throw new Error(data.message || 'Failed to like profile')
    }

    liked.value = true
    if (data.matched) profile.value.matched = true
  } catch (err) {
    console.error('Failed to like profile:', err)
    error.value = err.message
  }
}

onMounted(async () => {
  try {
    const token = getToken()
    const userResponse = await fetch('/api/v1/user/', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    const userData = await parseResponse(userResponse)
    if (userResponse.ok) currentUsername.value = userData.user?.username || ''

    const response = await fetch(`/api/v1/profile/${route.params.username}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    const data = await parseResponse(response)
    if (!response.ok) throw new Error(data.message || 'Failed to fetch profile')
    profile.value = normalizeProfile(data.profile)
  } catch (err) {
    console.error('Failed to load profile:', err)
    error.value = err.message || 'Could not load profile.'
  }
})
</script>

<style scoped>
/* ── Page ─────────────────────────────────────────────────── */
.dd-profile-page {
  padding: 1rem 0 3rem;
}

/* ── Hero ─────────────────────────────────────────────────── */
.dd-profile-hero {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  flex-wrap: wrap;
  gap: 2rem;
  background:
    linear-gradient(rgba(255,255,255,0.93), rgba(255,255,255,0.93)),
    radial-gradient(circle at top left, #FDEEF2 0%, transparent 55%),
    radial-gradient(circle at bottom right, #fff0e8 0%, transparent 50%);
  border-radius: 28px;
  border: 1px solid rgba(192, 57, 90, 0.09);
  padding: 2rem 2.5rem;
  box-shadow: 0 6px 32px rgba(192, 57, 90, 0.07);
}

/* ── Avatar ───────────────────────────────────────────────── */
.dd-profile-avatar-wrap {
  position: relative;
  flex-shrink: 0;
}

.dd-profile-avatar {
  width: 148px;
  height: 148px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--dd-rose), var(--dd-coral));
  color: white;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  font-size: 3.2rem;
  font-weight: 700;
  box-shadow: 0 12px 36px rgba(192, 57, 90, 0.22);
  overflow: hidden;
  border: 4px solid white;
  text-decoration: none;
}

.dd-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.dd-avatar-initials {
  line-height: 1;
  display: block;
}

.dd-online-badge {
  position: absolute;
  bottom: 8px;
  right: 4px;
  background: white;
  color: #16a34a;
  border-radius: 100px;
  padding: 0.28rem 0.65rem;
  display: flex !important;
  align-items: center !important;
  gap: 0.38rem;
  font-size: 0.72rem;
  font-weight: 700;
  box-shadow: 0 2px 10px rgba(0,0,0,0.10);
  border: 1.5px solid rgba(22, 163, 74, 0.15);
  white-space: nowrap;
}

.dd-online-badge i {
  font-size: 0.52rem;
}

/* ── Hero Content ─────────────────────────────────────────── */
.dd-profile-hero-content {
  flex: 1;
  min-width: 260px;
  display: block !important;
}

.dd-hero-top {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
}

.dd-profile-name {
  color: var(--dd-dark);
  font-weight: 800;
  font-size: 1.75rem;
  margin: 0;
  letter-spacing: -0.4px;
  display: inline;
}

.dd-age {
  font-weight: 500;
  color: var(--dd-muted);
}

.dd-match-score {
  display: inline-flex !important;
  align-items: center;
  background: var(--dd-rose-pale);
  color: var(--dd-rose);
  border-radius: 100px;
  padding: 0.28rem 0.8rem;
  font-size: 0.78rem;
  font-weight: 700;
  white-space: nowrap;
  border: 1px solid rgba(192, 57, 90, 0.12);
}

.dd-profile-meta {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: wrap;
  gap: 1rem;
  color: var(--dd-muted);
  font-size: 0.875rem;
  align-items: center !important;
  margin-bottom: 0.75rem;
}

.dd-profile-meta span {
  display: inline-flex !important;
  align-items: center;
  gap: 0.35rem;
}

.dd-profile-meta i {
  color: var(--dd-rose);
  font-size: 0.8rem;
}

.dd-profile-bio {
  display: block;
  color: var(--dd-mid);
  line-height: 1.75;
  margin-bottom: 0.75rem;
  max-width: 680px;
}

.dd-profile-actions {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: wrap;
  gap: 0.85rem;
  align-items: center;
  margin-top: 0.5rem;
}

/* ── Body column stack ────────────────────────────────────── */
.dd-body-col {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* ── Cards ────────────────────────────────────────────────── */
.dd-profile-card {
  display: block !important;      /* defeat any Bootstrap flex bleed */
  width: 100%;
  background: white;
  border-radius: 22px;
  border: 1px solid rgba(192, 57, 90, 0.08);
  padding: 1.6rem;
  box-shadow: 0 4px 20px rgba(192, 57, 90, 0.05);
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}

.dd-profile-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(192, 57, 90, 0.10);
}

.dd-card-title {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  gap: 0.5rem;
  color: var(--dd-dark);
  font-weight: 700;
  font-size: 1rem;
  margin-bottom: 1.1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(192, 57, 90, 0.07);
}

.dd-title-icon {
  color: var(--dd-rose);
  font-size: 0.9rem;
}

.dd-card-text {
  display: block;
  color: var(--dd-mid);
  line-height: 1.85;
  margin: 0;
}

/* ── Hobbies ────────────────────────────────────────────── */
.dd-interest-wrap {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.dd-interest-tag {
  display: inline-block;
  background: var(--dd-rose-pale);
  color: var(--dd-rose);
  padding: 0.45rem 1rem;
  border-radius: 100px;
  font-size: 0.82rem;
  font-weight: 600;
  border: 1px solid rgba(192, 57, 90, 0.10);
  transition: background 0.2s, transform 0.2s;
  cursor: default;
}

.dd-interest-tag:hover {
  background: rgba(192, 57, 90, 0.13);
  transform: translateY(-1px);
}

.dd-empty-hint {
  color: var(--dd-muted);
  font-size: 0.85rem;
  font-style: italic;
}

/* ── Details ──────────────────────────────────────────────── */
.dd-detail-item {
  display: flex !important;
  flex-direction: row !important;
  justify-content: space-between !important;
  align-items: center !important;
  gap: 0.75rem;
  padding: 0.85rem 0;
  border-bottom: 1px solid rgba(192, 57, 90, 0.07);
  font-size: 0.9rem;
}

.dd-detail-item:first-of-type {
  padding-top: 0;
}

.dd-detail-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.dd-detail-label {
  display: inline-flex !important;
  align-items: center;
  gap: 0.45rem;
  color: var(--dd-muted);
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

.dd-detail-label i {
  color: var(--dd-rose);
  font-size: 0.85rem;
}

.dd-detail-value {
  color: var(--dd-dark);
  font-weight: 500;
  text-align: right;
}

/* ── Buttons ──────────────────────────────────────────────── */
.dd-btn-outline {
  background: white;
  border: 1.5px solid rgba(192, 57, 90, 0.18);
  color: var(--dd-rose);
  border-radius: 100px;
  font-weight: 600;
  padding: 0.6rem 1.5rem;
  transition: all 0.2s ease;
}

.dd-btn-outline:hover {
  background: var(--dd-rose-pale);
  color: var(--dd-rose);
  border-color: rgba(192, 57, 90, 0.3);
  transform: translateY(-2px);
}

/* ── Error Banner ─────────────────────────────────────────── */
.dd-error-banner {
  padding: 0.85rem 1.25rem;
  background: #fef2f2;
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 14px;
  color: #dc2626;
  font-size: 0.88rem;
  font-weight: 500;
  display: flex !important;
  align-items: center;
}

/* ── Responsive ───────────────────────────────────────────── */
@media (max-width: 768px) {
  .dd-profile-hero {
    flex-direction: column !important;
    text-align: center;
    align-items: center !important;
    padding: 1.5rem;
  }

  .dd-hero-top {
    justify-content: center !important;
  }

  .dd-profile-meta {
    justify-content: center !important;
  }

  .dd-profile-actions {
    justify-content: center !important;
  }

  .dd-profile-avatar {
    width: 116px;
    height: 116px;
    font-size: 2.4rem;
  }

  .dd-profile-name {
    font-size: 1.45rem;
  }
}
</style>
