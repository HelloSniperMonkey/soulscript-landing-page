"use client"

import AuthRequired from "@/components/auth-required"

export default function PersonaDashboardPage() {
  return (
    <AuthRequired>
      <div className="container mx-auto py-20 px-4">
        <div className="mt-16">
          <h1 className="text-3xl font-bold mb-8">Persona Dashboard</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Placeholder cards for the personas */}
            {Array.from({ length: 3 }).map((_, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h3 className="text-xl font-semibold mb-2">Persona {index + 1}</h3>
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                  This is a placeholder for your therapy persona.
                </p>
                <button className="text-blue-600 hover:text-blue-800 font-medium">
                  Select this persona
                </button>
              </div>
            ))}
            
            {/* Add new persona card */}
            <div className="bg-gray-100 dark:bg-gray-700 rounded-lg shadow p-6 border-2 border-dashed border-gray-300 dark:border-gray-600 flex flex-col items-center justify-center">
              <svg
                className="w-12 h-12 text-gray-400 mb-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              <h3 className="text-xl font-semibold mb-1">Create New Persona</h3>
              <p className="text-gray-500 dark:text-gray-400 text-center">
                Add a new therapy persona to customize your experience
              </p>
            </div>
          </div>
        </div>
      </div>
    </AuthRequired>
  )
}
