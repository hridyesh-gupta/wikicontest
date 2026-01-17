<template>
  <!-- Full-screen overlay for requesting contest creator rights (trusted member status) -->
  <div v-if="isVisible" class="fullscreen-overlay" @click.self="handleClose">
    <div class="fullscreen-content">
      <!-- Header -->
      <div class="fullscreen-header">
        <h2 class="fullscreen-title">
          <i class="fas fa-user-plus me-2"></i>Request Contest Creator Rights
        </h2>
        <button type="button" class="btn-close-fullscreen" @click="handleClose">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- Body with form -->
      <div class="fullscreen-body">
        <!-- Information about trusted member status -->
        <div class="alert alert-info mb-4">
          <i class="fas fa-info-circle me-2"></i>
          <strong>About Contest Creator Rights:</strong>
          <ul class="mb-0 mt-2">
            <li>Contest creators can create and manage contests</li>
            <li>Users with 300+ edits are automatically approved</li>
            <li>Users with fewer edits need to provide a reason for review</li>
          </ul>
        </div>

        <!-- Form for requesting trusted member status -->
        <form @submit.prevent="handleSubmit">
          <!-- Reason field (required for users with < 300 edits) -->
          <div class="mb-4">
            <label for="requestReason" class="form-label">
              Reason for Request
              <span v-if="requiresReason" class="text-danger">*</span>
              <span v-else class="text-muted">(Optional)</span>
            </label>
            <textarea
              id="requestReason"
              class="form-control"
              v-model="formData.reason"
              rows="8"
              :required="requiresReason"
              :placeholder="
                'Please explain why you would like to become a contest creator. ' +
                'Include information about your experience, contributions, or any relevant background.'
              "
            ></textarea>
            <small v-if="requiresReason" class="form-text text-muted">
              <i class="fas fa-exclamation-triangle me-1"></i>
              A reason is required because you have fewer than 300 edits. A superadmin will review your request.
            </small>
            <small v-else class="form-text text-muted">
              <i class="fas fa-check-circle me-1"></i>
              You have 300+ edits, so you may be automatically approved. Providing a reason is optional but recommended.
            </small>
          </div>

          <!-- Display edit count if available -->
          <div v-if="editCount !== null" class="mb-4">
            <div class="alert" :class="editCount >= 300 ? 'alert-success' : 'alert-warning'">
              <i :class="editCount >= 300 ? 'fas fa-check-circle me-2' : 'fas fa-info-circle me-2'"></i>
              <strong>Your Edit Count:</strong> {{ editCount }} edits
              <span v-if="editCount >= 300" class="ms-2">
                (You meet the minimum requirement for automatic approval!)
              </span>
              <span v-else class="ms-2">
                (Minimum {{ minEditCount }} edits required for automatic approval)
              </span>
            </div>
          </div>
        </form>
      </div>

      <!-- Footer with action buttons -->
      <div class="fullscreen-footer">
        <button type="button" class="btn btn-secondary" @click="handleClose">
          Cancel
        </button>
        <button
          type="button"
          class="btn btn-primary"
          @click="handleSubmit"
          :disabled="loading || (requiresReason && !formData.reason.trim())"
        >
          <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
          <i v-else class="fas fa-paper-plane me-2"></i>
          Submit Request
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue'
import api from '../services/api'
import { showAlert } from '../utils/alerts'

export default {
  name: 'RequestTrustedMemberModal',
  emits: ['requested', 'close'],
  props: {
    // Control visibility from parent component
    show: {
      type: Boolean,
      default: false
    }
  },
  setup(props, { emit }) {
    const loading = ref(false)
    const requiresReason = ref(false)
    const editCount = ref(null)
    const minEditCount = ref(300)
    const isVisible = ref(false)

    // Form data for the request
    const formData = reactive({
      reason: ''
    })

    // Watch for show prop changes
    watch(() => props.show, (newValue) => {
      isVisible.value = newValue
      if (newValue) {
        // Reset form when opened
        formData.reason = ''
        requiresReason.value = false
        editCount.value = null
        loading.value = false
        // Prevent body scroll when fullscreen is open
        document.body.style.overflow = 'hidden'
      } else {
        // Restore body scroll when closed
        document.body.style.overflow = ''
      }
    }, { immediate: true })

    // Handle close action
    const handleClose = () => {
      isVisible.value = false
      emit('close')
      // Restore body scroll
      document.body.style.overflow = ''
    }

    // Submit the trusted member request
    const handleSubmit = async () => {
      // Validate form
      if (requiresReason.value && !formData.reason.trim()) {
        showAlert('Please provide a reason for your request', 'warning')
        return
      }

      loading.value = true
      try {
        // Prepare request data
        const requestData = {}
        if (formData.reason.trim()) {
          requestData.reason = formData.reason.trim()
        }

        // Submit request to backend
        const response = await api.post('/user/trusted-members/request', requestData)

        // Check if auto-approved or requires review
        if (response.auto_approved) {
          showAlert(
            response.message || 'Congratulations! Your creator account has been automatically approved.',
            'success'
          )
          // Update edit count if provided
          if (response.edit_count !== undefined) {
            editCount.value = response.edit_count
          }
        } else {
          showAlert(
            response.message || 'Your request has been submitted for review. A superadmin will review it.',
            'success'
          )
          // Update edit count if provided
          if (response.edit_count !== undefined) {
            editCount.value = response.edit_count
            requiresReason.value = response.edit_count < minEditCount.value
          }
        }

        // Emit event to parent component
        emit('requested')

        // Close fullscreen view
        handleClose()

        // Reset form
        formData.reason = ''
      } catch (error) {
        console.error('Error submitting trusted member request:', error)

        // Handle specific error cases
        if (error.response?.data?.requires_reason) {
          requiresReason.value = true
          showAlert(
            error.response.data.error || 'A reason is required for your request',
            'warning'
          )
          // Update edit count if provided
          if (error.response.data.edit_count !== undefined) {
            editCount.value = error.response.data.edit_count
            minEditCount.value = error.response.data.min_edit_count || 300
          }
        } else {
          showAlert(
            error.response?.data?.error || error.message || 'Failed to submit request',
            'danger'
          )
        }
      } finally {
        loading.value = false
      }
    }

    // Cleanup on unmount
    onMounted(() => {
      // Ensure body scroll is restored if component is unmounted
      return () => {
        document.body.style.overflow = ''
      }
    })

    return {
      formData,
      loading,
      requiresReason,
      editCount,
      minEditCount,
      isVisible,
      handleSubmit,
      handleClose
    }
  }
}
</script>

