<template>
  <div class="container py-5">
    <div class="dashboard-header mb-4">
      <h2 class="page-header">Dashboard</h2>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="dashboardData">

      <!-- Statistics Cards -->
      <div class="row g-3 mb-4">
        <div class="col-12 col-sm-6 col-lg-4">
          <div class="stat-card stat-card-primary">
            <div class="stat-icon">
              <i class="fas fa-trophy"></i>
            </div>
            <div class="stat-content">
              <h3 class="stat-value">{{ dashboardData.total_score || 0 }}</h3>
              <p class="stat-label">Total Score</p>
            </div>
          </div>
        </div>

        <div class="col-12 col-sm-6 col-lg-4">
          <div class="stat-card stat-card-success">
            <div class="stat-icon">
              <i class="fas fa-medal"></i>
            </div>
            <div class="stat-content">
              <h3 class="stat-value">{{ dashboardData.created_contests?.length || 0 }}</h3>
              <p class="stat-label">Created Contests</p>
            </div>
          </div>
        </div>

        <div class="col-12 col-sm-6 col-lg-4">
          <div class="stat-card stat-card-warning">
            <div class="stat-icon">
              <i class="fas fa-gavel"></i>
            </div>
            <div class="stat-content">
              <h3 class="stat-value">{{ dashboardData.jury_contests?.length || 0 }}</h3>
              <p class="stat-label">Jury Member</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Overview Section -->
      <div class="row g-3 mb-4">
        <!-- Recent Submissions -  -->
        <div class="col-12 col-lg-6">
          <div class="section-card">
            <div class="section-header">
              <h4 class="section-title">
                <i class="fas fa-file-alt me-2"></i>Recent Submissions
              </h4>
              <span class="badge bg-primary">{{ totalSubmissions }}</span>
            </div>

            <div class="section-body">
              <div v-if="dashboardData.submissions_by_contest?.length > 0">
                <!-- Scrollable submissions container -->
                <div class="submissions-container" :class="{ 'expanded': showAllSubmissions }">
                  <div
                    v-for="contest in (showAllSubmissions ? dashboardData.submissions_by_contest : dashboardData.submissions_by_contest.slice(0, 3))"
                    :key="contest.contest_id" class="submission-group mb-3">
                    <div class="contest-name-badge">{{ contest.contest_name }}</div>

                    <div v-for="submission in contest.submissions.slice(0, showAllSubmissions ? undefined : 2)"
                      :key="submission.id" class="submission-item"
                      :class="{ 'submission-clickable': submission.reviewed_at }"
                      @click="handleSubmissionClick(submission)">
                      <div class="submission-info">
                        <span class="submission-title">{{ submission.article_title }}</span>
                        <span class="submission-date">{{ formatDateShort(submission.submitted_at) }}</span>
                      </div>
                      <div class="submission-actions">
                        <span :class="`badge badge-${getStatusColor(submission.status)}`">
                          {{ submission.status }}
                        </span>
                        <button v-if="submission.reviewed_at" class="btn-icon btn-feedback"
                          @click.stop="openFeedbackModal(submission)" title="View Feedback">
                          <i class="fas fa-comment-dots"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-if="dashboardData.submissions_by_contest.length > 3 || totalSubmissions > 6"
                  class="text-center mt-3 pt-3 border-top">
                  <button class="btn btn-sm btn-outline-primary" @click="showAllSubmissions = !showAllSubmissions">
                    <i class="fas" :class="showAllSubmissions ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
                    {{ showAllSubmissions ? 'Show Less' : `View All (${totalSubmissions})` }}
                  </button>
                </div>
              </div>

              <div v-else class="empty-state">
                <i class="fas fa-inbox fa-3x mb-3"></i>
                <p class="text-muted">No submissions yet</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Contest Scores -->
        <div class="col-12 col-lg-6">
          <div class="section-card">
            <div class="section-header">
              <h4 class="section-title">
                <i class="fas fa-chart-bar me-2"></i>Contest Scores
              </h4>
              <span class="badge bg-success">{{ dashboardData.contest_wise_scores?.length || 0 }}</span>
            </div>

            <div class="section-body">
              <div v-if="dashboardData.contest_wise_scores?.length > 0">
                <!-- Scrollable scores container -->
                <div class="scores-container" :class="{ 'expanded': showAllScores }">
                  <div
                    v-for="score in (showAllScores ? dashboardData.contest_wise_scores : dashboardData.contest_wise_scores.slice(0, 6))"
                    :key="score.contest_id" class="score-item">
                    <span class="score-contest">{{ score.contest_name }}</span>
                    <span class="score-points">{{ score.contest_score }} pts</span>
                  </div>
                </div>

                <div v-if="dashboardData.contest_wise_scores.length > 6" class="text-center mt-3 pt-3 border-top">
                  <button class="btn btn-sm btn-outline-primary" @click="showAllScores = !showAllScores">
                    <i class="fas" :class="showAllScores ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
                    {{ showAllScores ? 'Show Less' : `View All (${dashboardData.contest_wise_scores.length})` }}
                  </button>
                </div>
              </div>

              <div v-else class="empty-state">
                <i class="fas fa-chart-line fa-3x mb-3"></i>
                <p class="text-muted">No scores yet</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Contests Management Section -->
      <div class="contests-section">
        <div class="section-card">
          <!-- Section Header with Tabs -->
          <div class="section-header bordered">
            <div class="d-flex align-items-center gap-3 flex-wrap">
              <h4 class="section-title mb-0">
                <i class="fas fa-trophy me-2"></i>Contests
              </h4>

              <!-- Tabs -->
              <div class="btn-group contest-tabs" role="group">
                <button type="button" class="btn btn-sm"
                  :class="activeTab === 'created' ? 'btn-primary' : 'btn-outline-primary'"
                  @click="switchTab('created')">
                  Your Contests ({{ dashboardData.created_contests?.length || 0 }})
                </button>
                <button type="button" class="btn btn-sm"
                  :class="activeTab === 'jury' ? 'btn-primary' : 'btn-outline-primary'" @click="switchTab('jury')">
                  Jury Contests ({{ dashboardData.jury_contests?.length || 0 }})
                </button>
              </div>
            </div>

            <!-- Search and Filter Controls -->
            <div class="controls-row mt-3">
              <div class="search-box">
                <i class="fas fa-search search-icon"></i>
                <input type="text" class="form-control search-input" placeholder="Search contests..."
                  v-model="searchQuery" @input="handleSearchInput" />
                <button v-if="searchQuery" class="btn-clear" @click="clearSearch" title="Clear search">
                  <i class="fas fa-times"></i>
                </button>
              </div>

              <div class="filter-buttons">
                <button v-for="status in ['all', 'current', 'upcoming', 'past']" :key="status" class="btn btn-sm"
                  :class="filterStatus === status ? 'btn-primary' : 'btn-outline-secondary'"
                  @click="filterStatus = status; currentPage = 1">
                  {{ status.charAt(0).toUpperCase() + status.slice(1) }}
                </button>
              </div>
            </div>
          </div>

          <!-- Contests Content -->
          <div class="section-body p-0">
            <!-- Created Contests Tab -->
            <div v-if="activeTab === 'created'">
              <div v-if="filteredCreatedContests.length > 0">
                <!-- Desktop Table View -->
                <div class="table-responsive d-none d-md-block">
                  <table class="table table-hover mb-0">
                    <thead>
                      <tr>
                        <th>Contest Name</th>
                        <th>Project</th>
                        <th>Status</th>
                        <th>Submissions</th>
                        <th>Created</th>
                        <th class="text-end">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="contest in paginatedCreatedContests" :key="contest.id" @click="viewContest(contest.id)"
                        class="table-row-clickable">
                        <td>
                          <div class="contest-name-cell">
                            <strong>{{ contest.name }}</strong>
                          </div>
                        </td>
                        <td>{{ contest.project_name || 'N/A' }}</td>
                        <td>
                          <span class="badge" :class="`badge-${getStatusBadgeColor(contest.status)}`">
                            {{ contest.status || 'Unknown' }}
                          </span>
                        </td>
                        <td>
                          <span class="submission-count">
                            <i class="fas fa-file-alt me-1"></i>
                            {{ contest.submission_count || 0 }}
                          </span>
                        </td>
                        <td>{{ formatDate(contest.created_at) }}</td>
                        <td class="text-end">
                          <button class="btn btn-sm btn-outline-primary" @click.stop="viewContest(contest.id)">
                            <i class="fas fa-eye me-1"></i>View
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <!-- Mobile Card View -->
                <div class="d-md-none">
                  <div v-for="contest in paginatedCreatedContests" :key="contest.id" class="contest-card"
                    @click="viewContest(contest.id)">
                    <div class="contest-card-header">
                      <strong>{{ contest.name }}</strong>
                      <span class="badge" :class="`badge-${getStatusBadgeColor(contest.status)}`">
                        {{ contest.status }}
                      </span>
                    </div>
                    <div class="contest-card-body">
                      <div class="contest-card-info">
                        <span><i class="fas fa-project-diagram me-1"></i>{{ contest.project_name || 'N/A' }}</span>
                        <span><i class="fas fa-file-alt me-1"></i>{{ contest.submission_count || 0 }} submissions</span>
                        <span><i class="fas fa-calendar me-1"></i>{{ formatDate(contest.created_at) }}</span>
                      </div>
                      <button class="btn btn-sm btn-primary w-100 mt-2" @click.stop="viewContest(contest.id)">
                        <i class="fas fa-eye me-1"></i>View Details
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Pagination -->
                <div v-if="filteredCreatedContests.length > itemsPerPage" class="pagination-wrapper">
                  <nav>
                    <ul class="pagination pagination-sm mb-0">
                      <li class="page-item" :class="{ disabled: currentPage === 1 }">
                        <button class="page-link" @click="currentPage--" :disabled="currentPage === 1">
                          <i class="fas fa-chevron-left"></i>
                        </button>
                      </li>

                      <li v-for="page in totalPagesCreated" :key="page" class="page-item"
                        :class="{ active: currentPage === page }">
                        <button class="page-link" @click="currentPage = page">
                          {{ page }}
                        </button>
                      </li>

                      <li class="page-item" :class="{ disabled: currentPage === totalPagesCreated }">
                        <button class="page-link" @click="currentPage++" :disabled="currentPage === totalPagesCreated">
                          <i class="fas fa-chevron-right"></i>
                        </button>
                      </li>
                    </ul>
                  </nav>

                  <div class="pagination-info">
                    Showing {{ (currentPage - 1) * itemsPerPage + 1 }} -
                    {{ Math.min(currentPage * itemsPerPage, filteredCreatedContests.length) }}
                    of {{ filteredCreatedContests.length }} contests
                  </div>
                </div>
              </div>

              <!-- Empty State -->
              <div v-else class="empty-state-large">
                <i class="fas fa-trophy fa-4x mb-3"></i>
                <h5>No Contests Found</h5>
                <p class="text-muted">
                  {{ searchQuery ? 'Try adjusting your search or filters' : 'Create your first contest to get started'
                  }}
                </p>
                <button v-if="!searchQuery && !filterStatus" class="btn btn-primary mt-2"
                  @click="$router.push('/create-contest')">
                  <i class="fas fa-plus me-2"></i>Create Contest
                </button>
              </div>
            </div>

            <!-- Jury Contests Tab -->
            <div v-if="activeTab === 'jury'">
              <div v-if="filteredJuryContests.length > 0">
                <!-- Desktop Table View -->
                <div class="table-responsive d-none d-md-block">
                  <table class="table table-hover mb-0">
                    <thead>
                      <tr>
                        <th>Contest Name</th>
                        <th>Project</th>
                        <th>Status</th>
                        <th>Pending Reviews</th>
                        <th class="text-end">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="contest in paginatedJuryContests" :key="contest.id" @click="viewContest(contest.id)"
                        class="table-row-clickable">
                        <td><strong>{{ contest.name }}</strong></td>
                        <td>{{ contest.project_name || 'N/A' }}</td>
                        <td>
                          <span class="badge" :class="`badge-${getStatusBadgeColor(contest.status)}`">
                            {{ contest.status }}
                          </span>
                        </td>
                        <td>
                          <span class="badge bg-warning">
                            {{ contest.pending_reviews || 0 }}
                          </span>
                        </td>
                        <td class="text-end">
                          <button class="btn btn-sm btn-outline-primary" @click.stop="viewContest(contest.id)">
                            <i class="fas fa-gavel me-1"></i>Review
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <!-- Mobile View -->
                <div class="d-md-none">
                  <div v-for="contest in paginatedJuryContests" :key="contest.id" class="contest-card"
                    @click="viewContest(contest.id)">
                    <div class="contest-card-header">
                      <strong>{{ contest.name }}</strong>
                      <span class="badge" :class="`badge-${getStatusBadgeColor(contest.status)}`">
                        {{ contest.status }}
                      </span>
                    </div>
                    <div class="contest-card-body">
                      <div class="contest-card-info">
                        <span><i class="fas fa-project-diagram me-1"></i>{{ contest.project_name || 'N/A' }}</span>
                        <span><i class="fas fa-clock me-1"></i>{{ contest.pending_reviews || 0 }} pending</span>
                      </div>
                      <button class="btn btn-sm btn-warning w-100 mt-2" @click.stop="viewContest(contest.id)">
                        <i class="fas fa-gavel me-1"></i>Review Submissions
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Pagination for Jury Contests -->
                <div v-if="filteredJuryContests.length > itemsPerPage" class="pagination-wrapper">
                  <nav>
                    <ul class="pagination pagination-sm mb-0">
                      <li class="page-item" :class="{ disabled: currentPage === 1 }">
                        <button class="page-link" @click="currentPage--" :disabled="currentPage === 1">
                          <i class="fas fa-chevron-left"></i>
                        </button>
                      </li>

                      <li v-for="page in totalPagesJury" :key="page" class="page-item"
                        :class="{ active: currentPage === page }">
                        <button class="page-link" @click="currentPage = page">
                          {{ page }}
                        </button>
                      </li>

                      <li class="page-item" :class="{ disabled: currentPage === totalPagesJury }">
                        <button class="page-link" @click="currentPage++" :disabled="currentPage === totalPagesJury">
                          <i class="fas fa-chevron-right"></i>
                        </button>
                      </li>
                    </ul>
                  </nav>

                  <div class="pagination-info">
                    Showing {{ (currentPage - 1) * itemsPerPage + 1 }} -
                    {{ Math.min(currentPage * itemsPerPage, filteredJuryContests.length) }}
                    of {{ filteredJuryContests.length }} contests
                  </div>
                </div>
              </div>

              <!-- Empty State -->
              <div v-else class="empty-state-large">
                <i class="fas fa-gavel fa-4x mb-3"></i>
                <h5>No Jury Assignments</h5>
                <p class="text-muted">
                  {{ searchQuery ? 'Try adjusting your search or filters' : `You haven't been assigned as a jury member
                  yet` }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="fas fa-exclamation-circle me-2"></i>
      {{ error }}
    </div>

    <!-- Submit Article Modal -->
    <SubmitArticleModal v-if="submittingToContestId" :contest-id="submittingToContestId"
      @submitted="handleArticleSubmitted" />

    <!-- Jury Feedback Modal -->
    <JuryFeedbackModal v-if="selectedSubmission" :submission="selectedSubmission" :reviewer-name="reviewerName"
      :loading-reviewer="loadingReviewer" />
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '../store'
import api from '../services/api'
import { showAlert } from '../utils/alerts'
import { slugify } from '../utils/slugify'
import SubmitArticleModal from '../components/SubmitArticleModal.vue'
import JuryFeedbackModal from '../components/JuryFeedbackModal.vue'

export default {
  name: 'Dashboard',
  components: {
    SubmitArticleModal,
    JuryFeedbackModal
  },
  setup() {
    const router = useRouter()
    const store = useStore()

    // State
    const dashboardData = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const submittingToContestId = ref(null)

    // Feedback modal state
    const selectedSubmission = ref(null)
    const reviewerName = ref('')
    const loadingReviewer = ref(false)

    // UI State
    const activeTab = ref('created')
    const searchQuery = ref('')
    const debouncedSearch = ref('')
    const filterStatus = ref('all')
    const currentPage = ref(1)
    const itemsPerPage = ref(10)
    const showAllSubmissions = ref(false)
    const showAllScores = ref(false)

    // Date formatters - memoized for performance
    const dateFormatterShort = new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric'
    })

    const dateFormatterFull = new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })

    // Debounce search input
    let searchTimeout = null
    const handleSearchInput = () => {
      if (searchTimeout) clearTimeout(searchTimeout)
      searchTimeout = setTimeout(() => {
        debouncedSearch.value = searchQuery.value
        currentPage.value = 1
      }, 300)
    }

    // Switch tab and reset state
    const switchTab = (tab) => {
      activeTab.value = tab
      currentPage.value = 1
      searchQuery.value = ''
      debouncedSearch.value = ''
      filterStatus.value = 'all'
    }

    // - Total submissions count
    const totalSubmissions = computed(() => {
      if (!dashboardData.value?.submissions_by_contest) return 0
      return dashboardData.value.submissions_by_contest.reduce((total, contest) => {
        return total + (contest.submissions?.length || 0)
      }, 0)
    })

    // - Filtered Created Contests
    const filteredCreatedContests = computed(() => {
      if (!dashboardData.value?.created_contests) return []

      let contests = [...dashboardData.value.created_contests]

      // Apply search filter with debounced value
      if (debouncedSearch.value) {
        const query = debouncedSearch.value.toLowerCase()
        contests = contests.filter(c =>
          c.name?.toLowerCase().includes(query) ||
          c.project_name?.toLowerCase().includes(query)
        )
      }

      // Apply status filter
      if (filterStatus.value !== 'all') {
        contests = contests.filter(c =>
          c.status?.toLowerCase() === filterStatus.value
        )
      }

      return contests
    })

    // - Filtered Jury Contests
    const filteredJuryContests = computed(() => {
      if (!dashboardData.value?.jury_contests) return []

      let contests = [...dashboardData.value.jury_contests]

      // Apply search filter with debounced value
      if (debouncedSearch.value) {
        const query = debouncedSearch.value.toLowerCase()
        contests = contests.filter(c =>
          c.name?.toLowerCase().includes(query) ||
          c.project_name?.toLowerCase().includes(query)
        )
      }

      // Apply status filter
      if (filterStatus.value !== 'all') {
        contests = contests.filter(c =>
          c.status?.toLowerCase() === filterStatus.value
        )
      }

      return contests
    })

    // - Paginated Created Contests
    const paginatedCreatedContests = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return filteredCreatedContests.value.slice(start, end)
    })

    // - Paginated Jury Contests
    const paginatedJuryContests = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return filteredJuryContests.value.slice(start, end)
    })

    // - Total Pages for Created Contests (always >= 1)
    const totalPagesCreated = computed(() => {
      const total = Math.ceil(filteredCreatedContests.value.length / itemsPerPage.value)
      return Math.max(1, total)
    })

    // - Total Pages for Jury Contests (always >= 1)
    const totalPagesJury = computed(() => {
      const total = Math.ceil(filteredJuryContests.value.length / itemsPerPage.value)
      return Math.max(1, total)
    })

    // Watch current page to ensure it's valid
    watch([filteredCreatedContests, filteredJuryContests], () => {
      const maxPage = activeTab.value === 'created' ? totalPagesCreated.value : totalPagesJury.value
      if (currentPage.value > maxPage) {
        currentPage.value = maxPage
      }
    })

    // Clear search function
    const clearSearch = () => {
      searchQuery.value = ''
      debouncedSearch.value = ''
      currentPage.value = 1
    }

    // Load dashboard data with validation
    const loadDashboard = async () => {
      loading.value = true
      error.value = null
      try {
        const data = await api.get('/user/dashboard')

        // Validate data structure
        if (!data || typeof data !== 'object') {
          throw new Error('Invalid dashboard data received')
        }

        // Ensure all arrays exist and are valid
        dashboardData.value = {
          total_score: data.total_score || 0,
          created_contests: Array.isArray(data.created_contests) ? data.created_contests : [],
          jury_contests: Array.isArray(data.jury_contests) ? data.jury_contests : [],
          submissions_by_contest: Array.isArray(data.submissions_by_contest) ? data.submissions_by_contest : [],
          contest_wise_scores: Array.isArray(data.contest_wise_scores) ? data.contest_wise_scores : []
        }
      } catch (err) {
        console.error('Dashboard load error:', err)
        error.value = err.message || 'Failed to load dashboard'
        showAlert(error.value, 'danger')

        // Set empty data structure to prevent errors
        dashboardData.value = {
          total_score: 0,
          created_contests: [],
          jury_contests: [],
          submissions_by_contest: [],
          contest_wise_scores: []
        }
      } finally {
        loading.value = false
      }
    }

    // Get status color for badges
    const getStatusColor = (status) => {
      const statusColors = {
        accepted: 'success',
        rejected: 'danger',
        pending: 'warning'
      }
      return statusColors[status?.toLowerCase()] || 'secondary'
    }

    // Get status badge color for contest status
    const getStatusBadgeColor = (status) => {
      const statusColors = {
        current: 'success',
        active: 'success',
        upcoming: 'warning',
        past: 'secondary',
        completed: 'info'
      }
      return statusColors[status?.toLowerCase()] || 'primary'
    }

    // Format date for display (memoized)
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      try {
        const date = new Date(dateString)
        if (isNaN(date.getTime())) return dateString
        return dateFormatterFull.format(date)
      } catch (e) {
        console.error('Date formatting error:', e)
        return dateString
      }
    }

    // Format date short (memoized)
    const formatDateShort = (dateString) => {
      if (!dateString) return ''
      try {
        const date = new Date(dateString)
        if (isNaN(date.getTime())) return dateString
        return dateFormatterShort.format(date)
      } catch (e) {
        console.error('Date formatting error:', e)
        return dateString
      }
    }

    // Handle submission click
    const handleSubmissionClick = (submission) => {
      if (submission?.reviewed_at) {
        openFeedbackModal(submission)
      }
    }

    // Fetch reviewer username with error handling
    const fetchReviewerName = async (reviewerId) => {
      if (!reviewerId) {
        reviewerName.value = 'Jury Member'
        return
      }

      loadingReviewer.value = true
      try {
        const userData = await api.get(`/user/${reviewerId}/username`)
        if (userData && userData.username) {
          reviewerName.value = userData.username
        } else {
          reviewerName.value = 'Jury Member'
        }
      } catch (err) {
        console.warn('Could not fetch reviewer name:', err)
        reviewerName.value = 'Jury Member'
      } finally {
        loadingReviewer.value = false
      }
    }

    // Open feedback modal 
    const openFeedbackModal = async (submission) => {
      if (!submission || !submission.reviewed_at) {
        showAlert('This submission has not been reviewed yet', 'info')
        return
      }

      selectedSubmission.value = submission

      if (submission.reviewed_by) {
        await fetchReviewerName(submission.reviewed_by)
      } else {
        reviewerName.value = 'Jury Member'
      }

      await nextTick()

      const modalEl = document.getElementById('juryFeedbackModal')
      if (!modalEl) {
        console.error('JuryFeedbackModal DOM not found')
        showAlert('Unable to open feedback modal', 'danger')
        return
      }

      // Check if Bootstrap is loaded
      if (typeof window.bootstrap === 'undefined') {
        console.error('Bootstrap is not loaded')
        showAlert('Unable to open feedback modal', 'danger')
        return
      }

      try {
        const modal = new window.bootstrap.Modal(modalEl)
        modal.show()
      } catch (error) {
        console.error('Error opening modal:', error)
        showAlert('Error opening feedback modal', 'danger')
      }
    }

    const viewContest = async (contestId) => {
      if (!contestId) {
        showAlert('Invalid contest ID', 'danger')
        return
      }

      let contestData = null

      // Try to find contest in dashboard data
      if (dashboardData.value?.created_contests) {
        contestData = dashboardData.value.created_contests.find(c => c.id === contestId)
      }

      if (!contestData && dashboardData.value?.jury_contests) {
        contestData = dashboardData.value.jury_contests.find(c => c.id === contestId)
      }

      // Try store data
      if (!contestData) {
        try {
          const allContests = store.getContestsByCategory('current')
            .concat(store.getContestsByCategory('upcoming'))
            .concat(store.getContestsByCategory('past'))
          contestData = allContests.find(c => c.id === contestId)
        } catch (err) {
          console.error('Error getting contests from store:', err)
        }
      }

      // Fetch from API if not found
      if (!contestData) {
        try {
          const contest = await api.get(`/contest/${contestId}`)
          if (contest && contest.name) {
            const contestSlug = slugify(contest.name)
            await router.push({ name: 'ContestView', params: { name: contestSlug } })
            return
          } else {
            throw new Error('Invalid contest data')
          }
        } catch (error) {
          console.error('Error loading contest:', error)
          showAlert('Contest not found or failed to load', 'danger')
          return
        }
      }

      // Navigate to contest
      if (contestData && contestData.name) {
        try {
          const contestSlug = slugify(contestData.name)
          await router.push({ name: 'ContestView', params: { name: contestSlug } })
        } catch (error) {
          console.error('Navigation error:', error)
          showAlert('Failed to navigate to contest', 'danger')
        }
      } else {
        showAlert('Contest not found', 'danger')
      }
    }

    // Handle submit article with proper DOM waiting
    const handleSubmitArticle = async (contestId) => {
      if (!store.isAuthenticated) {
        showAlert('Please login to submit an article', 'warning')
        return
      }

      submittingToContestId.value = contestId

      // Wait for DOM update
      await nextTick()

      const modalElement = document.getElementById('submitArticleModal')
      if (!modalElement) {
        console.error('Submit article modal not found')
        showAlert('Unable to open submission form', 'danger')
        submittingToContestId.value = null
        return
      }

      // Check if Bootstrap is loaded
      if (typeof window.bootstrap === 'undefined') {
        console.error('Bootstrap not loaded')
        showAlert('Unable to open submission form', 'danger')
        submittingToContestId.value = null
        return
      }

      try {
        const modal = new window.bootstrap.Modal(modalElement)
        modal.show()
      } catch (error) {
        console.error('Error opening modal:', error)
        showAlert('Error opening submission form', 'danger')
        submittingToContestId.value = null
      }
    }

    // Handle article submitted
    const handleArticleSubmitted = () => {
      submittingToContestId.value = null
      selectedSubmission.value = null
      loadDashboard()
    }

    // Cleanup on unmount
    onUnmounted(() => {
      // Clear search timeout
      if (searchTimeout) {
        clearTimeout(searchTimeout)
      }

      // Cleanup any open modals
      const modals = document.querySelectorAll('.modal.show')
      modals.forEach(modalEl => {
        try {
          const modal = window.bootstrap?.Modal?.getInstance(modalEl)
          if (modal) {
            modal.hide()
            modal.dispose()
          }
        } catch (err) {
          console.error('Error disposing modal:', err)
        }
      })
    })

    // Load data on mount
    onMounted(() => {
      loadDashboard()
    })

    return {
      dashboardData,
      loading,
      error,
      submittingToContestId,
      selectedSubmission,
      reviewerName,
      loadingReviewer,
      activeTab,
      searchQuery,
      debouncedSearch,
      filterStatus,
      currentPage,
      itemsPerPage,
      showAllSubmissions,
      showAllScores,
      totalSubmissions,
      filteredCreatedContests,
      filteredJuryContests,
      paginatedCreatedContests,
      paginatedJuryContests,
      totalPagesCreated,
      totalPagesJury,
      switchTab,
      clearSearch,
      handleSearchInput,
      getStatusColor,
      getStatusBadgeColor,
      formatDate,
      formatDateShort,
      viewContest,
      handleSubmitArticle,
      handleArticleSubmitted,
      handleSubmissionClick,
      openFeedbackModal
    }
  }
}
</script>

