from django.apps import AppConfig

class CMSJWTImportAuthConfig(AppConfig):
    name = "cms_jwt_import_auth"
    verbose_name = "CMS JWT-or-Session auth for course import"

    plugin_app = {
        'settings_config': {
            'cms.djangoapp': {
                'common': {'relative_path': 'settings.common'},
                'production': {'relative_path': 'settings.production'},
            },
        },
    }

