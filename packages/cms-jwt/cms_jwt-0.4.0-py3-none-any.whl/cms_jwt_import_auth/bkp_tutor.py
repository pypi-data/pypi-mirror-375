from tutor import hooks

def register():
    # Ensure the Django app is present in the image
    hooks.Filters.CMS_EXTRA_REQUIREMENTS.add_item("edx-drf-extensions")
    # If your Django app is published to pip, add it here too:
    # hooks.Filters.CMS_EXTRA_REQUIREMENTS.add_item("cms-jwt-import-auth>=0.1.0")

    # Load the Django app + middleware
    hooks.Filters.CMS_EXTRA_APPS.add_item("cms_jwt_import_auth")
    hooks.Filters.CMS_EXTRA_MIDDLEWARE.add_item(
        "cms_jwt_import_auth.middleware.ImportJWTOrSessionMiddleware"
    )

    # Optional settings patch
    def _patch(settings):
        settings.setdefault("REST_FRAMEWORK", {})
        settings["REST_FRAMEWORK"]["DEFAULT_AUTHENTICATION_CLASSES"] = (
            "edx_rest_framework_extensions.auth.jwt.authentication.JwtAuthentication",
            "rest_framework.authentication.SessionAuthentication",
        )
        settings.setdefault("JWT_AUTH", {})
        settings["JWT_AUTH"].update({
            "JWT_ISSUER": "https://campus-dev.nextere.com/oauth2",
            "JWT_AUDIENCE": "openedx",
        })
    hooks.Filters.CMS_EXTRA_SETTINGS.add_item(_patch)

