import logging
import random

from . import stats
from ..action.timeout import Timeout
from ..config import config
from ..extensions import datetime_ext

from datetime import timedelta
from discord import Member, Message
from extensions.roulette.roll import permissions

logger = logging.getLogger(__name__)


async def native_timeout(timeout: Timeout,
                         message: Message,
                         target: Member):
    # Duration as a pure timedelta object can contain seconds; round to nearest minutes.
    duration = timeout.generate_duration()
    duration_label = datetime_ext.convert_seconds_to_display_str(int(duration.total_seconds()))
    logger.info(f"Rolled timeout of length {duration} for {target.name}")

    is_self_target = target == message.author
    logger.debug(f"Message is targeting self: {is_self_target}")

    # If target is protected, respond with a safe message and return immediately.
    if permissions.is_protected(target) or permissions.is_moderator(target) or permissions.is_admin(target):
        logger.debug("Responding with protected message.")
        try:
            responses = timeout.responses.unaffected_self if is_self_target \
                else timeout.responses.unaffected_other
        except AttributeError:  # Catch access on None object (timeout.responses)
            responses = config.timeout_responses_default().unaffected_self if is_self_target \
                else timeout.responses.unaffected_other
        reply = random.choice(responses)
        await message.reply(reply.format(user_name=target.display_name,
                                         duration_label=duration_label))
        return

    if duration > timedelta(days=28):
        logger.warning(f"Received a mute for {duration_label}. This duration is currently unsupported.")
        await message.reply("Sorry, something went wrong. Please contact an administrator!")
        return

    # TODO: Refactor this into temporary_role logic.
    # During deployment testing, apply the role silently to users. We assume the role doesn't actually do
    # anything - we just want to verify with audit logs that this is actually working.
    # try:
    #     if await self._apply_timeout_roles(target, duration_label):
    #        await self._record_timeout_in_redis(duration, target)
    #        self.logger.info(f"Applied timeout role to user {target.id} ({target.name})")
    # except RuntimeError as e:
    #   self.logger.critical(e)
    # await message.reply("Sorry, something went wrong. Please contact an administrator!")
    # return

    await target.timeout(duration, reason=f"Timed out for {duration_label} via Roulette")
    logger.info(f"Timed {target.name} out for {duration_label}")

    logger.debug("Responding with affected message.")
    try:
        responses = timeout.responses.affected_self if is_self_target \
            else config.timeout_responses_default().affected_self
    except AttributeError:  # Catch access on None object (timeout.responses)
        responses = timeout.responses.affected_other if is_self_target \
            else config.timeout_responses_default().affected_other
    reply = random.choice(responses)
    await message.reply(reply.format(user_name=target.display_name,
                                     duration_label=duration_label))

    stats.timeout_record_stats(duration, message)
