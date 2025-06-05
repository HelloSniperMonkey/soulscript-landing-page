# SoulScript - Firebase Authentication

## Authentication Setup

This project uses [Firebase Authentication](https://firebase.google.com/docs/auth) for user authentication. Follow these steps to set up authentication:

1. Create a Firebase project at https://console.firebase.google.com/
2. Enable Authentication in your Firebase project:
   - Go to Authentication > Sign-in method
   - Enable Email/Password and Google sign-in providers
3. Get your Firebase configuration:
   - Go to Project Settings > General
   - Find your Firebase SDK snippet (Config)
   - Copy the configuration values

4. Set up Firebase Admin SDK (for server-side authentication):
   - Go to Project Settings > Service accounts
   - Click "Generate new private key" 
   - Download the JSON file with your service account credentials

5. Create a `.env.local` file in the root of your project by copying the `example.env.local` file:
   ```
   cp example.env.local .env.local
   ```

6. Update the `.env.local` file with your actual Firebase configuration:
   ```
   NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
   NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
   ```

   **Note**: This project now uses only Firebase Client SDK. Admin SDK configuration is no longer required.

## Authentication Features

- **Sign In / Sign Up**: Pre-built pages at `/sign-in` and `/sign-up`
- **User Profile**: Access your profile at `/profile`
- **Account Settings**: Manage your account at `/settings`
- **Protected Routes**: The following routes require authentication:
  - `/persona-dashboard`
  - `/profile`
  - `/settings`
  - `/blogs/new`

## Using Authentication in Components

You can use the auth context in your components:

```tsx
import { useAuth } from "@/context/auth-context"

export default function MyComponent() {
  const { isLoggedIn, user, login, logout, userButton } = useAuth()
  
  return (
    <div>
      {isLoggedIn ? (
        <>
          <p>Welcome, {user?.firstName}!</p>
          <button onClick={logout}>Sign Out</button>
        </>
      ) : (
        <button onClick={login}>Sign In</button>
      )}
    </div>
  )
}
```

## Protecting Routes

To protect a route, wrap the component with the `AuthRequired` component:

```tsx
import AuthRequired from "@/components/auth-required"

export default function ProtectedPage() {
  return (
    <AuthRequired>
      <div>This content is only visible to authenticated users</div>
    </AuthRequired>
  )
}
```
