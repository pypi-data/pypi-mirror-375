from django.apps import AppConfig, apps
from django.db.models.signals import post_migrate

class SocialAuthPipelineCMSConfig(AppConfig):
    name = "fullname_plugin"
    verbose_name = "social_auth_pipeline_config"

    plugin_app = {
        'settings_config': {
            'cms.djangoapp': {
                'common': {'relative_path': 'settings.common'},
                'production': {'relative_path': 'settings.production'},
            }
        },
    }

    def ready(self):
        from django.conf import settings

        pipeline = list(getattr(settings, "SOCIAL_AUTH_PIPELINE", ()))
        step = "fullname_plugin.pipeline.set_full_name"
        if step not in pipeline:
            pipeline.append(step)
        settings.SOCIAL_AUTH_PIPELINE = tuple(pipeline)
        print(">>> Pipeline patched after apply_settings:", settings.SOCIAL_AUTH_PIPELINE)
        

class SocialAuthPipelineLMSConfig(AppConfig):
    name = "fullname_plugin"
    verbose_name = "social_auth_pipeline_config"

    plugin_app = {
        'settings_config': {
           'lms.djangoapp': {
                "lms": {"relative_path": "settings.lms"},
                'common': {'relative_path': 'settings.common'},
                'production': {'relative_path': 'settings.production'},
            },
        },
    }
    def ready(self):
        from django.conf import settings

        def patch_pipeline(**kwargs):

            pipeline = list(getattr(settings, "SOCIAL_AUTH_PIPELINE", ()))
            step = "fullname_plugin.pipeline.set_full_name"
            if step not in pipeline:
                pipeline.append(step)
            settings.SOCIAL_AUTH_PIPELINE = tuple(pipeline)
            print(">>> Pipeline patched after apply_settings:", settings.SOCIAL_AUTH_PIPELINE)
 
        post_migrate.connect(patch_pipeline, weak=False)
