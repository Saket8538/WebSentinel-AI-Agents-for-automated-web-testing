"""
Secure Authentication Manager
Stores and retrieves credentials securely using keyring + Fernet encryption.
Supports auto-login for authenticated testing and session validation.
"""
import os
import time
import json
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path
import keyring
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class SecureAuthManager:
    """
    Manages authentication for browser-based testing.

    Features:
    - Secure credential storage via system keyring
    - Encrypted auth state persistence (cookies)
    - Auto-login flow for testing behind authentication
    - Session validity checking
    """

    def __init__(self, profile_name: str = "test_profile"):
        self.profile_name = profile_name
        self.auth_dir = Path("auth_data") / profile_name
        self.auth_dir.mkdir(parents=True, exist_ok=True)
        self.service_name = f"browser_use_{profile_name}"

    # ── Credential Storage ──────────────────────────────────

    def store_test_credentials(self, site: str, username: str, password: str):
        """Securely store test account credentials in system keyring."""
        keyring.set_password(self.service_name, f"{site}_user", username)
        keyring.set_password(self.service_name, f"{site}_pass", password)
        logger.info(f"Stored credentials for {site}")

    def get_credentials(self, site: str) -> Tuple[str, str]:
        """Retrieve test account credentials from keyring."""
        username = keyring.get_password(self.service_name, f"{site}_user")
        password = keyring.get_password(self.service_name, f"{site}_pass")
        if not username or not password:
            raise ValueError(f"No credentials found for {site}")
        return username, password

    def has_credentials(self, site: str) -> bool:
        """Check if credentials exist for a site."""
        try:
            self.get_credentials(site)
            return True
        except ValueError:
            return False

    # ── Auth State Persistence ──────────────────────────────

    async def save_auth_state(self, context, site: str):
        """Save authentication state (cookies) after successful login."""
        auth_file = self.auth_dir / f"{site}_auth.json"

        # Get cookies from the browser context
        cookies = await context.session.context.cookies()

        auth_data = {
            "cookies": cookies,
            "timestamp": time.time()
        }

        # Encrypt and save
        key = self._get_or_create_key()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(json.dumps(auth_data).encode())
        auth_file.write_bytes(encrypted)
        logger.info(f"Saved auth state for {site}")

    async def load_auth_state(self, context, site: str) -> bool:
        """Load saved authentication state into browser context."""
        auth_file = self.auth_dir / f"{site}_auth.json"

        if not auth_file.exists():
            return False

        try:
            key = self._get_or_create_key()
            fernet = Fernet(key)
            encrypted = auth_file.read_bytes()
            auth_data = json.loads(fernet.decrypt(encrypted).decode())

            # Check freshness (7 days)
            if time.time() - auth_data["timestamp"] > 7 * 24 * 3600:
                logger.info(f"Auth state for {site} is expired (>7 days)")
                return False

            # Load cookies into context
            session = await context.get_session()
            await session.context.add_cookies(auth_data["cookies"])
            logger.info(f"Loaded auth state for {site}")
            return True

        except Exception as e:
            logger.error(f"Failed to load auth state: {e}")
            return False

    def is_auth_state_valid(self, site: str) -> bool:
        """Check if saved auth state exists and is still fresh."""
        auth_file = self.auth_dir / f"{site}_auth.json"
        if not auth_file.exists():
            return False

        try:
            key = self._get_or_create_key()
            fernet = Fernet(key)
            encrypted = auth_file.read_bytes()
            auth_data = json.loads(fernet.decrypt(encrypted).decode())
            return time.time() - auth_data["timestamp"] < 7 * 24 * 3600
        except Exception:
            return False

    # ── Auto-Login Flow ─────────────────────────────────────

    async def auto_login(
        self,
        page,
        site: str,
        login_url: str,
        username_selector: str = 'input[type="text"], input[type="email"], input[name*="user"], input[name*="email"]',
        password_selector: str = 'input[type="password"]',
        submit_selector: str = 'button[type="submit"], input[type="submit"]',
    ) -> bool:
        """
        Perform an automated login using stored credentials.

        Args:
            page: Playwright Page object
            site: Site identifier (used to look up credentials)
            login_url: URL of the login page
            username_selector: CSS selector for username/email field
            password_selector: CSS selector for password field
            submit_selector: CSS selector for submit button

        Returns:
            True if login appeared successful, False otherwise
        """
        try:
            username, password = self.get_credentials(site)
        except ValueError as e:
            logger.error(f"Auto-login failed: {e}")
            return False

        try:
            await page.goto(login_url, wait_until='domcontentloaded', timeout=15000)

            # Find and fill username
            username_field = await page.query_selector(username_selector)
            if not username_field:
                logger.error("Could not find username field")
                return False
            await username_field.fill(username)

            # Find and fill password
            password_field = await page.query_selector(password_selector)
            if not password_field:
                logger.error("Could not find password field")
                return False
            await password_field.fill(password)

            # Submit
            submit_btn = await page.query_selector(submit_selector)
            if submit_btn:
                await submit_btn.click()
            else:
                await page.keyboard.press('Enter')

            # Wait for navigation after login
            await page.wait_for_load_state('domcontentloaded', timeout=10000)

            # Simple heuristic: login succeeded if we're no longer on the login page
            current_url = page.url
            if current_url != login_url:
                logger.info(f"Auto-login to {site} appears successful (navigated away from login page)")
                return True
            else:
                logger.warning(f"Auto-login to {site} may have failed (still on login page)")
                return False

        except Exception as e:
            logger.error(f"Auto-login error: {e}")
            return False

    # ── Private Helpers ─────────────────────────────────────

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key for auth data."""
        key_file = self.auth_dir / ".key"
        if key_file.exists():
            return key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            key_file.write_bytes(key)
            return key