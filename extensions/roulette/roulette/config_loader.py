import logging
import requests
import toml
import sys

from cerberus import Validator
from typing import Tuple, Set

# TODO: Ablate this file and move all configurations to be locally defined.

_SCHEMA = {
    'acl': {
        'type': 'dict',
        'schema': {
            'channels': {
                'type': 'list',
                'schema': {'type': 'string'}
            },
            'protected': {
                'type': 'list',
                'schema': {'type': 'string'}
            },
            'moderator': {
                'type': 'list',
                'schema': {'type': 'string'}
            },
            'administrator': {
                'type': 'list',
                'schema': {'type': 'string'}
            }
        }
    },
    'messages': {
        'type': 'dict',
        'schema': {
            'timeout_affected_messages_self': {
                'type': 'list',
                'schema': {'type': 'string'}
            },
            'timeout_affected_messages_other': {
                'type': 'list',
                'schema': {'type': 'string'}
            },
            'timeout_protected_messages_self': {
                'type': 'list',
                'schema': {'type': 'string'}
            },
            'timeout_protected_messages_other': {
                'type': 'list',
                'schema': {'type': 'string'}
            }
        }
    }
}
_VALIDATOR = Validator(_SCHEMA, require_all=True)
_VALIDATOR.allow_unknown = True

logger = logging.getLogger("roulette")


class Config:

    def __init__(self, res):
        self._channels: Set[str] = set([channel.strip() for channel in res["acl"]["channels"]])
        self._match_patterns: Tuple[str] = tuple(res["acl"]["match_patterns"])
        self._protected: Set[str] = set([role.strip() for role in res["acl"]["protected"]])
        self._moderators: Set[str] = set([role.strip() for role in res["acl"]["moderator"]])
        self._administrators: Set[str] = set([user_id.strip() for user_id in res["acl"]["administrator"]])

        self._timeout_affected_messages_self: Tuple[str] = tuple(res["messages"]["timeout_affected_messages_self"])
        self._timeout_affected_messages_other: Tuple[str] = tuple(res["messages"]["timeout_affected_messages_other"])
        self._timeout_protected_messages_self: Tuple[str] = tuple(res["messages"]["timeout_protected_messages_self"])
        self._timeout_protected_messages_other: Tuple[str] = tuple(res["messages"]["timeout_protected_messages_other"])

    @property
    def channels(self):
        return self._channels

    @property
    def match_patterns(self):
        return self._match_patterns

    @property
    def protected(self):
        return self._protected

    @property
    def moderators(self):
        return self._moderators

    @property
    def administrators(self):
        return self._administrators

    @property
    def timeout_affected_messages_self(self):
        return self._timeout_affected_messages_self

    @property
    def timeout_affected_messages_other(self):
        return self._timeout_affected_messages_other

    @property
    def timeout_protected_messages_self(self):
        return self._timeout_protected_messages_self

    @property
    def timeout_protected_messages_other(self):
        return self._timeout_protected_messages_other


def load_config() -> Config:
    try:
        raw_config = requests.get("https://raw.githubusercontent.com/Moe-and-Friends/Configurations/main/roulette2.toml")
        config = toml.loads(raw_config.text)
        if not _VALIDATOR.validate(config):
            logger.critical(_VALIDATOR.errors)
            logger.critical("Remote schema is invalid, now exiting...")
            sys.exit(1)

        return Config(config)

    except:
        # TODO: Tighten exception catch states
        logger.critical("Unable to fetch remote config, now exiting...")
        sys.exit(1)