<style scoped>
:root {
  --wiki-primary: #006699;
  --wiki-primary-hover: #004d73;
  --wiki-primary-light: rgba(0, 102, 153, 0.1);
  --wiki-success: #28a745;
  --wiki-warning: #ffc107;
  --wiki-danger: #dc3545;
  --wiki-dark: #202122;
  --wiki-text: #202122;
  --wiki-text-muted: #6c757d;
  --wiki-border: #e5e7eb;
  --wiki-light-bg: #f8f9fa;
  --wiki-hover-bg: rgba(0, 102, 153, 0.05);
  --wiki-card-bg: #ffffff;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
  --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.12);
}

[data-theme="dark"] {
  --wiki-primary: #5db8e6;
  --wiki-primary-hover: #7cc5ea;
  --wiki-primary-light: rgba(93, 184, 230, 0.15);
  --wiki-success: #4ade80;
  --wiki-warning: #fbbf24;
  --wiki-danger: #f87171;
  --wiki-dark: #ffffff;
  --wiki-text: #e0e0e0;
  --wiki-text-muted: #a0a0a0;
  --wiki-border: #404040;
  --wiki-light-bg: #1f1f1f;
  --wiki-hover-bg: rgba(93, 184, 230, 0.1);
  --wiki-card-bg: #2a2a2a;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.5);
}

