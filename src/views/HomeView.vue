<script setup>
import { ref } from "vue";
import { RouterLink } from "vue-router";

const features = ref([
  { icon: '🎯', title: 'Smart Matching', desc: 'Our algorithm matches you by location, age, and shared interests to find your most compatible connections.' },
  { icon: '💬', title: 'Real-Time Messaging', desc: 'Once matched, start chatting instantly. Your conversation history is always saved and accessible.' },
  { icon: '🔍', title: 'Advanced Search', desc: 'Filter profiles by location, age range, and interests. Save favourites to revisit anytime.' },
  { icon: '🔒', title: 'Safe & Private', desc: 'Encrypted passwords, profile visibility controls, and secure sessions keep your data protected.' }
])

const steps = ref([
  { num: '1', title: 'Create Your Profile', desc: 'Sign up and build a detailed profile with photos, your bio, interests, and location preferences.' },
  { num: '2', title: 'Discover & Like', desc: 'Browse profiles matched to your preferences. Like profiles you are interested in and pass on others.' },
  { num: '3', title: 'Connect & Chat', desc: 'When both of you like each other it is a match! Start messaging and let the sparks begin.' }
])
</script>

<template>
  <div>
 
    <!-- ── HERO ── -->
    <section class="dd-hero">
      <div class="container">
        <div class="row align-items-center min-vh-100 py-5">
          <div class="col-lg-7">
            <span class="dd-badge mb-3 d-inline-block">♥ New connections every day</span>
            <h1 class="dd-hero-title">Find Your <em>Perfect</em> Flame</h1>
            <p class="dd-hero-sub">
              DriftDater brings hearts together through meaningful connections.
              Discover compatible matches, spark conversations, and let love drift your way.
            </p>
            <div class="d-flex flex-wrap gap-3 mt-4">
              <RouterLink to="/register" class="btn dd-btn-primary px-4 py-2">♥ Start Matching</RouterLink>
            </div>
 
            <!-- Stats -->
            <div class="dd-stats mt-5 pt-4">
              <div class="dd-stat">
                <span class="dd-stat-num">10k+</span>
                <span class="dd-stat-label">Active Profiles</span>
              </div>
              <div class="dd-stat">
                <span class="dd-stat-num">94%</span>
                <span class="dd-stat-label">Match Rate</span>
              </div>
              <div class="dd-stat">
                <span class="dd-stat-num">3.2k</span>
                <span class="dd-stat-label">Connections Made</span>
              </div>
            </div>
          </div>
 
          <!-- Floating profile cards -->
          <div class="col-lg-5 d-none d-lg-flex flex-column gap-3 align-items-center">
            <div class="dd-profile-card">
              <div class="dd-avatar av1">🌸</div>
              <div class="dd-card-info">
                <div class="dd-card-name">Sofia, 24</div>
                <div class="dd-card-detail">Kingston · Hiking & art</div>
              </div>
              <span class="dd-match-pct">92%</span>
            </div>
            <div class="dd-profile-card ms-5">
              <div class="dd-avatar av2">🌻</div>
              <div class="dd-card-info">
                <div class="dd-card-name">Marcus, 27</div>
                <div class="dd-card-detail">Montego Bay · Music & travel</div>
              </div>
              <span class="dd-match-pct">88%</span>
            </div>
            <div class="dd-profile-card">
              <div class="dd-avatar av3">🦋</div>
              <div class="dd-card-info">
                <div class="dd-card-name">Isla, 23</div>
                <div class="dd-card-detail">Portmore · Coffee & books</div>
              </div>
              <span class="dd-match-pct">85%</span>
            </div>
          </div>
        </div>
      </div>
    </section>
 
    <!-- ── FEATURES ── -->
    <section class="dd-features py-5" id="features">
      <div class="container py-4">
        <div class="text-center mb-5">
          <span class="dd-section-label">Why DriftDater</span>
          <h2 class="dd-section-title">Everything You Need to Find <em>the One</em></h2>
          <p class="dd-section-sub mx-auto">
            From intelligent matching to real-time messaging, every feature is built with your love story in mind.
          </p>
        </div>
        <div class="row g-4">
          <div class="col-sm-6 col-lg-3" v-for="feature in features" :key="feature.title">
            <div class="dd-feature-card h-100">
              <div class="dd-feature-icon mb-3">{{ feature.icon }}</div>
              <h5 class="dd-feature-title">{{ feature.title }}</h5>
              <p class="dd-feature-desc">{{ feature.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
 
    <!-- ── HOW IT WORKS ── -->
    <section class="dd-how py-5" id="how-it-works">
      <div class="container py-4">
        <div class="row align-items-center g-5">
          <div class="col-lg-5">
            <span class="dd-section-label">How It Works</span>
            <h2 class="dd-section-title">Love in <em>Three Steps</em></h2>
            <p class="dd-section-sub">
              Getting started is simple. You are just minutes away from finding your match.
            </p>
            <div class="dd-steps mt-4">
              <div class="dd-step" v-for="step in steps" :key="step.num">
                <div class="dd-step-num">{{ step.num }}</div>
                <div>
                  <h6 class="dd-step-title">{{ step.title }}</h6>
                  <p class="dd-step-desc">{{ step.desc }}</p>
                </div>
              </div>
            </div>
          </div>
 
          <!-- Match preview mockup -->
          <div class="col-lg-7">
            <div class="dd-match-preview">
              <p class="dd-preview-label">Browse Potential Matches</p>
              <div class="dd-match-row">
                <div class="dd-avatar av1">🌸</div>
                <div class="flex-grow-1">
                  <div class="dd-card-name">Alice Wonder, 25</div>
                  <div class="dd-card-detail">Loves hiking and adventure · Kingston</div>
                </div>
                <div class="d-flex gap-2">
                  <button class="btn dd-btn-like btn-sm">♥ Like</button>
                  <button class="btn dd-btn-pass btn-sm">Pass</button>
                </div>
              </div>
              <div class="dd-match-row">
                <div class="dd-avatar av2">🌻</div>
                <div class="flex-grow-1">
                  <div class="dd-card-name">Grace Gamer, 22</div>
                  <div class="dd-card-detail">Gamer & coffee enthusiast · MoBay</div>
                </div>
                <div class="d-flex gap-2">
                  <button class="btn dd-btn-like btn-sm">♥ Like</button>
                  <button class="btn dd-btn-pass btn-sm">Pass</button>
                </div>
              </div>
              <div class="dd-match-row">
                <div class="dd-avatar av3">🦋</div>
                <div class="flex-grow-1">
                  <div class="dd-card-name">Carol Cook, 24</div>
                  <div class="dd-card-detail">Chef and food lover · Spanish Town</div>
                </div>
                <div class="d-flex gap-2">
                  <button class="btn dd-btn-like btn-sm">♥ Like</button>
                  <button class="btn dd-btn-pass btn-sm">Pass</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
 
    <!-- ── CTA BANNER ── -->
    <section class="dd-cta mx-3 mx-md-5 my-5 rounded-4 text-center py-5 px-3">
      <h2 class="dd-cta-title">Ready to Find Your Flame?</h2>
      <p class="dd-cta-sub mb-4">
        Join thousands of singles already making meaningful connections on DriftDater.
      </p>
      <RouterLink to="/register" class="btn dd-btn-white px-4 py-2">♥ Create Free Account</RouterLink>
    </section>
 
  </div>
</template>

<style>
/* ── Hero ── */
.dd-hero {
  background: linear-gradient(135deg, #fff6ee 0%, #fdeef2 50%, #fff0e8 100%);
  position: relative;
  overflow: hidden;
}
.dd-hero::before {
  content: '';
  position: absolute;
  width: 600px; height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(192,57,90,0.10) 0%, transparent 70%);
  top: -150px; right: -100px;
  pointer-events: none;
}
.dd-badge {
  font-size: 0.78rem; font-weight: 600;
  letter-spacing: 0.08em; text-transform: uppercase;
  color: #C0395A;
  background: #FDEEF2;
  border: 1px solid rgba(192,57,90,0.25);
  padding: 0.35rem 0.9rem;
  border-radius: 100px;
}
.dd-hero-title {
  font-family: 'Georgia', serif;
  font-size: clamp(2.4rem, 5vw, 4rem);
  font-weight: 700; line-height: 1.1;
  color: #2A1018; letter-spacing: -0.02em;
}
.dd-hero-title em { font-style: italic; color: #C0395A; }
.dd-hero-sub {
  font-size: 1.05rem; line-height: 1.75;
  color: #9E6373; max-width: 480px;
}
 
/* Stats */
.dd-stats {
  display: flex; gap: 2.5rem; flex-wrap: wrap;
  border-top: 1px solid rgba(192,57,90,0.15);
}
.dd-stat { display: flex; flex-direction: column; gap: 0.15rem; }
.dd-stat-num {
  font-family: 'Georgia', serif;
  font-size: 2rem; font-weight: 700;
  color: #C0395A; line-height: 1;
}
.dd-stat-label { font-size: 0.78rem; color: #9E6373; }
 
/* Profile cards */
.dd-profile-card {
  background: #fff; border-radius: 20px;
  padding: 1rem 1.2rem;
  box-shadow: 0 12px 40px rgba(192,57,90,0.12);
  border: 1px solid rgba(192,57,90,0.08);
  display: flex; align-items: center; gap: 0.9rem;
  width: 260px;
  transition: transform 0.3s;
}
.dd-profile-card:hover { transform: translateY(-4px); }
.dd-avatar {
  width: 48px; height: 48px; border-radius: 50%;
  display: flex; align-items: center;
  justify-content: center; font-size: 1.3rem; flex-shrink: 0;
}
.av1 { background: #FDEEF2; }
.av2 { background: #FFF0E8; }
.av3 { background: #FFF8E1; }
.dd-card-info { flex: 1; }
.dd-card-name { font-weight: 600; font-size: 0.9rem; color: #2A1018; }
.dd-card-detail { font-size: 0.76rem; color: #9E6373; margin-top: 0.1rem; }
.dd-match-pct {
  font-size: 0.72rem; font-weight: 600;
  background: #FDEEF2; color: #C0395A;
  padding: 0.25rem 0.55rem; border-radius: 100px;
  white-space: nowrap;
}
 
/* Buttons */
.dd-btn-primary {
  background: linear-gradient(135deg, #C0395A 0%, #E8563A 100%);
  color: #fff !important; border: none; border-radius: 100px;
  font-weight: 600; font-size: 0.95rem;
  box-shadow: 0 6px 20px rgba(192,57,90,0.28);
  transition: opacity 0.2s, transform 0.15s;
}
.dd-btn-primary:hover { opacity: 0.9; transform: translateY(-2px); }
.dd-btn-outline {
  background: transparent; color: #C0395A;
  border: 1.5px solid rgba(192,57,90,0.4);
  border-radius: 100px; font-weight: 600;
  transition: background 0.2s;
}
.dd-btn-outline:hover { background: #FDEEF2; }
 
/* Sections */
.dd-section-label {
  display: block; font-size: 0.78rem; font-weight: 600;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: #C0395A; margin-bottom: 0.5rem;
}
.dd-section-title {
  font-family: 'Georgia', serif;
  font-size: clamp(1.8rem, 3.5vw, 2.5rem);
  font-weight: 700; color: #2A1018;
  letter-spacing: -0.02em; margin-bottom: 0.8rem;
}
.dd-section-title em { font-style: italic; color: #C0395A; }
.dd-section-sub { font-size: 1rem; color: #9E6373; line-height: 1.7; max-width: 500px; }
 
/* Features */
.dd-features { background: #fff; }
.dd-feature-card {
  background: #fff; border-radius: 18px;
  padding: 1.8rem 1.5rem;
  border: 1px solid rgba(192,57,90,0.12);
  transition: transform 0.25s, box-shadow 0.25s;
}
.dd-feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 16px 40px rgba(192,57,90,0.10);
}
.dd-feature-icon { font-size: 2rem; }
.dd-feature-title { font-weight: 600; color: #2A1018; margin-bottom: 0.5rem; }
.dd-feature-desc { font-size: 0.88rem; color: #9E6373; line-height: 1.7; margin: 0; }
 
/* How it works */
.dd-how { background: linear-gradient(135deg, #FDEEF2 0%, #FFF0E8 100%); }
.dd-steps { display: flex; flex-direction: column; gap: 0; }
.dd-step {
  display: flex; gap: 1.2rem; align-items: flex-start;
  padding: 1.2rem 0; position: relative;
}
.dd-step:not(:last-child)::after {
  content: ''; position: absolute;
  left: 22px; top: 60px;
  width: 2px; height: calc(100% - 30px);
  background: linear-gradient(180deg, rgba(192,57,90,0.3) 0%, transparent 100%);
}
.dd-step-num {
  width: 46px; height: 46px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, #C0395A 0%, #E8563A 100%);
  color: #fff; font-weight: 700; font-size: 1.1rem;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Georgia', serif;
  box-shadow: 0 4px 14px rgba(192,57,90,0.28);
}
.dd-step-title { font-weight: 600; color: #2A1018; margin-bottom: 0.25rem; }
.dd-step-desc { font-size: 0.87rem; color: #9E6373; margin: 0; line-height: 1.65; }
 
/* Match preview */
.dd-match-preview {
  background: #fff; border-radius: 20px;
  padding: 1.8rem;
  box-shadow: 0 16px 50px rgba(192,57,90,0.10);
  border: 1px solid rgba(192,57,90,0.08);
}
.dd-preview-label {
  font-size: 0.78rem; font-weight: 600;
  letter-spacing: 0.06em; text-transform: uppercase;
  color: #9E6373; margin-bottom: 1rem;
}
.dd-match-row {
  display: flex; align-items: center; gap: 0.9rem;
  padding: 0.85rem; border-radius: 12px;
  border: 1px solid rgba(192,57,90,0.08);
  margin-bottom: 0.7rem; transition: background 0.2s;
}
.dd-match-row:hover { background: #FDEEF2; }
.dd-match-row:last-child { margin-bottom: 0; }
.dd-btn-like {
  background: #C0395A; color: #fff;
  border: none; border-radius: 100px;
  font-size: 0.78rem; font-weight: 600;
}
.dd-btn-like:hover { background: #E8617F; color: #fff; }
.dd-btn-pass {
  background: #f1f1f1; color: #888;
  border: none; border-radius: 100px;
  font-size: 0.78rem; font-weight: 600;
}
.dd-btn-pass:hover { background: #e0e0e0; }
 
/* CTA Banner */
.dd-cta {
  background: linear-gradient(135deg, #C0395A 0%, #E8563A 100%);
  position: relative; overflow: hidden;
}
.dd-cta::before {
  content: '♥'; position: absolute;
  font-size: 12rem; opacity: 0.06;
  color: #fff; top: -1.5rem; right: 1rem;
  pointer-events: none;
}
.dd-cta-title {
  font-family: 'Georgia', serif;
  font-size: clamp(1.8rem, 3.5vw, 2.5rem);
  font-weight: 700; color: #fff;
  letter-spacing: -0.02em;
}
.dd-cta-sub { color: rgba(255,255,255,0.82); font-size: 1rem; }
.dd-btn-white {
  background: #fff; color: #C0395A;
  border: none; border-radius: 100px;
  font-weight: 700; font-size: 0.95rem;
  box-shadow: 0 6px 20px rgba(0,0,0,0.15);
  transition: transform 0.2s, box-shadow 0.2s;
}
.dd-btn-white:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(0,0,0,0.2);
  color: #C0395A;
}
</style>