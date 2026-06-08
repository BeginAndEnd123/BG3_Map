<template>
  <div class="auth-page">
    <div class="auth-bg">
      <span class="bg-rune bg-rune--1">◆</span>
      <span class="bg-rune bg-rune--2">✦</span>
      <span class="bg-rune bg-rune--3">◇</span>
    </div>
    <div class="auth-card">
      <div class="deco-line">
        <span class="deco-seg"></span>
        <span class="deco-diamond">◆</span>
        <span class="deco-seg"></span>
      </div>
      <h2>{{ title }}</h2>
      <div class="divider"><span></span></div>
      <form @submit.prevent="$emit('submit')">
        <slot />
        <button type="submit" :disabled="submitting">
          <span class="btn-text">{{ submitting ? (submitLabel || '请稍候...') : title }}</span>
        </button>
      </form>
      <p v-if="linkText" class="auth-link">
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
  flex: 1; background: radial-gradient(ellipse at 50% 40%, #14141e 0%, var(--bg-deep) 60%, #06060f 100%);
  position: relative; overflow: hidden;
}

/* ── 背景装饰符文 ── */
.auth-bg { position: absolute; inset: 0; pointer-events: none; }
.bg-rune {
  position: absolute; color: rgba(200, 164, 78, 0.04);
  font-size: 120px; font-family: var(--font-display);
  animation: rune-float 12s ease-in-out infinite;
}
.bg-rune--1 { top: 8%; left: 10%; animation-delay: 0s; }
.bg-rune--2 { top: 60%; right: 8%; animation-delay: -4s; font-size: 80px; }
.bg-rune--3 { bottom: 12%; left: 18%; animation-delay: -8s; font-size: 100px; }
@keyframes rune-float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50%      { transform: translateY(-18px) rotate(4deg); }
}

/* ── 卡片 ── */
.auth-card {
  position: relative; z-index: 1;
  background: linear-gradient(160deg, rgba(18,18,31,0.95) 0%, rgba(10,10,20,0.98) 100%);
  padding: 48px 44px 40px;
  border: 1px solid var(--border-gold);
  border-radius: 3px;
  width: 380px;
  box-shadow:
    0 0 60px rgba(200,164,78,0.04),
    0 0 120px rgba(0,0,0,0.4),
    inset 0 1px 0 rgba(200,164,78,0.06);
}

/* ── 顶部装饰线 ── */
.deco-line {
  display: flex; align-items: center; justify-content: center;
  gap: 10px; margin-bottom: 12px;
}
.deco-seg {
  display: block; width: 36px; height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold-dim), transparent);
}
.deco-diamond {
  color: var(--gold); font-size: 10px;
  opacity: 0.6; animation: diamond-pulse 3s ease-in-out infinite;
}
@keyframes diamond-pulse {
  0%, 100% { opacity: 0.4; }
  50%      { opacity: 0.9; }
}

.auth-card h2 {
  font-family: var(--font-display); font-size: 24px; font-weight: 600;
  text-align: center; margin: 0 0 8px; color: var(--gold);
  letter-spacing: 0.12em;
}

/* ── 分隔线 ── */
.divider {
  display: flex; justify-content: center; margin-bottom: 28px;
}
.divider span {
  display: block; width: 48px; height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
}

/* ── 输入框 ── */
:deep(input) {
  width: 100%; padding: 11px 14px; margin: 8px 0;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: rgba(10,10,20,0.6);
  color: var(--text-primary);
  font-size: 14px; font-family: var(--font-body);
  outline: none;
  transition: border-color var(--transition), box-shadow var(--transition);
}
:deep(input)::placeholder { color: var(--text-muted); font-style: italic; }
:deep(input):focus {
  border-color: var(--gold);
  box-shadow: 0 0 0 2px rgba(200,164,78,0.08), 0 0 16px rgba(200,164,78,0.04);
}

/* ── 提交按钮 ── */
button[type="submit"] {
  width: 100%; padding: 12px; margin-top: 20px;
  border: 1px solid var(--gold);
  border-radius: var(--radius-sm);
  background: linear-gradient(180deg, rgba(200,164,78,0.1) 0%, rgba(200,164,78,0.03) 100%);
  color: var(--gold);
  font-family: var(--font-display); font-size: 13px;
  font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase;
  cursor: pointer; position: relative; overflow: hidden;
  transition: all 0.3s ease;
}
button[type="submit"]::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(90deg, transparent, rgba(200,164,78,0.06), transparent);
  transform: translateX(-100%);
  transition: transform 0.6s ease;
}
button[type="submit"]:hover:not(:disabled) {
  background: var(--gold); color: var(--bg-deep);
  border-color: var(--gold);
  box-shadow: 0 0 28px rgba(200,164,78,0.2), 0 0 60px rgba(200,164,78,0.06);
  transform: translateY(-1px);
}
button[type="submit"]:hover:not(:disabled)::after {
  transform: translateX(100%);
}
button[type="submit"]:disabled {
  opacity: 0.35; cursor: not-allowed;
}
button[type="submit"]:active:not(:disabled) {
  transform: translateY(0);
}

.btn-text { position: relative; z-index: 1; }

/* ── 链接 ── */
.auth-link {
  text-align: center; margin-top: 22px;
  font-size: 14px; color: var(--text-muted);
  letter-spacing: 0.04em;
}
.auth-link a {
  color: var(--gold); text-decoration: none;
  margin-left: 4px; transition: color var(--transition);
}
.auth-link a:hover { color: var(--gold-light); }

/* ── 错误 ── */
.error {
  color: var(--danger); text-align: center;
  margin-top: 16px; font-size: 13px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  background: rgba(184,68,68,0.08);
  border: 1px solid rgba(184,68,68,0.15);
}
</style>
