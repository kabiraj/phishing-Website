import { useEffect, useRef } from 'react'
import * as d3 from 'd3'

function BarChart({ data, xKey, yKey, colorFor, tooltipFor, onBarClick }) {
  const frameRef = useRef(null)
  const colorRef = useRef(colorFor)
  const tooltipRef = useRef(tooltipFor)
  const clickRef = useRef(onBarClick)
  colorRef.current = colorFor
  tooltipRef.current = tooltipFor
  clickRef.current = onBarClick

  useEffect(() => {
    const frame = frameRef.current
    if (!frame) {
      return undefined
    }

    const draw = () => {
      frame.replaceChildren()

      const width = frame.clientWidth || 320
      const height = 240
      const margin = { top: 12, right: 8, bottom: 36, left: 44 }
      const innerWidth = width - margin.left - margin.right
      const innerHeight = height - margin.top - margin.bottom

      const svg = d3
        .select(frame)
        .append('svg')
        .attr('viewBox', `0 0 ${width} ${height}`)
        .attr('width', '100%')
        .attr('height', height)
        .attr('preserveAspectRatio', 'xMidYMid meet')
        .attr('role', 'img')

      const plot = svg
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)

      const x = d3
        .scaleBand()
        .domain(data.map((row) => row[xKey]))
        .range([0, innerWidth])
        .padding(0.35)

      const y = d3.scaleLinear().domain([0, 100]).range([innerHeight, 0])

      plot
        .append('g')
        .attr('transform', `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x))
        .selectAll('text')
        .attr('fill', '#02070a')

      plot
        .append('g')
        .call(d3.axisLeft(y).ticks(5).tickFormat((tick) => `${tick}%`))
        .selectAll('text')
        .attr('fill', '#02070a')

      const tip = d3.select(frame).append('div').attr('class', 'd3-tip')

      plot
        .selectAll('rect')
        .data(data)
        .join('rect')
        .attr('x', (row) => x(row[xKey]))
        .attr('y', (row) => y(row[yKey]))
        .attr('width', x.bandwidth())
        .attr('height', (row) => innerHeight - y(row[yKey]))
        .attr('rx', 8)
        .attr('fill', (row) => colorRef.current(row))
        .attr('cursor', clickRef.current ? 'pointer' : 'default')
        .attr('tabindex', clickRef.current ? 0 : null)
        .attr('role', clickRef.current ? 'button' : null)
        .attr('aria-label', (row) => tooltipRef.current(row))
        .on('keydown', (event, row) => {
          if (!clickRef.current) {
            return
          }
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault()
            clickRef.current(row)
          }
        })
        .on('mousemove', (event, row) => {
          tip
            .style('opacity', 1)
            .style('left', `${event.offsetX + 12}px`)
            .style('top', `${event.offsetY}px`)
            .text(tooltipRef.current(row))
        })
        .on('mouseleave', () => tip.style('opacity', 0))
        .on('click', (_event, row) => {
          if (clickRef.current) {
            clickRef.current(row)
          }
        })
    }

    draw()
    const watcher = new ResizeObserver(draw)
    watcher.observe(frame)
    return () => watcher.disconnect()
  }, [data, xKey, yKey])

  return <div className="chart-frame" ref={frameRef} />
}

export default BarChart
