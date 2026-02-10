declare global {
  interface Window {
    __AION_CONFIG__?: {
      API_BASE_URL?: string
    }
  }
}

function resolveApiBaseUrl(): string {
  const runtimeBaseUrl = window.__AION_CONFIG__?.API_BASE_URL?.trim()
  const buildTimeBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim()

  const rawBaseUrl = runtimeBaseUrl || buildTimeBaseUrl || '/api'
  return rawBaseUrl.replace(/\/+$/, '')
}

export function apiUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${resolveApiBaseUrl()}${normalizedPath}`
}
