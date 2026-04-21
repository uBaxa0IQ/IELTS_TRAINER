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

function buildHeaders(token?: string): HeadersInit {
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options)
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

export function register(email: string, password: string): Promise<AuthResponse> {
  return request<AuthResponse>('/auth/register', {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({ email, password }),
  })
}

export function login(email: string, password: string): Promise<AuthResponse> {
  return request<AuthResponse>('/auth/login', {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({ email, password }),
  })
}

export function me(token: string): Promise<User> {
  return request<User>('/auth/me', {
    headers: buildHeaders(token),
  })
}

export function patchMe(token: string, body: { analysis_language: string }): Promise<User> {
  return request<User>('/auth/me', {
    method: 'PATCH',
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
