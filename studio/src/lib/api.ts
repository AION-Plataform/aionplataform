declare global {
  interface Window {
    __AION_CONFIG__?: {
      API_BASE_URL?: string
    }
  }
}

function normalizePath(path: string): string {
  return path.startsWith('/') ? path : `/${path}`
}

function normalizeBase(base: string): string {
  if (!base) return ''
  return base.replace(/\/+$/, '')
}

function resolveApiBases(): string[] {
  const runtimeBaseUrl = window.__AION_CONFIG__?.API_BASE_URL?.trim()
  const buildTimeBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim()
  const preferredBase = normalizeBase(runtimeBaseUrl || buildTimeBaseUrl || '/api')

  // Keep compatibility with deployments where API is served at root
  // (e.g. `/auth/token`) and `/api/*` is not routed.
  if (preferredBase === '/api') {
    return ['/api', '']
  }

  return [preferredBase]
}

function shouldFallbackFromApiPrefix(response: Response, base: string, hasFallback: boolean): boolean {
  if (base !== '/api' || !hasFallback) return false

  const contentType = (response.headers.get('content-type') || '').toLowerCase()
  const isHtml = contentType.includes('text/html')
  const isJson = contentType.includes('application/json')
  const isLikelyProxyMiss = [404, 405, 502, 503, 504].includes(response.status)

  // Our Runtime API endpoints return JSON. If `/api/*` returns a non-JSON response,
  // it's commonly a proxy miss to an HTML app/static page: fallback to root endpoints.
  const isNonJsonApiResponse = response.status < 500 && !isJson

  return isHtml || isLikelyProxyMiss || isNonJsonApiResponse
}

export function apiUrl(path: string): string {
  const normalizedPath = normalizePath(path)
  return `${resolveApiBases()[0]}${normalizedPath}`
}

export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const normalizedPath = normalizePath(path)
  const bases = resolveApiBases()

  let lastResponse: Response | null = null
  let lastError: unknown = null

  for (const base of bases) {
    const requestUrl = `${base}${normalizedPath}`

    try {
      const response = await fetch(requestUrl, init)
      lastResponse = response

      if (!shouldFallbackFromApiPrefix(response, base, bases.length > 1)) {
        return response
      }
    } catch (error) {
      lastError = error
    }
  }

  if (lastResponse) return lastResponse
  throw lastError || new Error('Unable to reach API')
}
