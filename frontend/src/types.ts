export type User = {
  id: string
  email: string
  analysis_language?: string
}

export type AuthResponse = {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export type Prompt = {
  id: string
  topic_text: string
  source: 'preset' | 'generated' | 'manual'
}

export type DetailedFeedback = {
  task_response: string
  coherence_and_cohesion: string
  lexical_resource: string
  grammatical_range_and_accuracy: string
}

export type SpellingError = {
  word: string
  correction: string
}

export type EvaluationResult = {
  submission_id: string
  word_count: number
  overall_band: number
  task_response_band: number
  coherence_band: number
  lexical_band: number
  grammar_band: number
  short_feedback: string
  detailed_feedback: DetailedFeedback
  improvement_tips: string[]
  spelling_errors: SpellingError[]
}

export type SubmissionListItem = {
  id: string
  prompt_id: string
  word_count: number
  overall_band: number | null
  short_feedback: string | null
  status: 'pending' | 'scored' | 'failed'
  created_at: string
}

export type SubmissionDetail = {
  id: string
  prompt_id: string
  prompt_text: string
  essay_text: string
  word_count: number
  timer_enabled: boolean
  timer_duration_seconds: number | null
  timer_expired: boolean
  overall_band: number | null
  task_response_band: number | null
  coherence_band: number | null
  lexical_band: number | null
  grammar_band: number | null
  short_feedback: string | null
  analysis_json: {
    detailed_feedback?: DetailedFeedback
    improvement_tips?: string[]
    spelling_errors?: SpellingError[]
  } | null
  status: 'pending' | 'scored' | 'failed'
  created_at: string
}

export type ProgressPoint = {
  submission_id: string
  created_at: string
  overall_band: number
}
