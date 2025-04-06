import logging

from discord import Member, User
from extensions.roulette.config import config

logger = logging.getLogger(__name__)


def is_admin(user: User | Member) -> bool:
    """Returns whether the given user/member has administrator-level privileges."""
    is_user_admin = str(user.id) in config.administrator()
    logger.debug(f"User {user.name}'s admin status: {is_user_admin}")
    return is_user_admin


def is_moderator(member: Member) -> bool:
    """Returns whether the given member has moderator-level privileges."""
    moderator_roles = set(config.moderator())
    is_member_moderator = not moderator_roles.isdisjoint(set([str(role.id) for role in member.roles]))
    logger.debug(f"User {member.name}'s mod status: {is_member_moderator}")
    return is_member_moderator


def is_protected(member: Member) -> bool:
    """Returns whether the given member should be protected against (immune to) negative rolls."""
    protected_roles = set(config.protected())
    is_member_protected = not protected_roles.isdisjoint(set([str(role.id) for role in member.roles]))
    logger.debug(f"Member {member.name}'s protected status: {is_member_protected}")
    return is_member_protected
