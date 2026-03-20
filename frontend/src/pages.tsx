import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { ANALYSIS_LANGUAGE_OPTIONS } from './analysisLanguage'
import {
  createManualPrompt,
  evaluateEssay,
  evaluateEssayAnon,
  generatePrompt,
  generatePromptAnon,
  getHistory,
  getProgress,
  getSubmission,
  me,
  postAnalyticsEvent,
  patchMe,
} from './api'
import { useAuth } from './auth'
import { EssayWithErrors, LoadingDots, ScoreDisplay, Shell } from './components'
import type { EvaluationResult, ProgressPoint, Prompt, SubmissionDetail, SubmissionListItem } from './types'
import { countWords, formatDate, formatTimer } from './utils'

const DRAFT_KEY = 'ielts-trainer-draft'
const DRAFT_VERSION = 1

type PersistedDraft = {
  v: number
  prompt: Prompt
  essayText: string
  timerEnabled?: boolean
  secondsLeft?: number
  timerExpired?: boolean
  timerRunning?: boolean
}

const defaultTimerState = {
  timerEnabled: false,
  secondsLeft: 40 * 60,
  timerExpired: false,
  timerRunning: false,
}

/* ───── Practice Page (public) ───── */

function loadDraft(): {
  prompt: Prompt | null
  essayText: string
  timerEnabled: boolean
  secondsLeft: number
  timerExpired: boolean
  timerRunning: boolean
} {
  try {
    const raw = localStorage.getItem(DRAFT_KEY)
    if (!raw) {
      return { prompt: null, essayText: '', ...defaultTimerState }
    }
    const data = JSON.parse(raw) as Partial<PersistedDraft> & { essayText?: string }
    if (data?.prompt?.topic_text && data.prompt.id) {
      return {
        prompt: data.prompt,
        essayText: typeof data.essayText === 'string' ? data.essayText : '',
        timerEnabled: Boolean(data.timerEnabled),
        secondsLeft:
          typeof data.secondsLeft === 'number' && data.secondsLeft >= 0
            ? data.secondsLeft
            : 40 * 60,
        timerExpired: Boolean(data.timerExpired),
        timerRunning: Boolean(data.timerRunning),
      }
    }
  } catch {
    /* corrupted or legacy format */
  }
  return { prompt: null, essayText: '', ...defaultTimerState }
}

