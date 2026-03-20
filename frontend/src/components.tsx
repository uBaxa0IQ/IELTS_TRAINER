import { type ReactElement, type ReactNode, useMemo } from 'react'
import { Link, Navigate } from 'react-router-dom'

import { useAuth } from './auth'
import type { EvaluationResult, SpellingError } from './types'

export function ProtectedRoute({ children }: { children: ReactElement }) {
  const { ready, user } = useAuth()
  if (!ready) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <span className="text-text-secondary font-mono text-sm">loading...</span>
      </div>
    )
  }
  if (!user) {
    return <Navigate to="/login" replace />
  }
  return children
}

export function TopBar() {
  const { user } = useAuth()

  return (
    <header className="flex items-center justify-between px-4 sm:px-6 py-4 max-w-[960px] mx-auto w-full">
      <Link to="/" className="no-underline">
        <div className="flex items-baseline gap-2">
          <span className="text-text-secondary text-sm tracking-wider font-light">ielts</span>
          <span className="text-accent text-sm tracking-wider font-medium">writing</span>
        </div>
      </Link>
      <div className="flex items-center gap-4">
        {user ? (
          <>
            <Link
              to="/profile"
              className="text-text-secondary hover:text-text-primary text-sm no-underline transition-colors duration-200"
            >
              {user.nickname ?? user.email}
            </Link>
          </>
        ) : (
          <Link
            to="/login"
            className="text-text-secondary hover:text-accent text-sm no-underline transition-colors duration-200"
          >
            sign in
          </Link>
        )}
      </div>
    </header>
  )
}

export function ScoreDisplay({ result, expanded, onToggle }: {
  result: EvaluationResult
  expanded: boolean
  onToggle: () => void
}) {
  const criteria = [
    { label: 'task', value: result.task_response_band },
    { label: 'coherence', value: result.coherence_band },
    { label: 'lexical', value: result.lexical_band },
    { label: 'grammar', value: result.grammar_band },
  ]

  return (
    <div className="animate-fade-in mt-12 mb-8">
      <div className="text-center mb-8">
        <div className="text-text-secondary text-xs tracking-widest uppercase mb-2">overall band</div>
        <div className="text-accent text-4xl sm:text-5xl font-mono font-light tracking-tight">
          {result.overall_band.toFixed(1)}
        </div>
      </div>

      <div className="flex justify-center flex-wrap gap-6 sm:gap-8 mb-8">
        {criteria.map((c) => (
          <div key={c.label} className="text-center">
            <div className="text-text-secondary text-xs mb-1">{c.label}</div>
            <div className="text-text-primary font-mono text-lg">{c.value.toFixed(1)}</div>
          </div>
        ))}
      </div>

      <p className="text-text-primary text-sm leading-relaxed text-center max-w-[640px] mx-auto mb-4">
        {result.short_feedback}
      </p>

      <div className="text-center">
        <button
          onClick={onToggle}
          className="text-text-secondary hover:text-accent text-xs bg-transparent border-none cursor-pointer transition-colors duration-200 p-0 font-sans"
        >
          {expanded ? 'hide details' : 'show details'}
        </button>
      </div>

      {expanded && (
        <div className="animate-fade-in mt-6 max-w-[720px] mx-auto space-y-5">
          <DetailSection title="Task Response" body={result.detailed_feedback.task_response} />
          <DetailSection title="Coherence & Cohesion" body={result.detailed_feedback.coherence_and_cohesion} />
          <DetailSection title="Lexical Resource" body={result.detailed_feedback.lexical_resource} />
          <DetailSection title="Grammar" body={result.detailed_feedback.grammatical_range_and_accuracy} />

          {result.improvement_tips.length > 0 && (
            <div>
              <h4 className="text-text-secondary text-xs tracking-widest uppercase mb-2">tips</h4>
              <ul className="list-none p-0 m-0 space-y-1">
                {result.improvement_tips.map((tip, i) => (
                  <li key={i} className="text-text-primary text-sm leading-relaxed">
                    <span className="text-accent mr-2">-</span>{tip}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function DetailSection({ title, body }: { title: string; body: string }) {
  return (
    <div>
      <h4 className="text-text-secondary text-xs tracking-widest uppercase mb-1">{title}</h4>
      <p className="text-text-primary text-sm leading-relaxed m-0">{body}</p>
    </div>
  )
}

export function EssayWithErrors({ text, errors }: { text: string; errors: SpellingError[] }) {
  const highlighted = useMemo(() => {
    if (!errors.length) return [{ text, isError: false, correction: '' }]

    const errorWords = new Set(errors.map((e) => e.word.toLowerCase()))
    const errorMap = new Map(errors.map((e) => [e.word.toLowerCase(), e.correction]))

    const words = text.split(/(\s+)/)
    return words.map((segment) => {
      const clean = segment.replace(/[.,!?;:'"()]/g, '').toLowerCase()
      if (errorWords.has(clean)) {
        return { text: segment, isError: true, correction: errorMap.get(clean) ?? '' }
      }
      return { text: segment, isError: false, correction: '' }
    })
  }, [text, errors])

  return (
    <div className="font-mono text-text-primary text-base leading-[2] whitespace-pre-wrap">
      {highlighted.map((part, i) =>
        part.isError ? (
          <span key={i} className="spelling-error" title={`→ ${part.correction}`}>
            {part.text}
          </span>
        ) : (
          <span key={i}>{part.text}</span>
        ),
      )}
    </div>
  )
}

export function LoadingDots() {
  return (
    <span className="inline-flex gap-1">
      <span className="w-1.5 h-1.5 rounded-full bg-text-secondary animate-pulse" style={{ animationDelay: '0ms' }} />
      <span className="w-1.5 h-1.5 rounded-full bg-text-secondary animate-pulse" style={{ animationDelay: '150ms' }} />
      <span className="w-1.5 h-1.5 rounded-full bg-text-secondary animate-pulse" style={{ animationDelay: '300ms' }} />
    </span>
  )
}

export function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-dvh flex flex-col">
      <TopBar />
      <main className="flex flex-1 flex-col min-h-0 max-w-[960px] mx-auto w-full px-4 sm:px-6 pb-4 sm:pb-6">
        {children}
      </main>
    </div>
  )
}
