const rawBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim()

const sanitizedBaseUrl = rawBaseUrl
  ? rawBaseUrl.replace(/\/+$/, '')
  : '/api'

export function apiUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${sanitizedBaseUrl}${normalizedPath}`
}