.dashboard-header {
  margin-bottom: 2rem;
}

.page-header {
  font-size: 2rem;
  font-weight: 700;
  color: var(--wiki-dark);
  margin-bottom: 0.5rem;
  letter-spacing: -0.02em;
}

.dashboard-subtitle {
  color: var(--wiki-text-muted);
  font-size: 1rem;
  margin-bottom: 0;
}

.stat-card {
  background: var(--wiki-card-bg);
  border: 1px solid var(--wiki-border);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
  will-change: transform;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
}

.stat-card-primary::before {
  background: var(--wiki-primary);
}

.stat-card-success::before {
  background: var(--wiki-success);
}

.stat-card-warning::before {
  background: var(--wiki-warning);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.stat-card-primary .stat-icon {
  background: var(--wiki-primary-light);
  color: var(--wiki-primary);
}

.stat-card-success .stat-icon {
  background: rgba(40, 167, 69, 0.1);
  color: var(--wiki-success);
}

.stat-card-warning .stat-icon {
  background: rgba(255, 193, 7, 0.1);
  color: var(--wiki-warning);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--wiki-dark);
  margin: 0;
  line-height: 1;
}

.stat-label {
  color: var(--wiki-text-muted);
  font-size: 0.875rem;
  font-weight: 500;
  margin: 0.25rem 0 0 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-card {
  background: var(--wiki-card-bg);
  border: 1px solid var(--wiki-border);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.section-header {
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.section-header.bordered {
  border-bottom: 1px solid var(--wiki-border);
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--wiki-dark);
  margin: 0;
  display: flex;
  align-items: center;
}

.section-body {
  padding: 1.5rem;
}

.section-body.p-0 {
  padding: 0;
}

.controls-row {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  width: 100%;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--wiki-text-muted);
  pointer-events: none;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding: 0.5rem 3rem 0.5rem 2.5rem;
  border: 1px solid var(--wiki-border);
  border-radius: 8px;
  background: var(--wiki-light-bg);
  color: var(--wiki-text);
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--wiki-primary);
  background: var(--wiki-card-bg);
  box-shadow: 0 0 0 3px var(--wiki-primary-light);
}

