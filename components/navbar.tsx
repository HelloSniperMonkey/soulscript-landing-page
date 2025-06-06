"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Menu, X } from "lucide-react"
import { useAuth } from "@/context/auth-context"

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const { isLoggedIn, login, logout, userButton } = useAuth()

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen)
  }

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-md border-b border-gray-800">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center">
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-500 to-purple-500">
              SoulScript
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            {isLoggedIn && (
              <Link href="/dashboard" className="text-gray-300 hover:text-white transition-colors">
                Dashboard
              </Link>
            )}
            <Link href="/therapists-near-you" className="text-gray-300 hover:text-white transition-colors">
              Find Therapists
            </Link>
            <Link href="/blogs" className="text-gray-300 hover:text-white transition-colors">
              Blogs
            </Link>
          </nav>

          {/* Auth Buttons - Desktop */}
          <div className="hidden md:flex items-center space-x-4">
            {isLoggedIn ? (
              <div className="flex items-center space-x-4">
                <span className="text-white">
                  {userButton()}
                </span>
                <Button variant="ghost" asChild className="text-white hover:bg-purple-900/30">
                  <span>{logout()}</span>
                </Button>
              </div>
            ) : (
              <>
                <Button variant="ghost" asChild className="text-white hover:bg-purple-900/30">
                  <span>{login()}</span>
                </Button>
                <Button asChild className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white border-0">
                  <Link href="/sign-up">Sign Up</Link>
                </Button>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={toggleMenu}
              className="p-2 text-gray-300 hover:text-white focus:outline-none"
              aria-label="Toggle menu"
            >
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-gray-900 border-b border-gray-800">
          <div className="container mx-auto px-4 py-4 space-y-4">
            {isLoggedIn && (
              <Link
                href="/dashboard"
                className="block text-gray-300 hover:text-white py-2"
                onClick={() => setIsMenuOpen(false)}
              >
                Dashboard
              </Link>
            )}
            <Link
              href="/therapists-near-you"
              className="block text-gray-300 hover:text-white py-2"
              onClick={() => setIsMenuOpen(false)}
            >
              Find Therapists
            </Link>
            <Link
              href="/blogs"
              className="block text-gray-300 hover:text-white py-2"
              onClick={() => setIsMenuOpen(false)}
            >
              Blogs
            </Link>

            <div className="pt-4 border-t border-gray-800 flex flex-col space-y-3">
              {isLoggedIn ? (
                <>
                  <div className="flex justify-center py-2">
                    {userButton()}
                  </div>
                  <Button
                    variant="ghost"
                    asChild
                    className="justify-center text-white hover:bg-purple-900/30"
                  >
                    <span>{logout()}</span>
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    variant="ghost"
                    asChild
                    className="justify-center text-white hover:bg-purple-900/30"
                  >
                    <span>{login()}</span>
                  </Button>
                  <Button
                    asChild
                    className="justify-center bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white border-0"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <Link href="/sign-up">Sign Up</Link>
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  )
}
