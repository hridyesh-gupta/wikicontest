<template>
  <div class="outreach-dashboard-tab">
    <!-- Nested Tabs for Course and Users -->
    <ul class="nav nav-tabs mb-4" role="tablist">
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{ active: activeSubTab === 'course' }"
          @click="activeSubTab = 'course'"
          type="button"
          role="tab"
        >
          <i class="fas fa-graduation-cap me-2"></i>Course
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{ active: activeSubTab === 'users' }"
          @click="handleUsersTabClick"
          type="button"
          role="tab"
        >
          <i class="fas fa-users me-2"></i>Users
        </button>
      </li>
    </ul>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Course Tab -->
      <div 
        v-show="activeSubTab === 'course'"
        class="tab-pane"
        :class="{ 'active': activeSubTab === 'course' }"
        role="tabpanel"
      >
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-3 text-muted">Loading Outreach Dashboard data...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger">
          <i class="fas fa-exclamation-circle me-2"></i>
          <strong>Error loading Outreach Dashboard data:</strong> {{ error }}
          <button class="btn btn-sm btn-outline-danger ms-3" @click="loadCourseData">
            <i class="fas fa-redo me-1"></i>Retry
          </button>
        </div>

        <!-- Course Data Display -->
        <div v-else-if="courseData" class="course-data">
      <!-- Header with Refresh Button -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h5 class="mb-0">
          <i class="fas fa-graduation-cap me-2"></i>Course Information
        </h5>
        <button class="btn btn-sm btn-outline-primary" @click="loadData" :disabled="loading">
          <i class="fas fa-sync-alt me-1" :class="{ 'fa-spin': loading }"></i>Refresh
        </button>
      </div>

      <!-- Course Basic Information -->
      <div class="card mb-4">
        <div class="card-header">
          <h6 class="mb-0"><i class="fas fa-info-circle me-2"></i>Basic Information</h6>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6 mb-3">
              <strong>Course Title:</strong>
              <p class="mb-0">{{ courseData.title || 'N/A' }}</p>
            </div>
            <div class="col-md-6 mb-3">
              <strong>School/Institution:</strong>
              <p class="mb-0">{{ courseData.school || 'N/A' }}</p>
            </div>
            <div class="col-12 mb-3" v-if="courseData.description">
              <strong>Description:</strong>
              <p class="mb-0">{{ courseData.description }}</p>
            </div>
            <div class="col-md-6 mb-3">
              <strong>Course Type:</strong>
              <p class="mb-0">{{ courseData.type || 'N/A' }}</p>
            </div>
            <div class="col-md-6 mb-3" v-if="courseData.home_wiki">
              <strong>Home Wiki:</strong>
              <p class="mb-0">
                {{ courseData.home_wiki.language || 'N/A' }} - {{ courseData.home_wiki.project || 'N/A' }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Timeline Information -->
      <div class="card mb-4" v-if="courseData.start || courseData.end">
        <div class="card-header">
          <h6 class="mb-0"><i class="fas fa-calendar-alt me-2"></i>Timeline</h6>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6 mb-3" v-if="courseData.start">
              <strong>Start Date:</strong>
              <p class="mb-0">{{ formatDate(courseData.start) }}</p>
            </div>
            <div class="col-md-6 mb-3" v-if="courseData.end">
              <strong>End Date:</strong>
              <p class="mb-0">{{ formatDate(courseData.end) }}</p>
            </div>
            <div class="col-md-6 mb-3" v-if="courseData.timeline_start">
              <strong>Timeline Start:</strong>
              <p class="mb-0">{{ formatDate(courseData.timeline_start) }}</p>
            </div>
            <div class="col-md-6 mb-3" v-if="courseData.timeline_end">
              <strong>Timeline End:</strong>
              <p class="mb-0">{{ formatDate(courseData.timeline_end) }}</p>
            </div>
            <div class="col-12 mb-3" v-if="courseData.updated_at">
              <strong>Last Updated:</strong>
              <p class="mb-0">{{ formatDate(courseData.updated_at) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Indicators -->
      <div class="card mb-4">
        <div class="card-header">
          <h6 class="mb-0"><i class="fas fa-toggle-on me-2"></i>Status</h6>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-3 mb-2">
              <span class="badge" :class="courseData.published ? 'bg-success' : 'bg-secondary'">
                {{ courseData.published ? 'Published' : 'Not Published' }}
              </span>
            </div>
            <div class="col-md-3 mb-2">
              <span class="badge" :class="courseData.ended ? 'bg-warning' : 'bg-info'">
                {{ courseData.ended ? 'Ended' : 'Active' }}
              </span>
            </div>
            <div class="col-md-3 mb-2">
              <span class="badge" :class="courseData.closed ? 'bg-danger' : 'bg-success'">
                {{ courseData.closed ? 'Closed' : 'Open' }}
              </span>
            </div>
            <div class="col-md-3 mb-2" v-if="courseData.wiki_edits_enabled !== undefined">
              <span class="badge" :class="courseData.wiki_edits_enabled ? 'bg-success' : 'bg-secondary'">
                {{ courseData.wiki_edits_enabled ? 'Edits Enabled' : 'Edits Disabled' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Statistics -->
      <div class="card mb-4">
        <div class="card-header">
          <h6 class="mb-0"><i class="fas fa-chart-bar me-2"></i>Statistics</h6>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-4 mb-3">
              <div class="stat-item">
                <i class="fas fa-users text-primary me-2"></i>
                <strong>Students:</strong>
                <span class="stat-value">{{ courseData.student_count || 0 }}</span>
              </div>
            </div>
            <div class="col-md-4 mb-3">
              <div class="stat-item">
                <i class="fas fa-user-check text-success me-2"></i>
                <strong>Trained:</strong>
                <span class="stat-value">{{ courseData.trained_count || 0 }}</span>
              </div>
            </div>
            <div class="col-md-4 mb-3">
              <div class="stat-item">
                <i class="fas fa-edit text-info me-2"></i>
                <strong>Edits:</strong>
                <span class="stat-value">{{ courseData.edit_count || '0' }}</span>
              </div>
            </div>
            <div class="col-md-4 mb-3">
              <div class="stat-item">
                <i class="fas fa-file-alt text-warning me-2"></i>
                <strong>Articles:</strong>
                <span class="stat-value">{{ courseData.article_count || 0 }}</span>
              </div>
            </div>
            <div class="col-md-4 mb-3">
              <div class="stat-item">
                <i class="fas fa-font text-secondary me-2"></i>
                <strong>Words:</strong>
                <span class="stat-value">{{ courseData.word_count || '0' }}</span>
              </div>
            </div>
            <div class="col-md-4 mb-3">
              <div class="stat-item">
                <i class="fas fa-eye text-danger me-2"></i>
                <strong>Views:</strong>
                <span class="stat-value">{{ courseData.view_count || '0' }}</span>
              </div>
            </div>
            <div class="col-md-4 mb-3" v-if="courseData.upload_count !== undefined">
              <div class="stat-item">
                <i class="fas fa-upload text-primary me-2"></i>
                <strong>Uploads:</strong>
                <span class="stat-value">{{ courseData.upload_count || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Enrollment Link -->
      <div class="card" v-if="courseData.enroll_url">
        <div class="card-header">
          <h6 class="mb-0"><i class="fas fa-link me-2"></i>Enrollment</h6>
        </div>
        <div class="card-body">
          <a :href="courseData.enroll_url" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
            <i class="fas fa-external-link-alt me-2"></i>Enroll in Course
          </a>
          <small class="d-block mt-2 text-muted" v-if="courseData.passcode_required">
            <i class="fas fa-lock me-1"></i>This course requires a passcode to enroll.
          </small>
        </div>
      </div>
        </div>

        <!-- No Data State -->
        <div v-else class="text-center py-5 text-muted">
          <i class="fas fa-info-circle fa-3x mb-3"></i>
          <p>No course data available.</p>
        </div>
      </div>

      <!-- Users Tab -->
      <div 
        v-show="activeSubTab === 'users'"
        class="tab-pane"
        :class="{ 'active': activeSubTab === 'users' }"
        role="tabpanel"
      >
        <!-- Loading State -->
        <div v-if="loadingUsers" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-3 text-muted">Loading course users...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="usersError" class="alert alert-danger">
          <i class="fas fa-exclamation-circle me-2"></i>
          <strong>Error loading course users:</strong> {{ usersError }}
          <button class="btn btn-sm btn-outline-danger ms-3" @click="loadUsersData">
            <i class="fas fa-redo me-1"></i>Retry
          </button>
        </div>

        <!-- Users Data Display -->
        <div v-else-if="usersData && usersData.length > 0" class="users-data">
          <!-- Header with Refresh Button -->
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="mb-0">
              <i class="fas fa-users me-2"></i>Course Participants ({{ usersData.length }})
            </h5>
            <button class="btn btn-sm btn-outline-primary" @click="loadUsersData" :disabled="loadingUsers">
              <i class="fas fa-sync-alt me-1" :class="{ 'fa-spin': loadingUsers }"></i>Refresh
            </button>
          </div>

          <!-- Users Table -->
          <div class="card">
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Username</th>
                      <th>Role</th>
                      <th>Enrolled</th>
                      <th>Mainspace</th>
                      <th>Userspace</th>
                      <th>Uploads</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="user in usersData" :key="user.id">
                      <td>
                        <strong>{{ user.username || 'N/A' }}</strong>
                        <span v-if="user.admin" class="badge bg-warning ms-2">Admin</span>
                      </td>
                      <td>
                        <span class="badge" :class="user.role === 1 ? 'bg-primary' : 'bg-secondary'">
                          {{ user.role === 1 ? 'Instructor' : 'Student' }}
                        </span>
                      </td>
                      <td>{{ formatDate(user.enrolled_at) }}</td>
                      <td>{{ formatNumber(user.character_sum_ms || 0) }}</td>
                      <td>{{ formatNumber(user.character_sum_us || 0) }}</td>
                      <td>{{ user.total_uploads || 0 }}</td>
                      <td>
                        <a 
                          v-if="user.contribution_url" 
                          :href="user.contribution_url" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          class="btn btn-sm btn-outline-primary"
                          title="View Contributions"
                        >
                          <i class="fas fa-external-link-alt"></i>
                        </a>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- No Users State -->
        <div v-else-if="usersData && usersData.length === 0" class="text-center py-5 text-muted">
          <i class="fas fa-users fa-3x mb-3"></i>
          <p>No users enrolled in this course.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { fetchCourseData, fetchCourseUsers } from '../services/outreachDashboard'

export default {
  name: 'OutreachDashboardTab',
  props: {
    baseUrl: {
      type: String,
      required: true
    },
    contestId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const activeSubTab = ref('course')
    const loading = ref(false)
    const error = ref(null)
    const courseData = ref(null)
    
    const loadingUsers = ref(false)
    const usersError = ref(null)
    const usersData = ref(null)

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      try {
        const date = new Date(dateString)
        return date.toLocaleString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (e) {
        return dateString
      }
    }

    const formatNumber = (num) => {
      if (num === 0) return '0'
      if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
      if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
      return num.toLocaleString()
    }

    const loadCourseData = async () => {
      if (!props.baseUrl) {
        error.value = 'No Outreach Dashboard URL provided'
        return
      }

      loading.value = true
      error.value = null

      try {
        const result = await fetchCourseData(props.baseUrl)
        if (result.success) {
          courseData.value = result.data
        } else {
          error.value = result.error || 'Failed to load course data'
          courseData.value = null
        }
      } catch (err) {
        error.value = err.message || 'Unexpected error occurred'
        courseData.value = null
      } finally {
        loading.value = false
      }
    }

    const loadUsersData = async () => {
      if (!props.contestId) {
        usersError.value = 'Contest ID is required'
        return
      }

      loadingUsers.value = true
      usersError.value = null

      try {
        const result = await fetchCourseUsers(props.contestId)
        if (result.success) {
          usersData.value = result.data || []
        } else {
          usersError.value = result.error || 'Failed to load course users'
          usersData.value = null
        }
      } catch (err) {
        usersError.value = err.message || 'Unexpected error occurred'
        usersData.value = null
      } finally {
        loadingUsers.value = false
      }
    }

    const handleUsersTabClick = () => {
      activeSubTab.value = 'users'
      // Load users data when tab is clicked (only if not already loaded)
      if (!usersData.value && !loadingUsers.value) {
        loadUsersData()
      }
    }

    onMounted(() => {
      // Load course data on mount
      loadCourseData()
    })

    return {
      activeSubTab,
      loading,
      error,
      courseData,
      loadingUsers,
      usersError,
      usersData,
      formatDate,
      formatNumber,
      loadCourseData,
      loadUsersData,
      handleUsersTabClick
    }
  }
}
</script>

<style scoped>
.outreach-dashboard-tab {
  padding: 1rem 0;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  background-color: var(--wiki-hover-bg, #f8f9fa);
  border-radius: 4px;
}

.stat-value {
  margin-left: auto;
  font-size: 1.25rem;
  font-weight: bold;
  color: var(--wiki-primary, #006699);
}

.card {
  border: 1px solid var(--wiki-border, #dee2e6);
  border-radius: 8px;
}

.card-header {
  background-color: var(--wiki-card-header-bg, #f8f9fa);
  border-bottom: 1px solid var(--wiki-border, #dee2e6);
  font-weight: 600;
}

.card-body {
  padding: 1.25rem;
}

.badge {
  font-size: 0.875rem;
  padding: 0.5em 0.75em;
}

.btn {
  transition: all 0.2s ease;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>

