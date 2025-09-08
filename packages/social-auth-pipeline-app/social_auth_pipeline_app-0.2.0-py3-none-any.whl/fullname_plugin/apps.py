from django.apps import AppConfig

class SocialAuthPipelineConfig(AppConfig):
    name = "fullname_plugin"
    verbose_name = "social_auth_pipeline_config"

    plugin_app = {
        'settings_config': {
            'cms.djangoapp': {
                'common': {'relative_path': 'settings.common'},
                'production': {'relative_path': 'settings.production'},
            },
            'lms.djangoapp': {
                'common': {'relative_path': 'settings.common'},
                'production': {'relative_path': 'settings.production'},
            },
        },
    }