<style scoped>
/* Full-screen overlay */
.fullscreen-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  overflow-y: auto;
  animation: fadeIn 0.2s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Full-screen content container */
.fullscreen-content {
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  background-color: var(--wiki-modal-bg);
  border-radius: 8px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Header with Wikipedia primary color */
.fullscreen-header {
  background-color: var(--wiki-primary);
  color: white;
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.fullscreen-title {
  font-weight: 600;
  font-size: 1.5rem;
  margin: 0;
  display: flex;
  align-items: center;
}

/* Close button */
.btn-close-fullscreen {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.btn-close-fullscreen:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

/* Body section */
.fullscreen-body {
  background-color: var(--wiki-modal-bg);
  color: var(--wiki-text);
  padding: 2rem;
  flex: 1;
  overflow-y: auto;
}

/* Form labels */
.form-label {
  color: var(--wiki-dark);
  font-weight: 500;
  margin-bottom: 0.5rem;
  font-size: 1rem;
}

[data-theme="dark"] .form-label {
  color: #ffffff;
}

/* Form inputs */
.form-control {
  border-color: var(--wiki-input-border);
  background-color: var(--wiki-input-bg);
  color: var(--wiki-text);
  transition: all 0.2s ease;
  font-size: 1rem;
  padding: 0.75rem;
}

.form-control:focus {
  border-color: var(--wiki-primary);
  box-shadow: 0 0 0 0.2rem rgba(0, 102, 153, 0.25);
  outline: none;
}

/* Textarea - larger for full screen */
textarea.form-control {
  resize: vertical;
  min-height: 200px;
  font-size: 1rem;
  line-height: 1.5;
}

/* Alert styling */
.alert {
  border-radius: 4px;
  border-left: 4px solid;
  padding: 1rem 1.25rem;
  font-size: 0.95rem;
}

.alert-info {
  background-color: rgba(0, 102, 153, 0.1);
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
}

.alert-success {
  background-color: rgba(40, 167, 69, 0.1);
  border-color: #28a745;
  color: #28a745;
}

.alert-warning {
  background-color: rgba(255, 193, 7, 0.1);
  border-color: #ffc107;
  color: #856404;
}

/* Alert list styling */
.alert ul {
  padding-left: 1.5rem;
  margin-top: 0.5rem;
  margin-bottom: 0;
}

.alert li {
  margin-bottom: 0.25rem;
}

/* Form text (help text) */
.form-text {
  font-size: 0.875rem;
  margin-top: 0.5rem;
  display: block;
}

/* Primary button */
.btn-primary {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  font-weight: 500;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}

.btn-primary:hover {
  background-color: var(--wiki-primary-hover);
  border-color: var(--wiki-primary-hover);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Secondary button */
.btn-secondary {
  background-color: var(--wiki-text-muted);
  border-color: var(--wiki-text-muted);
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}

.btn-secondary:hover {
  background-color: #6c757d;
  border-color: #6c757d;
}

/* Footer */
.fullscreen-footer {
  border-top: 1px solid var(--wiki-border);
  padding: 1.5rem 2rem;
  background-color: var(--wiki-modal-bg);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  flex-shrink: 0;
}

/* Spinner */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}

/* Dark mode adjustments */
[data-theme="dark"] .fullscreen-content {
  background-color: #2a2a2a;
}

[data-theme="dark"] .fullscreen-body {
  background-color: #2a2a2a;
}

[data-theme="dark"] .form-control {
  background-color: #3a3a3a;
  border-color: #555;
  color: #fff;
}

[data-theme="dark"] .form-control:focus {
  background-color: #3a3a3a;
  border-color: var(--wiki-primary);
  color: #fff;
}

[data-theme="dark"] .fullscreen-footer {
  background-color: #2a2a2a;
  border-top-color: #444;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .fullscreen-overlay {
    padding: 0;
  }

  .fullscreen-content {
    max-width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }

  .fullscreen-header {
    padding: 1.25rem 1.5rem;
  }

  .fullscreen-title {
    font-size: 1.25rem;
  }

  .fullscreen-body {
    padding: 1.5rem;
  }

  .fullscreen-footer {
    padding: 1.25rem 1.5rem;
    flex-direction: column-reverse;
  }

  .fullscreen-footer .btn {
    width: 100%;
  }
}
</style>
