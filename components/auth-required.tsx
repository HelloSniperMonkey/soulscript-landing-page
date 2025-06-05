"use client"

import { useAuth } from "@/context/auth-context"
import { redirect } from "next/navigation"
import { ReactNode } from "react"

export default function AuthRequired({ children }: { children: ReactNode }) {
  const { userId, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }
  
  if (!userId) {
    redirect("/sign-in")
  }
  
  return <>{children}</>
}
