"use client"

import { createContext, useContext, type ReactNode } from "react"
import { useAuthState, useSignInWithEmailAndPassword, useSignInWithGoogle } from 'react-firebase-hooks/auth'
import { signOut } from 'firebase/auth'
import { auth } from '@/lib/firebase'
import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'
import type { JSX } from "react"

interface AuthContextType {
  isLoggedIn: boolean
  userId: string | null
  login: () => JSX.Element
  logout: () => JSX.Element
  userButton: () => JSX.Element
  user: any
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, loading, error] = useAuthState(auth)
  const router = useRouter()
  
  const isLoggedIn = !!user && !loading

  const login = () => (
    <Button 
      onClick={() => router.push('/sign-in')}
      variant="ghost" 
      className="text-white hover:bg-purple-900/30"
    >
      Sign In
    </Button>
  )
  
  const logout = () => (
    <Button 
      onClick={() => signOut(auth)}
      variant="ghost" 
      className="text-white hover:bg-purple-900/30"
    >
      Sign Out
    </Button>
  )
  
  const userButton = () => (
    <div className="flex items-center space-x-2">
      {user?.photoURL && (
        <img 
          src={user.photoURL} 
          alt="User avatar" 
          className="w-8 h-8 rounded-full"
        />
      )}
      <span className="text-sm text-white">
        {user?.displayName || user?.email}
      </span>
    </div>
  )

  return (
    <AuthContext.Provider 
      value={{ 
        isLoggedIn, 
        userId: user?.uid || null, 
        login, 
        logout, 
        userButton, 
        user,
        loading
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
