import BarChart from './BarChart.jsx'

function Results({ current, history, onSelect, usingSample }) {
  const thisCheck = [
    {
      name: 'Phishing',
      value: Math.round(current.probabilities.phishing * 100),
    },
    {
      name: 'Legitimate',
      value: Math.round(current.probabilities.legitimate * 100),
    },
  ]

  const session = history.map((item, index) => ({
    id: item.id,
    name: String(index + 1),
    url: item.url,
    prediction: item.prediction,
    confidence: Math.round(item.confidence * 100),
  }))

  const verdict = current.prediction === 'phishing' ? 'Phishing' : 'Legitimate'
  const confidence = Math.round(current.confidence * 100)

  return (
    <section className="results">
      <p className={`verdict verdict-${current.prediction}`}>{verdict}</p>
      <p className="confidence">{confidence}% confidence</p>
      {usingSample ? (
        <p className="sample-note">Sample numbers until the API is connected.</p>
      ) : null}

      <div className="charts">
        <figure className="chart">
          <figcaption>
            <h2>This check</h2>
            <p>How this URL was split between phishing and legitimate.</p>
          </figcaption>
          <BarChart
            data={thisCheck}
            xKey="name"
            yKey="value"
            colorFor={(row) => (row.name === 'Phishing' ? '#FC734D' : '#0297DE')}
            tooltipFor={(row) => `${row.name}: ${row.value}%`}
          />
          <ul className="legend">
            <li>
              <span className="swatch swatch-phishing" />
              Phishing
            </li>
            <li>
              <span className="swatch swatch-legitimate" />
              Legitimate
            </li>
          </ul>
        </figure>

        <figure className="chart">
          <figcaption>
            <h2>This session</h2>
            <p>Click a bar or a row to reopen that check.</p>
          </figcaption>
          <BarChart
            data={session}
            xKey="name"
            yKey="confidence"
            colorFor={(row) => (row.id === current.id ? '#0297DE' : '#FC734D')}
            tooltipFor={(row) => `${row.url} — ${row.prediction} ${row.confidence}%`}
            onBarClick={(row) => onSelect(row.id)}
          />
          <ul className="legend">
            <li>
              <span className="swatch swatch-current" />
              Selected check
            </li>
            <li>
              <span className="swatch swatch-other" />
              Other checks this session
            </li>
          </ul>
          <ul className="session-list">
            {history.map((item, index) => (
              <li key={item.id}>
                <button
                  type="button"
                  className={item.id === current.id ? 'is-current' : ''}
                  onClick={() => onSelect(item.id)}
                >
                  {index + 1}. {item.url} — {item.prediction}
                </button>
              </li>
            ))}
          </ul>
        </figure>
      </div>
    </section>
  )
}

export default Results