export function PracticePage() {
  const { token, user } = useAuth()
  const analysisLanguage = user?.analysis_language ?? 'en'

  const initialDraftRef = useRef<ReturnType<typeof loadDraft> | null>(null)
  if (initialDraftRef.current === null) {
    initialDraftRef.current = loadDraft()
  }
  const d0 = initialDraftRef.current

  const [prompt, setPrompt] = useState<Prompt | null>(d0.prompt)
  const [showCustom, setShowCustom] = useState(false)
  const [customTopic, setCustomTopic] = useState('')
  const [essayText, setEssayText] = useState(d0.essayText)
  const [loadingPrompt, setLoadingPrompt] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<EvaluationResult | null>(null)
  const [evaluatedPrompt, setEvaluatedPrompt] = useState<Prompt | null>(null)
  const [evaluatedEssayText, setEvaluatedEssayText] = useState('')
  const [showDetails, setShowDetails] = useState(false)

  const [timerEnabled, setTimerEnabled] = useState(d0.timerEnabled)
  const [secondsLeft, setSecondsLeft] = useState(d0.secondsLeft)
  const [timerExpired, setTimerExpired] = useState(d0.timerExpired)
  const [timerRunning, setTimerRunning] = useState(d0.timerRunning)

  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const wordCount = useMemo(() => countWords(essayText), [essayText])
  const goalReached = wordCount >= 250

  useEffect(() => {
    if (prompt) {
      const payload: PersistedDraft = {
        v: DRAFT_VERSION,
        prompt,
        essayText,
        timerEnabled,
        secondsLeft,
        timerExpired,
        timerRunning,
      }
      localStorage.setItem(DRAFT_KEY, JSON.stringify(payload))
    } else {
      localStorage.removeItem(DRAFT_KEY)
    }
  }, [essayText, prompt, timerEnabled, secondsLeft, timerExpired, timerRunning])

  // Timer countdown
  useEffect(() => {
    if (!timerRunning || timerExpired) return
    const interval = window.setInterval(() => {
      setSecondsLeft((s) => {
        if (s <= 1) {
          setTimerExpired(true)
          setTimerRunning(false)
          window.clearInterval(interval)
          return 0
        }
        return s - 1
      })
    }, 1000)
    return () => window.clearInterval(interval)
  }, [timerRunning, timerExpired])

  const handleToggleTimer = useCallback(() => {
    if (!timerEnabled) {
      setTimerEnabled(true)
      setTimerRunning(true)
      setSecondsLeft(40 * 60)
      setTimerExpired(false)
    } else {
      setTimerEnabled(false)
      setTimerRunning(false)
      setSecondsLeft(40 * 60)
      setTimerExpired(false)
    }
  }, [timerEnabled])

  async function handleGenerateTopic() {
    setLoadingPrompt(true)
    setError(null)
    try {
      const p = token ? await generatePrompt(token) : await generatePromptAnon()
      if (token) {
        void postAnalyticsEvent(token, {
          event_type: 'topic_generated',
          meta: { prompt_id: p.id, source: p.source },
        }).catch(() => {})
      }
      setPrompt(p)
      setEssayText('')
      setResult(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to generate topic.')
    } finally {
      setLoadingPrompt(false)
    }
  }

  async function handleUseCustomTopic() {
    if (!customTopic.trim()) return
    setLoadingPrompt(true)
    setError(null)
    try {
      if (token) {
        const p = await createManualPrompt(token, customTopic.trim())
        setPrompt(p)
      } else {
        setPrompt({ id: 'custom', topic_text: customTopic.trim(), source: 'manual' })
      }
      setEssayText('')
      setShowCustom(false)
      setResult(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to set topic.')
    } finally {
      setLoadingPrompt(false)
    }
  }

  async function handleEvaluate() {
    if (!prompt) {
      setError('Generate or enter a topic first.')
      return
    }
    if (!essayText.trim()) {
      setError('Write your essay before evaluating.')
      return
    }
    if (wordCount < 250) {
      setError('Write at least 250 words before evaluating.')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      let res: EvaluationResult
      const submittedPrompt = prompt
      const submittedEssayText = essayText
      if (token && prompt.id !== 'custom') {
        res = await evaluateEssay(token, {
          prompt_id: prompt.id,
          essay_text: essayText,
          timer_enabled: timerEnabled,
          timer_duration_seconds: timerEnabled ? 40 * 60 : null,
          timer_expired: timerExpired,
        })
      } else {
        res = await evaluateEssayAnon({
          topic_text: prompt.topic_text,
          essay_text: essayText,
          timer_enabled: timerEnabled,
          timer_duration_seconds: timerEnabled ? 40 * 60 : null,
          timer_expired: timerExpired,
          analysis_language: analysisLanguage,
        })
      }

      if (token) {
        void postAnalyticsEvent(token, {
          event_type: 'essay_evaluated',
          meta: {
            prompt_id: submittedPrompt.id,
            word_count: res.word_count,
            timer_enabled: timerEnabled,
            timer_expired: timerExpired,
            analysis_language: analysisLanguage,
          },
        }).catch(() => {})
      }

      setEvaluatedPrompt(submittedPrompt)
      setEvaluatedEssayText(submittedEssayText)
      setResult(res)
      setShowDetails(false)
      setEssayText('')
      try {
        const nextPrompt = token ? await generatePrompt(token) : await generatePromptAnon()
        if (token) {
          void postAnalyticsEvent(token, {
            event_type: 'topic_generated',
            meta: { prompt_id: nextPrompt.id, source: nextPrompt.source },
          }).catch(() => {})
        }
        setPrompt(nextPrompt)
      } catch {
        setError('Essay evaluated, but unable to load a new topic.')
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to evaluate essay.')
    } finally {
      setSubmitting(false)
    }
  }

  function handleReset() {
    setResult(null)
    setEvaluatedPrompt(null)
    setEvaluatedEssayText('')
    setShowDetails(false)
    setTimerEnabled(false)
    setTimerRunning(false)
    setTimerExpired(false)
    setSecondsLeft(40 * 60)
    localStorage.removeItem(DRAFT_KEY)
  }

  const evaluateDisabled = !prompt || wordCount < 250 || submitting

  return (
    <Shell>
      {result ? (
        <div className="w-full max-w-[720px] mx-auto pt-8 pb-12 flex-1 overflow-y-auto min-h-0">
          {evaluatedPrompt ? (
            <div className="text-center mb-8 px-4">
              <p className="text-text-secondary text-xs tracking-widest uppercase mb-2">topic</p>
              <p className="text-accent text-base leading-relaxed m-0">{evaluatedPrompt.topic_text}</p>
            </div>
          ) : null}
          <EssayWithErrors text={evaluatedEssayText} errors={result.spelling_errors} />
          <ScoreDisplay
            result={result}
            expanded={showDetails}
            onToggle={() => setShowDetails((d) => !d)}
          />
          <div className="text-center mt-4">
            <button
              onClick={handleReset}
              className="text-text-secondary hover:text-accent text-xs bg-transparent border-none cursor-pointer transition-colors duration-200 p-0 font-sans"
            >
              write another essay
            </button>
          </div>
          {!user && (
            <p className="text-text-secondary text-xs text-center mt-4">
              results not saved.{' '}
              <a href="/login" className="text-accent no-underline hover:underline">sign in</a>
              {' '}to keep history.
            </p>
          )}
          {error ? (
            <div className="text-error text-sm text-center mt-4 animate-fade-in">{error}</div>
          ) : null}
        </div>
      ) : (
        <div className="flex flex-col flex-1 min-h-0 w-full max-w-[720px] mx-auto pt-4 sm:pt-6">
          {/* Timer */}
          <div className="shrink-0 flex items-center justify-center gap-3 mb-4">
            <button
              onClick={handleToggleTimer}
              className={`text-xs bg-transparent border-none cursor-pointer transition-colors duration-200 p-0 font-sans ${
                timerEnabled ? 'text-accent' : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              {timerEnabled ? 'stop timer' : 'start timer'}
            </button>
            {timerEnabled && (
              <span
                className={`font-mono text-lg tracking-wider transition-colors duration-500 ${
                  timerExpired
                    ? 'text-error animate-pulse-glow'
                    : secondsLeft < 300
                      ? 'text-error'
                      : 'text-text-secondary'
                }`}
              >
                {formatTimer(secondsLeft)}
              </span>
            )}
          </div>

          {/* Prompt area */}
          <div className="shrink-0 w-full text-center mb-4">
            {prompt ? (
              <div className="relative group">
                <p className="text-accent text-base leading-relaxed m-0 px-4">
                  {prompt.topic_text}
                </p>
                <div className="flex justify-center gap-4 mt-3">
                  <button
                    onClick={handleGenerateTopic}
                    disabled={loadingPrompt}
                    className="text-text-secondary hover:text-accent text-xs bg-transparent border-none cursor-pointer transition-colors duration-200 p-0 font-sans disabled:opacity-40"
                  >
                    {loadingPrompt ? 'loading...' : 'new topic'}
                  </button>
                  <button
                    onClick={() => setShowCustom(!showCustom)}
                    className="text-text-secondary hover:text-accent text-xs bg-transparent border-none cursor-pointer transition-colors duration-200 p-0 font-sans"
                  >
                    custom
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <button
                  onClick={handleGenerateTopic}
                  disabled={loadingPrompt}
                  className="text-text-secondary hover:text-accent text-sm bg-transparent border-none cursor-pointer transition-colors duration-200 font-sans disabled:opacity-40 p-0"
                >
                  {loadingPrompt ? 'generating...' : 'click to generate a topic'}
                </button>
                <div className="mt-2">
                  <button
                    onClick={() => setShowCustom(!showCustom)}
                    className="text-text-secondary hover:text-accent text-xs bg-transparent border-none cursor-pointer transition-colors duration-200 p-0 font-sans"
                  >
                    or enter your own
                  </button>
                </div>
              </div>
            )}

            {showCustom && (
              <div className="animate-fade-in mt-4 flex gap-2 items-end max-w-[720px] mx-auto">
                <input
                  type="text"
                  value={customTopic}
                  onChange={(e) => setCustomTopic(e.target.value)}
                  placeholder="enter your IELTS Task 2 topic..."
                  className="flex-1 bg-transparent border-b border-text-secondary text-text-primary text-sm py-2 px-1 font-sans placeholder:text-text-secondary/50"
                  onKeyDown={(e) => e.key === 'Enter' && handleUseCustomTopic()}
                />
                <button
                  onClick={handleUseCustomTopic}
                  className="text-accent text-xs bg-transparent border-none cursor-pointer p-0 font-sans"
                >
                  use
                </button>
              </div>
            )}
          </div>

          {/* Scrollable essay + fixed footer (counter + evaluate) */}
          <div className="flex flex-col flex-1 min-h-0">
            <div className="relative flex-1 min-h-0 min-h-[12rem]">
              <textarea
                ref={textareaRef}
                value={essayText}
                onChange={(e) => setEssayText(e.target.value)}
                spellCheck={false}
                placeholder={prompt ? 'start writing your essay...' : ''}
                disabled={!prompt}
                className="absolute inset-0 w-full h-full bg-transparent border-none resize-none overflow-y-auto font-mono text-text-primary text-base leading-[2] placeholder:text-text-secondary/30 disabled:opacity-30 p-0 [scrollbar-gutter:stable]"
              />
            </div>

            <div className="shrink-0 pt-2 pb-3 space-y-1.5">
              <div className="text-center">
                <span
                  className={`font-mono text-sm transition-all duration-500 ${
                    goalReached ? 'text-accent animate-accent-pop' : 'text-text-secondary'
                  }`}
                >
                  {wordCount} / 250
                </span>
                {goalReached && (
                  <span className="text-accent text-xs ml-2 animate-fade-in">goal reached</span>
                )}
              </div>

              {prompt ? (
                <div className="text-center">
                  <button
                    type="button"
                    onClick={handleEvaluate}
                    disabled={evaluateDisabled}
                    title={wordCount < 250 ? 'need 250 words' : undefined}
                    className={`text-sm bg-transparent border-none transition-colors duration-200 font-sans p-0 ${
                      evaluateDisabled
                        ? 'text-text-secondary/40 cursor-not-allowed'
                        : 'text-text-secondary hover:text-accent cursor-pointer'
                    }`}
                  >
                    {submitting ? <LoadingDots /> : 'evaluate'}
                  </button>
                </div>
              ) : null}

              {error ? (
                <div className="text-error text-sm text-center animate-fade-in">{error}</div>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </Shell>
  )
}

/* ───── Profile Page (auth required) ───── */

export function ProfilePage() {
  const { token, user, logout } = useAuth()
  const [history, setHistory] = useState<SubmissionListItem[]>([])
  const [points, setPoints] = useState<ProgressPoint[]>([])
  const [selected, setSelected] = useState<SubmissionDetail | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return
    getHistory(token).then(setHistory).catch(() => setError('Unable to load history.'))
    getProgress(token).then(setPoints).catch(() => {})
  }, [token])

  async function handleSelect(id: string) {
    if (!token) return
    try {
      setSelected(await getSubmission(token, id))
    } catch {
      setError('Unable to load submission.')
    }
  }

  return (
    <Shell>
      <div className="pt-8 max-w-[720px] mx-auto flex-1 min-h-0 overflow-y-auto pb-12">
        <section className="mb-10 pb-4 border-b border-bg-secondary/60">
          <p className="text-text-secondary text-xs tracking-widest uppercase mb-2">profile</p>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-text-primary text-sm m-0">{user?.nickname ?? user?.email}</p>
              <p className="text-text-secondary text-xs mt-1 mb-0">Manage your preferences and review progress.</p>
            </div>
            <div className="flex items-center gap-4">
              <Link
                to="/profile/settings"
                className="text-text-secondary hover:text-accent text-xs no-underline transition-colors duration-200"
              >
                settings
              </Link>
              <button
                onClick={logout}
                className="text-text-secondary hover:text-text-primary text-xs bg-transparent border-none cursor-pointer transition-colors duration-200 p-0 font-sans"
              >
                logout
              </button>
            </div>
          </div>
        </section>

        {/* Score chart */}
        {points.length > 1 && (
          <div className="mb-12">
            <h2 className="text-text-secondary text-xs tracking-widest uppercase mb-4">progress</h2>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={points}>
                  <XAxis
                    dataKey="created_at"
                    tickFormatter={(v) => formatDate(v).slice(0, 10)}
                    stroke="#646669"
                    tick={{ fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    domain={[0, 9]}
                    stroke="#646669"
                    tick={{ fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    labelFormatter={(v) => formatDate(String(v))}
                    contentStyle={{
                      background: '#2c2e31',
                      border: 'none',
                      borderRadius: 8,
                      color: '#d1d0c5',
                      fontSize: 12,
                    }}
                  />
                  <Line
                    dataKey="overall_band"
                    stroke="#e2b714"
                    strokeWidth={2}
                    dot={{ fill: '#e2b714', r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* History */}
        <h2 className="text-text-secondary text-xs tracking-widest uppercase mb-4">
          history ({history.length})
        </h2>

        {error && <div className="text-error text-sm mb-4">{error}</div>}

        <div className="space-y-2">
          {history.map((item) => (
            <button
              key={item.id}
              onClick={() => handleSelect(item.id)}
              className="w-full flex items-center justify-between py-3 px-1 bg-transparent border-0 border-b border-solid border-bg-secondary cursor-pointer text-left transition-colors duration-200 hover:bg-bg-secondary/30 font-sans group"
            >
              <div className="flex items-center gap-4">
                <span className="text-accent font-mono text-lg">
                  {item.overall_band?.toFixed(1) ?? '—'}
                </span>
                <span className="text-text-secondary text-xs">
                  {formatDate(item.created_at)}
                </span>
              </div>
              <span className="text-text-secondary text-xs">
                {item.word_count} words
              </span>
            </button>
          ))}
          {history.length === 0 && (
            <p className="text-text-secondary text-sm">No essays yet.</p>
          )}
        </div>

        {/* Selected detail */}
        {selected && (
          <div className="animate-fade-in mt-8 pb-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-text-secondary text-xs tracking-widest uppercase m-0">submission</h3>
              <button
                onClick={() => setSelected(null)}
                className="text-text-secondary hover:text-text-primary text-xs bg-transparent border-none cursor-pointer p-0 font-sans transition-colors duration-200"
              >
                close
              </button>
            </div>
            <p className="text-text-secondary text-sm leading-relaxed mb-4">{selected.prompt_text}</p>
            <div className="font-mono text-text-primary text-sm leading-[2] whitespace-pre-wrap mb-6">
              {selected.essay_text}
            </div>
            <div className="flex gap-6">
              {[
                { label: 'overall', value: selected.overall_band },
                { label: 'task', value: selected.task_response_band },
                { label: 'coherence', value: selected.coherence_band },
                { label: 'lexical', value: selected.lexical_band },
                { label: 'grammar', value: selected.grammar_band },
              ].map((c) => (
                <div key={c.label} className="text-center">
                  <div className="text-text-secondary text-xs mb-1">{c.label}</div>
                  <div className="text-text-primary font-mono">{c.value?.toFixed(1) ?? '—'}</div>
                </div>
              ))}
            </div>
            {selected.short_feedback && (
              <p className="text-text-primary text-sm mt-4 leading-relaxed">{selected.short_feedback}</p>
            )}
          </div>
        )}
      </div>
    </Shell>
  )
}

export function ProfileSettingsPage() {
  const { token, user, setUser } = useAuth()
  const [langError, setLangError] = useState<string | null>(null)
  const [nickDraft, setNickDraft] = useState(user?.nickname ?? '')
  const [nickError, setNickError] = useState<string | null>(null)

  useEffect(() => {
    setNickDraft(user?.nickname ?? '')
  }, [user?.nickname])

  async function handleAnalysisLanguageChange(code: string) {
    if (!token) return
    setLangError(null)
    try {
      const updatedUser = await patchMe(token, { analysis_language: code })
      setUser(updatedUser)
    } catch (e) {
      setLangError(e instanceof Error ? e.message : 'Could not save language.')
    }
  }

  async function handleNicknameSave() {
    if (!token) return
    setNickError(null)
    try {
      const next = nickDraft.trim()
      if (!next) {
        setNickError('Nickname is required.')
        return
      }
      const updatedUser = await patchMe(token, { nickname: next })
      setUser(updatedUser)
    } catch (e) {
      setNickError(e instanceof Error ? e.message : 'Could not save nickname.')
    }
  }

  return (
    <Shell>
      <div className="pt-8 max-w-[720px] mx-auto flex-1 min-h-0 overflow-y-auto pb-12">
        <section className="mb-10">
          <div className="flex items-center justify-between gap-4 mb-4">
            <h2 className="text-text-secondary text-xs tracking-widest uppercase m-0">settings</h2>
            <Link
              to="/profile"
              className="text-text-secondary hover:text-accent text-xs no-underline transition-colors duration-200"
            >
              back to profile
            </Link>
          </div>
          <h3 className="text-text-secondary text-xs tracking-widest uppercase mb-2">feedback language</h3>
          <p className="text-text-secondary text-xs mb-3 max-w-md">
            IELTS bands stay the same; written feedback and tips are shown in this language.
          </p>
          <select
            value={user?.analysis_language ?? 'en'}
            onChange={(e) => void handleAnalysisLanguageChange(e.target.value)}
            className="bg-bg-secondary text-text-primary text-sm py-2 px-3 rounded border border-text-secondary/30 font-sans cursor-pointer max-w-xs w-full"
          >
            {ANALYSIS_LANGUAGE_OPTIONS.map((o) => (
              <option key={o.code} value={o.code}>
                {o.label}
              </option>
            ))}
          </select>
          {langError ? <p className="text-error text-xs mt-2">{langError}</p> : null}
        </section>

        <section className="mb-10">
          <h3 className="text-text-secondary text-xs tracking-widest uppercase mb-2">nickname</h3>
          <p className="text-text-secondary text-xs mb-3 max-w-md">
            This name is shown in the top bar and on your profile.
          </p>
          <input
            type="text"
            value={nickDraft}
            onChange={(e) => setNickDraft(e.target.value)}
            onBlur={() => void handleNicknameSave()}
            onKeyDown={(e) => {
              if (e.key !== 'Enter') return
              e.preventDefault()
              void handleNicknameSave()
            }}
            placeholder="nickname"
            className="bg-bg-secondary text-text-primary text-sm py-2 px-3 rounded border border-text-secondary/30 font-sans cursor-text max-w-xs w-full"
          />
          {nickError ? <p className="text-error text-xs mt-2">{nickError}</p> : null}
        </section>
      </div>
    </Shell>
  )
}

/* ───── Auth Page ───── */

export function AuthPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

  useEffect(() => {
    if (user) navigate('/', { replace: true })
  }, [navigate, user])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6">
      <div className="flex items-baseline gap-2 mb-10">
        <span className="text-text-secondary text-sm tracking-wider font-light">ielts</span>
        <span className="text-accent text-sm tracking-wider font-medium">writing</span>
      </div>

      <div className="w-full max-w-[340px] space-y-6">
        <h1 className="text-text-primary text-lg font-light text-center m-0">sign in</h1>

        <button
          type="button"
          onClick={() => {
            window.location.href = `${API_BASE}/auth/google/login`
          }}
          className="w-full bg-bg-secondary text-text-primary py-3 text-sm font-medium rounded-sm border-none cursor-pointer transition-opacity duration-200 hover:opacity-90 font-sans"
        >
          Continue with Google
        </button>
      </div>
    </div>
  )
}

export function GoogleCallbackPage() {
  const { setSession } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const accessToken = searchParams.get('token')
  const refreshToken = searchParams.get('refresh_token') ?? ''
  const newUser = searchParams.get('new_user')

  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!accessToken) {
      setError('Missing OAuth token.')
      return
    }

    setError(null)
    const eventType = newUser === '1' ? 'signup_google' : 'login_google'
    me(accessToken)
      .then((user) => {
        setSession({
          access_token: accessToken,
          refresh_token: refreshToken,
          token_type: 'bearer',
          user,
        })
        void postAnalyticsEvent(accessToken, { event_type: eventType, meta: {} }).catch(() => {})
        navigate('/', { replace: true })
      })
      .catch(() => setError('Google sign-in failed.'))
  }, [navigate, setSession, accessToken, refreshToken, newUser])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6">
      {error ? (
        <div className="text-error text-sm text-center">{error}</div>
      ) : (
        <div className="text-text-secondary flex items-center gap-2">
          <span>Signing you in</span>
          <LoadingDots />
        </div>
      )}
    </div>
  )
}