.search-input::placeholder {
  color: var(--wiki-text-muted);
}

.btn-clear {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 28px;
  background: var(--wiki-danger);
  border: none;
  color: white;
  padding: 0;
  cursor: pointer;
  border-radius: 50%;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.btn-clear:hover {
  background: var(--wiki-danger);
  transform: translateY(-50%) scale(1.1);
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
}

.btn-clear:active {
  transform: translateY(-50%) scale(0.95);
}

.btn-clear i {
  font-size: 0.75rem;
}

[data-theme="dark"] .btn-clear {
  background: #f87171;
}

[data-theme="dark"] .btn-clear:hover {
  background: #ef4444;
}

.filter-buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-buttons .btn {
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
}

.contest-tabs {
  border-radius: 8px;
  overflow: hidden;
}

.contest-tabs .btn {
  border-radius: 0;
  font-weight: 500;
  font-size: 0.875rem;
  padding: 0.5rem 1rem;
}

.submissions-container {
  max-height: 450px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 0.5rem;
  scrollbar-width: thin;
  scrollbar-color: var(--wiki-primary) var(--wiki-light-bg);
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
}

.submissions-container::-webkit-scrollbar {
  width: 6px;
}

.submissions-container::-webkit-scrollbar-track {
  background: var(--wiki-light-bg);
  border-radius: 10px;
}

.submissions-container::-webkit-scrollbar-thumb {
  background: var(--wiki-primary);
  border-radius: 10px;
}

.submissions-container::-webkit-scrollbar-thumb:hover {
  background: var(--wiki-primary-hover);
}

.submissions-container.expanded {
  max-height: 600px;
}

.submission-group {
  margin-bottom: 1.5rem;
}

.submission-group:last-child {
  margin-bottom: 0.5rem;
}

.contest-name-badge {
  background: var(--wiki-primary-light);
  color: var(--wiki-primary);
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.875rem;
  margin-bottom: 0.75rem;
  display: inline-block;
  position: sticky;
  top: 0;
  z-index: 5;
  backdrop-filter: blur(10px);
}

.submission-item {
  background: var(--wiki-light-bg);
  border: 1px solid var(--wiki-border);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  transition: all 0.2s ease;
}

.submission-item.submission-clickable {
  cursor: pointer;
  will-change: transform, background-color;
}

.submission-item.submission-clickable:hover {
  background: var(--wiki-hover-bg);
  border-color: var(--wiki-primary);
  transform: translateX(4px);
}

.submission-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.submission-title {
  font-weight: 500;
  color: var(--wiki-dark);
  font-size: 0.9375rem;
}

.submission-date {
  font-size: 0.8125rem;
  color: var(--wiki-text-muted);
}

.submission-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-icon {
  background: none;
  border: none;
  padding: 0.5rem;
  color: var(--wiki-primary);
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: var(--wiki-primary-light);
  transform: scale(1.1);
}

.btn-feedback {
  color: var(--wiki-primary);
}

.scores-container {
  max-height: 450px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 0.5rem;
  scrollbar-width: thin;
  scrollbar-color: var(--wiki-success) var(--wiki-light-bg);
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
}

.scores-container::-webkit-scrollbar {
  width: 6px;
}

.scores-container::-webkit-scrollbar-track {
  background: var(--wiki-light-bg);
  border-radius: 10px;
}

.scores-container::-webkit-scrollbar-thumb {
  background: var(--wiki-success);
  border-radius: 10px;
}

.scores-container::-webkit-scrollbar-thumb:hover {
  background: #218838;
}

.scores-container.expanded {
  max-height: 600px;
}

.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--wiki-light-bg);
  border: 1px solid var(--wiki-border);
  border-radius: 8px;
  margin-bottom: 0.5rem;
  transition: all 0.2s ease;
}

