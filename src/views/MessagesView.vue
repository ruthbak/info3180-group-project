<template>
  <div class="dd-messages-page">

    <!-- Conversations -->
    <aside class="dd-conversations">

      <div class="dd-conv-header">
        <h5 class="mb-0">Chats</h5>
        <span class="dd-count-badge">{{ conversations.length }}</span>
      </div>

      <div
        v-for="chat in conversations"
        :key="chat.id"
        class="dd-conv-item"
        :class="{ active: activeChat.id === chat.id }"
        @click="openChat(chat)"

        function openChat(chat) {
          activeChat.value = chat
          chat.unread = 0
        }
      >
        <div class="dd-conv-avatar">
          {{ chat.name.charAt(0) }}
        </div>

        <div class="flex-grow-1">
        <div class="d-flex justify-content-between align-items-start">

          <div>
            <span
              class="dd-conv-name"
              :class="{ 'dd-unread-name': chat.unread > 0 }"
            >
              {{ chat.name }}
            </span>

            <p class="dd-conv-preview mb-0">
              {{ chat.lastMessage }}
            </p>
          </div>

          <div class="dd-chat-meta">

            <small
              class="dd-conv-time"
              :class="{ 'dd-unread-time': chat.unread > 0 }"
            >
              {{ chat.time }}
            </small>

            <span
              v-if="chat.unread > 0"
              class="dd-unread-badge"
            >
              {{ chat.unread }}
            </span>

            </div>

          </div>

        </div>
      </div>

    </aside>

    <!-- Chat Window -->
    <section
      v-if="activeChat"
      class="dd-chat-window"
    >

      <!-- Header -->
      <div class="dd-chat-header">
        <div class="d-flex align-items-center gap-3">
          <div class="dd-conv-avatar">
            {{ activeChat.name.charAt(0) }}
          </div>

          <div>
            <h6 class="mb-0">{{ activeChat.name }}</h6>
            <small class="text-muted">Online</small>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div class="dd-chat-body">

        <div
          v-for="message in activeChat.messages"
          :key="message.id"
          class="dd-message-row"
          :class="{ mine: message.mine }"
        >
          <div class="dd-message-bubble">
            {{ message.text }}
          </div>
        </div>

      </div>

      <!-- Input -->
      <div class="dd-chat-input-wrap">

        <input
          v-model="newMessage"
          type="text"
          class="form-control dd-chat-input"
          placeholder="Type a message..."
          @keyup.enter="sendMessage"
        />

        <button
          class="btn dd-btn-primary"
          @click="sendMessage"
        >
          <i class="bi bi-send-fill"></i>
        </button>

      </div>

    </section>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const conversations = ref([])

const activeChat = ref(null)
onMounted(async () => {
  try {

    const response = await fetch('/api/chats')

    if (!response.ok) {
      throw new Error('Failed to fetch chats')
    }

    const data = await response.json()

    conversations.value = data

    if (data.length > 0) {
      activeChat.value = data[0]
    }

  } catch (err) {
    console.error('Failed to load chats:', err)
  }
})

function sendMessage() {
  if (!newMessage.value.trim()) return

  activeChat.value.messages.push({
    id: Date.now(),
    text: newMessage.value,
    mine: true
  })

  activeChat.value.lastMessage = newMessage.value
  newMessage.value = ''
}
</script>

<style scoped>
.dd-messages-page {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 1.5rem;
  min-height: calc(100vh - 140px);
}

/* LEFT PANEL */
.dd-conversations {
  background: #fff;
  border-radius: 18px;
  border: 1px solid rgba(192,57,90,0.08);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dd-conv-header {
  padding: 1.2rem;
  border-bottom: 1px solid rgba(192,57,90,0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dd-conv-item {
  display: flex;
  gap: 0.9rem;
  padding: 1rem 1.2rem;
  cursor: pointer;
  transition: background 0.18s;
  border-bottom: 1px solid rgba(192,57,90,0.05);
}

.dd-conv-item:hover {
  background: #FFF6EE;
}

.dd-conv-item.active {
  background: #FDEEF2;
}


.dd-conv-name {
  font-weight: 600;
  color: #2A1018;
}

.dd-conv-preview {
  font-size: 0.82rem;
  color: #9E6373;
}

.dd-conv-time {
  color: #9E6373;
}

/* CHAT WINDOW */
.dd-chat-window {
  background: #fff;
  border-radius: 18px;
  border: 1px solid rgba(192,57,90,0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dd-chat-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(192,57,90,0.08);
}

.dd-chat-body {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  background:
    linear-gradient(rgba(255,255,255,0.92), rgba(255,255,255,0.92)),
    radial-gradient(circle at top left, #FDEEF2, transparent 40%);
}

.dd-message-row {
  display: flex;
  margin-bottom: 1rem;
}

.dd-message-row.mine {
  justify-content: flex-end;
}

.dd-message-bubble {
  max-width: 70%;
  padding: 0.75rem 1rem;
  border-radius: 18px;
  background: #F4ECE8;
  color: #2A1018;
  font-size: 0.9rem;
}

.dd-message-row.mine .dd-message-bubble {
  background: linear-gradient(135deg, #C0395A, #E8563A);
  color: white;
}

.dd-chat-input-wrap {
  display: flex;
  gap: 0.8rem;
  padding: 1rem 1.2rem;
  border-top: 1px solid rgba(192,57,90,0.08);
}

.dd-chat-input {
  border-radius: 100px;
  border: 1.5px solid rgba(192,57,90,0.15);
  padding: 0.7rem 1rem;
}

.dd-chat-input:focus {
  border-color: #C0395A;
  box-shadow: 0 0 0 3px rgba(192,57,90,0.08);
}

/* MOBILE */
@media (max-width: 992px) {
  .dd-messages-page {
    grid-template-columns: 1fr;
  }

  .dd-conversations {
    max-height: 280px;
  }
}

.dd-chat-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.45rem;
}


.dd-unread-name {
  color: var(--dd-dark);
  font-weight: 700;
}

.dd-unread-time {
  color: var(--dd-rose);
  font-weight: 700;
}
</style>