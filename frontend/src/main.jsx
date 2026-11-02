import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import './index.css'
import App from './App.jsx'
import Banner from './Banner.jsx'
import Boom from './Boom.jsx'
import { ErrorBoundary } from './ErrorBoundary.jsx'
import NotFound from './NotFound.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Banner />
      <ErrorBoundary>
        <div className="content">
          <Routes>
            <Route path="/" element={<App />} />
            <Route path="/boom" element={<Boom />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </ErrorBoundary>
    </BrowserRouter>
  </StrictMode>,
)
