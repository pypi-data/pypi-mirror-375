from .slack_connector import SlackConnector

activate = False

if activate:
    from .license_manager import LicenseManager
    __all__ = ["SlackConnector", "LicenseManager"]

    # Global license manager instance
    _license_manager = LicenseManager()

    def activate_license(api_key: str, license_key: str) -> bool:
        """Activate the SDK with API key and license key"""
        return _license_manager.activate(api_key, license_key)

    def check_license() -> bool:
        """Check if license is valid"""
        return _license_manager.is_valid()

__all__ = ["SlackConnector"]