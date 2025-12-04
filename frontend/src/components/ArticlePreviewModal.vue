<template>
  <div class="modal fade" id="articlePreviewModal" tabindex="-1">
    <div class="modal-dialog modal-xl modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-eye me-2"></i>Article Preview: {{ actualArticleTitle }}
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <!-- Loading state -->
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading article...</span>
            </div>
            <p class="mt-3 text-muted">Loading article preview...</p>
          </div>
          
          <!-- Error state -->
          <div v-else-if="error" class="alert alert-danger">
            <i class="fas fa-exclamation-circle me-2"></i>
            {{ error }}
            <div class="mt-3">
              <a 
                :href="articleUrl" 
                target="_blank" 
                rel="noopener noreferrer"
                class="btn btn-sm btn-outline-primary"
              >
                <i class="fas fa-external-link-alt me-2"></i>Open Article in New Tab
              </a>
            </div>
          </div>
          
          <!-- MediaWiki content preview -->
          <div v-else-if="mediaWikiContent" class="article-preview-container mediawiki-content">
            <div class="mediawiki-preview" v-html="mediaWikiContent"></div>
          </div>
          
          <!-- Article preview iframe (for non-MediaWiki pages) -->
          <div v-else class="article-preview-container">
            <iframe
              :src="articleUrl"
              class="article-preview-iframe"
              frameborder="0"
              allowfullscreen
              @load="handleIframeLoad"
              @error="handleIframeError"
            ></iframe>
          </div>
        </div>
        <div class="modal-footer">
          <a 
            :href="articleUrl" 
            target="_blank" 
            rel="noopener noreferrer"
            class="btn btn-outline-primary"
          >
            <i class="fas fa-external-link-alt me-2"></i>Open in New Tab
          </a>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            <i class="fas fa-times me-2"></i>Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onUnmounted } from 'vue'

