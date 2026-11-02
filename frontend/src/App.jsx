import { useState } from 'react'
import { checkUrl, usingSample } from './api.js'
import Results from './Results.jsx'

function isHttpUrl(value) {
  try {
    const parsed = new URL(value)
    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
  } catch {
    return false
  }
}

function App() {
  const [url, setUrl] = useState('')
  const [error, setError] = useState('')
  const [status, setStatus] = useState('idle')
  const [current, setCurrent] = useState(null)
  const [history, setHistory] = useState([])

  async function handleSubmit(event) {
    event.preventDefault()
    const trimmed = url.trim()

    if (!trimmed) {
      setError('Enter a URL.')
      return
    }

    if (!isHttpUrl(trimmed)) {
      setError('Use a full URL that starts with http:// or https://')
      return
    }

    setError('')
    setStatus('loading')

    try {
      const result = await checkUrl(trimmed)
      setCurrent(result)
      setHistory((checks) => [...checks, result])
      setStatus('success')
    } catch {
      setStatus('failed')
    }
  }

  return (
    <main className={current ? 'page page-wide' : 'page'}>
      <div className={current ? 'split split-wide' : 'split'}>
        <div className="check">
          <h1>
            <span>Phishing</span> URL Check
          </h1>
          <p className="lead">Paste your URL below</p>
          <form onSubmit={handleSubmit} noValidate>
            <label htmlFor="url">URL</label>
            <input
              id="url"
              name="url"
              type="url"
              placeholder="https://example.com/login"
              autoComplete="url"
              value={url}
              disabled={status === 'loading'}
              onChange={(event) => {
                setUrl(event.target.value)
                if (status === 'failed') {
                  setStatus('idle')
                }
              }}
              aria-invalid={Boolean(error)}
              aria-describedby={error ? 'url-error' : undefined}
            />
            {error ? (
              <p id="url-error" className="error" role="alert">
                {error}
              </p>
            ) : null}
            <button type="submit" disabled={status === 'loading'}>
              {status === 'loading' ? 'Checking…' : 'Check URL'}
            </button>
          </form>

          {status === 'loading' ? (
            <div className="status" role="status" aria-live="polite">
              <span className="spinner" aria-hidden="true" />
              <p>Checking this URL…</p>
            </div>
          ) : null}

          {status === 'failed' ? (
            <div className="status status-failed" role="alert">
              <h2>Check failed</h2>
              <p>The check could not be completed. Try another URL, or try again.</p>
            </div>
          ) : null}
        </div>

        {status === 'success' && current ? (
          <Results
            current={current}
            history={history}
            usingSample={usingSample}
            onSelect={(id) => {
              const chosen = history.find((item) => item.id === id)
              if (chosen) {
                setCurrent(chosen)
                setUrl(chosen.url)
              }
            }}
          />
        ) : null}
      </div>
    </main>
  )
}

export default App
