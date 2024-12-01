from ..config import config
from typing import Set

from discord import Object


def get_timeout_roles(guild) -> Set[Object]:
    role_ids = config.timeout_roles()
    timeout_roles = set()

    # TODO: Check if call to fetch_roles is needed.
    for role_id in role_ids:
        role = guild.get_role(int(role_id))
        if role:
            timeout_roles.add(role_id)

    return {Object(id=timeout_role) for timeout_role in timeout_roles}