from ..config import config
from typing import Set


class Role:
    def __init__(self, id: int):
        self.id = id


def _get_timeout_roles(guild) -> Set[Role]:
    role_ids_conf = config.timeout_roles()
    role_ids = set()

    for role_id_conf in role_ids_conf:
        role = guild.get_role(int(role_id_conf))
        if role:
            role_ids.add(role_id_conf)

    return {Role(role_id) for role_id in role_ids}


def fetch_timeout_roles(guild) -> Set[Role]:
    return _get_timeout_roles(guild)
