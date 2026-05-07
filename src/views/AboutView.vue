<template>
  <div class="about-page">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">About Us</h1>
        <h2 class="hero-subtitle">
          <i>DriftDater — Drift into real relationships.</i>
        </h2>
      </div>
    </section>

    <!-- Mission Section -->
    <section class="mission">
      <div class="container">
        <div class="mission-grid">
          <div class="mission-text">
            <span class="tag">Who We Are</span>
            <h2>Working as matchmaker, no matter what you're looking for.</h2>
            <p>
              We believe that everyone deserves to find love, friendship, and genuine connections in an easy, respectful environment. 
              That's why we built a platform focused on authentic conversations, shared values, 
              and meaningful compatibility, not just looks or bios.
            </p>
          </div>
          <div class="mission-icon">
            <span class="icon-heart">❤️</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Values Section -->
    <section class="values">
      <div class="container">
        <div class="section-header">
          <span class="tag">Why Choose Us</span>
          <h2>Our Core Values</h2>
        </div>
        <div class="values-grid">
          <div 
            v-for="value in coreValues" 
            :key="value.title" 
            class="value-card"
          >
            <div class="value-icon">{{ value.icon }}</div>
            <h3>{{ value.title }}</h3>
            <p>{{ value.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats">
      <div class="container">
        <div class="stats-grid">
          <div 
            v-for="stat in statistics" 
            :key="stat.label" 
            class="stat-item"
          >
            <div class="stat-number">{{ stat.number }}+</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Team Section (Optional) -->
    <section class="team">
      <div class="container">
        <div class="section-header">
          <span class="tag">Behind the Scenes</span>
          <h2>Meet the Team</h2>
        </div>
        <div class="team-grid">
          <div 
            v-for="member in teamMembers" 
            :key="member.name" 
            class="team-card"
          >
            <div class="team-avatar">{{ member.avatar }}</div>
            <h3>{{ member.name }}</h3>
            <p>{{ member.role }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <div class="container">
        <h2>Ready to write your love story?</h2>
        <p>Join thousands of singles who found their match with us.</p>
        <button class="btn-primary" @click="openRegisterView">Start Your Journey →</button>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'AboutPage',
  data() {
    return {
      coreValues: [
        {
          icon: '🔒',
          title: 'Find People Looking for the Same Thing',
          description: 'Verified profiles and a messaging system related to what each person is looking for.'
        },
        {
          icon: '🎯',
          title: 'Create Meaningful Connections',
          description: 'Smart algorithms that focus on compatibility, goals and proximity.'
        },
        {
          icon: '😊',
          title: 'Inclusive and Welcoming Community',
          description: 'A welcoming space for all people island-wide.'
        },
        {
          icon: '💬',
          title: 'Authentic Conversations',
          description: 'Features that encourage real talk, not small talk or fake accounts.'
        }
      ],
      statistics: [
        { number: '50K', label: 'Happy Matches' },
        { number: '1.2M', label: ' Real Users' },
        { number: '30K', label: 'Success Stories' },
        { number: '95%', label: 'Satisfaction Rate' }
      ],
      teamMembers: [
        { name: 'Daniel Bingham', role: 'CEO & Founder', avatar: '👨‍💻' },
        { name: 'Rashene Dillon', role: 'Major Programmer', avatar: '🛡️' },
        { name: 'Ruth-Ann Allen', role: 'Co-Founder', avatar: '👩‍💻' },
        { name: 'Sukanayna Hoo', role: 'Community Lead', avatar: '💬' },
        { name: 'Darrin Bellamy', role: 'Assistant Programmer', avatar: '🌟' },
        { name: 'And More...', role: ' ', avatar: ' ' }
      ]
    };
  },
  methods: {
    openRegisterView() {
      import('./RegisterView.vue');
    }
  }
};
</script>

<style scoped>
.about-page {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #2c3e50;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Hero Section */
.hero {
  background: linear-gradient(135deg, #fe019a 0%, #764ba2 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
}

.hero-title {
  font-size: 3rem;
  margin-bottom: 1rem;
  font-weight: 700;
}

.hero-subtitle {
  font-size: 3rem;
  opacity: 0.95;
  max-width: 600px;
  margin: 0 auto;
  -webkit-text-stroke-width: 0.2px;
  -webkit-text-stroke-color: white;
}

/* Common Section Styles */
section {
  padding: 60px 20px;
}

.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.tag {
  display: inline-block;
  background: #f0f0f0;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #667eea;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 1rem;
}

h2 {
  font-size: 2.2rem;
  margin-bottom: 1rem;
  color: #2c3e50;
}

/* Mission Section */
.mission {
  background: #faf9ff;
}

.mission-grid {
  display: flex;
  align-items: center;
  gap: 48px;
}

.mission-text {
  flex: 2;
}

.mission-icon {
  flex: 1;
  text-align: center;
  font-size: 5rem;
}

/* Values Grid */
.values-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.value-card {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
  text-align: center;
}

.value-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.value-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.value-card h3 {
  margin-bottom: 0.75rem;
  color: #2c3e50;
}

.value-card p {
  color: #7f8c8d;
  line-height: 1.5;
}

/* Stats Section */
.stats {
  background: linear-gradient(120deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stats-grid {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 30px;
  text-align: center;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 1rem;
  opacity: 0.9;
}

/* Team Grid */
.team-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
}

.team-card {
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.team-avatar {
  font-size: 3.5rem;
  margin-bottom: 1rem;
}

.team-card h3 {
  margin-bottom: 0.25rem;
  color: #2c3e50;
}

.team-card p {
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* CTA Section */
.cta {
  background: #2c3e50;
  color: white;
  text-align: center;
}

.cta h2 {
  color: white;
  margin-bottom: 1rem;
}

.cta p {
  margin-bottom: 2rem;
  opacity: 0.9;
}

.btn-primary {
  background: #667eea;
  color: white;
  border: none;
  padding: 14px 32px;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 50px;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}

.btn-primary:hover {
  background: #5a67d8;
}

.btn-primary:active {
  transform: scale(0.98);
}

/* Responsive */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .mission-grid {
    flex-direction: column;
    text-align: center;
  }
  
  h2 {
    font-size: 1.6rem;
  }
  
  section {
    padding: 40px 20px;
  }
}
</style>
