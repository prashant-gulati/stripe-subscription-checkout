import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export default function Checkout() {
  const [loading, setLoading] = useState(false)

  const handleCheckout = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/create-checkout-session`, {
        method: 'POST',
      })
      const data = await res.json()
      if (data.url) {
        window.location.href = data.url
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>Sample Subscription — $20.00/month</h1>
      <button onClick={handleCheckout} disabled={loading}>
        {loading ? 'Redirecting…' : 'Checkout'}
      </button>
    </div>
  )
}
