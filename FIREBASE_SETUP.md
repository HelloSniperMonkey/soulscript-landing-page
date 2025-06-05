# Firebase Auth Migration - Setup Guide

## Overview
This project has been migrated from Clerk Auth to Firebase Authentication. This guide will help you set up Firebase Auth for your SoulScript application.

## 🔥 Firebase Project Setup

### 1. Create a Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter your project name (e.g., "soulscript-app")
4. Enable Google Analytics (optional)
5. Click "Create project"

### 2. Enable Authentication
1. In your Firebase project, go to **Authentication** in the left sidebar
2. Click **Get started**
3. Go to the **Sign-in method** tab
4. Enable the following providers:
   - **Email/Password**: Click to enable
   - **Google**: Click to enable, configure OAuth consent screen

### 3. Get Firebase Configuration
1. Go to **Project Settings** (gear icon)
2. Scroll down to "Your apps" section
3. Click **Web app** icon (`</>`)
4. Register your app with a nickname
5. Copy the `firebaseConfig` object values

### 4. Set up Firebase Admin SDK
1. In **Project Settings**, go to **Service accounts** tab
2. Click **Generate new private key**
3. Download the JSON file (keep it secure!)
4. Extract the required values from the JSON file

## 🔧 Environment Configuration

Create a `.env.local` file in your project root:

```bash
cp example.env.local .env.local
```

Fill in your Firebase configuration:

```env
# Firebase Client Configuration (from Firebase Console > Project Settings)
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyC...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abc123
```

⚠️ **Important**: Never commit your `.env.local` file to version control!

**Note**: This project uses Firebase Client SDK only. Firebase Admin SDK has been removed to simplify the architecture and authentication is handled entirely on the client side.

## 📱 Features Implemented

### Authentication Features
- ✅ Email/Password sign-up and sign-in
- ✅ Google OAuth sign-in
- ✅ User profile management
- ✅ Protected routes
- ✅ Session management
- ✅ Client-side authentication

### Components Updated
- ✅ `AuthProvider` context
- ✅ `AuthRequired` component
- ✅ Sign-in and Sign-up pages
- ✅ Navbar with user authentication
- ✅ Profile and Settings pages

## 🛠 Usage

### In Components
```tsx
import { useCurrentUser } from "@/hooks/use-current-user"

export default function MyComponent() {
  const { user, loading, error } = useCurrentUser()
  
  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  
  return (
    <div>
      {user ? (
        <>
          <p>Welcome, {user.displayName}!</p>
          <p>Email: {user.email}</p>
        </>
      ) : (
        <p>Please sign in</p>
      )}
    </div>
  )
}
```

### Protecting Routes
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

### API Route Protection
```tsx
import { NextResponse } from 'next/server'
import type { NextRequest } from "next/server"

export async function GET(req: NextRequest) {
  try {
    // Since we've moved to client-side authentication,
    // authentication checks are now handled on the client side
    // Server-side routes can be used for public data or other operations
    return NextResponse.json({ message: "API endpoint working" })
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
  } catch (error) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
  }
}
```

## 🚀 Getting Started

1. Complete the Firebase setup above
2. Install dependencies: `pnpm install`
3. Set up your `.env.local` file
4. Start the development server: `pnpm dev`
5. Navigate to `http://localhost:3000`
6. Test sign-up/sign-in functionality

## 🔒 Security Considerations

- Environment variables are properly configured
- Private keys are securely stored
- Admin SDK is only used on the server
- Client-side authentication uses Firebase Auth SDK
- Protected routes require valid authentication

## 📚 Additional Resources

- [Firebase Auth Documentation](https://firebase.google.com/docs/auth)
- [Next.js with Firebase](https://firebase.google.com/docs/web/setup)
- [React Firebase Hooks](https://github.com/CSFrequency/react-firebase-hooks)

## 🆘 Troubleshooting

### Common Issues

1. **"Firebase config is invalid"**
   - Check your environment variables
   - Ensure all Firebase config values are correct

2. **"Authentication failed"**
   - Verify your Firebase project has Auth enabled
   - Check if sign-in methods are enabled

3. **"Admin SDK error"**
   - Ensure service account JSON values are correct
   - Check private key formatting (include `\n` for line breaks)

4. **Build errors**
   - Make sure all dependencies are installed
   - Check for TypeScript errors: `pnpm build`
