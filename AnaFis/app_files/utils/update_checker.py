"""
GitHub update checker for AnaFis application.
Checks for new releases on GitHub and provides update information.
"""

import json
import urllib.request
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import threading
from app_files.utils.translations.api import get_string


class UpdateChecker:
    """Checks for application updates from GitHub"""

    def __init__(self, repo: str = "CokieMiner/AnaFis"):
        """
        Initialize the update checker

        Args:
            repo: GitHub repository in format 'username/repo'
        """
        self.repo = repo
        self.api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        self.fallback_url = (
            "https://raw.githubusercontent.com/CokieMiner/AnaFis/main/version.json"
        )
        self.last_check_time: Optional[datetime] = None
        self.update_available = False
        self.latest_version: Optional[str] = None
        self.release_url: Optional[str] = None
        self.release_notes: Optional[str] = None
        self.error: Optional[str] = None
        self._initialized = False
        self._checking = False

    def initialize(self) -> None:
        """Initialize the update checker"""
        if self._initialized:
            return

        # Load previous check data from user preferences
        try:
            from .user_preferences import user_preferences

            update_data = user_preferences.get_preference("update_check", {})

            if update_data:
                last_check_str = update_data.get("last_check_time")
                if last_check_str:
                    self.last_check_time = datetime.fromisoformat(last_check_str)
                self.latest_version = update_data.get("latest_version")
                self.update_available = update_data.get("update_available", False)
                self.release_url = update_data.get("release_url")
                self.release_notes = update_data.get("release_notes")
        except Exception as e:
            logging.error(f"Failed to load update check data: {e}")

        self._initialized = True

        # Check if we should auto-check for updates
        from .user_preferences import user_preferences

        if user_preferences.get_preference("auto_check_updates", True):
            # Run in background thread to not block startup
            thread = threading.Thread(target=self.check_for_updates, daemon=True)
            thread.start()

    def check_for_updates(self) -> Dict[str, Any]:
        """
        Check for updates from GitHub

        Returns:
            Dictionary with update status information
        """
        if self._checking:
            return self._get_status_dict()

        self._checking = True
        self.error = None

        try:
            # First try GitHub API
            return self._check_github_api()
        except Exception as github_error:
            logging.warning(f"GitHub API failed: {github_error}")

            try:
                # Fallback to simple version file
                return self._check_fallback_version()
            except Exception as fallback_error:
                logging.error(f"Fallback version check failed: {fallback_error}")

                # Both failed - return error status
                self.error = f"Update check failed: {str(github_error)}"
                self.last_check_time = datetime.now()
                self._save_check_data()

                from app_files import __version__

                return {
                    "error": self.error,
                    "update_available": False,
                    "current_version": __version__,
                    "last_check_time": self.last_check_time.isoformat(),
                    "is_mock": False,
                }
        finally:
            self._checking = False

    def _check_github_api(self) -> Dict[str, Any]:
        """Check for updates using GitHub API"""
        headers = {
            "User-Agent": "AnaFis-Update-Checker",
            "Accept": "application/vnd.github.v3+json",
        }
        req = urllib.request.Request(self.api_url, headers=headers)

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        return self._process_github_response(data)

    def _check_fallback_version(self) -> Dict[str, Any]:
        """Check for updates using fallback version file"""
        headers = {"User-Agent": "AnaFis-Update-Checker", "Cache-Control": "no-cache"}
        req = urllib.request.Request(self.fallback_url, headers=headers)

        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())

        # Format similar to GitHub API response
        formatted_data = {
            "tag_name": data.get("version", "1.0.0"),
            "html_url": data.get(
                "download_url", f"https://github.com/{self.repo}/releases"
            ),
            "body": data.get(
                "release_notes", "Check the repository for release notes."
            ),
        }

        return self._process_github_response(formatted_data)

    def _process_github_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process GitHub API response"""
        # Get current version
        from app_files import __version__

        current_version = __version__

        # Get latest version from response (remove leading 'v' if present)
        latest_version = data.get("tag_name", "").lstrip("v")

        # Record check time and information
        self.last_check_time = datetime.now()
        self.latest_version = latest_version
        self.release_url = data.get("html_url")
        self.release_notes = data.get("body")

        # Compare versions
        self.update_available = self._compare_versions(latest_version, current_version)

        # Save to user preferences
        self._save_check_data()

        result = self._get_status_dict()
        result["current_version"] = current_version
        result["is_mock"] = False

        return result

    def _compare_versions(self, latest: str, current: str) -> bool:
        """
        Compare version strings to determine if an update is available

        Args:
            latest: Latest version string (from GitHub)
            current: Current version string

        Returns:
            True if update is available, False otherwise
        """
        # Clean and normalize version strings
        try:
            # Remove common prefixes and suffixes
            latest_clean = latest.strip().upper()
            current_clean = current.strip()

            # Remove 'V' prefix if present
            if latest_clean.startswith("V"):
                latest_clean = latest_clean[1:]
            if current_clean.startswith("V"):
                current_clean = current_clean[1:]

            # Remove common suffixes like "-PORTABLE", "-BETA", etc.
            suffixes = ["-PORTABLE", "-BETA", "-ALPHA", "-RC"]
            for suffix in suffixes:
                if latest_clean.endswith(suffix):
                    latest_clean = latest_clean.replace(suffix, "")
                if current_clean.upper().endswith(suffix):
                    current_clean = current_clean.upper().replace(suffix, "")

            # Try to extract numeric version parts
            import re

            latest_numbers = re.findall(r"\d+", latest_clean)
            current_numbers = re.findall(r"\d+", current_clean)

            if not latest_numbers or not current_numbers:
                # If we can't extract numbers, do string comparison
                return latest_clean > current_clean

            # Convert to integers and pad to same length
            latest_parts = [int(x) for x in latest_numbers]
            current_parts = [int(x) for x in current_numbers]

            # Pad shorter version with zeros
            while len(latest_parts) < len(current_parts):
                latest_parts.append(0)
            while len(current_parts) < len(latest_parts):
                current_parts.append(0)
            # Compare components
            for l, c in zip(latest_parts, current_parts):
                if l > c:
                    return True
                if l < c:
                    return False

            # If numeric parts are equal, versions are considered equal
            # Suffixes like "-Portable", "-Beta" don't make a version newer
            # if the core version number is the same
            return False

        except Exception as e:
            # If we can't parse the versions, assume no update
            logging.warning(f"Failed to compare versions: {latest} vs {current} - {e}")
            return False

    def _get_status_dict(self) -> Dict[str, Any]:
        """
        Get the current update status as a dictionary

        Returns:
            Dictionary with update status information
        """
        return {
            "update_available": self.update_available,
            "latest_version": self.latest_version,
            "release_url": self.release_url,
            "release_notes": self.release_notes,
            "last_check_time": (
                self.last_check_time.isoformat() if self.last_check_time else None
            ),
            "error": self.error,
        }

    def _save_check_data(self) -> None:
        """Save update check data to user preferences"""
        try:
            from .user_preferences import user_preferences

            user_preferences.set_preference("update_check", self._get_status_dict())
        except Exception as e:
            logging.error(f"Failed to save update check data: {e}")

    def force_check_updates(self) -> Dict[str, Any]:
        """Force an immediate update check, bypassing cache"""
        self._checking = False  # Reset checking flag
        return self.check_for_updates()

    def get_update_status(self) -> Dict[str, Any]:
        """Get current update status without checking"""
        return self._get_status_dict()

    def show_update_dialog(self) -> None:
        """Show update dialog if update is available"""
        if not self.update_available:
            return

        try:
            from tkinter import messagebox
            from app_files.utils.user_preferences import user_preferences

            language = user_preferences.get_preference("language", "pt")

            # Create update dialog
            title = get_string("update_checker", "update_available", language)
            message = f"{get_string('update_checker', 'new_version_available', language)}: v{self.latest_version}\n\n"

            if self.release_notes:
                # Truncate release notes if too long
                notes = (
                    self.release_notes[:300] + "..."
                    if len(self.release_notes) > 300
                    else self.release_notes
                )
                message += f"{get_string('update_checker', 'release_notes', language)}:\n{notes}\n\n"

            message += get_string("update_checker", "visit_download_page", language)

            result = messagebox.askyesno(title, message)
            if result and self.release_url:
                import webbrowser

                webbrowser.open(self.release_url)

        except Exception as e:
            logging.error(f"Error showing update dialog: {e}")


# Create a singleton instance
update_checker = UpdateChecker()
