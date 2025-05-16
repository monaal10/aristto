import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { PostHogProvider } from 'posthog-js/react'
const REACT_APP_PUBLIC_POSTHOG_KEY= "phc_UB4yNdQwnmrCttITOLywMauixnnT9CAybM6EMwdYiiW"
const REACT_APP_PUBLIC_POSTHOG_HOST= "https://us.i.posthog.com"
const options = {
  api_host: REACT_APP_PUBLIC_POSTHOG_HOST,
}
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <PostHogProvider
      apiKey={REACT_APP_PUBLIC_POSTHOG_KEY}
      options={options}
    >
    <App />
    </PostHogProvider>
  </StrictMode>,
)