.score-item:last-child {
  margin-bottom: 0;
}

.score-item:hover {
  background: var(--wiki-hover-bg);
  border-color: var(--wiki-primary);
}

.score-contest {
  font-weight: 500;
  color: var(--wiki-dark);
  font-size: 0.9375rem;
}

.score-points {
  font-weight: 600;
  color: var(--wiki-primary);
  background: var(--wiki-primary-light);
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
}

.badge {
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-weight: 500;
  font-size: 0.8125rem;
  text-transform: capitalize;
}

.badge-primary {
  background: var(--wiki-primary);
  color: white;
}

.badge-success {
  background: var(--wiki-success);
  color: white;
}

.badge-warning {
  background: var(--wiki-warning);
  color: #000;
}

.badge-danger {
  background: var(--wiki-danger);
  color: white;
}

.badge-secondary {
  background: var(--wiki-text-muted);
  color: white;
}

.badge-info {
  background: #17a2b8;
  color: white;
}

.table {
  margin: 0;
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.table thead th {
  background: var(--wiki-light-bg);
  border-bottom: 2px solid var(--wiki-border);
  padding: 1rem 1.5rem;
  font-weight: 600;
  font-size: 0.8125rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--wiki-text-muted);
  position: sticky;
  top: 0;
  z-index: 10;
}

