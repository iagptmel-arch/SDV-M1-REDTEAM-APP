<template>
  <div class="min-h-screen bg-slate-100 flex">
    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-40 w-64 bg-slate-900 text-white flex flex-col transition-transform duration-200 lg:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Logo -->
      <div class="flex items-center gap-3 px-6 h-16 border-b border-slate-700">
        <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-sm font-bold">S</div>
        <span class="text-lg font-bold tracking-tight">RedTeam</span>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors"
          :class="isActive(item.path) ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800 hover:text-white'"
          @click="sidebarOpen = false"
        >
          <span class="w-5 h-5 flex items-center justify-center" v-html="item.icon" />
          {{ item.label }}
        </router-link>
      </nav>

      <!-- Footer sidebar -->
      <div class="px-4 py-3 border-t border-slate-700">
        <button
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-slate-400 hover:text-white hover:bg-slate-800 w-full transition-colors"
          @click="logout"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          Déconnexion
        </button>
      </div>
    </aside>

    <!-- Overlay mobile -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/50 z-30 lg:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Contenu principal -->
    <div class="flex-1 flex flex-col lg:ml-64">
      <!-- TopBar -->
      <header class="sticky top-0 z-20 bg-white border-b border-gray-200 shadow-sm">
        <div class="flex items-center justify-between h-16 px-4 lg:px-6">
          <!-- Hamburger (mobile) -->
          <button class="lg:hidden p-2 rounded-lg hover:bg-gray-100" @click="sidebarOpen = !sidebarOpen">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!sidebarOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <!-- Search -->
          <div class="hidden sm:flex relative flex-1 max-w-md mx-4">
            <svg class="absolute left-3 top-2.5 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Rechercher..."
              class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>

          <!-- Right actions -->
          <div class="flex items-center gap-3">
            <!-- Notifications -->
            <button class="relative p-2 rounded-lg hover:bg-gray-100">
              <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
            </button>

            <!-- Avatar -->
            <div class="relative" @click="showUserMenu = !showUserMenu">
              <div class="flex items-center gap-2 cursor-pointer p-1.5 rounded-lg hover:bg-gray-100">
                <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-bold">
                  {{ userInitials }}
                </div>
                <span class="hidden md:block text-sm font-medium text-gray-700">{{ userName }}</span>
              </div>

              <!-- Dropdown -->
              <div
                v-if="showUserMenu"
                class="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 py-1 z-50"
                @click.stop
              >
                <div class="px-4 py-2 border-b border-gray-100">
                  <p class="text-sm font-medium text-gray-700">{{ userName }}</p>
                  <p class="text-xs text-gray-400">{{ userEmail }}</p>
                </div>
                <router-link to="/profile" class="block px-4 py-2 text-sm text-gray-600 hover:bg-gray-50">Profil</router-link>
                <button class="w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-gray-50" @click="logout">Déconnexion</button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-4 lg:p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const sidebarOpen = ref(false)
const showUserMenu = ref(false)

const userName = ref('Admin')
const userEmail = ref('admin@redteam.local')
const userInitials = computed(() =>
  userName.value.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
)

const navItems = [
  { path: '/', label: 'Dashboard', icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>' },
  { path: '/hosts', label: 'Hôtes', icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" /></svg>' },
  { path: '/services', label: 'Services', icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>' },
  { path: '/vulnerabilities', label: 'Vulnérabilités', icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" /></svg>' },
  { path: '/campaigns', label: 'Campagnes', icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>' },
  { path: '/reports', label: 'Rapports', icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>' },
]

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function logout() {
  localStorage.removeItem('access_token')
  router.push('/login')
}

// Close user menu on click outside
function handleClickOutside() {
  showUserMenu.value = false
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
