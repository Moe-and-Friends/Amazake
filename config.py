from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="ROULETTE",
    environments=True,
    load_dotenv=True,
    settings_files=[
        'settings.toml',
        '.secrets.toml',
        'settings.yml',
        '.secrets.yml'
    ],
    validators=[
        Validator("discord_bot_token", must_exist=True, is_type_of=str),
        Validator("remote_config_url", must_exist=True, is_type_of=str),
        Validator("remote_roulette_url", must_exist=True, is_type_of=str),
        Validator("timeout_leaderboard_url", is_type_of=str),
    ]
)

# `envvar_prefix` = export envvars with `export ROULETTE_FOO=bar`.
# `settings_files` = Load these files in the order.
# `environments` = Export `ENV_FOR_DYNACONF=` to set an environment.