export default {
  name: 'ArticlePreviewModal',
  props: {
    articleUrl: {
      type: String,
      default: ''
    },
    articleTitle: {
      type: String,
      default: 'Article'
    }
  },
  setup(props) {
    const loading = ref(true)
    const error = ref('')
    const mediaWikiContent = ref('')
    const actualArticleTitle = ref(props.articleTitle || 'Article')
    let loadTimeout = null
    let iframeCheckInterval = null

    // Check if URL is a MediaWiki page
    const isMediaWikiUrl = (url) => {
      if (!url) return false
      try {
        const urlObj = new URL(url)
        // Check for common MediaWiki patterns
        return (
          urlObj.hostname.includes('wiki') ||
          urlObj.pathname.includes('/wiki/') ||
          urlObj.pathname.includes('/w/index.php') ||
          urlObj.searchParams.has('title')
        )
      } catch (e) {
        return false
      }
    }

    // Extract MediaWiki API base URL from article URL
    const getMediaWikiApiUrl = (articleUrl) => {
      try {
        const urlObj = new URL(articleUrl)
        // Get the base URL (protocol + hostname)
        const baseUrl = `${urlObj.protocol}//${urlObj.hostname}`
        
        // Extract page title from URL
        let pageTitle = ''
        if (urlObj.pathname.includes('/wiki/')) {
          // Standard MediaWiki URL format: /wiki/Page_Title
          pageTitle = decodeURIComponent(urlObj.pathname.split('/wiki/')[1])
        } else if (urlObj.searchParams.has('title')) {
          // Old-style URL: /w/index.php?title=Page_Title
          pageTitle = urlObj.searchParams.get('title')
        } else {
          // Try to extract from pathname
          const parts = urlObj.pathname.split('/')
          pageTitle = parts[parts.length - 1] || ''
        }
        
        // Build API URL
        const apiUrl = `${baseUrl}/w/api.php?action=parse&page=${encodeURIComponent(pageTitle)}&format=json&origin=*`
        return { apiUrl, pageTitle }
      } catch (e) {
        return null
      }
    }

    // Fetch MediaWiki content via API
    const fetchMediaWikiContent = async (articleUrl) => {
      try {
        const apiInfo = getMediaWikiApiUrl(articleUrl)
        if (!apiInfo || !apiInfo.pageTitle) {
          throw new Error('Could not parse MediaWiki URL or extract page title')
        }

        // Fetch content from MediaWiki API with timeout
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 8000) // 8 second timeout

        try {
          const response = await fetch(apiInfo.apiUrl, {
            signal: controller.signal,
            headers: {
              'Accept': 'application/json'
            }
          })
          
          clearTimeout(timeoutId)
          
          if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`)
          }

          const data = await response.json()
          
          if (data.error) {
            throw new Error(data.error.info || `API error: ${data.error.code || 'Unknown error'}`)
          }

          if (data.parse && data.parse.text && data.parse.text['*']) {
            // Get the HTML content
            let htmlContent = data.parse.text['*']
            
            // Get the actual page title from API response (more accurate than URL)
            const actualPageTitle = data.parse.title || data.parse.displaytitle || null
            
            // Make links absolute (convert relative links to absolute)
            const urlObj = new URL(articleUrl)
            const baseUrl = `${urlObj.protocol}//${urlObj.hostname}`
            
            // Replace relative links with absolute links
            htmlContent = htmlContent.replace(/href="\/wiki\//g, `href="${baseUrl}/wiki/`)
            htmlContent = htmlContent.replace(/href="\/w\//g, `href="${baseUrl}/w/`)
            htmlContent = htmlContent.replace(/src="\/wiki\//g, `src="${baseUrl}/wiki/`)
            htmlContent = htmlContent.replace(/src="\/w\//g, `src="${baseUrl}/w/`)
            
            // Return both content and actual page title
            return { htmlContent, actualPageTitle }
          } else {
            throw new Error('No content found in API response')
          }
        } catch (fetchErr) {
          clearTimeout(timeoutId)
          if (fetchErr.name === 'AbortError') {
            throw new Error('Request timed out. The MediaWiki API may be slow or unavailable.')
          }
          throw fetchErr
        }
      } catch (err) {
        console.error('Error fetching MediaWiki content:', err)
        throw err
      }
    }

    // Load article preview
    const loadPreview = async () => {
      if (!props.articleUrl) return

      loading.value = true
      error.value = ''
      mediaWikiContent.value = ''
      // Reset title to prop value (will be updated if API provides better title)
      actualArticleTitle.value = props.articleTitle || 'Article'

      // Clear any existing timeouts
      if (loadTimeout) {
        clearTimeout(loadTimeout)
      }

      // Check if it's a MediaWiki URL
      if (isMediaWikiUrl(props.articleUrl)) {
        try {
          // Try to fetch via MediaWiki API
          const result = await fetchMediaWikiContent(props.articleUrl)
          
          // Update content and title
          if (typeof result === 'object' && result.htmlContent) {
            mediaWikiContent.value = result.htmlContent
            // Use actual page title from API if available, otherwise use prop
            if (result.actualPageTitle) {
              actualArticleTitle.value = result.actualPageTitle
            }
          } else {
            // Fallback for old format (string)
            mediaWikiContent.value = result
          }
          
          loading.value = false
        } catch (err) {
          console.error('MediaWiki API fetch failed:', err)
          // If API fails, show error message
          loading.value = false
          error.value = 'Unable to load MediaWiki article preview. This may be due to CORS restrictions or the page not being accessible. Please use "Open in New Tab" to view the article.'
        }
      } else {
        // For non-MediaWiki pages, use iframe with timeout
        loadTimeout = setTimeout(() => {
          if (loading.value) {
            loading.value = false
            error.value = 'The article preview is taking too long to load. The page may block embedding. Please use "Open in New Tab" to view the article.'
          }
        }, 10000) // 10 second timeout
      }
    }

    // Handle iframe load event
    const handleIframeLoad = () => {
      if (loadTimeout) {
        clearTimeout(loadTimeout)
        loadTimeout = null
      }
      loading.value = false
      error.value = ''
    }

    // Handle iframe error event
    const handleIframeError = () => {
      if (loadTimeout) {
        clearTimeout(loadTimeout)
        loadTimeout = null
      }
      loading.value = false
      error.value = 'Failed to load article preview. The article may not be accessible or may have security restrictions that prevent embedding.'
    }

    // Watch for URL changes
    watch(() => props.articleUrl, (newUrl) => {
      if (newUrl) {
        loadPreview()
      }
    }, { immediate: true })

    // Watch for title changes
    watch(() => props.articleTitle, (newTitle) => {
      if (newTitle) {
        actualArticleTitle.value = newTitle
      }
    }, { immediate: true })

    // Cleanup on unmount
    onUnmounted(() => {
      if (loadTimeout) {
        clearTimeout(loadTimeout)
      }
      if (iframeCheckInterval) {
        clearInterval(iframeCheckInterval)
      }
    })

    return {
      loading,
      error,
      mediaWikiContent,
      actualArticleTitle,
      handleIframeLoad,
      handleIframeError
    }
  }
}
</script>

<style scoped>
/* Article Preview Modal Styling with Wikipedia Colors */

/* Modal header - solid color, no gradient - matches theme */
.modal-header {
  background-color: var(--wiki-primary);
  color: white;
  border-bottom: none;
  padding: 1.25rem 1.5rem;
  transition: background-color 0.2s ease;
}

.modal-title {
  font-weight: 600;
  font-size: 1.5rem;
  color: white;
}

.modal-header .btn-close {
  filter: invert(1) brightness(1.2);
  opacity: 0.9;
  transition: opacity 0.2s ease;
}

.modal-header .btn-close:hover {
  opacity: 1;
}

/* Modal body - matches theme */
.modal-body {
  padding: 0;
  background-color: var(--wiki-modal-bg);
  color: var(--wiki-text);
  transition: background-color 0.3s ease, color 0.3s ease;
  min-height: 500px;
  display: flex;
  flex-direction: column;
}

