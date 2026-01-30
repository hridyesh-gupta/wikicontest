/**
 * Outreach Dashboard API Service
 * 
 * This module provides functions to interact with Wikimedia's Outreach Dashboard API
 * from the frontend. It handles fetching course data and parsing URLs.
 */

/**
 * Parse an Outreach Dashboard URL to extract components
 * 
 * @param {string} url - The Outreach Dashboard URL
 * @returns {Object} Object with school, course_slug, and valid flag
 */
export function parseOutreachUrl(url) {
  if (!url || typeof url !== 'string') {
    return { school: null, course_slug: null, valid: false }
  }

  url = url.trim()

  try {
    const urlObj = new URL(url)
    
    // Check if it's an Outreach Dashboard URL
    if (!urlObj.hostname.includes('outreachdashboard.wmflabs.org')) {
      return { school: null, course_slug: null, valid: false }
    }

    // Extract path components
    // Pattern: /courses/{school}/{course_slug} or /courses/{school}/{course_slug}/course.json
    const pathMatch = urlObj.pathname.match(/^\/courses\/([^/]+)\/([^/]+)(?:\/course\.json)?\/?$/)
    
    if (pathMatch) {
      return {
        school: pathMatch[1],
        course_slug: pathMatch[2],
        valid: true
      }
    }
  } catch (e) {
    // Invalid URL format
    return { school: null, course_slug: null, valid: false }
  }

  return { school: null, course_slug: null, valid: false }
}

/**
 * Validate an Outreach Dashboard URL format
 * 
 * @param {string} url - The URL to validate
 * @returns {Object} Object with valid flag and optional error message
 */
export function validateOutreachUrl(url) {
  if (!url || typeof url !== 'string') {
    return { valid: false, error: 'URL is required' }
  }

  url = url.trim()

  if (!url) {
    return { valid: false, error: 'URL cannot be empty' }
  }

  // Check basic URL format
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    return { valid: false, error: 'URL must start with http:// or https://' }
  }

  // Parse the URL
  const parsed = parseOutreachUrl(url)

  if (!parsed.valid) {
    return {
      valid: false,
      error: 'Invalid Outreach Dashboard URL format. Expected: https://outreachdashboard.wmflabs.org/courses/{school}/{course_slug}'
    }
  }

  return { valid: true, error: null }
}

/**
 * Fetch course data from Outreach Dashboard API
 * 
 * @param {string} baseUrl - Base URL of the course (without /course.json)
 * @returns {Promise<Object>} Promise resolving to course data or error
 */
export async function fetchCourseData(baseUrl) {
  if (!baseUrl || typeof baseUrl !== 'string') {
    return {
      success: false,
      data: null,
      error: 'Base URL is required'
    }
  }

  baseUrl = baseUrl.trim()

  // Ensure baseUrl doesn't end with /course.json
  if (baseUrl.endsWith('/course.json')) {
    baseUrl = baseUrl.slice(0, -12)
  }
  baseUrl = baseUrl.replace(/\/$/, '') // Remove trailing slash

  // Parse URL to get school and course_slug
  const parsed = parseOutreachUrl(baseUrl)
  if (!parsed.valid) {
    return {
      success: false,
      data: null,
      error: 'Invalid Outreach Dashboard URL format'
    }
  }

  // Build API URL
  const apiUrl = `https://outreachdashboard.wmflabs.org/courses/${parsed.school}/${parsed.course_slug}/course.json`

  try {
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    })

    if (response.status === 404) {
      return {
        success: false,
        data: null,
        error: 'Course not found. Please verify the URL is correct.'
      }
    }

    if (!response.ok) {
      return {
        success: false,
        data: null,
        error: `API returned status code ${response.status}`
      }
    }

    const data = await response.json()

    // Extract course data from response
    if (data.course) {
      return {
        success: true,
        data: data.course,
        error: null
      }
    } else {
      return {
        success: false,
        data: null,
        error: 'Invalid API response format'
      }
    }
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return {
        success: false,
        data: null,
        error: 'Failed to connect to Outreach Dashboard API. Please check your internet connection.'
      }
    }
    return {
      success: false,
      data: null,
      error: error.message || 'Unexpected error occurred'
    }
  }
}

