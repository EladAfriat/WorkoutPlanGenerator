# 🔐 Authentication System Setup Guide

This guide will help you set up the authentication system with email verification for your Workout Plan Generator app.

## Table of Contents

1. [Quick Start (Skip Email)](#quick-start)
2. [Full Setup (With Email)](#full-setup)
3. [Database Setup (Supabase)](#database-setup)
4. [Email Setup (SendGrid)](#email-setup)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### For Testing Without Email Verification

The app works perfectly without email verification! Here's the minimum setup:

1. **Set up Supabase database** (see Database Setup below)
2. **Create `.env` file** with only Supabase credentials
3. **Run the app** - everything works except email verification

**Skip to [Database Setup](#database-setup) section below.**

---

## Full Setup

### Requirements

- ✅ Supabase account (free) - for database
- ✅ SendGrid account (free) - for email verification (optional)
- ✅ Python 3.8+
- ✅ Streamlit Cloud account (for deployment)

---

## Database Setup

### Step 1: Create Supabase Account

1. Go to https://supabase.com
2. Sign up (free account)
3. Create new project:
   - Name: `workout-plan-generator`
   - Database password: Create a strong password (save it!)
   - Region: Choose closest to you
   - Wait 2-3 minutes for setup

### Step 2: Create Database Tables

1. In Supabase, go to **SQL Editor** → **New query**
2. Copy and paste the SQL from `database_schema.sql`
3. Click **"Run"** to execute

### Step 3: Get API Keys

1. Go to **Settings** → **API**
2. Copy:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon/public key**: `eyJ...` (long string)

---

## Email Setup

### Step 1: Create SendGrid Account

1. Go to https://sendgrid.com
2. Sign up for free account (100 emails/day free tier)
3. Verify your email address

### Step 2: Create API Key

1. Go to **Settings** → **API Keys**
2. Click **"Create API Key"**
3. Name: `workout-app-key`
4. Select **"Full Access"** or **"Custom Access"** (with Mail Send enabled)
5. Click **"Create & View"**
6. **⚠️ COPY THE KEY IMMEDIATELY!** (starts with `SG.`)

**Note:** If you can't select permissions in the UI, you can skip email setup for now (see Quick Start above).

### Step 3: Verify Sender Email

1. Go to **Settings** → **Sender Authentication**
2. Click **"Verify a Single Sender"**
3. Fill in the form:
   - **From Email**: Your email address
   - **From Name**: Workout Plan Generator
   - Complete all required fields
4. Check your email and verify the sender
5. Copy the verified email address

---

## Configuration

### Step 1: Create `.env` File

Create a file named `.env` in your project root:

```env
# Supabase Configuration (REQUIRED)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# SendGrid Configuration (OPTIONAL - leave empty to skip email)
SENDGRID_API_KEY=your-sendgrid-api-key-here
SENDGRID_FROM_EMAIL=your-verified-email@example.com

# App Configuration
APP_URL=http://localhost:8501
```

**For Streamlit Cloud**, add these in:
- App dashboard → **Settings** → **Secrets** tab
- Use TOML format:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
SENDGRID_API_KEY = "your-sendgrid-api-key-here"
SENDGRID_FROM_EMAIL = "your-verified-email@example.com"
APP_URL = "https://your-app-name.streamlit.app"
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Test the Setup

1. Run: `streamlit run src/streamlit_app.py`
2. Try signing up with your email
3. If email is configured: Check email for verification link
4. If email not configured: Account works but no verification email

---

## Troubleshooting

### Database Connection Fails

- Check `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Verify Supabase project is active
- Check internet connection

### Email Not Sending

- Verify `SENDGRID_API_KEY` is correct
- Check `SENDGRID_FROM_EMAIL` is verified in SendGrid
- Check SendGrid activity log
- Free tier: 100 emails/day limit

### SendGrid API Key Creation Issues

- If UI doesn't work: Skip email setup for now
- App works without email verification
- Can add email later when needed

### Verification Link Not Working

- Check `APP_URL` is correct (your Streamlit Cloud URL)
- Links expire after 24 hours
- Make sure token is saved in database

---

## Development Mode

If database/email not configured:
- App uses local storage (session state)
- Accounts auto-verify (no email needed)
- Data resets on Streamlit restart
- Good for testing only

---

## What's Implemented

- ✅ User sign up with email and password
- ✅ Email verification (if SendGrid configured)
- ✅ User login/logout
- ✅ Password hashing (secure)
- ✅ Database storage (Supabase)
- ✅ User data collection
- ✅ Workout preferences saved per user

---

## Need Help?

- Supabase Docs: https://supabase.com/docs
- SendGrid Docs: https://docs.sendgrid.com
- Streamlit Secrets: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management

