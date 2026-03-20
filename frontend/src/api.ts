import type {
  AuthResponse,
  EvaluationResult,
  ProgressPoint,
  Prompt,
  SubmissionDetail,
  SubmissionListItem,
  User,
} from './types'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

/** Must match AuthProvider localStorage key */
export const SESSION_KEY = 'ielts-trainer-session'

export const SESSION_REFRESHED_EVENT = 'ielts-session-refreshed'

function buildHeaders(token?: string): HeadersInit {
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

function hasAuthorizationHeader(headers: HeadersInit | undefined): boolean {
  if (!headers) return false
  if (headers instanceof Headers) return headers.has('Authorization')
  if (Array.isArray(headers)) {
    return headers.some(([k]) => k.toLowerCase() === 'authorization')
  }
  return Boolean((headers as Record<string, string>).Authorization)
}

function persistTokens(access_token: string, refresh_token: string) {
  localStorage.setItem(
    SESSION_KEY,
    JSON.stringify({ access_token, refresh_token }),
  )
  window.dispatchEvent(
    new CustomEvent(SESSION_REFRESHED_EVENT, {
      detail: { access_token, refresh_token },
    }),
  )
}

let refreshInFlight: Promise<string | null> | null = null

async function tryRefreshFromStorage(): Promise<string | null> {
  if (refreshInFlight) return refreshInFlight

  refreshInFlight = (async () => {
    try {
      const raw = localStorage.getItem(SESSION_KEY)
      if (!raw) return null
      const s = JSON.parse(raw) as {
        access_token?: string
        refresh_token?: string
        token?: string
      }
      const rt = s.refresh_token
      if (!rt) return null

      const response = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: rt }),
      })
      if (!response.ok) return null

      const data = (await response.json()) as AuthResponse
      persistTokens(data.access_token, data.refresh_token)
      return data.access_token
    } catch {
      return null
    } finally {
      refreshInFlight = null
    }
  })()

  return refreshInFlight
}

async function request<T>(path: string, options: RequestInit = {}, retried = false): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options)

  if (
    response.status === 401 &&
    !retried &&
    path !== '/auth/refresh' &&
    hasAuthorizationHeader(options.headers)
  ) {
    const newAccess = await tryRefreshFromStorage()
    if (newAccess) {
      return request<T>(
        path,
        {
          ...options,
          headers: buildHeaders(newAccess),
        },
        true,
      )
    }
    localStorage.removeItem(SESSION_KEY)
  }

  if (!response.ok) {
    const data = await response.json().catch(() => null)
    const message =
      typeof data?.detail === 'string'
        ? data.detail
        : data?.detail?.message ?? 'Request failed'
    throw new Error(message)
  }
  return response.json() as Promise<T>
}

/** Used on bootstrap when access token expired; does not use `request()` (no 401 retry loop). */
export async function refreshSession(refreshToken: string): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  })
  if (!response.ok) {
    const data = await response.json().catch(() => null)
    const message =
      typeof data?.detail === 'string'
        ? data.detail
        : data?.detail?.message ?? 'Request failed'
    throw new Error(message)
  }
  const auth = (await response.json()) as AuthResponse
  persistTokens(auth.access_token, auth.refresh_token)
  return auth
}

export function me(token: string): Promise<User> {
  return request<User>('/auth/me', {
    headers: buildHeaders(token),
  })
}

export function patchMe(
  token: string,
  body: { analysis_language?: string; nickname?: string },
): Promise<User> {
  return request<User>('/auth/me', {
    method: 'PATCH',
    headers: buildHeaders(token),
    body: JSON.stringify(body),
  })
}

export function postAnalyticsEvent(
  token: string,
  body: { event_type: string; meta?: Record<string, unknown> },
): Promise<{ ok: string }> {
  return request<{ ok: string }>('/analytics/events', {
    method: 'POST',
    headers: buildHeaders(token),
    body: JSON.stringify(body),
  })
}

export function generatePrompt(token: string): Promise<Prompt> {
  return request<Prompt>('/prompts/generate', {
    method: 'POST',
    headers: buildHeaders(token),
    body: JSON.stringify({ mode: 'generated' }),
  })
}

export function generatePromptAnon(): Promise<Prompt> {
  return request<Prompt>('/prompts/generate-anon', {
    method: 'POST',
    headers: buildHeaders(),
  })
}

export function createManualPrompt(token: string, topicText: string): Promise<Prompt> {
  return request<Prompt>('/prompts/manual', {
    method: 'POST',
    headers: buildHeaders(token),
    body: JSON.stringify({ topic_text: topicText }),
  })
}

export function evaluateEssay(
  token: string,
  payload: {
    prompt_id: string
    essay_text: string
    timer_enabled: boolean
    timer_duration_seconds: number | null
    timer_expired: boolean
  },
): Promise<EvaluationResult> {
  return request<EvaluationResult>('/essays/evaluate', {
    method: 'POST',
    headers: buildHeaders(token),
    body: JSON.stringify(payload),
  })
}

export function evaluateEssayAnon(payload: {
  topic_text: string
  essay_text: string
  timer_enabled: boolean
  timer_duration_seconds: number | null
  timer_expired: boolean
  analysis_language: string
}): Promise<EvaluationResult> {
  return request<EvaluationResult>('/essays/evaluate-anon', {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify(payload),
  })
}

export function getHistory(token: string): Promise<SubmissionListItem[]> {
  return request<SubmissionListItem[]>('/essays', {
    headers: buildHeaders(token),
  })
}

export function getSubmission(token: string, submissionId: string): Promise<SubmissionDetail> {
  return request<SubmissionDetail>(`/essays/${submissionId}`, {
    headers: buildHeaders(token),
  })
}

export async function getProgress(token: string): Promise<ProgressPoint[]> {
  const response = await request<{ points: ProgressPoint[] }>('/analytics/progress', {
    headers: buildHeaders(token),
  })
  return response.points
}
