"use client"

import AuthRequired from "@/components/auth-required"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { useCurrentUser } from "@/hooks/use-current-user"
import { 
  BookOpen, 
  MessageSquare, 
  User, 
  Settings, 
  PlusCircle,
  ExternalLink
} from "lucide-react"

export default function UserDashboard() {
  const { user, loading } = useCurrentUser()

  if (loading) {
    return (
      <div className="container mx-auto py-20 px-4">
        <div className="mt-16 max-w-6xl mx-auto">
          <div className="text-center">Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <AuthRequired>
      <div className="container mx-auto py-20 px-4">
        <div className="mt-16 max-w-6xl mx-auto">
          {/* Welcome Section */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2">
              Welcome back, {user?.displayName || user?.email?.split('@')[0]}!
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Here's your personalized dashboard to access all your SoulScript tools.
            </p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Journal Entries</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">12</div>
                <p className="text-xs text-muted-foreground">
                  +2 from last week
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Chat Sessions</CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">8</div>
                <p className="text-xs text-muted-foreground">
                  +3 from last week
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Personas</CardTitle>
                <User className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">3</div>
                <p className="text-xs text-muted-foreground">
                  Therapy personas
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Main Tools */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {/* Journal */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <BookOpen className="h-6 w-6 text-purple-500" />
                  <CardTitle>Personal Journal</CardTitle>
                </div>
                <CardDescription>
                  Write and reflect on your thoughts, feelings, and daily experiences.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
                  <Link 
                    href="https://v0-mongo-db-journal-app.vercel.app/" 
                    target="_blank"
                    className="flex items-center justify-center space-x-2"
                  >
                    <span>Open Journal</span>
                    <ExternalLink className="h-4 w-4" />
                  </Link>
                </Button>
              </CardContent>
            </Card>

            {/* Persona Dashboard */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <User className="h-6 w-6 text-blue-500" />
                  <CardTitle>Persona Dashboard</CardTitle>
                </div>
                <CardDescription>
                  Manage and customize your therapy personas for personalized experiences.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild className="w-full">
                  <Link href="/persona-dashboard">
                    Manage Personas
                  </Link>
                </Button>
              </CardContent>
            </Card>

            {/* Interactive Chatbot */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <MessageSquare className="h-6 w-6 text-green-500" />
                  <CardTitle>Interactive Chatbot</CardTitle>
                </div>
                <CardDescription>
                  Chat with AI-powered therapy assistant for guidance and support.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild className="w-full">
                  <Link 
                    href="https://soulscript01.vercel.app" 
                    target="_blank"
                    className="flex items-center justify-center space-x-2"
                  >
                    <span>Start Chat</span>
                    <ExternalLink className="h-4 w-4" />
                  </Link>
                </Button>
              </CardContent>
            </Card>

            {/* Blogs */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <BookOpen className="h-6 w-6 text-orange-500" />
                  <CardTitle>Mental Health Blogs</CardTitle>
                </div>
                <CardDescription>
                  Read insightful articles and share your own mental health journey.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex space-x-2">
                  <Button asChild variant="outline" className="flex-1">
                    <Link href="/blogs">
                      Read Blogs
                    </Link>
                  </Button>
                  <Button asChild className="flex-1">
                    <Link href="/blogs/new" className="flex items-center justify-center space-x-1">
                      <PlusCircle className="h-4 w-4" />
                      <span>Write</span>
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Profile */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <User className="h-6 w-6 text-indigo-500" />
                  <CardTitle>Your Profile</CardTitle>
                </div>
                <CardDescription>
                  Update your personal information and preferences.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild variant="outline" className="w-full">
                  <Link href="/profile">
                    Edit Profile
                  </Link>
                </Button>
              </CardContent>
            </Card>

            {/* Settings */}
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center space-x-2">
                  <Settings className="h-6 w-6 text-gray-500" />
                  <CardTitle>Account Settings</CardTitle>
                </div>
                <CardDescription>
                  Manage your account security and preferences.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button asChild variant="outline" className="w-full">
                  <Link href="/settings">
                    Open Settings
                  </Link>
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Your latest interactions with SoulScript tools
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center space-x-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <BookOpen className="h-5 w-5 text-purple-500" />
                  <div className="flex-1">
                    <p className="font-medium">New journal entry</p>
                    <p className="text-sm text-gray-500">2 hours ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <MessageSquare className="h-5 w-5 text-green-500" />
                  <div className="flex-1">
                    <p className="font-medium">Chat session completed</p>
                    <p className="text-sm text-gray-500">1 day ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <User className="h-5 w-5 text-blue-500" />
                  <div className="flex-1">
                    <p className="font-medium">Persona updated</p>
                    <p className="text-sm text-gray-500">3 days ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </AuthRequired>
  )
}
