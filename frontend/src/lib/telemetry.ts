/**
 * SAMAAN AI — Frontend Production Observability & Web Vitals Telemetry
 * ===================================================================
 * Tracks:
 * - Core Web Vitals: LCP (Largest Contentful Paint), INP (Interaction to Next Paint), CLS (Cumulative Layout Shift)
 * - Navigation & initial load timing
 * - API request latency & network failures
 * - Audio playback errors & fallback triggers
 */

export interface WebVitalsMetrics {
  lcp: number | null // Target: < 2500ms
  inp: number | null // Target: < 200ms
  cls: number        // Target: < 0.1
  ttfb: number | null
  fcp: number | null
}

export interface ClientTelemetryReport {
  vitals: WebVitalsMetrics
  apiLatency: {
    avgMs: number
    p95Ms: number
    totalRequests: number
    failedRequests: number
  }
  audioFailures: number
  sessionDurationSec: number
}

class FrontendTelemetryCollector {
  private vitals: WebVitalsMetrics = {
    lcp: null,
    inp: null,
    cls: 0,
    ttfb: null,
    fcp: null,
  }

  private apiLatencies: number[] = []
  private apiFailures = 0
  private audioPlaybackFailures = 0
  private startTime = Date.now()

  constructor() {
    if (typeof window !== 'undefined') {
      this.initPerformanceObservers()
      this.measureNavigationTiming()
      // Expose to window for automated headless tests and debugging
      ;(window as any).__SAMAAN_TELEMETRY__ = this
    }
  }

  private initPerformanceObservers(): void {
    if (!('PerformanceObserver' in window)) return

    // 1. LCP — Largest Contentful Paint
    try {
      const lcpObserver = new PerformanceObserver((entryList) => {
        const entries = entryList.getEntries()
        const lastEntry = entries[entries.length - 1] as any
        if (lastEntry) {
          this.vitals.lcp = Math.round(lastEntry.startTime)
        }
      })
      lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true })
    } catch {}

    // 2. CLS — Cumulative Layout Shift
    try {
      const clsObserver = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries() as any[]) {
          if (!entry.hadRecentInput) {
            this.vitals.cls = Number((this.vitals.cls + entry.value).toFixed(4))
          }
        }
      })
      clsObserver.observe({ type: 'layout-shift', buffered: true })
    } catch {}

    // 3. INP / FID — Interaction to Next Paint
    try {
      const eventObserver = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries() as any[]) {
          const duration = Math.round(entry.duration)
          if (this.vitals.inp === null || duration > this.vitals.inp) {
            this.vitals.inp = duration
          }
        }
      })
      eventObserver.observe({ type: 'event', durationThreshold: 16, buffered: true } as any)
    } catch {}

    // 4. Paint Timing (FCP)
    try {
      const paintObserver = new PerformanceObserver((entryList) => {
        for (const entry of entryList.getEntries()) {
          if (entry.name === 'first-contentful-paint') {
            this.vitals.fcp = Math.round(entry.startTime)
          }
        }
      })
      paintObserver.observe({ type: 'paint', buffered: true })
    } catch {}
  }

  private measureNavigationTiming(): void {
    if (typeof performance === 'undefined') return
    const navEntries = performance.getEntriesByType('navigation') as PerformanceNavigationTiming[]
    if (navEntries && navEntries.length > 0) {
      const nav = navEntries[0]
      this.vitals.ttfb = Math.round(nav.responseStart - nav.requestStart)
    }
  }

  // ── Public Instrumentation API ───────────────────────────────────────────

  public recordApiRequest(durationMs: number, success: boolean): void {
    this.apiLatencies.push(durationMs)
    if (!success) {
      this.apiFailures += 1
    }
    // Keep max 200 samples
    if (this.apiLatencies.length > 200) {
      this.apiLatencies.shift()
    }
  }

  public recordAudioFailure(errorDetail: any): void {
    this.audioPlaybackFailures += 1
    console.warn('[Telemetry] Audio playback failure recorded:', errorDetail)
  }

  public getReport(): ClientTelemetryReport {
    const latencies = [...this.apiLatencies].sort((a, b) => a - b)
    const n = latencies.length
    const avg = n > 0 ? Math.round(latencies.reduce((a, b) => a + b, 0) / n) : 0
    const p95 = n > 0 ? Math.round(latencies[Math.min(Math.floor(n * 0.95), n - 1)]) : 0

    return {
      vitals: { ...this.vitals },
      apiLatency: {
        avgMs: avg,
        p95Ms: p95,
        totalRequests: n,
        failedRequests: this.apiFailures,
      },
      audioFailures: this.audioPlaybackFailures,
      sessionDurationSec: Math.round((Date.now() - this.startTime) / 1000),
    }
  }
}

export const telemetry = new FrontendTelemetryCollector()