.table tbody td {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--wiki-border);
  color: var(--wiki-text);
  vertical-align: middle;
}

.table tbody tr {
  transition: background-color 0.2s ease;
}

.table-row-clickable {
  cursor: pointer;
}

.table-row-clickable:hover {
  background: var(--wiki-hover-bg);
}

.table tbody tr:last-child td {
  border-bottom: none;
}

.contest-name-cell strong {
  color: var(--wiki-dark);
  font-weight: 600;
}

.submission-count {
  color: var(--wiki-text-muted);
  font-size: 0.9375rem;
}

.contest-card {
  background: var(--wiki-card-bg);
  border: 1px solid var(--wiki-border);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  will-change: transform, box-shadow;
}

.contest-card:hover {
  border-color: var(--wiki-primary);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.contest-card-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  gap: 1rem;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--wiki-border);
}

.contest-card-header strong {
  color: var(--wiki-dark);
  font-weight: 600;
  font-size: 1rem;
  flex: 1;
}

.contest-card-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.contest-card-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.contest-card-info span {
  color: var(--wiki-text-muted);
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}

.contest-card-info i {
  color: var(--wiki-primary);
  margin-right: 0.5rem;
}

.pagination-wrapper {
  padding: 1.5rem;
  border-top: 1px solid var(--wiki-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  background: var(--wiki-light-bg);
}

.pagination {
  margin: 0;
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
  justify-content: center;
}

.page-item .page-link {
  border: 1px solid var(--wiki-border);
  color: var(--wiki-text);
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  transition: all 0.2s ease;
  background: var(--wiki-card-bg);
  min-width: 40px;
  text-align: center;
}

.page-item.active .page-link {
  background: var(--wiki-primary);
  border-color: var(--wiki-primary);
  color: white;
}

.page-item.disabled .page-link {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-item:not(.disabled) .page-link:hover {
  background: var(--wiki-primary-light);
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
}

.pagination-info {
  color: var(--wiki-text-muted);
  font-size: 0.875rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
}

.empty-state i {
  color: var(--wiki-text-muted);
  opacity: 0.5;
}

.empty-state p {
  color: var(--wiki-text-muted);
  margin: 0;
}

.empty-state-large {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-state-large i {
  color: var(--wiki-text-muted);
  opacity: 0.4;
}

.empty-state-large h5 {
  color: var(--wiki-dark);
  font-weight: 600;
  margin: 1rem 0 0.5rem 0;
}

.empty-state-large p {
  color: var(--wiki-text-muted);
  margin-bottom: 0;
}

.btn {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.btn-primary {
  background: var(--wiki-primary);
  border-color: var(--wiki-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--wiki-primary-hover);
  border-color: var(--wiki-primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-outline-primary {
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
  background: transparent;
}

.btn-outline-primary:hover {
  background: var(--wiki-primary);
  color: white;
}

.btn-outline-secondary {
  border-color: var(--wiki-border);
  color: var(--wiki-text-muted);
  background: transparent;
}

.btn-outline-secondary:hover {
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
  background: var(--wiki-primary-light);
}

.btn-warning {
  background: var(--wiki-warning);
  border-color: var(--wiki-warning);
  color: #000;
}

.btn-warning:hover {
  background: #e0a800;
  border-color: #e0a800;
}

.spinner-border.text-primary {
  width: 3rem;
  height: 3rem;
  border-width: 0.3em;
  color: var(--wiki-primary);
}

@media (max-width: 992px) {
  .controls-row {
    flex-direction: column;
  }

  .search-box {
    width: 100%;
    min-width: 100%;
  }

  .filter-buttons {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    margin-bottom: 1.5rem;
  }

  .page-header {
    font-size: 1.75rem;
  }

  .dashboard-subtitle {
    font-size: 0.9375rem;
  }

  .stat-card {
    padding: 1.25rem;
  }

  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 1.25rem;
  }

  .stat-value {
    font-size: 1.75rem;
  }

  .section-header {
    padding: 1rem;
  }

  .section-body {
    padding: 1rem;
  }

  .submission-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .submission-info {
    width: 100%;
  }

  .submission-actions {
    width: 100%;
    justify-content: space-between;
    flex-direction: row;
  }

  .contest-name-badge {
    display: block;
    width: fit-content;
    margin-bottom: 0.75rem;
  }

  .submission-group {
    margin-bottom: 1.25rem;
  }

  .pagination-wrapper {
    flex-direction: column;
    padding: 1rem;
    gap: 1rem;
  }

  .pagination {
    width: 100%;
    justify-content: center;
    overflow-x: auto;
    padding: 0.5rem 0;
  }

  .pagination-info {
    order: -1;
    text-align: center;
    width: 100%;
  }

  .page-item .page-link {
    padding: 0.4rem 0.6rem;
    min-width: 36px;
    font-size: 0.875rem;
  }
}

@media (max-width: 576px) {
  .stat-card {
    flex-direction: column;
    text-align: center;
  }

  .stat-icon {
    margin: 0 auto;
  }

  .contest-tabs {
    width: 100%;
  }

  .contest-tabs .btn {
    flex: 1;
    font-size: 0.8125rem;
    padding: 0.5rem;
  }

  .submission-item {
    padding: 1rem;
  }

  .submission-title {
    font-size: 0.9rem;
    line-height: 1.4;
  }

  .submission-date {
    font-size: 0.75rem;
  }

  .contest-name-badge {
    width: 100%;
    text-align: center;
    display: block;
  }

  .score-item {
    padding: 0.875rem;
    flex-wrap: wrap;
  }

  .score-contest {
    font-size: 0.875rem;
    flex: 1;
    min-width: 100%;
    margin-bottom: 0.5rem;
  }

  .score-points {
    width: 100%;
    text-align: center;
  }
}
</style>