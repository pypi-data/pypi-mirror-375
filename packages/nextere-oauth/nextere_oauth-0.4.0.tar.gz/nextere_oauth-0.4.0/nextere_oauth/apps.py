from django.apps import AppConfig

class LMSAuthConfig(AppConfig):
    name = "nextere_oauth"
    verbose_name = "LMS auth config"

    plugin_app = {
        'settings_config': {
            'lms.djangoapp': {
                'common': {'relative_path': 'settings.common'},
                'production': {'relative_path': 'settings.production'},
            },
        },
    }

