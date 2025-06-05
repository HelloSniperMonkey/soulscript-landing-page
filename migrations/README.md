# Supabase Migration Guide

This document explains how to apply database migrations to your Supabase project.

## Adding the clerk_user_id Column

The error "invalid input syntax for type uuid" occurred because Clerk's user IDs are not in UUID format, but the `user_id` column in the `posts` table expects a UUID.

To fix this, we need to add a new `clerk_user_id` column that can store Clerk's user IDs as text strings.

### Option 1: Using Supabase Dashboard

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Paste and run the contents of the `migrations/add_clerk_user_id.sql` file

### Option 2: Using Supabase CLI

If you have the Supabase CLI installed:

```bash
# Login to Supabase CLI
supabase login

# Navigate to project directory
cd /path/to/project

# Apply migration
supabase db push -f migrations/add_clerk_user_id.sql --db-url YOUR_DATABASE_URL
```

## Verifying the Migration

After applying the migration, you can verify it was successful by:

1. Going to the Table Editor in your Supabase dashboard
2. Checking that the `posts` table now has a `clerk_user_id` column
3. Creating a new blog post with the updated code

## Troubleshooting

If you encounter any issues:

- Check that the SQL ran successfully without errors
- Verify the column was added with the correct data type (TEXT)
- Check that the application is correctly using the new column

## Further Steps

Once the migration has been successfully applied, you may want to:

1. Update any other parts of your application that directly query the `posts` table
2. Create appropriate RLS (Row Level Security) policies that use the `clerk_user_id` field
3. Consider if you need any data migration for existing records
