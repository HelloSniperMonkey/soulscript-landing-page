"use client"

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function MapPage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to the new therapists near you page
    router.replace('/therapists-near-you')
  }, [router])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
        <p>Redirecting to Therapists Near You...</p>
      </div>
    </div>
  )
}
