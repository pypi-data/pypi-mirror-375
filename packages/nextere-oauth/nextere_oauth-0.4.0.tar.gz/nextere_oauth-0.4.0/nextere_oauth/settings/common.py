def plugin_settings(settings):
    settings.AUTHENTICATION_BACKENDS+=[
        "nextere_oauth.auth_backend.NextereOIDCBackend",
        ]
