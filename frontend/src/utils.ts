export function countWords(text: string) {
  return text
    .trim()
    .split(/\s+/)
    .filter(Boolean).length
}

export function formatDate(value: string) {
  return new Date(value).toLocaleString()
}

export function formatTimer(totalSeconds: number) {
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}
