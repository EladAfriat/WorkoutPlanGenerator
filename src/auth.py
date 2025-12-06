"""
Authentication Module
Handles user registration, login, and email verification using Supabase and SendGrid.
"""

import streamlit as st
import bcrypt
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib

# Optional imports - will work without them but features will be disabled
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_supabase_client() -> Optional[Any]:
    """Initialize and return Supabase client."""
    if not SUPABASE_AVAILABLE:
        return None
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        return None
    
    try:
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return None


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def generate_verification_token() -> str:
    """Generate a secure random verification token."""
    return secrets.token_urlsafe(32)


def send_verification_email(email: str, token: str, app_url: str) -> bool:
    """
    Send verification email using SendGrid.
    
    Args:
        email: User's email address
        token: Verification token
        app_url: Base URL of the application
        
    Returns:
        True if email sent successfully, False otherwise
    """
    if not SENDGRID_AVAILABLE:
        return False
    
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    if not sendgrid_api_key:
        return False
    
    try:
        verification_link = f"{app_url}/?token={token}&email={email}"
        
        message = Mail(
            from_email=os.getenv("SENDGRID_FROM_EMAIL", "noreply@workoutapp.com"),
            to_emails=email,
            subject='Verify Your Workout Plan Generator Account',
            html_content=f"""
            <html>
            <body>
                <h2>Welcome to Workout Plan Generator! 💪</h2>
                <p>Thank you for signing up. Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_link}" style="background-color: #1f77b4; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
                <p>Or copy and paste this link into your browser:</p>
                <p>{verification_link}</p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create an account, please ignore this email.</p>
            </body>
            </html>
            """
        )
        
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False


