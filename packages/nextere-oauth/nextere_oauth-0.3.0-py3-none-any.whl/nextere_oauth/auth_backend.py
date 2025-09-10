import logging
from social_core.backends.open_id_connect import OpenIdConnectAuth

logger = logging.getLogger(__name__)

class NextereOIDCBackend(OpenIdConnectAuth):
    """
    Subclass of OpenIdConnectAuth that ensures fullname is set
    from given_name + family_name for Nextere OAuth.
    Keeps backend name as 'oidc' to match existing provider.
    """

    name = "oidc"

    def get_user_details(self, response):
        details = super().get_user_details(response)

        given_name = response.get("given_name", "").strip()
        family_name = response.get("family_name", "").strip()

        if given_name or family_name:
            details["fullname"] = f"{given_name} {family_name}".strip()
        elif not details.get("fullname"):
            details["fullname"] = details.get("username") or details.get("email") or "User"

        logger.info("[NextereOIDCBackend] Final user details: %s", details)
        return details
