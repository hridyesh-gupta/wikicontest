<template>
  <div
    id="alertContainer"
    class="position-fixed end-0 p-3"
    style="z-index: 1050; top: 80px;"
  >
    <transition-group name="alert" tag="div">
  <div
    v-for="alert in alerts"
    :key="alert.id"
    :class="['alert-card', `alert-${alert.type}`]"
    role="alert"
  >
    <div class="alert-content">
      <span class="alert-message">{{ alert.message }}</span>
      <button type="button" class="close-btn" @click="removeAlert(alert.id)">✕</button>
    </div>
  </div>
</transition-group>

  </div>
</template>

<script>
import { getAlertState, removeAlert } from '../utils/alerts'

export default {
  name: 'AlertContainer',
  setup() {
    const alertState = getAlertState()
    return {
      alerts: alertState.alerts,
      removeAlert
    }
  }
}
</script>

<!-- <style scoped>
/* --- Smooth Enter/Leave Animations --- */
.alert-enter-active,
.alert-leave-active {
  transition: all 0.35s ease;
}

.alert-enter-from {
  opacity: 0;
  transform: translateX(60px) scale(0.95);
}

.alert-leave-to {
  opacity: 0;
  transform: translateX(60px) scale(0.95);
}

/* --- Container --- */
#alertContainer {
  max-width: 420px;
  right: 1rem;
}

/* --- Solid Alert Card --- */
.alert-card {
  width: 100%;
  padding: 1rem 1.2rem;
  margin-bottom: 1rem;
  border-radius: 5px;

  background-color: #fff; /* gets replaced below by type color */
  border-left-width: 8px;
  border-style: solid;

  color: #fff;
  font-weight: 600;
  font-size: 0.95rem;

  box-shadow: 0 4px 10px rgba(0,0,0,0.15);
  transition: transform 0.25s ease;
}

.alert-card:hover {
  transform: translateY(-2px);
}

/* --- Content Styling --- */
.alert-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.1rem;
  font-weight: bold;
  color: rgba(255,255,255,0.8);
  cursor: pointer;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.close-btn:hover {
  opacity: 1;
  transform: scale(1.25);
}

/* ---------------------------------- */
/* WIKIDATA COLORS (SOLID BLOCK STYLE) */
/* ---------------------------------- */

/* Crimson (#990000) */
.alert-danger {
  background-color: #990000 !important;
  border-color: #660000 !important;
  color: #fff !important;
}

/* Emerald (#339966) */
.alert-success {
  background-color: #339966 !important;
  border-color: #267353 !important;
  color: #fff !important;
}

/* Sea Blue (#006699) */
.alert-info {
  background-color: #006699 !important;
  border-color: #004766 !important;
  color: #fff !important;
}

/* Amber-ish Warning */
.alert-warning {
  background-color: #cc6600 !important;
  border-color: #994d00 !important;
  color: #fff !important;
}

/* ------------------------ */
/* DARK MODE SOLID COLORS   */
/* ------------------------ */
[data-theme="dark"] .alert-card {
  box-shadow: 0 6px 14px rgba(0,0,0,0.5);
}

/* Keep solid but slightly brighter in dark mode */
[data-theme="dark"] .alert-danger {
  background-color: #cc0000 !important;
  border-color: #990000 !important;
}

[data-theme="dark"] .alert-success {
  background-color: #44cc88 !important;
  border-color: #2a875b !important;
}

[data-theme="dark"] .alert-info {
  background-color: #0099cc !important;
  border-color: #006699 !important;
}

[data-theme="dark"] .alert-warning {
  background-color: #ff8c1a !important;
  border-color: #cc6600 !important;
}

[data-theme="dark"] .close-btn {
  color: #fff;
}

/* --- Mobile --- */
@media (max-width: 768px) {
  #alertContainer {
    max-width: 90%;
  }

  .alert-card {
    padding: 0.9rem 1rem;
  }
}
</style> -->

<style scoped>
/* ========================================================= */
/*                Modern Premium Toast Alerts                */
/* ========================================================= */

#alertContainer {
  max-width: 420px;
  right: 1rem;
}

/* --- Animations (fade + slide + slight scale) --- */
.alert-enter-active,
.alert-leave-active {
  transition: all 0.35s cubic-bezier(0.25, 0.1, 0.25, 1);
}

.alert-enter-from,
.alert-leave-to {
  opacity: 0;
  transform: translateX(40px) scale(0.97);
}

/* ========================================================= */
/*                        CARD BASE                          */
/* ========================================================= */

.alert-card {
  width: 100%;
  padding: 1rem 1.3rem;
  margin-bottom: 1rem;

  border-radius: 5px;

  /* Glass effect */
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);

  border: 1px solid rgba(255, 255, 255, 0.4);

  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.15);

  color: #000;
  font-size: 0.95rem;
  font-weight: 500;
  overflow: hidden;

  display: flex;
  justify-content: space-between;
}

/* Hover Lift */
.alert-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.25);
}

/* ========================================================= */
/*                       INNER LAYOUT                        */
/* ========================================================= */

.alert-content {
  display: flex;
  justify-content: space-between;
  width: 100%;
  align-items: center;
}

.alert-message {
  line-height: 1.4;
}

/* Close Button */
.close-btn {
  background: rgba(255, 255, 255, 0.6);
  border: none;
  border-radius: 50%;
  width: 26px;
  height: 26px;

  font-size: 1rem;
  font-weight: bold;
  color: #444;

  cursor: pointer;
  transition: 0.25s ease;
}

.close-btn:hover {
  transform: scale(1.18) rotate(10deg);
  background: rgba(255, 255, 255, 0.85);
}

/* ========================================================= */
/*                    COLOR ACCENTS (left bar)               */
/* ========================================================= */

.alert-card {
  position: relative;
}

.alert-card::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  width: 8px;
  height: 100%;
  border-radius: 5px 0 0 5px;
}

/* Success – green */
.alert-success::before {
  background: #2ecc71;
}

/* Danger – red */
.alert-danger::before {
  background: #e74c3c;
}

/* Info – blue */
.alert-info::before {
  background: #3498db;
}

/* Warning – orange */
.alert-warning::before {
  background: #f39c12;
}

/* ========================================================= */
/*                      DARK MODE TWEAKS                     */
/* ========================================================= */

[data-theme="dark"] .alert-card {
  background: rgba(40, 40, 40, 0.55);
  border-color: rgba(255, 255, 255, 0.12);
  color: #eee;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
}

[data-theme="dark"] .close-btn {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

[data-theme="dark"] .close-btn:hover {
  background: rgba(255, 255, 255, 0.35);
}

/* ========================================================= */
/*                         RESPONSIVE                         */
/* ========================================================= */

@media (max-width: 768px) {
  #alertContainer {
    max-width: 92%;
  }
  .alert-card {
    padding: 0.85rem 1rem;
  }
}
</style>
