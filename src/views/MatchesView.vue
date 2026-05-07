<template>
  <div>

    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="dd-section-title mb-1">Your Matches ❤️</h4>
        <p class="dd-matches-sub mb-0">
          People who liked you back.
        </p>
      </div>

      <span class="dd-count-badge">
        {{ matches.length }} matches
      </span>
    </div>

    <!-- Empty State -->
    <div v-if="matches.length === 0" class="dd-empty text-center py-5">
      <div class="dd-empty-emoji">💔</div>
      <h5 class="dd-empty-title mt-3">No matches yet</h5>
      <p class="dd-empty-sub">
        Keep exploring profiles to find connections.
      </p>

      <RouterLink to="/dashboard" class="btn dd-btn-primary mt-2">
        Browse Profiles
      </RouterLink>
    </div>

    <!-- Match Grid -->
    <div v-else class="row g-4">

      <div
        v-for="match in matches"
        :key="match.id"
        class="col-12 col-md-6 col-xl-4"
      >
        <div class="dd-match-card h-100">

          <!-- Avatar -->
          <div
            class="dd-match-avatar"
            :style="{ background: match.avatarBg }"
          >
            {{ match.name.charAt(0) }}
          </div>

          <!-- Info -->
          <div class="dd-match-body">

            <div class="d-flex align-items-center gap-2 mb-2">
              <h5 class="dd-match-name mb-0">
                {{ match.name }}, {{ match.age }}
              </h5>

              <span class="dd-match-score">
                {{ match.matchScore }}%
              </span>
            </div>

            <div class="dd-match-meta mb-2">
              <span>
                <i class="bi bi-geo-alt-fill"></i>
                {{ match.location }}
              </span>

              <span>
                <i class="bi bi-clock"></i>
                {{ match.active }}
              </span>
            </div>

            <p class="dd-match-bio">
              {{ match.bio }}
            </p>

            <!-- Interests -->
            <div class="dd-match-tags">
              <span
                class="dd-tag"
                v-for="interest in match.interests"
                :key="interest"
              >
                {{ interest }}
              </span>
            </div>

          </div>

          <!-- Actions -->
          <div class="dd-match-actions">

            <RouterLink
              to="/messages"
              class="btn dd-btn-primary"
            >
              <i class="bi bi-chat-heart-fill me-1"></i>
              Message
            </RouterLink>

            <button class="btn dd-btn-view">
              <i class="bi bi-person-heart me-1"></i>
              View Profile
            </button>

          </div>

        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'

const matches = ref([])

onMounted(async () => {
  try {

    const response = await fetch('/api/matches')

    if (!response.ok) {
      throw new Error('Failed to fetch matches')
    }

    const data = await response.json()

    matches.value = data

  } catch (err) {
    console.error('Failed to load matches:', err)
  }
})
</script>

<style scoped>
.dd-matches-sub {
  font-size: 0.88rem;
  color: var(--dd-muted);
}

/* CARD */
.dd-match-card {
  background: #fff;
  border-radius: 22px;
  padding: 1.5rem;
  border: 1px solid rgba(192,57,90,0.08);
  box-shadow: 0 4px 20px rgba(192,57,90,0.07);
  transition: transform 0.2s, box-shadow 0.2s;

  display: flex;
  flex-direction: column;
}

.dd-match-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(192,57,90,0.14);
}

/* AVATAR */
.dd-match-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;

  display: flex;
  align-items: center;
  justify-content: center;

  font-size: 1.6rem;
  font-weight: 700;
  color: var(--dd-rose);

  margin-bottom: 1rem;
}

/* BODY */
.dd-match-body {
  flex: 1;
}

.dd-match-name {
  font-size: 1rem;
  font-weight: 700;
  color: var(--dd-dark);
}

.dd-match-score {
  background: var(--dd-rose-pale);
  color: var(--dd-rose);

  font-size: 0.72rem;
  font-weight: 700;

  padding: 0.2rem 0.55rem;
  border-radius: 100px;
}

.dd-match-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;

  font-size: 0.8rem;
  color: var(--dd-muted);
}

.dd-match-bio {
  font-size: 0.88rem;
  color: var(--dd-mid);
  line-height: 1.6;
}

/* TAGS */
.dd-match-tags {
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

/* ACTIONS */
.dd-match-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.4rem;
}

.dd-btn-view {
  background: #fff;
  border: 1.5px solid rgba(192,57,90,0.14);
  color: var(--dd-rose);

  border-radius: 100px;
  font-weight: 600;
  font-size: 0.85rem;
}

.dd-btn-view:hover {
  background: var(--dd-rose-pale);
  color: var(--dd-rose);
}

/* MOBILE */
@media (max-width: 576px) {
  .dd-match-actions {
    flex-direction: column;
  }

  .dd-match-actions .btn {
    width: 100%;
  }
}
</style>
