<template>
  <div class="section">
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card">
            <div class="card-body">
              <h3 class="card-title text-center mb-4">Log in</h3>

              <!-- Show loading state while checking auth -->
              <div v-if="checkingAuth" class="text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary" role="status">
                  <span class="visually-hidden">Checking authentication...</span>
                </div>
              </div>

              <!-- Show dismissible message if already logged in (but still show form) -->
              <!-- Only show if we've finished checking auth AND user is actually authenticated with valid ID -->
              <div
                v-if="!checkingAuth && isAuthenticated && currentUser && currentUser.id"
                class="alert alert-info alert-dismissible fade show"
                role="alert"
              >
                <i class="fas fa-info-circle me-2"></i>
                You are already logged in as <strong>{{ currentUser.username || currentUser.email || 'User' }}</strong>.
                <router-link to="/dashboard" class="alert-link">Go to Dashboard</router-link>.
                <button type="button"
class="btn-close"
data-bs-dismiss="alert"
aria-label="Close"></button>
              </div>

              <!-- Wikimedia OAuth Login (only login option) -->
              <div v-if="!checkingAuth" class="text-center">
                <a
                  :href="`${getApiBaseUrl()}/user/oauth/login`"
                  class="btn btn-primary w-100"
                  title="Login using Wikimedia OAuth 1.0a"
                >
                  <i class="fab fa-wikipedia-w me-2"></i>Log in with Wikimedia
                </a>
                <p class="text-muted mt-2" style="font-size: 0.85rem;">
                  <i class="fas fa-info-circle me-1"></i>
                  Uses OAuth 1.0a authentication
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from '../store'

export default {
  name: 'Login',
  setup() {
    const store = useStore()

    const checkingAuth = ref(true)

    // Check authentication status
    const isAuthenticated = computed(() => store.isAuthenticated)
    const currentUser = computed(() => store.currentUser)

    // Check auth on mount - force fresh check
    onMounted(async () => {
      checkingAuth.value = true

      // Small delay to ensure any logout operations have completed
      // This prevents race conditions where cookies might still be present
      await new Promise(resolve => setTimeout(resolve, 100))

      try {
        // Force a fresh auth check from server
        // This will clear state if user is not authenticated
        const authenticated = await store.checkAuth()

        // Double-check: if checkAuth returned false, ensure state is cleared
        if (!authenticated) {
          // Explicitly clear state to be sure
          store.state.currentUser = null
        }
      } catch (error) {
        // Silently handle errors - checkAuth already clears state
        // But ensure state is definitely cleared
        store.state.currentUser = null
        console.log('Auth check on mount:', error.message)
      } finally {
        checkingAuth.value = false
      }
    })


    // Get API base URL - use full URL for OAuth to ensure proper redirect
    const getApiBaseUrl = () => {
      // In development, use full URL to Flask backend
      if (import.meta.env.DEV) {
        return 'http://localhost:5000/api'
      }
      // In production, use relative URL
      return '/api'
    }

    return {
      checkingAuth,
      isAuthenticated,
      currentUser,
      getApiBaseUrl
    }
  }
}
</script>

<style scoped>
/* Login Page Styling with Wikipedia Colors */

.section {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
}

/* Card styling - professional */
.card {
  border: 1px solid var(--wiki-border);
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  background-color: var(--wiki-card-bg);
  overflow: hidden;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

[data-theme="dark"] .card {
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.card-body {
  padding: 2.5rem;
}

.card-title {
  color: var(--wiki-primary);
  font-weight: 700;
  font-size: 2rem;
  margin-bottom: 2rem;
  transition: color 0.3s ease;
}

/* Form styling */
.form-label {
  color: var(--wiki-dark);
  font-weight: 500;
  margin-bottom: 0.5rem;
  transition: color 0.3s ease;
}

.form-control {
  border-color: var(--wiki-input-border);
  background-color: var(--wiki-input-bg);
  color: var(--wiki-text);
  transition: all 0.2s ease;
  padding: 0.75rem;
}

.form-control:focus {
  border-color: var(--wiki-primary);
  box-shadow: 0 0 0 0.2rem rgba(0, 102, 153, 0.25);
  background-color: var(--wiki-input-bg);
  color: var(--wiki-text);
}

/* Button styling */
.btn-primary {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  color: #ffffff !important;
  font-weight: 500;
  padding: 0.75rem;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background-color: var(--wiki-primary-hover);
  border-color: var(--wiki-primary-hover);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.2);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outline-primary {
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
  font-weight: 500;
  padding: 0.75rem;
  transition: all 0.2s ease;
}

.btn-outline-primary:hover {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  color: white;
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.2);
}

/* Alert styling - professional */
.alert-info {
  background-color: rgba(0, 102, 153, 0.1);
  border: 1px solid var(--wiki-primary);
  border-left: 4px solid var(--wiki-primary);
  color: var(--wiki-primary);
  border-radius: 4px;
}

[data-theme="dark"] .alert-info {
  background-color: rgba(77, 166, 204, 0.15);
}

.alert-info .alert-link {
  color: var(--wiki-primary-hover);
  font-weight: 600;
  text-decoration: underline;
}

.alert-info .alert-link:hover {
  color: var(--wiki-primary);
}

/* Divider */
hr {
  border-color: var(--wiki-border);
  margin: 1.5rem 0;
  transition: border-color 0.3s ease;
}

.text-muted {
  color: var(--wiki-text-muted) !important;
}

/* Link styling */
a {
  color: var(--wiki-primary);
  font-weight: 500;
  transition: color 0.2s ease;
}

a:hover {
  color: var(--wiki-primary-hover);
  text-decoration: underline;
}

/* Spinner */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}

.spinner-border.text-primary {
  color: var(--wiki-primary) !important;
}

/* Wikipedia icon - white color for primary button */
.btn-primary .fab.fa-wikipedia-w {
  font-size: 1.2em;
  color: #ffffff !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .section {
    min-height: calc(100vh - 150px);
    padding: 1rem 0;
  }

  .card-body {
    padding: 1.5rem;
  }

  .card-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 576px) {
  .section {
    min-height: auto;
    padding: 0.5rem 0;
  }

  .card-body {
    padding: 1.25rem;
  }

  .card-title {
    font-size: 1.25rem;
    margin-bottom: 1.5rem;
  }

  .form-control {
    font-size: 16px; /* Prevents zoom on iOS */
  }
}
</style>

