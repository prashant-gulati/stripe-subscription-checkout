import { useSearchParams } from 'react-router-dom'

export default function Success() {
  const [params] = useSearchParams()
  const sessionId = params.get('session_id')

  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>Payment successful</h1>
      {sessionId && <p>Session: {sessionId}</p>}
    </div>
  )
}
