<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import MainLayout from './layouts/MainLayout.vue';

const route = useRoute();
const noLayoutRoutes = ['/login'];
const isNoLayout = computed(() => noLayoutRoutes.includes(route.path));
</script>

<template>
  <router-view v-if="isNoLayout" />
  <MainLayout v-else />
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;600;700&family=Source+Sans+3:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&family=Noto+Serif+SC:wght@400;600;700&display=swap');

/* Global Variables & Reset defined here as requested */
:root {
  /* Colors */
  --color-bg-primary: #0f172a;
  --color-bg-secondary: #1b263b;
  --color-bg-card: #1e293b;

  --color-text-primary: #f8fafc;
  --color-text-secondary: #94a3b8;

  --color-accent: #8b5cf6;
  --color-accent-hover: #7c3aed;
  --color-accent-glow: rgba(139, 92, 246, 0.38);

  --color-success: #10b981;
  --color-danger: #ef4444;
  --color-warning: #f59e0b;

  /* Surfaces */
  --color-ink: #f8fafc;
  --color-paper: #0f172a;
  --color-muted: rgba(148, 163, 184, 0.12);

  /* Borders */
  --border-color: #334155;
  --radius-md: 10px;
  --radius-lg: 18px;

  /* Typography */
  --font-body: 'Source Sans 3', 'Noto Sans SC', sans-serif;
  --font-display: 'Crimson Pro', 'Noto Serif SC', serif;
}

*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: var(--font-body);
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
  line-height: 1.6;
  background-image:
    radial-gradient(circle at 15% 10%, rgba(139, 92, 246, 0.24), transparent 38%),
    radial-gradient(circle at 85% 0%, rgba(59, 130, 246, 0.2), transparent 36%);
  background-attachment: fixed;
}

a {
  color: inherit;
  text-decoration: none;
}

button {
  cursor: pointer;
  border: none;
  font-family: inherit;
}

/* Utilities */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-md);
  font-weight: 600;
  transition: all 0.3s ease;
  letter-spacing: 0.02em;
}

.btn-primary {
  background-color: var(--color-accent);
  color: white;
  box-shadow: 0 10px 22px var(--color-accent-glow);
}

.btn-primary:hover {
  background-color: var(--color-accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 14px 28px var(--color-accent-glow);
}
</style>
