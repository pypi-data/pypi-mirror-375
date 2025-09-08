
PIPELINE_STEP = "fullname_plugin.pipeline.set_full_name"
def plugin_settings(settings):
    settings.SOCIAL_AUTH_PIPELINE+=[
        "fullname_plugin.pipeline.set_full_name",
        ]
    pipeline = list(getattr(settings, "SOCIAL_AUTH_PIPELINE", []))
    if PIPELINE_STEP not in pipeline:
    # Insert after create_user if it exists, else append at the end
        try:
            idx = pipeline.index("common.djangoapps.third_party_auth.pipeline.associate_by_email_if_oauth")
            pipeline.insert(idx + 1, PIPELINE_STEP)
        except ValueError:
            pipeline.append(PIPELINE_STEP)
        settings.SOCIAL_AUTH_PIPELINE = tuple(pipeline)
