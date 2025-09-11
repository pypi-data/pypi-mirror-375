import os
import xml.etree.ElementTree as ET
from typing import Optional, Set

import requests


class LicenseVerifier:
    """Verify maXerial license via local activation server and check features.

    Initialize with a path to the license XML file.
    """

    def __init__(self, license_file_path: str, server_endpoint: Optional[str] = None, server_ip: Optional[str] = None, server_port: Optional[int] = None) -> None:
        self.license_file_path = license_file_path
        # Default endpoint per API spec
        self.server_endpoint = server_endpoint or "/api/verify_license"
        self.server_ip = server_ip or "127.0.0.1"
        self.server_port = server_port or 61040
        self.verified: bool = False

    def _get_activation_url(self) -> str:
        endpoint = self.server_endpoint
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return f"http://{self.server_ip}:{self.server_port}{endpoint}"

    def verify_license(self, timeout_seconds: float = 5.0) -> bool:
        """Call the activation server with the license file path.

        GET to /api/verify_license with query param 'path' containing Windows path to license file.
        On HTTP success, sets verified to True. Returns True if request succeeded.
        Parses response with 'status' and 'returnCode' fields.
        """
        url = self._get_activation_url()
        try:
            response = requests.get(url, params={"path": self.license_file_path}, timeout=timeout_seconds)
            response.raise_for_status()
        except requests.RequestException as exc:
            self.verified = False
            raise RuntimeError(f"Failed to contact activation server at {url}: {exc}") from exc

        # Parse the server response format: {"message": "...", "returnCode": 0/1, "status": "valid/invalid"}
        is_valid = False
        try:
            data = response.json()
            if isinstance(data, dict):
                status = data.get("status", "").lower()
                return_code = data.get("returnCode")
                # Consider valid if status is "valid" and returnCode is 0
                is_valid = status == "valid" and return_code == 0
        except ValueError:
            # Not JSON; treat as invalid
            pass

        self.verified = is_valid
        return is_valid

    def _windows_to_unix_path(self, windows_path: str) -> str:
        """Convert Windows path to Unix style for local file access."""
        # Replace backslashes with forward slashes
        unix_path = windows_path.replace("\\", "/")
        # Handle Windows drive letters (C: -> /c)
        if len(unix_path) >= 2 and unix_path[1] == ":":
            drive_letter = unix_path[0].lower()
            unix_path = f"/{drive_letter}{unix_path[2:]}"
        return unix_path

    def _extract_features(self, root: ET.Element) -> Set[str]:
        """Extract feature names from LicenseBody/LicenseInfo/Features/Feature elements.

        Returns a set of lower-cased feature strings. Ignores empty entries.
        """
        features: Set[str] = set()

        # Try exact path first
        features_parent = root.find(".//LicenseBody/LicenseInfo/Features")
        if features_parent is not None:
            for child in list(features_parent):
                if child.tag.lower() == "feature":
                    text = (child.text or "").strip()
                    if text:
                        features.add(text.lower())

        # Fallback: in case of different casing (<Features> vs <features>) or structure,
        # gather any <Feature> elements under any <Features>
        if not features:
            for any_features in root.iter():
                if any_features.tag.lower() == "features":
                    for child in list(any_features):
                        if child.tag.lower() == "feature":
                            text = (child.text or "").strip()
                            if text:
                                features.add(text.lower())

        return features

    def check_feature(self, feature_name: str) -> bool:
        """Check if the provided feature is present in the license XML.

        Requires self.verified to be True.
        Uses Unix-style path for local file access.
        """
        if not self.verified:
            raise RuntimeError("License not verified. Call verify_license() first.")

        # Convert Windows path to Unix style for local file access
        unix_path = self._windows_to_unix_path(self.license_file_path)
        
        try:
            tree = ET.parse(unix_path)
            root = tree.getroot()
        except (OSError, ET.ParseError) as exc:
            raise RuntimeError(f"Failed to read or parse license file '{unix_path}': {exc}") from exc

        features = self._extract_features(root)
        target = feature_name.strip().lower()
        return target in features
