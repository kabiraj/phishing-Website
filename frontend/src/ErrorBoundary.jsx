import { Component } from 'react'
import { Link } from 'react-router-dom'

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="content">
          <main className="page">
            <h1>Something went wrong</h1>
            <p className="lead">
              The page failed unexpectedly. You can go back to the check.
            </p>
            <p>
              <Link to="/" onClick={() => this.setState({ hasError: false })}>
                Back to check
              </Link>
            </p>
          </main>
        </div>
      )
    }

    return this.props.children
  }
}
