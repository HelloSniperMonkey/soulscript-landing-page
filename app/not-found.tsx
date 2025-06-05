import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function NotFound() {
  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center text-white p-4">
      <div className="text-center max-w-md">
        <h1 className="text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-500 to-purple-500 mb-6">
          404
        </h1>
        <h2 className="text-2xl font-bold mb-4">Page Not Found</h2>
        <p className="text-gray-400 mb-8">The page you are looking for doesn't exist or has been moved.</p>
        <Link href="/">
          <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white border-0">
            Return Home
          </Button>
        </Link>
      </div>
    </div>
  )
}
