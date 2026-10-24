"""ColdChain 360 - Initial Administrator Provisioning CLI Script.

Secure, repeatable, and idempotent administrative user provisioning tool.
Assigns the 'admin' role server-side directly in the database.

Usage:
  1. Via CLI arguments:
     python backend/scripts/provision_admin.py --email admin@example.com --password SecurePassword123! --name "Vikramaditya Rao"

  2. Via environment variables (preferred for CI/CD and secure environments):
     $env:ADMIN_EMAIL="admin@example.com"
     $env:ADMIN_PASSWORD="SecurePassword123!"
     $env:ADMIN_NAME="Vikramaditya Rao"
     python backend/scripts/provision_admin.py

  3. As a module:
     python -m backend.scripts.provision_admin --email admin@example.com --password SecurePassword123!
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional, Tuple

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlalchemy import select
from sqlalchemy.orm import Session
from models.User import User as UserModel
from services.auth import get_password_hash
from db.session import SessionLocal, check_db_configured


def validate_credentials(email: str, password: str) -> Optional[str]:
    """Validate email format and password strength requirements."""
    if not email or "@" not in email or "." not in email:
        return "Invalid email address format."
    if not password or len(password) < 8:
        return "Password must be at least 8 characters long."
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one numeric digit."
    if not any(c.isalpha() for c in password):
        return "Password must contain at least one alphabetical letter."
    return None


def provision_admin(
    email: str,
    password: str,
    name: Optional[str] = None,
    force_upgrade: bool = False,
    db: Optional[Session] = None,
) -> Tuple[bool, str, Optional[int]]:
    """Idempotently provision an administrative user in the database.

    Returns:
        (success: bool, message: str, user_id: Optional[int])
    """
    clean_email = email.lower().strip()

    validation_err = validate_credentials(clean_email, password)
    if validation_err:
        return False, validation_err, None

    should_close = False
    if db is None:
        check_db_configured()
        db = SessionLocal()
        should_close = True

    try:
        # Check if user already exists
        existing_user = db.execute(
            select(UserModel).where(UserModel.email == clean_email)
        ).scalar_one_or_none()

        if existing_user:
            if existing_user.role == "admin":
                # Idempotent: Admin account already exists and holds admin role
                return (
                    True,
                    f"Administrator account for '{clean_email}' already exists (ID: {existing_user.id}). No changes made.",
                    existing_user.id,
                )
            else:
                # User exists but is not an admin
                if not force_upgrade:
                    return (
                        False,
                        f"User '{clean_email}' exists with role '{existing_user.role}'. "
                        "Refusing to alter permissions without --force-upgrade flag.",
                        existing_user.id,
                    )
                # Force upgrade requested
                existing_user.role = "admin"
                existing_user.hashed_password = get_password_hash(password)
                if name:
                    existing_user.full_name = name
                existing_user.is_active = True
                db.commit()
                db.refresh(existing_user)
                return (
                    True,
                    f"Existing user '{clean_email}' successfully promoted to 'admin' role (ID: {existing_user.id}).",
                    existing_user.id,
                )

        # Create new admin user
        hashed = get_password_hash(password)
        new_admin = UserModel(
            email=clean_email,
            hashed_password=hashed,
            role="admin",  # Server-side enforced admin role
            full_name=name or "System Administrator",
            clearance_level="Chief Dispatcher · National Ops",
            organization="ColdChain 360 HQ",
            is_active=True,
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)

        return (
            True,
            f"Initial administrator '{clean_email}' provisioned successfully (ID: {new_admin.id}).",
            new_admin.id,
        )

    except Exception as e:
        db.rollback()
        return False, f"Database provisioning error: {e}", None
    finally:
        if should_close:
            db.close()


def main():
    parser = argparse.ArgumentParser(description="Provision initial admin user for ColdChain 360")
    parser.add_argument("--email", help="Admin email address (or env ADMIN_EMAIL)")
    parser.add_argument("--password", help="Admin password (or env ADMIN_PASSWORD)")
    parser.add_argument("--name", help="Admin full name (or env ADMIN_NAME)")
    parser.add_argument(
        "--force-upgrade",
        action="store_true",
        help="Promote an existing non-admin user to admin role",
    )

    args = parser.parse_args()

    email = args.email or os.getenv("ADMIN_EMAIL")
    password = args.password or os.getenv("ADMIN_PASSWORD")
    name = args.name or os.getenv("ADMIN_NAME")

    if not email:
        if sys.stdin.isatty():
            try:
                email = input("Enter admin email address: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nOperation cancelled.", file=sys.stderr)
                sys.exit(1)
        if not email:
            print("ERROR: Admin email must be provided via --email or ADMIN_EMAIL environment variable.", file=sys.stderr)
            sys.exit(1)

    if not password:
        if sys.stdin.isatty():
            import getpass
            try:
                password = getpass.getpass("Enter admin password (min 8 chars, 1 digit, 1 letter): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nOperation cancelled.", file=sys.stderr)
                sys.exit(1)
        if not password:
            print("ERROR: Admin password must be provided via --password or ADMIN_PASSWORD environment variable.", file=sys.stderr)
            sys.exit(1)

    success, message, user_id = provision_admin(
        email=email,
        password=password,
        name=name,
        force_upgrade=args.force_upgrade,
    )

    if success:
        print(f"[SUCCESS] {message}")
        sys.exit(0)
    else:
        print(f"[FAILED] {message}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
