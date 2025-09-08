def plugin_settings(settings):
    settings.MIDDLEWARE+=[
        "cms_jwt_import_auth.middleware.ImportJWTOrSessionMiddleware",
        ]

