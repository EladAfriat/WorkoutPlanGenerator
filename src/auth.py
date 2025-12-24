"""
Authentication Module
Handles user registration, login, and email verification using Supabase and SendGrid.
"""

import streamlit as st
import bcrypt
import secrets
import string
from datetime import datetime, timedelta, timezone
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
            
            # If email service is not configured, auto-verify the user
            if not email_sent:
                # Auto-verify user since email service is not available
                try:
                    supabase.table("users").update({
                        "is_verified": True,
                        "verification_token": None,
                        "token_expiry": None,
                        "verified_at": datetime.utcnow().isoformat()
                    }).eq("id", user_id).execute()
                except Exception as e:
                    # If update fails, continue anyway - user can still log in
                    st.warning(f"Note: Could not auto-verify account: {e}")
            
            return {
                "success": True,
                "message": "Account created! Please check your email for verification." if email_sent else "Account created! You can now log in.",
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
        # If email service is not configured, allow login even if not verified
        sendgrid_configured = bool(os.getenv("SENDGRID_API_KEY"))
        if not user.get("is_verified") and sendgrid_configured:
            return {
                "success": False,
                "message": "Please verify your email before logging in. Check your inbox for the verification link."
            }
        
        # Auto-verify if email service is not configured
        if not user.get("is_verified") and not sendgrid_configured:
            supabase.table("users").update({
                "is_verified": True,
                "verification_token": None,
                "token_expiry": None,
                "verified_at": datetime.utcnow().isoformat()
            }).eq("id", user["id"]).execute()
            user["is_verified"] = True
        
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


def send_password_reset_email(email: str, reset_code: str) -> bool:
    """
    Send password reset email using SendGrid.
    
    Args:
        email: User's email address
        reset_code: 6-digit reset code
        
    Returns:
        True if email sent successfully, False otherwise
    """
    if not SENDGRID_AVAILABLE:
        return False
    
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    if not sendgrid_api_key:
        return False
    
    try:
        app_url = os.getenv("APP_URL", "http://localhost:8501")
        
        message = Mail(
            from_email=os.getenv("SENDGRID_FROM_EMAIL", "noreply@workoutapp.com"),
            to_emails=email,
            subject='Password Reset Code - Workout Plan Generator',
            html_content=f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1f77b4;">🔑 Password Reset Request</h2>
                <p>You requested to reset your password for your Workout Plan Generator account.</p>
                
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; margin: 20px 0;">
                    <p style="margin: 0; font-size: 14px; color: #666;">Your reset code is:</p>
                    <h1 style="color: #1f77b4; font-size: 3rem; letter-spacing: 0.5rem; margin: 10px 0;">{reset_code}</h1>
                    <p style="margin: 0; font-size: 12px; color: #999;">This code expires in 1 hour</p>
                </div>
                
                <p>Enter this code on the password reset page to create a new password.</p>
                
                <p style="color: #999; font-size: 12px; margin-top: 30px;">
                    If you didn't request a password reset, please ignore this email. Your password will remain unchanged.
                </p>
            </body>
            </html>
            """
        )
        
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        if response.status_code == 202:
            return True
        else:
            # Log the error for debugging
            error_body = getattr(response, 'body', 'No error details')
            st.error(f"SendGrid returned status code {response.status_code}. Check SendGrid dashboard for details.")
            return False
    except Exception as e:
        # Log detailed error for debugging
        error_msg = str(e)
        st.error(f"Error sending password reset email: {error_msg}")
        # Check common issues
        if "API key" in error_msg.lower() or "unauthorized" in error_msg.lower():
            st.warning("⚠️ SendGrid API key may be invalid. Check your Streamlit Cloud secrets.")
        elif "sender" in error_msg.lower() or "from_email" in error_msg.lower():
            st.warning("⚠️ SendGrid sender email may not be verified. Check your SendGrid account.")
        return False


def request_password_reset(email: str) -> Dict[str, Any]:
    """
    Request a password reset. Generates a reset code and sends it via email (SendGrid).
    Falls back to displaying code on screen if SendGrid is not configured.
    
    Args:
        email: User's email address
        
    Returns:
        Dictionary with 'success', 'message', and optionally 'reset_code' if email not sent
    """
    if not email:
        return {"success": False, "message": "Email is required"}
    
    supabase = get_supabase_client()
    if not supabase:
        return {"success": False, "message": "Password reset not available in local mode"}
    
    try:
        # Find user by email
        result = supabase.table("users").select("id, email").eq("email", email.lower()).execute()
        
        if not result.data:
            # Don't reveal if email exists (security best practice)
            return {
                "success": True,
                "message": "If an account exists with this email, you will receive a password reset code.",
                "reset_code": None,
                "email_sent": False
            }
        
        user = result.data[0]
        
        # Generate reset code (6-digit number)
        reset_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        
        # Hash the reset code for storage
        reset_token = hashlib.sha256(reset_code.encode()).hexdigest()
        token_expiry = datetime.utcnow() + timedelta(hours=1)  # Code expires in 1 hour
        
        # Store reset token in database (reuse verification_token field)
        supabase.table("users").update({
            "verification_token": reset_token,
            "token_expiry": token_expiry.isoformat()
        }).eq("id", user["id"]).execute()
        
        # Try to send email via SendGrid
        email_sent = send_password_reset_email(email.lower(), reset_code)
        
        if email_sent:
            return {
                "success": True,
                "message": f"✅ Password reset code sent to {email.lower()}. Please check your email (including spam folder).",
                "reset_code": None,  # Don't show code if email sent
                "email_sent": True,
                "email": email.lower()
            }
        else:
            # Check if SendGrid is configured
            sendgrid_configured = bool(os.getenv("SENDGRID_API_KEY"))
            if sendgrid_configured:
                # SendGrid is configured but email failed - DO NOT show code, ask user to check email or try again
                return {
                    "success": False,  # Fail the request - don't show code
                    "message": f"❌ Failed to send email to {email.lower()}. Please check your email (including spam folder) or try again. If the problem persists, check your SendGrid configuration.",
                    "reset_code": None,  # NEVER show code if SendGrid is configured
                    "email_sent": False,
                    "email": email.lower()
                }
            else:
                # SendGrid not configured - only then show code on screen as fallback
                return {
                    "success": True,
                    "message": f"⚠️ Email service not configured. Your reset code is shown below.",
                    "reset_code": reset_code,  # Show code ONLY if email service not configured
                    "email_sent": False,
                    "email": email.lower()
                }
        
    except Exception as e:
        return {"success": False, "message": f"Error generating reset code: {str(e)}"}


def reset_password_with_code(email: str, code: str, new_password: str) -> Dict[str, Any]:
    """
    Reset password using the code.
    
    Args:
        email: User's email address
        code: Reset code (6 digits)
        new_password: New password
        
    Returns:
        Dictionary with 'success' and 'message'
    """
    if not email or not code or not new_password:
        return {"success": False, "message": "Email, code, and new password are required"}
    
    if len(new_password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters"}
    
    if len(code) != 6 or not code.isdigit():
        return {"success": False, "message": "Reset code must be 6 digits"}
    
    supabase = get_supabase_client()
    if not supabase:
        return {"success": False, "message": "Password reset not available in local mode"}
    
    try:
        # Hash the provided code to compare with stored token
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Find user with matching email and reset token
        result = supabase.table("users").select("*").eq("email", email.lower()).eq("verification_token", code_hash).execute()
        
        if not result.data:
            return {"success": False, "message": "Invalid reset code or email"}
        
        user = result.data[0]
        
        # Check if code expired
        if user.get("token_expiry"):
            expiry_str = user["token_expiry"]
            try:
                # Handle both timezone-aware and timezone-naive formats
                if expiry_str.endswith('Z'):
                    expiry = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
                elif '+' in expiry_str or expiry_str.count('-') > 2:
                    expiry = datetime.fromisoformat(expiry_str)
                else:
                    # Timezone-naive format, assume UTC
                    expiry = datetime.fromisoformat(expiry_str)
                
                # Make both timezone-aware for comparison (use UTC)
                now = datetime.now(timezone.utc)
                if expiry.tzinfo is None:
                    expiry = expiry.replace(tzinfo=timezone.utc)
                
                if now > expiry:
                    return {"success": False, "message": "Reset code has expired. Please request a new one."}
            except (ValueError, AttributeError) as e:
                # If parsing fails, log but don't block reset (might be old format)
                st.warning(f"Could not parse expiry date: {e}")
        
        # Update password
        hashed_password = hash_password(new_password)
        
        supabase.table("users").update({
            "password_hash": hashed_password,
            "verification_token": None,  # Clear reset token after use
            "token_expiry": None,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", user["id"]).execute()
        
        return {
            "success": True,
            "message": "Password reset successfully! You can now log in with your new password."
        }
        
    except Exception as e:
        return {"success": False, "message": f"Error resetting password: {str(e)}"}