/* Article preview container */
.article-preview-container {
  width: 100%;
  height: 100%;
  min-height: 500px;
  position: relative;
  overflow: hidden;
}

/* MediaWiki content preview */
.mediawiki-content {
  overflow-y: auto;
  padding: 1.5rem;
  background-color: white;
}

[data-theme="dark"] .mediawiki-content {
  background-color: #1a1a1a;
}

.mediawiki-preview {
  max-width: 100%;
  color: var(--wiki-text);
  line-height: 1.6;
}

/* Style MediaWiki content to match Wikipedia appearance */
.mediawiki-preview :deep(h1),
.mediawiki-preview :deep(h2),
.mediawiki-preview :deep(h3),
.mediawiki-preview :deep(h4),
.mediawiki-preview :deep(h5),
.mediawiki-preview :deep(h6) {
  color: var(--wiki-dark);
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  border-bottom: 1px solid var(--wiki-border);
  padding-bottom: 0.5rem;
}

[data-theme="dark"] .mediawiki-preview :deep(h1),
[data-theme="dark"] .mediawiki-preview :deep(h2),
[data-theme="dark"] .mediawiki-preview :deep(h3),
[data-theme="dark"] .mediawiki-preview :deep(h4),
[data-theme="dark"] .mediawiki-preview :deep(h5),
[data-theme="dark"] .mediawiki-preview :deep(h6) {
  color: #ffffff;
  border-bottom-color: #555;
}

.mediawiki-preview :deep(p) {
  margin-bottom: 1rem;
  color: var(--wiki-text);
}

.mediawiki-preview :deep(a) {
  color: var(--wiki-primary);
  text-decoration: none;
}

.mediawiki-preview :deep(a:hover) {
  text-decoration: underline;
}

.mediawiki-preview :deep(img) {
  max-width: 100%;
  height: auto;
  margin: 1rem 0;
}

.mediawiki-preview :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.mediawiki-preview :deep(table th),
.mediawiki-preview :deep(table td) {
  border: 1px solid var(--wiki-border);
  padding: 0.5rem;
}

.mediawiki-preview :deep(table th) {
  background-color: var(--wiki-hover-bg);
  font-weight: 600;
}

.mediawiki-preview :deep(ul),
.mediawiki-preview :deep(ol) {
  margin: 1rem 0;
  padding-left: 2rem;
}

.mediawiki-preview :deep(li) {
  margin-bottom: 0.5rem;
}

/* Article preview iframe - full size */
.article-preview-iframe {
  width: 100%;
  height: 70vh;
  min-height: 500px;
  border: none;
  background-color: white;
  transition: opacity 0.3s ease;
}

/* Dark mode iframe background */
[data-theme="dark"] .article-preview-iframe {
  background-color: #1a1a1a;
}

/* Loading spinner */
.spinner-border.text-primary {
  color: var(--wiki-primary) !important;
  width: 3rem;
  height: 3rem;
  border-width: 0.3em;
}

/* Alert styling */
.alert-danger {
  background-color: rgba(153, 0, 0, 0.1);
  border: 1px solid var(--wiki-danger);
  border-left: 4px solid var(--wiki-danger);
  color: var(--wiki-danger);
  border-radius: 0.5rem;
  margin: 1.5rem;
  padding: 1rem;
  transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}

.alert-danger .btn {
  margin-top: 0.5rem;
}

[data-theme="dark"] .alert-danger {
  background-color: rgba(230, 128, 128, 0.2);
}

/* Button styling */
.btn-outline-primary {
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-outline-primary:hover {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.3);
}

.btn-secondary {
  background-color: var(--wiki-text-muted);
  border-color: var(--wiki-text-muted);
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background-color: var(--wiki-text-muted);
  border-color: var(--wiki-text-muted);
}

[data-theme="dark"] .btn-secondary {
  background-color: #5a6268;
  border-color: #5a6268;
}

[data-theme="dark"] .btn-secondary:hover {
  background-color: #6c757d;
  border-color: #6c757d;
}

/* Modal footer - matches theme */
.modal-footer {
  border-top: 1px solid var(--wiki-border);
  padding: 1rem 1.5rem;
  background-color: var(--wiki-modal-bg);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

/* Modal content - ensures proper background */
.modal-content {
  background-color: var(--wiki-modal-bg);
  border-color: var(--wiki-border);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

/* Icon styling */
.fas {
  transition: transform 0.2s ease;
}

.btn:hover .fas {
  transform: scale(1.1);
}

/* Text muted */
.text-muted {
  color: var(--wiki-text-muted);
  transition: color 0.3s ease;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .modal-dialog {
    margin: 0.5rem;
  }
  
  .article-preview-iframe {
    height: 60vh;
    min-height: 400px;
  }
  
  .modal-body {
    min-height: 400px;
  }
  
  .article-preview-container {
    min-height: 400px;
  }
}
</style>
