import { Link } from 'react-router-dom'

function NotFound() {
  return (
    <main className="page">
      <h1>Page not found</h1>
      <p className="lead">That address does not exist in this app.</p>
      <p>
        <Link to="/">Back to check</Link>
      </p>
    </main>
  )
}

export default NotFound
