from .license_manager import LicenseManager
from .slack_connector import SlackConnector

__all__ = ["SlackConnector", "LicenseManager"]

# Global license manager instance
_license_manager = LicenseManager()

def activate_license(api_key: str, license_key: str) -> bool:
    """Activate the SDK with API key and license key"""
    return _license_manager.activate(api_key, license_key)

def check_license() -> bool:
    """Check if license is valid"""
    return _license_manager.is_valid()

# Pre-check license on import
#if not _license_manager.is_valid():
#    raise ImportError(
#        "SDK not activated. Please call securaops_mcp_marketplace.activate_license() "
#        "with your API key and license key before using any functionality."
#    )