const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
export const usingSample = import.meta.env.VITE_USE_SAMPLE !== 'false'

function wait(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}

function sampleCheck(url) {
  const risky = /login|verify|secure|account|update|confirm|password/.test(
    url.toLowerCase(),
  )
  const extra = (url.length % 19) / 100
  const phishing = Math.min(0.97, Math.max(0.08, (risky ? 0.78 : 0.24) + extra))
  const prediction = phishing >= 0.5 ? 'phishing' : 'legitimate'

  return {
    id: crypto.randomUUID(),
    url,
    prediction,
    confidence: prediction === 'phishing' ? phishing : 1 - phishing,
    probabilities: {
      phishing,
      legitimate: 1 - phishing,
    },
  }
}

function mapResponse(data, url) {
  const probs = data.probabilities || {}
  const legitimate = Number(probs.benign ?? probs.legitimate ?? 0)
  const phishing = Math.max(0, 1 - legitimate)
  const raw = String(data.prediction || '').toLowerCase()
  const prediction =
    raw === 'benign' || raw === 'legitimate' ? 'legitimate' : 'phishing'
  const confidence =
    prediction === 'legitimate' ? legitimate : Number(probs[raw] ?? phishing)

  return {
    id: crypto.randomUUID(),
    url: data.url || url,
    prediction,
    confidence,
    probabilities: {
      phishing,
      legitimate,
    },
  }
}

export async function checkUrl(url) {
  if (usingSample) {
    await wait(900)
    if (new URL(url).hostname === 'fail.test') {
      throw new Error('check failed')
    }
    return sampleCheck(url)
  }

  const response = await fetch(`${API_URL}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })

  if (!response.ok) {
    throw new Error('check failed')
  }

  return mapResponse(await response.json(), url)
}
