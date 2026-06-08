<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>{{ title }}</h2>
      <form @submit.prevent="$emit('submit')">
        <slot />
        <button type="submit" :disabled="submitting">{{ submitting ? submitLabel : title }}</button>
      </form>
      <p class="auth-link">
        {{ linkText }}<router-link :to="linkTo">{{ linkLabel }}</router-link>
      </p>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  submitting: { type: Boolean, default: false },
  submitLabel: { type: String, default: '' },
  error: { type: String, default: '' },
  linkText: { type: String, default: '' },
  linkLabel: { type: String, default: '' },
  linkTo: { type: String, default: '' },
})

defineEmits(['submit'])
</script>

<style scoped>
.auth-page {
  display: flex; justify-content: center; align-items: center;
  flex: 1; background: var(--bg-deep);
}
.auth-card {
  background: var(--bg-surface);
  padding: 44px 40px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  width: 360px;
  box-shadow: var(--shadow-gold);
}
.auth-card h2 {
  font-family: var(--font-display); font-size: 22px;
  text-align: center; margin-bottom: 28px; color: var(--gold);
  letter-spacing: 0.1em;
}
input {
  width: 100%; padding: 9px 12px; margin: 8px 0;
  border: 1px solid var(--border); border-radius: var(--radius-sm);
  background: var(--bg-input); color: var(--text-primary);
  font-size: 14px; font-family: var(--font-body);
  outline: none; transition: border var(--transition);
}
input::placeholder { color: var(--text-muted); }
input:focus { border-color: var(--gold-dim); }
button[type="submit"] {
  width: 100%; padding: 10px; margin-top: 16px;
  border: 1px solid var(--gold); border-radius: var(--radius-sm);
  background: transparent; color: var(--gold);
  font-family: var(--font-display); font-size: 14px;
  font-weight: 600; letter-spacing: 0.08em;
  cursor: pointer; transition: all var(--transition);
}
button[type="submit"]:hover { background: var(--gold); color: var(--bg-deep); }
button[type="submit"]:disabled { opacity: 0.4; cursor: not-allowed; }
.auth-link { text-align: center; margin-top: 20px; font-size: 14px; color: var(--text-secondary); }
.auth-link a { color: var(--gold); text-decoration: none; }
.auth-link a:hover { color: var(--gold-light); }
.error { color: var(--danger); text-align: center; margin-top: 14px; font-size: 14px; }
</style>
