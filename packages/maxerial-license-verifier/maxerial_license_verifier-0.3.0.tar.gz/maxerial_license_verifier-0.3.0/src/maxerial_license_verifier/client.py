import os
from typing import Optional, List

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
        self.features: List[str] = []

    def _get_activation_url(self) -> str:
        endpoint = self.server_endpoint
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        return f"http://{self.server_ip}:{self.server_port}{endpoint}"

    def verify_license(self, timeout_seconds: float = 5.0) -> bool:
        """Call the activation server with the license file path.

        GET to /api/verify_license with query param 'path' containing Windows path to license file.
        On HTTP success, sets verified to True. Returns True if request succeeded.
        Parses response with 'status', 'returnCode', and 'features' fields.
        """
        url = self._get_activation_url()
        try:
            response = requests.get(url, params={"path": self.license_file_path}, timeout=timeout_seconds)
            response.raise_for_status()
        except requests.RequestException as exc:
            self.verified = False
            self.features = []
            raise RuntimeError(f"Failed to contact activation server at {url}: {exc}") from exc

        # Parse the server response format: {"features": [...], "message": "...", "returnCode": 0/1, "status": "valid/invalid"}
        is_valid = False
        features = []
        try:
            data = response.json()
            if isinstance(data, dict):
                status = data.get("status", "").lower()
                return_code = data.get("returnCode")
                # Consider valid if status is "valid" and returnCode is 0
                is_valid = status == "valid" and return_code == 0
                # Extract features array
                features = data.get("features", [])
                if not isinstance(features, list):
                    features = []
        except ValueError:
            # Not JSON; treat as invalid
            pass

        self.verified = is_valid
        self.features = features
        return is_valid

    def check_feature(self, feature_name: str) -> bool:
        """Check if the provided feature is present in the license.

        Requires self.verified to be True.
        Uses features array from the API response.
        """
        if not self.verified:
            raise RuntimeError("License not verified. Call verify_license() first.")

        target = feature_name.strip().lower()
        # Check if feature exists in the features array (case-insensitive)
        return any(feature.lower() == target for feature in self.features)
