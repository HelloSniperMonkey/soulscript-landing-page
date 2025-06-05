"use client"

import { useState } from 'react'
import { useSignInWithEmailAndPassword, useSignInWithGoogle } from 'react-firebase-hooks/auth'
import { auth } from '@/lib/firebase'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function SignInPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [signInWithEmailAndPassword, user, loading, error] = useSignInWithEmailAndPassword(auth)
  const [signInWithGoogle, googleUser, googleLoading, googleError] = useSignInWithGoogle(auth)
  const router = useRouter()

  useEffect(() => {
    if (user || googleUser) {
      router.push('/dashboard')
    }
  }, [user, googleUser, router])

  const handleEmailSignIn = async (e: React.FormEvent) => {
    e.preventDefault()
    if (email && password) {
      await signInWithEmailAndPassword(email, password)
    }
  }

  const handleGoogleSignIn = async () => {
    await signInWithGoogle()
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Sign In to SoulScript</CardTitle>
          <CardDescription>
            Welcome back! Sign in to your account.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={handleEmailSignIn} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            {(error || googleError) && (
              <p className="text-sm text-red-600">
                {error?.message || googleError?.message}
              </p>
            )}
            <Button 
              type="submit" 
              className="w-full bg-blue-600 hover:bg-blue-700"
              disabled={loading}
            >
              {loading ? 'Signing In...' : 'Sign In'}
            </Button>
          </form>
          
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <Separator className="w-full" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-muted-foreground">Or continue with</span>
            </div>
          </div>
          
          <Button
            type="button"
            variant="outline"
            className="w-full"
            onClick={handleGoogleSignIn}
            disabled={googleLoading}
          >
            {googleLoading ? 'Signing In...' : 'Sign in with Google'}
          </Button>
          
          <div className="text-center text-sm">
            Don't have an account?{' '}
            <Link href="/sign-up" className="text-blue-600 hover:text-blue-800 underline">
              Sign up
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