def create_user(email: str, password: str, name: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new user account.
    
    Args:
        email: User's email address
        password: Plain text password (will be hashed)
        name: Optional user name
        
    Returns:
        Dictionary with 'success', 'message', and optionally 'user_id'
    """
    # Validate input
    if not email or not password:
        return {"success": False, "message": "Email and password are required"}
    
    if len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters"}
    
    # Check if user already exists
    supabase = get_supabase_client()
    if not supabase:
        # Fallback to session state storage (for development)
        return create_user_local(email, password, name)
    
    try:
        # Check if email already exists
        existing = supabase.table("users").select("email").eq("email", email.lower()).execute()
        if existing.data:
            return {"success": False, "message": "Email already registered"}
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Generate verification token
        verification_token = generate_verification_token()
        token_expiry = datetime.utcnow() + timedelta(hours=24)
        
        # Create user record
        user_data = {
            "email": email.lower(),
            "password_hash": hashed_password,
            "name": name or "",
            "is_verified": False,
            "verification_token": verification_token,
            "token_expiry": token_expiry.isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("users").insert(user_data).execute()
        
        if result.data:
            user_id = result.data[0].get("id")
            
            # Send verification email
            app_url = os.getenv("APP_URL", "http://localhost:8501")
            email_sent = send_verification_email(email, verification_token, app_url)
            
            return {
                "success": True,
                "message": "Account created! Please check your email for verification.",
                "user_id": user_id,
                "email_sent": email_sent
            }
        else:
            return {"success": False, "message": "Failed to create account"}
            
    except Exception as e:
        return {"success": False, "message": f"Error creating account: {str(e)}"}


def create_user_local(email: str, password: str, name: Optional[str] = None) -> Dict[str, Any]:
    """Fallback: Store user in session state (for development without database)."""
    if 'local_users' not in st.session_state:
        st.session_state.local_users = {}
    
    if email.lower() in st.session_state.local_users:
        return {"success": False, "message": "Email already registered"}
    
    hashed_password = hash_password(password)
    verification_token = generate_verification_token()
    
    st.session_state.local_users[email.lower()] = {
        "email": email.lower(),
        "password_hash": hashed_password,
        "name": name or "",
        "is_verified": False,
        "verification_token": verification_token,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # In local mode, auto-verify for testing
    st.session_state.local_users[email.lower()]["is_verified"] = True
    
    return {
        "success": True,
        "message": "Account created! (Local mode - auto-verified for testing)",
        "email_sent": False
    }


def verify_email_token(email: str, token: str) -> Dict[str, Any]:
    """
    Verify user's email using token.
    
    Args:
        email: User's email address
        token: Verification token
        
    Returns:
        Dictionary with 'success' and 'message'
    """
    supabase = get_supabase_client()
    if not supabase:
        # Fallback to local storage
        return verify_email_token_local(email, token)
    
    try:
        # Find user with matching email and token
        result = supabase.table("users").select("*").eq("email", email.lower()).eq("verification_token", token).execute()
        
        if not result.data:
            return {"success": False, "message": "Invalid or expired verification link"}
        
        user = result.data[0]
        
        # Check if token expired
        if user.get("token_expiry"):
            expiry = datetime.fromisoformat(user["token_expiry"].replace('Z', '+00:00'))
            if datetime.utcnow() > expiry:
                return {"success": False, "message": "Verification link has expired"}
        
        # Check if already verified
        if user.get("is_verified"):
            return {"success": True, "message": "Email already verified"}
        
        # Update user to verified
        supabase.table("users").update({
            "is_verified": True,
            "verification_token": None,
            "token_expiry": None,
            "verified_at": datetime.utcnow().isoformat()
        }).eq("id", user["id"]).execute()
        
        return {"success": True, "message": "Email verified successfully!"}
        
    except Exception as e:
        return {"success": False, "message": f"Error verifying email: {str(e)}"}


def verify_email_token_local(email: str, token: str) -> Dict[str, Any]:
    """Fallback: Verify email in local storage."""
    if 'local_users' not in st.session_state:
        return {"success": False, "message": "Invalid verification link"}
    
    user = st.session_state.local_users.get(email.lower())
    if not user or user.get("verification_token") != token:
        return {"success": False, "message": "Invalid verification link"}
    
    user["is_verified"] = True
    user["verified_at"] = datetime.utcnow().isoformat()
    
    return {"success": True, "message": "Email verified successfully!"}


def login_user(email: str, password: str) -> Dict[str, Any]:
    """
    Authenticate user login.
    
    Args:
        email: User's email address
        password: Plain text password
        
    Returns:
        Dictionary with 'success', 'message', and optionally 'user'
    """
    if not email or not password:
        return {"success": False, "message": "Email and password are required"}
    
    supabase = get_supabase_client()
    if not supabase:
        # Fallback to local storage
        return login_user_local(email, password)
    
    try:
        # Find user by email
        result = supabase.table("users").select("*").eq("email", email.lower()).execute()
        
        if not result.data:
            return {"success": False, "message": "Invalid email or password"}
        
        user = result.data[0]
        
        # Verify password
        if not verify_password(password, user["password_hash"]):
            return {"success": False, "message": "Invalid email or password"}
        
        # Check if email is verified
        if not user.get("is_verified"):
            return {
                "success": False,
                "message": "Please verify your email before logging in. Check your inbox for the verification link."
            }
        
        # Return user data (without password)
        user_data = {
            "id": user["id"],
            "email": user["email"],
            "name": user.get("name", ""),
            "is_verified": user.get("is_verified", False),
            "created_at": user.get("created_at")
        }
        
        return {
            "success": True,
            "message": "Login successful!",
            "user": user_data
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error during login: {str(e)}"}


def login_user_local(email: str, password: str) -> Dict[str, Any]:
    """Fallback: Login using local storage."""
    if 'local_users' not in st.session_state:
        return {"success": False, "message": "Invalid email or password"}
    
    user = st.session_state.local_users.get(email.lower())
    if not user:
        return {"success": False, "message": "Invalid email or password"}
    
    if not verify_password(password, user["password_hash"]):
        return {"success": False, "message": "Invalid email or password"}
    
    if not user.get("is_verified"):
        return {
            "success": False,
            "message": "Please verify your email before logging in."
        }
    
    return {
        "success": True,
        "message": "Login successful!",
        "user": {
            "email": user["email"],
            "name": user.get("name", ""),
            "is_verified": user.get("is_verified", False)
        }
    }


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get currently logged in user from session state."""
    return st.session_state.get("user")


def logout_user():
    """Logout current user."""
    if "user" in st.session_state:
        del st.session_state["user"]


def is_authenticated() -> bool:
    """Check if user is currently authenticated."""
    return "user" in st.session_state and st.session_state.get("user") is not None

