import { NextRequest, NextResponse } from 'next/server'

// Create a route matcher for protected routes
const protectedRoutes = [
  '/persona-dashboard',
  '/profile',
  '/blogs/new'
]

// Create a route matcher for public routes
const publicRoutes = [
  '/',
  '/sign-in',
  '/sign-up',
  '/blogs',
  '/api'
]

function isProtectedRoute(pathname: string): boolean {
  return protectedRoutes.some(route => pathname.startsWith(route))
}

function isPublicRoute(pathname: string): boolean {
  return publicRoutes.some(route => pathname.startsWith(route))
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // Allow public routes
  if (isPublicRoute(pathname)) {
    return NextResponse.next()
  }
  
  // Check for protected routes
  if (isProtectedRoute(pathname)) {
    // In a real implementation, you would verify the Firebase token here
    // For now, we'll redirect to sign-in if no session token is found
    const sessionToken = request.cookies.get('session')
    
    if (!sessionToken) {
      const signInUrl = new URL('/sign-in', request.url)
      signInUrl.searchParams.set('redirect', pathname)
      return NextResponse.redirect(signInUrl)
    }
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}